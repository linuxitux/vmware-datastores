# coding=utf-8

from config import LDAP_BASE_DN, LDAP_SERVER, LDAP_ATTRS
import ldap
import json

def check_credentials(username, password):
   """
   Verifies credentials for username and password.
   Returns None on success or a string describing the error on failure.
   """
   ldap_user = "uid=%s,%s" % (username, LDAP_BASE_DN)
   ldap_filter = "(uid=%s)" % username
   try:
       # Build a client
       ldap_client = ldap.initialize(LDAP_SERVER)
       # Set LDAPv3 option
       ldap_client.set_option(ldap.OPT_PROTOCOL_VERSION,3)
       # try to bind as username/password
       print("ldap_auth: %s" % ldap_user)
       ldap_client.simple_bind_s(ldap_user,password)
   except ldap.INVALID_CREDENTIALS:
       ldap_client.unbind()
       # Wrong username or password
       response = {}
       response['cn'] = 'unknown'
       response['msg'] = 'Usuario o contraseña incorrectos'
       return json.dumps(response)
   except ldap.SERVER_DOWN:
       raise Exception('LDAP server is not available')
       response = {}
       response['cn'] = 'unknown'
       response['msg'] = 'Servidor LDAP no disponible'
       return json.dumps(response)
   # All OK
   # Get user attributes
   response = {}
   search_result = ldap_client.search_s(LDAP_BASE_DN,
                                   ldap.SCOPE_SUBTREE,
                                   ldap_filter,
                                   LDAP_ATTRS)[0][1]

   # Proper formatting of JSON response
   response['msg'] = 'Ok'
   for attr in LDAP_ATTRS:
     try:
       # Recover just the first result for each attribute
       response[attr] = search_result[attr][0]
     except:
       pass
   user_info = json.dumps(response)
   ldap_client.unbind()
   return user_info
