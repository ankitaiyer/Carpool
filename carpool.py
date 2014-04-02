from flask import Flask, render_template, redirect, request, flash, url_for, session, flash
import model
import background
import json
import numpy 
from scipy.cluster.vq import *
import unicodedata 
import os
import geo
#from urlparse import urlparse

API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)
#app.config.from_object(config)
app.secret_key = "thisispainful"
app.jinja_env.globals.update(reverse_geocode=geo.reverse_geocode)

@app.route("/")
def index():
    if "email" not in session:
        user = None
        return render_template("index.html", user=user)
    else:
        user = session['email']
        return render_template("home.html", user=user)

@app.route("/info")
def info():
    return render_template("info.html")

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
    model.register_user(firstnameform,lastnameform,emailform,passwordform)
    return redirect(url_for("login"))

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
    if email != None:
        flash("User authenticated!")
        session['email'] = email
    else:
        flash("Password incorrect, please try again.")
    return redirect(url_for("main_menu"))

@app.route("/home")
def main_menu():
    if "email" in session:
        user = session['email']
    else:
        user = None
    return render_template("main_menu.html", user=user)

##########################################







@app.route("/signup")
def singup():
    return render_template("commute.html")

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
    start_addr_id = request.args.get('start_addr_id')
    dest_addr_id = request.args.get('dest_addr_id')
    possible_matches = model.match_users(start_addr_id, dest_addr_id)
    print "POSSIBLE MATCHES", possible_matches
    return render_template("match.html", start_addr_id=start_addr_id, dest_addr_id=dest_addr_id, possible_matches=possible_matches)

@app.route("/testmap1")
def testmap1():
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

    #return render_template("match_graph.html", API_KEY=API_KEY, lat=lat, lng=lng , dest_latlng_list=dest_latlng_list, start_latlng_list=start_latlng_list)

if __name__ == "__main__":
    app.run(debug = True)