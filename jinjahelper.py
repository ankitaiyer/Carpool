import urllib2, urllib, json, re, cookielib, requests
from gmaps import Geocoding
import simplejson, urllib


def reverse_geocode(latlng,sensor,location_type,result_type, **geo_args):
    print "LAT AND LNG ARE: ", latlng
    geo_args.update({
        'latlng': latlng,
        'location_type': location_type,
        'result_type': result_type,
        'sensor': sensor,
        'key':api_key
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    print url
    result = simplejson.load(urllib2.urlopen(url))
    print "FORMATTED ADDRESS IS ", simplejson.dumps([s['formatted_address'] for s in result['results']], indent=2)


