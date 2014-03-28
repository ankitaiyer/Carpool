import urllib2, urllib, json, re, cookielib, requests
from gmaps import Geocoding
import simplejson, urllib
import os

API_KEY = os.environ.get('API_KEY')
#Please collect your project api_key

GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

def geocode(address,sensor, **geo_args):
    geo_args.update({
        'address': address,
        'sensor': sensor
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))
    #prints formatted address 
    #print "FORMATTED ADDRESS IS ", simplejson.dumps([s['formatted_address'] for s in result['results']], indent=2)
    #prints lat and lng for the selected address
    #print  "LATTITUDE IS: " , simplejson.dumps([s['geometry']['location']['lat'] for s in result['results']], indent=2)    
    #print  "LONGITUDE IS: " , simplejson.dumps([s['geometry']['location']['lng'] for s in result['results']], indent=2)
    lat =  [s['geometry']['location']['lat'] for s in result['results']] 
    lng =  [s['geometry']['location']['lng'] for s in result['results']]
    return lat[0], lng[0]
  
def reverse_geocode(latlng,sensor,location_type,result_type, **geo_args):
    print "LAT AND LNG ARE: ", latlng
    geo_args.update({
        'latlng': latlng,
        'location_type': location_type,
        'result_type': result_type,
        'sensor': sensor,
        'key': API_KEY
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    print url
    result = simplejson.load(urllib2.urlopen(url))
    #return "FORMATTED ADDRESS IS ", simplejson.dumps([s['formatted_address'] for s in result['results']], indent=2)
    return [s['formatted_address'] for s in result['results']]



def getAction():
    print
    print "What would you like to do?"
    print "\tA - Get latitude/longitude of address."
    print "\tB - Get address from latitude/longutude"
    # print "\tC - Locate something near an address"
    # print "\tD - Get directions"
    print "\tQ - Terminate the program"
    return (raw_input('Selection: ')).upper()

# Pause function, saves typing.
def pause():
    print
    raw_input("(Press [enter] to continue...)")

def getLatLng(address):
    print address
    geocode(address=address ,sensor="false")
    pause()

def getAddress(latlng):
    print latlng
    location_type = "ROOFTOP"
    result_type = "street_address"
    reverse_geocode(latlng=latlng,location_type=location_type,result_type=result_type,sensor="true")
    
    
def main():
    #print "This is a console based google maps application, you can use various features of google maps using it."
    action = getAction()
    while (action != 'Q'):
        print
        if (action == 'A'):
            getLatLng(raw_input('Enter the address (format:683,Sutter St,San Francisco,CA,94108): '))
        elif (action == 'B'):
            getAddress(raw_input('Enter the latitude/longutude (format: 123.1234,-123.1234): '))
        # elif (action == 'C'):
        #     searchFor(raw_input('What would you like to find (i.e. cafe, gas station, etc.): '), raw_input('Near (gps, address, city, zip): '))
        # elif (action == 'D'):
        #     getDirections(raw_input('Start Location: '), raw_input('End Locations: '))
        else:
            exit

        action = getAction()

if __name__ == '__main__':
    main()

    # block = "1600"':
    # street = "Amphitheatre Parkway"
    # city = "Mountain View"
    # state = "CA"

    # lattitude = 40.714224
    # longitude =  -73.961452
    # location_type = "ROOFTOP" 
    # result_type = "street_address"

    
    # address = block + "+" + street + "+" + city + "+" + state
    # latlng = str(lattitude) + "," + str(longitude)
    # geocode(address=address ,sensor="false")
    # reverse_geocode(latlng=latlng,location_type=location_type,result_type=result_type,sensor="true")



