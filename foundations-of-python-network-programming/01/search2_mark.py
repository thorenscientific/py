#!/usr/bin/env python
# Foundations of Python Network Programming - Chapter 1 - search2.py

# Had to change up the original a bit, looks like the "web API" changed a bit.
# https://developers.google.com/maps/documentation/geocoding/intro



import urllib, urllib2
try:
    import json
except ImportError:  # for Python 2.5
    import simplejson as json

params = {'address': '207 N. Defiance St, Archbold, OH',
          'output': 'json', 'oe': 'utf8'}
print("params: ")
print(params)
#url = 'http://maps.google.com/maps/geo?' + urllib.urlencode(params)
url = 'https://maps.googleapis.com/maps/api/geocode/json?address=207+N.+Defiance+St,+Archbold,+OH'

rawreply = urllib2.urlopen(url).read()
print('raw reply:')
print(rawreply)

reply = json.loads(rawreply)
#print reply['Placemark'][0]['Point']['coordinates'][:-1]

print('\n\nDe-JSON reply:')
print(reply)
