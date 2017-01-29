#!/usr/bin/python
import os
import socket
import yaml
import cgi
import cgitb
import sys
import re


__author__ = "Anoop P Alias"
__copyright__ = "Copyright Anoop P Alias"
__license__ = "GPL"
__email__ = "anoopalias01@gmail.com"


installation_path = "/opt/nDeploy"  # Absolute Installation Path
app_template_file = installation_path+"/conf/apptemplates_subdir.yaml"
cpaneluser = os.environ["USER"]
user_app_template_file = installation_path+"/conf/"+cpaneluser+"_apptemplates_subdir.yaml"
backend_config_file = installation_path+"/conf/backends.yaml"


cgitb.enable()


def close_cpanel_liveapisock():
    """We close the cpanel LiveAPI socket here as we dont need those"""
    cp_socket = os.environ["CPANEL_CONNECT_SOCKET"]
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(cp_socket)
    sock.sendall('<cpanelxml shutdown="1" />')
    sock.close()


close_cpanel_liveapisock()
form = cgi.FieldStorage()


print('Content-Type: text/html')
print('')
print('<html>')
print('<head>')
print('<title>XtendWeb</title>')
print(('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">'))
print(('<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" crossorigin="anonymous"></script>'))
print(('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>'))
print(('<script src="js.js"></script>'))
print(('<link rel="stylesheet" href="styles.css">'))
print('</head>')
print('<body>')
print('<div id="main-container" class="container text-center">')
print('<div class="row">')
print('<div class="col-md-6 col-md-offset-3">')
print('<div class="logo">')
print('<a href="xtendweb.live.py" data-toggle="tooltip" data-placement="bottom" title="Start Over"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span></a>')
print('<h4>XtendWeb</h4>')
print('</div>')
print('<ol class="breadcrumb">')
print('<li><a href="xtendweb.live.py"><span class="glyphicon glyphicon-home"></span></a></li>')
print('<li><a href="xtendweb.live.py">Set Domain</a></li><li class="active">Sub-directory App Settings</li>')
print('</ol>')
print('<div class="panel panel-default">')
if form.getvalue('domain') and form.getvalue('thesubdir'):
    # Get the domain name from form data
    mydomain = form.getvalue('domain')
    thesubdir = form.getvalue('thesubdir')
    if thesubdir.startswith('/'):
        thesubdir = thesubdir[1:]
    if thesubdir.endswith('/'):
        thesubdir = thesubdir[:-1]
    if not thesubdir:
        print('ERROR: Invalid sub-directory name')
        sys.exit(0)
    if not re.match("^[0-9a-zA-Z/_-]*$", thesubdir):
        print("Error: Invalid char in sub-directory name")
        sys.exit(0)
    profileyaml = installation_path + "/domain-data/" + mydomain
    # Get data about the backends available
    if os.path.isfile(backend_config_file):
        with open(backend_config_file, 'r') as backend_data_yaml:
            backend_data_yaml_parsed = yaml.safe_load(backend_data_yaml)
    if os.path.isfile(profileyaml):
        # Get all config settings from the domains domain-data config file
        with open(profileyaml, 'r') as profileyaml_data_stream:
            yaml_parsed_profileyaml = yaml.safe_load(profileyaml_data_stream)
        subdir_apps_dict = yaml_parsed_profileyaml.get('subdir_apps')
        # If there are no entries in subdir_apps_dict or there is no specific config for the subdirectory
        # We do a fresh config
        if subdir_apps_dict:
            if not subdir_apps_dict.get(thesubdir):
                print(('<div class="panel-heading"><h3 class="panel-title">Domain: <strong>'+mydomain+'/'+thesubdir+'</strong></h3></div>'))
                print('<div class="panel-body">')
                print('<form action="subdir_select_app_settings.live.py" method="post">')
                print('<div class="desc">select a BACKEND from the drop down below:</div>')
                print('<select name="backend">')
                for backends_defined in backend_data_yaml_parsed.keys():
                    print(('<option value="'+backends_defined+'">'+backends_defined+'</option>'))
                print('</select>')
                # Pass on the domain name to the next stage
                print(('<input class="hidden" name="domain" value="'+mydomain+'">'))
                print(('<input class="hidden" name="thesubdir" value="'+thesubdir+'">'))
                print('<input class="btn btn-primary" type="submit" value="Submit">')
                print('</form>')
            else:
                # we get the current app settings for the subdir
                the_subdir_dict = subdir_apps_dict.get(thesubdir)
                backend_category = the_subdir_dict.get('backend_category')
                backend_version = the_subdir_dict.get('backend_version')
                backend_path = the_subdir_dict.get('backend_path')
                apptemplate_code = the_subdir_dict.get('apptemplate_code')
                # get the human friendly name of the app template
                if os.path.isfile(app_template_file):
                    with open(app_template_file, 'r') as apptemplate_data_yaml:
                        apptemplate_data_yaml_parsed = yaml.safe_load(apptemplate_data_yaml)
                    apptemplate_dict = apptemplate_data_yaml_parsed.get(backend_category)
                    if os.path.isfile(user_app_template_file):
                        with open(user_app_template_file, 'r') as user_apptemplate_data_yaml:
                            user_apptemplate_data_yaml_parsed = yaml.safe_load(user_apptemplate_data_yaml)
                        user_apptemplate_dict = user_apptemplate_data_yaml_parsed.get(backend_category)
                    else:
                        user_apptemplate_dict = {}
                    if apptemplate_code in apptemplate_dict.keys():
                        apptemplate_description = apptemplate_dict.get(apptemplate_code)
                    else:
                        if apptemplate_code in user_apptemplate_dict.keys():
                            apptemplate_description = user_apptemplate_dict.get(apptemplate_code)
                else:
                    print('<div class="alert alert-danger"><span class="glyphicon glyphicon-alert" aria-hidden="true"></span> ERROR: app template data file error</div>')
                    sys.exit(0)
                # Ok we are done with getting the settings,now lets present it to the user
                print(('<div class="panel-heading"><h3 class="panel-title">Domain: <strong>'+mydomain+'/'+thesubdir+'</strong></h3></div>'))
                print('<div class="panel-body">')
                print('<form id="config" class="form-inline config-save" action="subdir_select_app_settings.live.py" method="post">')
                print('<ul class="list-group">')
                if backend_category == 'PROXY':
                    print('<li class="list-group-item">')
                    print('<div class="row">')
                    print('<div class="col-sm-6 col-radio"><strong>NGINX is proxying to</strong></div>')
                    print(('<div class="col-sm-6"><div class="label label-success">'+backend_version+'</div>'))
                    print('</div>')
                    print('</li>')
                    print('<li class="list-group-item">')
                    print('<div class="row">')
                    print('<div class="col-sm-6 col-radio"><strong>Template</strong></div>')
                    print(('<div class="col-sm-6"><div class="label label-warning">'+apptemplate_description+'</div>'))
                    print('</div>')
                    print('</li>')
                else:
                    print('<li class="list-group-item">')
                    print('<div class="row">')
                    print('<div class="col-sm-6 col-radio"><strong>native NGINX and</strong></div>')
                    print(('<div class="col-sm-6"><div class="label label-success">'+backend_category+'</div>'))
                    print('</div>')
                    print('</li>')
                    print('<li class="list-group-item">')
                    print('<div class="row">')
                    print('<div class="col-sm-6 col-radio"><strong>Backend Version</strong></div>')
                    print(('<div class="col-sm-6"><div class="label label-warning">'+backend_version+'</div>'))
                    print('</div>')
                    print('</li>')
                    print('<li class="list-group-item">')
                    print('<div class="row">')
                    print('<div class="col-sm-6 col-radio"><strong>Template</strong></div>')
                    print(('<div class="col-sm-6"><div class="label label-info">'+apptemplate_description+'</div>'))
                    print('</div>')
                    print('</li>')
                print('</ul>')
                print('<p><em>To change application settings select a BACKEND from the drop down below:</em></p>')
                print('<select name="backend">')
                for backends_defined in backend_data_yaml_parsed.keys():
                    if backends_defined == backend_category:
                        print(('<option selected value="'+backends_defined+'">'+backends_defined+'</option>'))
                    else:
                        print(('<option value="'+backends_defined+'">'+backends_defined+'</option>'))
                print('</select>')
                # Pass on the domain name to the next stage
                print(('<input class="hidden" name="domain" value="'+mydomain+'">'))
                print(('<input class="hidden" name="thesubdir" value="'+thesubdir+'">'))
                print('<input class="btn btn-primary" type="submit" value="Submit">')
                print('</form>')
        else:
            print(('<div class="panel-heading"><h3 class="panel-title">Domain: <strong>'+mydomain+'/'+thesubdir+'</strong></h3></div><div class="panel-body">'))
            print('<form action="subdir_select_app_settings.live.py" method="post">')
            print('<p><em>Select a BACKEND from the drop down below:</em></p>')
            print('<select name="backend">')
            for backends_defined in backend_data_yaml_parsed.keys():
                print(('<option value="'+backends_defined+'">'+backends_defined+'</option>'))
            print('</select>')
            # Pass on the domain name to the next stage
            print(('<input class="hidden" name="domain" value="'+mydomain+'">'))
            print(('<input class="hidden" name="thesubdir" value="'+thesubdir+'">'))
            print('<input class="btn btn-primary" type="submit" value="Submit">')
            print('</form>')
    else:
        print('<div class="alert alert-danger"><span class="glyphicon glyphicon-alert" aria-hidden="true"></span> domain-data file i/o error</div>')
else:
    print('<div class="alert alert-danger"><span class="glyphicon glyphicon-alert" aria-hidden="true"></span> Forbidden</div>')
print('</div>')
print('<div class="panel-footer"><small>Need Help <span class="glyphicon glyphicon-flash" aria-hidden="true"></span> <a target="_blank" href="http://xtendweb.gnusys.net/">XtendWeb Docs</a></small></div>')
print('</div>')
print('</div>')
print('</div>')
print('</div>')
print('</body>')
print('</html>')