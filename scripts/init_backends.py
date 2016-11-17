#!/usr/bin/env python


import yaml
import argparse
import subprocess
import os
import signal
import time
import pwd
import jinja2
import codecs


__author__ = "Anoop P Alias"
__copyright__ = "Copyright Anoop P Alias"
__license__ = "GPL"
__email__ = "anoopalias01@gmail.com"


installation_path = "/opt/nDeploy"  # Absolute Installation Path
backend_config_file = installation_path+"/conf/backends.yaml"
php_fpm_config = installation_path+"/conf/php-fpm.conf"


# Function defs


def control_php_fpm(trigger):
    if "PHP" in backend_data_yaml_parsed:
        php_backends_dict = backend_data_yaml_parsed["PHP"]
        if trigger == "start":
            conf_list = os.listdir("/opt/nDeploy/php-fpm.d")
            for filename in conf_list:
                user, extension = filename.split('.')
                try:
                    pwd.getpwnam(user)
                except KeyError:
                    os.remove("/opt/nDeploy/php-fpm.d/"+filename)
                else:
                    pass
            subprocess.call("sysctl -q -w net.core.somaxconn=4096", shell=True)
            subprocess.call("sysctl -q -w vm.max_map_count=131070", shell=True)
            for path in list(php_backends_dict.values()):
                if os.path.isfile(path+"/sbin/php-fpm"):
                    php_fpm_bin = path+"/sbin/php-fpm"
                else:
                    php_fpm_bin = path+"/usr/sbin/php-fpm"
                subprocess.call(php_fpm_bin+" --prefix "+path+" --fpm-config "+php_fpm_config, shell=True)
        elif trigger == "stop":
            for path in list(php_backends_dict.values()):
                php_fpm_pid = path+"/var/run/php-fpm.pid"
                if os.path.isfile(php_fpm_pid):
                    with open(php_fpm_pid) as f:
                        mypid = f.read()
                    f.close()
                    try:
                        os.kill(int(mypid), signal.SIGQUIT)
                        time.sleep(3)  # Give enough time for all child process to exit
                    except OSError:
                        break
        elif trigger == "reload":
            for path in list(php_backends_dict.values()):
                php_fpm_pid = path+"/var/run/php-fpm.pid"
                if os.path.isfile(path+"/sbin/php-fpm"):
                    php_fpm_bin = path+"/sbin/php-fpm"
                else:
                    php_fpm_bin = path+"/usr/sbin/php-fpm"
                if os.path.isfile(php_fpm_pid):
                        with open(php_fpm_pid) as f:
                            mypid = f.read()
                        try:
                            os.kill(int(mypid), signal.SIGUSR2)
                        except OSError:
                            subprocess.call(php_fpm_bin+" --prefix "+path+" --fpm-config "+php_fpm_config, shell=True)
                        time.sleep(3)
                        try:
                            with open(path + "/var/run/php-fpm.pid") as f:
                                newpid = f.read()
                        except IOError:
                            subprocess.call(php_fpm_bin+" --prefix "+path+" --fpm-config "+php_fpm_config, shell=True)
                        try:
                            os.kill(int(newpid), 0)
                        except OSError:
                            subprocess.call(php_fpm_bin+" --prefix "+path+" --fpm-config "+php_fpm_config, shell=True)
                else:
                        subprocess.call(php_fpm_bin+" --prefix "+path+" --fpm-config "+php_fpm_config, shell=True)
        elif trigger == "secure-php":
            try:
                subprocess.call(['systemctl', '--version'])
                for backend_name in list(php_backends_dict.keys()):
                    systemd_socket_template = installation_path+"/conf/secure-php-fpm.socket.j2"
                    systemd_service_template = installation_path+"/conf/secure-php-fpm.service.j2"
                    systemd_socket_file = "/usr/lib/systemd/system/"+backend_name+"@.socket"
                    systemd_service_file = "/usr/lib/systemd/system/"+backend_name+"@.service"
                    templateLoader = jinja2.FileSystemLoader(installation_path + "/conf/")
                    templateEnv = jinja2.Environment(loader=templateLoader)
                    socket_template = templateEnv.get_template(systemd_socket_template)
                    templateVars = {"PHP-FPM_ROOT_PATH": php_backends_dict.get(backend_name)}
                    socket_generated_config = socket_template.render(templateVars)
                    with codecs.open(systemd_socket_file, "w", 'utf-8') as confout:
                        confout.write(socket_generated_config)
                    service_template = templateEnv.get_template(systemd_service_template)
                    service_generated_config = service_template.render(templateVars)
                    with codecs.open(systemd_service_file, "w", 'utf-8') as confout:
                        confout.write(service_generated_config)
                    os.mknod(installation_path+"/conf/secure-php-enabled")
            except OSError:
                print('secure-php needs systemd . upgrade your cPanel system to CentOS7/CloudLinux7 ')
        else:
            return


backend_data_yaml = open(backend_config_file, 'r')
backend_data_yaml_parsed = yaml.safe_load(backend_data_yaml)
backend_data_yaml.close()


parser = argparse.ArgumentParser(description="Start/Stop various nDeploy backends")
parser.add_argument("control_command")
args = parser.parse_args()
trigger = args.control_command
control_php_fpm(trigger)
