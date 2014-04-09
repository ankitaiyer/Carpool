from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import DateTime
import geo
import background
import os
import psycopg2
import sys


#ENGINE = create_engine("sqlite:///carpool.db", echo=False)
ENGINE = create_engine(os.environ.get("DATABASE_URL", 'postgres://localhost:5432/carpool'), echo=False)
session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False))



#NoResultFound = None

#ENGINE = None
#Session = None

Base = declarative_base()
Base.query = session.query_property()


## Class declarations go here
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(64), nullable=False)
    lastname = Column(String(64),nullable=False)
    email = Column(String(64), nullable =False)
    password = Column(String(64), nullable=False)
    mobile = Column(String(15), nullable=True)
    home = Column(String(15), nullable=True)
    work = Column(String(15), nullable=True)


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    street = Column(String(65), nullable=False)
    city = Column(String(65), nullable=False)
    state = Column(String(65), nullable=False)
    zipcode = Column(String(15), nullable=False)
    lng = Column(String, nullable=True)
    lat = Column(String, nullable=True)


class Commute(Base):
    __tablename__ = "commute"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    start_addr_id = Column(Integer, ForeignKey('addresses.id'))
    end_addr_id = Column(Integer, ForeignKey('addresses.id'))
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)


    Users = relationship("User", 
            backref=backref("Commute", order_by=id))

    #Addresses = relationship("Address", 
            #backref=backref("Commute", order_by=id))

    start_address = relationship("Address", primaryjoin="Commute.start_addr_id==Address.id")
    #foreign_keys=[start_addr_id]
    dest_address = relationship("Address", primaryjoin="Commute.end_addr_id==Address.id")

def connect():
    # Don't run this anymore
    return session

    # global ENGINE
    # global Session

    # ENGINE = create_engine("sqlite:///carpool.db", echo=True)
    # Session = sessionmaker(bind=ENGINE)

    # return Session()
    # any time you need a session later, you can just do 'session = Session()'

def authenticate(emailform, passwordform):
    user = session.query(User).filter_by(email=emailform).first()
    if user != None:
        if int(user.password) == int(passwordform):
            return user.email
    else:
        return "Auth failed"

def register_user(firstnameform, lastnameform, emailform, passwordform):
    temp_user = User(firstname=firstnameform, lastname=lastnameform, email=emailform, password=hash(passwordform))
    session.add(temp_user)
    session.commit()


def get_user_by_email(email):
    userid = session.query(User).filter_by(email=email).first()
    #print email
    #print "user", userid.id
    return userid.id

def get_commute_by_user(email):
    uid = get_user_by_email(email)
    commutes = session.query(Commute).filter_by(user_id=uid).all()
    #print "COMMUTE", commutes
    if commutes == []:
        return None
    else:
        commute_details = {}
        for commute in commutes:
            start_address_line = session.query(Address).filter_by(id=commute.start_addr_id).first()
            end_address_line = session.query(Address).filter_by(id=commute.end_addr_id).first()
            sa = start_address_line.street + "," + start_address_line.city + "," + start_address_line.state + " "+ start_address_line.zipcode 
            ea = end_address_line.street + "," + end_address_line.city + "," + end_address_line.state + " " + end_address_line.zipcode
            commute_details[commute.id] = [sa,ea,commute.start_time,commute.end_time]
        return commute_details

def split_address(adr):
    address = adr.split(',')
    street = address[0] + " " + address[1]
    return address, street

def get_address_by_addr_id(addr_id):
    a = session.query(Address).get(addr_id)
    address =a.street + " " + a.city + " " + a.state + " "+ a.zipcode 
    return address 

def complete_commute_profile(user_id, startaddrform, destaddrform, starttimeform,endtimform,mobileform,workform,homeform):
    current_user = session.query(User).filter_by(id=user_id).first()
    if current_user:
        current_user.mobile = mobileform
        current_user.home = homeform
        current_user.work = workform

    start_address = split_address(startaddrform)
    str_addr = Address(street=start_address[1], city=start_address[0][2], state=start_address[0][3], zipcode=start_address[0][4])
    
    dest_address = split_address(destaddrform)
    dest_addr = Address(street=dest_address[1], city=dest_address[0][2], state=dest_address[0][3], zipcode=dest_address[0][4])
    
    session.add(str_addr)
    session.add(dest_addr)
    session.commit()

    temp_commute = Commute(user_id=current_user.id, start_addr_id=str_addr.id, end_addr_id=dest_addr.id, start_time=starttimeform,end_time=endtimform)
    session.add(temp_commute)
    session.commit()

    background.load_latlng()

    return str_addr.id, dest_addr.id


def match_users(start_addr_id, end_addr_id):
    start_distances = session.execute("""SELECT C.user_id AS self_user_id, A.id as self_start_addr_id , C3.user_id AS other_user_id, U.email AS other_user_email, A2.id AS other_start_addr_id, A.lat, A.lng, A2.lat, A2.lng,
    earth_distance(ll_to_earth(cast(A.lat as double precision), cast(A.lng as double precision)), ll_to_earth(cast(A2.lat as double precision),cast(A2.lng as double precision))) as circle_distance
    FROM commute C
    JOIN addresses A ON (C.start_addr_id = A.id)
    JOIN ( SELECT A2.id, A2.lat, A2.lng
    FROM addresses A2
    JOIN commute C2 ON (A2.id = C2.start_addr_id)
    ) A2 ON (A2.id != A.id)
    JOIN commute C3 ON (A2.id = C3.start_addr_id)
    JOIN users U ON (C3.user_id = U.id AND C3.user_id != C.id)
    WHERE C.start_addr_id = :start_addr_id
    ORDER BY circle_distance""", { "start_addr_id": start_addr_id })

    possible_matches = { }
    for row in start_distances:
        key = row.other_user_email
        value = round(row.circle_distance,2)
        if key not in possible_matches :
            possible_matches[key] = [value]
    


    end_distances = session.execute("""SELECT C.user_id AS self_user_id, A.id as self_end_addr_id , C3.user_id AS other_user_id, U.email AS other_user_email, A2.id AS other_end_addr_id, A.lat, A.lng, A2.lat, A2.lng,
    earth_distance(ll_to_earth(cast(A.lat as double precision), cast(A.lng as double precision)), ll_to_earth(cast(A2.lat as double precision),cast(A2.lng as double precision))) as circle_distance
    FROM commute C
    JOIN addresses A ON (C.end_addr_id = A.id)
    JOIN ( SELECT A2.id, A2.lat, A2.lng
    FROM addresses A2
    JOIN commute C2 ON (A2.id = C2.end_addr_id)
    ) A2 ON (A2.id != A.id)
    JOIN commute C3 ON (A2.id = C3.end_addr_id)
    JOIN users U ON (C3.user_id = U.id AND C3.user_id != C.id)
    WHERE C.end_addr_id = :end_addr_id
    ORDER BY circle_distance""", { "end_addr_id": end_addr_id })
    
    for row in end_distances:
        key = row.other_user_email
        value = round(row.circle_distance,2)
        if key in possible_matches :
            if len(possible_matches[key]) < 2 :
                possible_matches[key].append(value)
        else:
            possible_matches[key] = [None, value]
    return possible_matches

def get_addressid_by_user(user):
    u= session.query(User).filter_by(email=user).first()
    c = session.query(Commute).filter_by(user_id=u.id).first()
    startA = session.query(Address).filter_by(id=c.start_addr_id).first()
    start_address = startA.id
    destA = session.query(Address).filter_by(id=c.end_addr_id).first()
    end_address = destA.id
    return start_address, end_address

def get_userdetails_by_email(email):
    u = session.query(User).filter_by(email=email).first()
    address = get_commute_by_user(email).values()[0]
    # user_info = address.values()
    #print "ADDRESS", address
    user_details = [u.email, u.firstname, u.lastname, u.mobile, u.work, u.home, address[0], address[1], address[2], address[3]]
    return user_details
    

def main():
    Base.metadata.create_all(ENGINE)
    
 
if __name__ == "__main__":
    main()












