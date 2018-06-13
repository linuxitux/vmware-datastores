# coding=utf-8

import atexit
import json
import ssl
import psycopg2
import sys

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

from config import VMWARE_HOST, VMWARE_HOST_DESA, VMWARE_HOST_PROD, VMWARE_USER, VMWARE_PASS, VMWARE_DISABLE_SSL
from config import PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB

#==== print_size ===============================================================
# http://stackoverflow.com/questions/1094841/
def print_size(num):
    """
    Returns the human readable version of a size in bytes

    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, item)
        num /= 1024.0
    return "%.1f %s" % (num, 'TB')

#==== list_datastore_space =====================================================
def list_datastore_space():
    """
    List all datastores and their free space
    """
    sslContext = None

    if VMWARE_DISABLE_SSL:
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslContext.verify_mode = ssl.CERT_NONE

    try:
        service_instance = connect.SmartConnect(host=VMWARE_HOST,
            user=VMWARE_USER,
            pwd=VMWARE_PASS,
            sslContext=sslContext)
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        # Search for all Datastores
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.Datastore],
                                                          True)
        datastores = objview.view
        objview.Destroy()

        datastore_space = {}
        for datastore in datastores:
          capacity = datastore.summary.capacity
          freeSpace = datastore.summary.freeSpace
          datastore_details = {
            'capacity': print_size(capacity),
            'free': print_size(freeSpace),
            'used': print_size(capacity-freeSpace),
            'pfree': "%2.2f" % (freeSpace*100.0/capacity)
          }
          datastore_space[datastore.summary.name] = datastore_details

        return datastore_space

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

#==== last_inserted_datastore_space ============================================
def last_inserted_datastore_space():
  # Retorna la última muestra insertada en la tabla "datastore_space"
  datastore_space = ""

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select the last inserted row
    sqlquery = "select fecha, jdata from datastore_space where id=(select max(id) from datastore_space);"
    cur.execute(sqlquery)

    # Query the database and obtain data as Python objects
    row = cur.fetchone()

    # Close communication with the database
    cur.close()
    conn.close()

    # Recover JSON data from Python object
    datastore_space = row[1]

    # Add date from row inside JSON response
    datastore_space['fecha'] = row[0].strftime("%Y-%m-%d %H:%M:%S")

  except:
    print("Database error")
    return "Database error"

  return datastore_space

#==== update_datastore_space ===================================================
def update_datastore_space():
  # Obtener el uso actual en formato JSON
  datastore_space = json.dumps(list_datastore_space())

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert a new row
    sqlquery = "insert into datastore_space (fecha, jdata) values (current_timestamp, '%s');" % datastore_space
    cur.execute(sqlquery)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

  except:
    print(sys.exc_info())
    return "Database error"

  return "Ok"

#==== report_datastore_space ===================================================
def report_datastore_space(ds):
  # Retorna las últimas muestras insertadas en la tabla "datastore_space" para un datastore
  datastore_space = []

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select the last inserted row
    sqlquery = "select fecha,jdata->'%s'->'capacity',jdata->'%s'->'pfree' from datastore_space;" % (ds, ds)

    cur.execute(sqlquery)

    # Query the database and obtain data as Python objects
    rows = cur.fetchall()

    # Convert datetime to string
    datastore_space = [(row[0].strftime("%d/%m/%Y"), row[1], row[2]) for row in rows]

    # Close communication with the database
    cur.close()
    conn.close()

  except:
    print("Database error")
    return "Database error"

  # Return data in JSON format
  return json.dumps(datastore_space)

#==== vm_datastore_usage =======================================================
def vm_datastore_usage():
    """
    List datastore usage for each virtual machine
    """
    sslContext = None
    datastores = {}

    if VMWARE_DISABLE_SSL:
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslContext.verify_mode = ssl.CERT_NONE

    # Desarrollo
    try:
        service_instance = connect.SmartConnect(host=VMWARE_HOST_DESA,
            user=VMWARE_USER,
            pwd=VMWARE_PASS,
            sslContext=sslContext)
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        # Search for all VirtualMachines
        objview = content.viewManager.CreateContainerView(content.rootFolder,
            [vim.VirtualMachine],
            True)
        vms = objview.view
        objview.Destroy()

        for vm in vms:
            vm_name = vm.config.name
            if vm.runtime.powerState == vim.VirtualMachine.PowerState.poweredOn:
                # Sólo recuperar datos de máquinas encendidas
                for ds in vm.storage.perDatastoreUsage:
                    ds_name = ds.datastore.info.name
                    if not ds_name in datastores:
                        # Crear un diccionario vacío si es la primera entrada
                        datastores[ds_name] = {}
                    if not vm_name in datastores[ds_name]:
                        # Crear un diccionario vacío si es la primera entrada
                        datastores[ds_name][vm_name] = {}
                    datastores[ds_name][vm_name]['committed'] = ds.committed
                    datastores[ds_name][vm_name]['uncommitted'] = ds.uncommitted

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    # Producción
    try:
        service_instance = connect.SmartConnect(host=VMWARE_HOST_PROD,
            user=VMWARE_USER,
            pwd=VMWARE_PASS,
            sslContext=sslContext)
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        # Search for all VirtualMachines
        objview = content.viewManager.CreateContainerView(content.rootFolder,
            [vim.VirtualMachine],
            True)
        vms = objview.view
        objview.Destroy()

        for vm in vms:
            vm_name = vm.config.name
            if vm.runtime.powerState == vim.VirtualMachine.PowerState.poweredOn:
                # Sólo recuperar datos de máquinas encendidas
                for ds in vm.storage.perDatastoreUsage:
                    ds_name = ds.datastore.info.name
                    if not ds_name in datastores:
                        # Crear un diccionario vacío si es la primera entrada
                        datastores[ds_name] = {}
                    if not vm_name in datastores[ds_name]:
                        # Crear un diccionario vacío si es la primera entrada
                        datastores[ds_name][vm_name] = {}
                    datastores[ds_name][vm_name]['committed'] = ds.committed
                    datastores[ds_name][vm_name]['uncommitted'] = ds.uncommitted

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1
 
    return datastores

#==== update_vm_datastore_usage ================================================
def update_vm_datastore_usage():
  # Obtener el uso actual en formato JSON
  datastore_usage = json.dumps(vm_datastore_usage())

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert a new row
    sqlquery = "insert into datastore_usage (fecha, jdata) values (current_timestamp, '%s');" % datastore_usage
    cur.execute(sqlquery)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

  except:
    print(sys.exc_info())
    return "Database error"

  return "Ok"

#==== get_last_vm_datastore_usage ==============================================
def get_last_vm_datastore_usage(vm,ds):
  # Obtener uso actual (committed en bytes) de una vm en un datastore en particular
  datastore_usage = ""

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select the last inserted row
    sqlquery = "select fecha, jdata->'%s'->'%s'->'committed' from datastore_usage where id=(select max(id) from datastore_usage);" % (ds, vm)
    cur.execute(sqlquery)

    # Query the database and obtain data as Python objects
    row = cur.fetchone()

    # Close communication with the database
    cur.close()
    conn.close()

    # Recover JSON data from Python object
    datastore_usage = row[1]

  except:
    print("Database error")
    return "Database error"

  return datastore_usage

#==== get_vm_datastore_usage ===================================================
def get_vm_datastore_usage(vm,ds):
  # Obtener historial de uso de una vm en un datastore en particular
  datastore_usage = []

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select the last inserted row
    sqlquery = "select fecha, jdata->'%s'->'%s'->'committed' from datastore_usage;" % (ds, vm)
    cur.execute(sqlquery)

    # Query the database and obtain data as Python objects
    rows = cur.fetchall()

    # Convert datetime to string
    datastore_usage = [(row[0].strftime("%d/%m/%Y"), row[1]) for row in rows]

    # Close communication with the database
    cur.close()
    conn.close()

  except:
    print("Database error")
    return "Database error"

  return json.dumps(datastore_usage)

#==== get_datastore_usage ======================================================
def get_datastore_usage(ds):
  # Obtener uso actual de un datastore por cada máquina virtual
  datastore_usage = ""

  try:
    # Connect to the database
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select the last inserted row
    sqlquery = "select fecha, jdata->'%s' from datastore_usage where id=(select max(id) from datastore_usage);" % ds
    cur.execute(sqlquery)

    # Query the database and obtain data as Python objects
    row = cur.fetchone()

    # Recover JSON data from Python object
    datastore_usage = row[1]

    # Add date from row inside JSON response
    datastore_usage['fecha'] = row[0].strftime("%Y-%m-%d %H:%M:%S")

    # Close communication with the database
    cur.close()
    conn.close()

  except:
    print("Database error")
    return "Database error"

  return json.dumps(datastore_usage)
