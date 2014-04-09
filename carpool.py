from flask import Flask, render_template, redirect, request, flash, url_for, session, flash
import model
import background
import json
import numpy 
from scipy.cluster.vq import *
import unicodedata 
import os
import geo
import operator
#from urlparse import urlparse

API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)
app.config["DEBUG"] = os.environ.get("DEBUG", False)
#app.config.from_object(config)
app.secret_key = "thisispainful"
app.jinja_env.globals.update(reverse_geocode=geo.reverse_geocode)

@app.route("/")
def index():
    if "email" not in session:
        user = None
        print "USER in Index", user
        return render_template("index.html", user=user)
    else:
        user = session['email']
        print "user in index", user
        return render_template("index.html", user=user)

@app.route("/info")
def info():
    if "email" not in session:
        user = None
    else:
        user = session['email']
    return render_template("info.html", user=user)

@app.route("/clear_session")
def session_clear():
    if "email" in session:
        session.clear()
    return redirect(url_for("index"))

@app.route("/register")
def register():
    if "email" in session:
        session.clear()
    user = None
    return render_template("register.html", user=user )
    
@app.route("/register", methods=["POST"])
def registerUser():
    firstnameform = request.form.get("firstname")
    lastnameform = request.form.get("lastname")
    emailform = request.form.get("email")
    passwordform = request.form.get("password")
    passwordConfirm = request.form.get("password_verify")
    if (passwordform == passwordConfirm):
        model.register_user(firstnameform,lastnameform,emailform,passwordform)
        return redirect(url_for("login"))
    else:
        flash("Confirm password does not match the password. Please try again")
        if "email" in session:
            session.clear()
        user = None
        return render_template("register.html", user=user )



@app.route("/login")
def login():
    if "email" in session:
        session_clear()
    user = None
    return render_template("login.html", user=user)

@app.route("/login", methods=["POST"])
def process_login():
    emailform = request.form.get("email")
    passwordform = request.form.get("password")

    email = model.authenticate(emailform, hash(passwordform))
    print "functionreturn", email
    if email == "Auth failed" or email == None:
        #flash("Password incorrect, please try again.")
        flash(email)
        user = None
        return render_template("login.html", user=user)
    else:
        flash("User authenticated!")
        session['email'] = email
        return redirect(url_for("main_menu"))

@app.route("/mycommute")
def main_menu():
    if "email" in session:
        user = session['email']
    else:
        user = None
    return render_template("main_menu.html", user=user)

@app.route("/signup")
def singup():
    if "email" in session:
        user = session['email']
    else:
        user = None
    return render_template("commute.html", user=user)

@app.route("/signup" , methods=["POST"])
def commute_profile():
    if session['email']:
        email = session['email']
        user_id = model.get_user_by_email(email)
    startaddrform = request.form.get("depart")
    destaddrform = request.form.get("destination")
    starttimeform = request.form.get("starttime")
    endtimform = request.form.get("endtime")
    mobileform = request.form.get("mobile")
    workform = request.form.get("work")
    homeform = request.form.get("home")
    start_addr_id, dest_addr_id = model.complete_commute_profile(user_id, startaddrform,destaddrform,starttimeform,endtimform,mobileform,workform,homeform)
    return redirect(url_for("match") + "?start_addr_id=%d&dest_addr_id=%d" % ( start_addr_id, dest_addr_id))

@app.route("/match")
def match():
    if "email" in session:
        user = session['email']
    start_addr_id = request.args.get('start_addr_id')
    dest_addr_id = request.args.get('dest_addr_id')
    matches = model.match_users(start_addr_id, dest_addr_id)
    start_addr = model.get_address_by_addr_id(start_addr_id)
    dest_addr = model.get_address_by_addr_id(dest_addr_id)
    possible_matches = sorted(matches.iteritems(), key=lambda (k,v): operator.itemgetter(1)(v), reverse=True)
    #print "POSSIBLE MATCHES", possible_matches
    return render_template("match.html", start_addr=start_addr, dest_addr=dest_addr, possible_matches=possible_matches, user=user)

@app.route("/commutelist")
def commutelist():
    if "email" not in session:
        user = None
    else:
        user = session['email']
        commute_details = model.get_commute_by_user(user)
        if commute_details != None:
            start_addr_id,dest_addr_id = model.get_addressid_by_user(user)
            return render_template("commutelist.html", user=user, commute_details=commute_details, start_addr_id=start_addr_id, dest_addr_id=dest_addr_id)
        else:
            return render_template("commutelist.html", user=user, commute_details=commute_details)

@app.route("/map")
def map():
    if "email" not in session:
        user = None
    else:
        user = session['email']
    #show markers for all destination addresses that exist in the Commute table
    dest_address_query = model.session.query(model.Address).filter_by(id=model.Commute.end_addr_id).all()
    dest_latlng_list = background.get_latlng(dest_address_query)

    start_address_query = model.session.query(model.Address).filter_by(id=model.Commute.start_addr_id).all()
    start_latlng_list = background.get_latlng(start_address_query)

    #all_latlng_list = dest_latlng_list + start_latlng_list
   
    data = numpy.array(dest_latlng_list)
    centers = background.get_latlng_clustercenter(data,1)
    #lat = centers[0][0] #37.61127878
    #lng = centers[0][1] #-122.1289833
    lat = 37.468914900000000000 #bay area center latlng
    lng = -122.155100899999980000 #bay area center latlng

    return render_template("match_graph.html", user=user, API_KEY=API_KEY, lat=lat, lng=lng , dest_latlng_list=dest_latlng_list, start_latlng_list=start_latlng_list)

@app.route("/users/<user>")
def user(user):
    user_details = model.get_userdetails_by_email(user)
    #print "USER", user_details
    return render_template("user_profile.html", user_details=user_details, user=user)




if __name__ == "__main__":
    app.run(debug = True)
