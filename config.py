# coding=utf-8

"""
config.py - Variables de configuración global
"""

# LDAP
LDAP_SERVER  = "ldap://ldap.linuxito.com"
LDAP_BASE_DN = "ou=people,dc=linuxito,dc=com"
LDAP_ATTRS   = ["cn", "dn", "sn", "givenName"]

# VMware
VMWARE_HOST_DESA = "192.168.1.1"
VMWARE_HOST_PROD = "192.168.1.2"
VMWARE_HOST = VMWARE_HOST_DESA
VMWARE_USER = "usr_readonly"
VMWARE_PASS = "****"
# No deshabilita SSL sino la verificación del certificado del host
VMWARE_DISABLE_SSL = 1

# Postgres
PSQL_HOST = "db.linuxito.com"
PSQL_PORT = "5434"
PSQL_USER = "usr_datastores"
PSQL_PASS = "****"
PSQL_DB   = "datastores"

