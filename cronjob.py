#!/usr/bin/env python

import vmware

salida = vmware.update_datastore_space()

if salida!="Ok":
  print(salida)
  exit(1)

salida = vmware.update_vm_datastore_usage()

if salida!="Ok":
  print(salida)
  exit(1)

exit(0)