from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import DateTime
from sqlalchemy import or_
import model
import geo
import numpy 
from scipy.cluster.vq import *
import unicodedata 



def load_latlng():
    result = model.session.query(model.Address).filter(or_(model.Address.lat == '', model.Address.lng == '', model.Address.lat == None, model.Address.lng == None)).all()
    for adr in result:
        addr = []
        if (adr.lat == None or adr.lng == None):
            addr = [adr.street,adr.city,adr.state,adr.zipcode]
            format_addr = ",".join(addr) 
            lat,lng = geo.geocode(format_addr,"false")  
            adr.lat = lat
            adr.lng = lng
    model.session.commit()
  
def get_latlng(address_query):
    result = address_query
    load_latlng()
    latlng = []
    for adr in result:
        tup_item1 = float(adr.lat) if adr.lat else None
        tup_item2 = float(adr.lng) if adr.lng else None
        tup = (tup_item1, tup_item2)   
        latlng.append(tup)
    return latlng

def get_latlng_clustercenter(data, clusterscount):
    #print "data", data
    centers = kmeans2(data, clusterscount)
    #print "centers: ", centers[0]
    return centers[0]
    #print "DATA IS: ",data
    #centers,idx = kmeans2(data, clusterscount)
    #return centers,idx



def main(session):
    # You'll call each of the load_* functions with the session as an argument

    ## Sample code to test geo function call
    # lat,lng = geo.geocode("84 Madrid place, Fremont, CA, 94539", "false")
    # return  lat,lng

    #Call geo code function to load latlng for addresses where latlng is missing
    load_latlng()

    #Get all latlngs available in the Address table to calculate ceter using kmeans clustering. Return data as Tuple
    query = model.session.query(model.Address).all()
    latlng_list = get_latlng(query)

    
    #Format latlngs into numpy array to calculate centroids usig kmeans clusterig technique.
    data = numpy.array(latlng_list)
    centers = get_latlng_clustercenter(data,6)
    # print "Centers are: ", centers
    # print "idx is:," ,idx


if __name__ == "__main__":
    session= model.connect()
    main(session)
   

