# coding=utf-8

from flask import Flask, session, render_template, request
from ldap_auth import check_credentials
from vmware import last_inserted_datastore_space, report_datastore_space, get_datastore_usage
import json

#---- Configuración de la aplicación -------------------------------------------

# Alias base de la aplicación Flask
FLASK_ALIAS  = "/datastores"

# Nombre del sitio/organización
FLASK_SITE   = "Linuxito.com"

# Clave de cifrado de cookies
# Something from /dev/urandom
#FreeBSD:   cat /dev/urandom | env LANG=C tr -dc '[:alnum:]' | head -c 32 ; echo
#Linux:     cat /dev/urandom | LANG=C tr -dc '[:alnum:]' | head -c 32 ; echo
FLASK_SECRET = "****"

#-------------------------------------------------------------------------------

application = Flask(__name__,static_url_path="%s/static" % FLASK_ALIAS)

application.secret_key = FLASK_SECRET

@application.before_request
def session_management():
  # Make the session persistent until it is cleared
  session.permanent = True

@application.route("%s/login.html" % FLASK_ALIAS)
def login_html():
  return render_template("login.html", site=FLASK_SITE)

@application.route("%s/login" % FLASK_ALIAS, methods=['POST'])
def login():
  # Recover POST data
  try:
    _user = request.form['user']
    _pass = request.form['pass']
  except:
    # Wrong username or password
    response = {}
    response['cn'] = 'unknown'
    response['msg'] = 'Usuario o contraseña incorrectos'
    return json.dumps(response)
  # Check credentials
  response = check_credentials(_user,_pass)
  # Set username (session wide)
  session["user"] = json.loads(response)["cn"]
  session["auth"] = 1
  return response

@application.route("%s/logout" % FLASK_ALIAS)
def logout():
  # Unset username
  session.clear()
  session["user"] = "unknown"
  session["auth"] = 0
  return index()

@application.route("%s/" % FLASK_ALIAS)
@application.route("%s/dashboard" % FLASK_ALIAS)
def index():
  # Recover username from session
  try:
    user = session["user"]
    auth = session["auth"]
  except:
    user = "unknown"
    auth = 0
  if auth == 0:
    return login_html()
  else:
    return render_template("index.html", user=user, site=FLASK_SITE)

@application.route("%s/list_datastore_space" % FLASK_ALIAS)
def vmware_list():
  # Check session
  try:
    auth = session["auth"]
  except:
    print("You shall not pass")
    auth = 0
  if auth == 0:
    return "You shall not pass"
  else:
    return json.dumps(last_inserted_datastore_space())

@application.route("%s/datastore_report" % FLASK_ALIAS, methods=['GET', 'POST'])
def vmware_report_template():
  # Check session
  try:
    auth = session["auth"]
    user = session["user"]
  except:
    print("You shall not pass")
    auth = 0
  if auth == 0:
    return "You shall not pass"
  else:
      # Recover GET/POST data
      ds = "test"
      if request.method == 'POST':
        try:
          # try to recover POST data
          ds = request.form['ds']
        except:
          print("Missing ds param")
          return "POST error"
      else:
        try:
          # try to recover GET data instead
          ds = request.args.get('ds', '')
        except:
          print("Missing ds param")
          return "GET error"

      # Return the report for ds
      return render_template("report.html", ds=ds, user=user, site=FLASK_SITE)

@application.route("%s/report_datastore_space" % FLASK_ALIAS, methods=['GET', 'POST'])
def vmware_report_json():
  # Check session
  try:
    auth = session["auth"]
  except:
    print("You shall not pass")
    auth = 0
  if auth == 0:
    return "You shall not pass"
  else:
      # Recover GET/POST data
      ds = "test"
      if request.method == 'POST':
        try:
          # try to recover POST data
          ds = request.form['ds']
        except:
          print("Missing ds param")
          return "POST error"
      else:
        try:
          # try to recover GET data instead
          ds = request.args.get('ds', '')
        except:
          print("Missing ds param")
          return "GET error"

      # Return the report for ds
      return report_datastore_space(ds)

@application.route("%s/datastore_detail" % FLASK_ALIAS, methods=['GET', 'POST'])
def vmware_detail_template():
  # Check session
  try:
    auth = session["auth"]
    user = session["user"]
  except:
    print("You shall not pass")
    auth = 0
  if auth == 0:
    return "You shall not pass"
  else:
      # Recover GET/POST data
      ds = "test"
      if request.method == 'POST':
        try:
          # try to recover POST data
          ds = request.form['ds']
        except:
          print("Missing ds param")
          return "POST error"
      else:
        try:
          # try to recover GET data instead
          ds = request.args.get('ds', '')
        except:
          print("Missing ds param")
          return "GET error"

      # Return the report for ds
      return render_template("detail.html", ds=ds, user=user, site=FLASK_SITE)

@application.route("%s/show_datastore_detail" % FLASK_ALIAS, methods=['GET', 'POST'])
def vmware_detail_json():
  # Check session
  try:
    auth = session["auth"]
  except:
    print("You shall not pass")
    auth = 0
  if auth == 0:
    return "You shall not pass"
  else:
      # Recover GET/POST data
      ds = "test"
      if request.method == 'POST':
        try:
          # try to recover POST data
          ds = request.form['ds']
        except:
          print("Missing ds param")
          return "POST error"
      else:
        try:
          # try to recover GET data instead
          ds = request.args.get('ds', '')
        except:
          print("Missing ds param")
          return "GET error"

      # Return the report for ds
      return get_datastore_usage(ds)

if __name__ == "__main__":
  application.run()
