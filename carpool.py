from flask import Flask, render_template, redirect, request, flash, url_for, session
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
app.secret_key = "thisispainful"
app.jinja_env.globals.update(reverse_geocode=geo.reverse_geocode)

@app.route("/")
def index():
    # if session.get("email"):
    #     return redirect(url_for("main_menu"))
    # else:
        return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

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

@app.route("/main_menu")
def main_menu():
    user = session['email']
    return render_template("main_menu.html", user=user)

@app.route("/register")
def register():
    return render_template("register.html")
    
@app.route("/register", methods=["POST"])
def registerUser():
    firstnameform = request.form.get("firstname")
    lastnameform = request.form.get("lastname")
    emailform = request.form.get("email")
    passwordform = request.form.get("password")
    model.register_user(firstnameform,lastnameform,emailform,passwordform)
    return redirect(url_for("index"))

@app.route("/clear_session")
def session_clear():
    print session['email']
    session.clear()
    return redirect(url_for("index"))

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
    model.complete_commute_profile(user_id, startaddrform,destaddrform,starttimeform,endtimform,mobileform,workform,homeform)
    return redirect(url_for("testmap"))

@app.route("/testmap")
def testmap():
    #show markers for all destination addresses that exist in the Commute table
    address_query = model.session.query(model.Address).filter_by(id=model.Commute.end_addr_id).all()
    #address_query = model.session.query(model.Address).all()
    latlng_list = background.get_latlng(address_query)
    #print "latlng_list" , latlng_list
    data = numpy.array(latlng_list)
    centers = background.get_latlng_clustercenter(data,1)
    #lat = centers[0][0] #37.61127878
    #lng = centers[0][1] #-122.1289833
    lat = 37.468914900000000000
    lng = -122.155100899999980000

    return render_template("match.html", API_KEY=API_KEY, lat=lat, lng=lng , latlng_list=latlng_list)

if __name__ == "__main__":
    app.run(debug = True)