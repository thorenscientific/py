#!/usr/bin/env python
# Foundations of Python Network Programming - Chapter 1 - search1.py

from googlemaps import Client as gmclient
address = '207 N. Defiance St, Archbold, OH'
gmclient.key = 'AIzaasdf'
print gmclient.address_to_latlng(address)
