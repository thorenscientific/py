import pywapi
import string

google_result = pywapi.get_weather_from_google('95035')
yahoo_result = pywapi.get_weather_from_yahoo('95035', '')
noaa_result = pywapi.get_weather_from_noaa('KSJC')

print "Google says: It is " + string.lower(google_result['current_conditions']['condition']) + " and " + google_result['current_conditions']['temp_f'] + "F now in Milpitas.\n\n"

print "Yahoo says: It is " + string.lower(yahoo_result['condition']['text']) + " and " + yahoo_result['condition']['temp'] + "F now in Milpitas.\n\n"

print "NOAA says: It is " + string.lower(noaa_result['weather']) + " and " + noaa_result['temp_f'] + "F now in SJC.\n"
