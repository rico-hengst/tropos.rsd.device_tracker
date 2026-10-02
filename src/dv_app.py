# (A) INIT
# (A1) LOAD REQUIRED PACKAGES
from flask import Flask, render_template, make_response, request, redirect, url_for, flash, jsonify, render_template_string, abort, session
#from werkzeug.datastructures import ImmutableMultiDict
#from werkzeug.middleware.dispatcher import DispatcherMiddleware ## for fixing url_for problems when using reversed proxy ( source: https://github.com/pallets/werkzeug/issues/1663)
import bcrypt, jwt, time, random
import requests
import json
import datetime
import re
import os
import sys
import pandas as pd
import numpy as np
from jinja2 import Environment


import hashlib
import secrets

# import logging
# logging.basicConfig(level=logging.WARNING)
import dv_config
# Initialize the logger once in the main entry point
logger = dv_config.setup_logger("DV-Logger")
# get ENV variables
ENV = dv_config.get_env()

import fhelper
import update_device_tracker
import selector



BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USER_CREDENTIALS = BASE_DIR + "/config/users.json"
if os.getenv("USER_CREDENTIALS_FILE"):
    USER_CREDENTIALS = BASE_DIR + "/" + os.getenv("USER_CREDENTIALS_FILE")

if not os.path.isfile(USER_CREDENTIALS):
    logger.error("File not exists: " + USER_CREDENTIALS)
    
logger.info(os.getenv("USER_CREDENTIALS_FILE"))

# (A2) FLASK INIT
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"),)
app.secret_key = secrets.token_hex(32)  # Secure random secret key

# create string_datetime_filter
env = Environment()

def format_string_datetime(value):
    # "2022-06-30T13:54:01Z" -> "2022-06-30 13:54"
    return value[:10] + " " + value[11:16]

# Register the filter with Flask's Jinja2 environment
app.jinja_env.filters['format_string_datetime'] = format_string_datetime

def get_serial_part_of_keyname(string, separator="#",whichpart=0):
    # "keyname#20220630135404#"
    my_list = string.split(separator)
    print(string)
    if not len(my_list) == 3:
        return
    if whichpart == 0:
        return my_list[0]
    elif whichpart == 1:
        return my_list[1].replace(separator,"",2)
app.jinja_env.filters['get_serial_part_of_keyname'] = get_serial_part_of_keyname


# @app.route("/")
# def index():
    # return render_template("index.html")
    # return "<p>Hello, World!</p>"

# http://127.0.0.1:3000/select?date=2024-12-31T14:49:36Z,2024-12-31T14:49:36Z,

# DT API
@app.route("/select", methods=["GET"])
def select():
    logger.debug("Select page")
    your_requests = request.args.to_dict()
    
    if ("date" in your_requests):
        #print(type(request.args.getlist('date')))
        your_requests["date"] = request.args.getlist('date')
    

    #devices=selector.select_history({"platform":"taro"}).to_json(indent=2) # works well as direct return
    devices=selector.select_history( your_requests ).replace([np.nan], [None], regex=False).to_dict()
    return jsonify(devices)

# DT API SVG
@app.route("/selectvis", methods=["GET"])
def selectvis():
    logger.debug("Selectvis page")
    your_requests = request.args.to_dict()
    
    if ("date" in your_requests):
        #print(type(request.args.getlist('date')))
        your_requests["date"] = request.args.getlist('date')
    
    devices=selector.select_history( your_requests ).replace([np.nan], [None], regex=False).to_json()
    classes0=selector.get_lookup_content("classes0")
    
    
    username = None
    userroles = None
    if 'username' in session:
        username = session['username']
    
    return render_template("selectvis.html",devices=devices,classes0=classes0, your_requests=your_requests, user=fhelper.get_signed_user(username))


# DT API TAB
@app.route("/selecttab", methods=["GET"])
def selecttab():
    logger.debug("Selecttab page")
    your_requests = request.args.to_dict()
    
    if ("date" in your_requests):
        #print(type(request.args.getlist('date')))
        your_requests["date"] = request.args.getlist('date')
        
    # remove empty key value sets
    your_requests=fhelper.purify_dict_v2(your_requests)

    devices=selector.select_history( your_requests ).replace([np.nan], [None], regex=False).to_dict()
    classes0=selector.get_lookup_content("classes0")
    
    username = None
    userroles = None
    if 'username' in session:
        username = session['username']
        

    return render_template("selecttab.html",devices=devices,classes0=classes0,your_requests=your_requests, user=fhelper.get_signed_user(username))
    


# Add device, authorized admin only
@app.route("/add/device", methods=["GET"])
def add_device():
    logger.debug("Add device page")
    username = None
    userroles = None
    if not 'username' in session:
        message = "Sorry, this page is login restricted, please login first"
        logger.info(message)
        flash(message, 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        user = fhelper.get_signed_user(username)
        
        # requests
        your_requests = request.args.to_dict()
        
        # init key
        devices = None
        device_keyname = None
        
        # if device was provided: edit versus add
        if "device" in your_requests:
            
            # look for uuid history device(s)
            devices=selector.get_lookup_content("devices")
            
            
            if your_requests["device"] in devices:
                device_keyname = your_requests["device"]
                flash("Device detected" )
                
                # warning if you want to edit a device and user_acces_role doesnt match the device class0
                class0 = devices[device_keyname]["metadata"]["class"][0]
                if class0 not in user["class_edit_roles"]:
                    your_requests = {}
                    flash("Your class_edit_roles avoids the modification of the current device with the class0: " + class0)
            else:
                logger.debug("no device exists")
                flash("No devices detected: " + your_requests["device"] )
        
        
        return render_template("add_device.html",classes0=selector.get_lookup_content("classes0"), devices=devices, device_keyname=device_keyname,your_requests=your_requests,user=user)
        
    
# Handle add device, authorized admin only
@app.route("/handle/add/device", methods=["GET"])
def handle_add_device():
    logger.debug("Handle add device page")
    username = None
    userroles = None
    if not 'username' in session:
        message = "Sorry, this page is login restricted, please login first"
        logger.debug(message)
        flash(message, 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        user=fhelper.get_signed_user(username)
            
        # requests
        your_requests = request.args.to_dict()
        # trim and delete empty form requests
        #your_requests = fhelper.purify_dict(your_requests)
        
        # check requests step by step
        # if(your_requests["metadata.name"] in selector.get_lookup_content("devices")):
            # flash('Sorry, name of instrument already exists: ' + your_requests["metadata.name"], 'info')
            # return render_template("handle_add_device.html",user=user)
        if not (your_requests["metadata.class0"] in user["class_edit_roles"]):
            message = "Sorry, you are not allowed to add devices with class: " + your_requests["metadata.class0"]
            logger.debug(message)
            flash(message, 'info')
            return render_template("handle_add_device.html",user=user)
            
        # update the database
        xxx=update_device_tracker.add_device(your_requests)
        
        if "message" in xxx:
            if "message" in xxx["message"]:
                flash(xxx["message"]["message"])

        return render_template("handle_add_device.html", user=user)
            

# Add history, authorized only
@app.route("/add/history", methods=["GET"])
def add_history():
    logger.debug("Add history page")
    username = None
    userroles = None
    if not 'username' in session:
        message = "Sorry, this page is login restricted, please login first"
        logger.debug(message)
        flash(message, 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        user=fhelper.get_signed_user(username)
        if not user["access"] == "readwrite":
            referrer_url = request.referrer
            flash('Sorry, this page is user access readwrite only restricted', 'info')
            return redirect(url_for(referrer))
        else:
            your_requests = request.args.to_dict()
            
            # init device tracker record(s)
            uuid_devices = None
            uuid_device_key = None
            
            # if uui was provided
            if "uuid" in your_requests:
                
                # look for uuid history device(s)
                uuid_devices=selector.select_history( {"uuid" : your_requests["uuid"] } ).replace([np.nan], [None], regex=False).to_dict()
                
                
                if uuid_devices:
                    if (len(uuid_devices)>1):
                        message = "Multiple uuids exists, based on your request!"
                        logger.warning(message)
                        exit()
                    uuid_device_key = list(uuid_devices.keys())[0]
                else:
                    message = "Your reuested uuids not exists:" + your_requests["uuid"]
                    logger.info(message)
                    flash(message)
                    
            # load schema
            with open("../config/schema_history.json", "r+") as file:
                try:
                    history_schema = json.load(file)
                except json.JSONDecodeError as e:
                    message = "Invalid JSON syntax at schema history:" + e
                    logger.error(message)
                    
            countries = history_schema["$defs"]["location"]["oneOf"][0]["properties"]["country"]["enum"]
                            
            
            devices = selector.get_lookup_content("devices")
            return render_template("add_history.html",countries=countries, locations=selector.get_lookup_content("locations"),devices=devices, uuid_devices=uuid_devices, uuid_device_key=uuid_device_key ,your_requests=your_requests,user=user)
            

# Handle add history
@app.route("/handle/add/history", methods=["GET"])
def handle_add_history():
    logger.debug("Handle add history page")
    username = None
    userroles = None
    if not 'username' in session:
        message = "Sorry, this page is session restricted, please login first"
        logger.info(message)
        flash(message, 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        user=fhelper.get_signed_user(username)
        
        your_requests = request.args.to_dict()
        
        xxx=update_device_tracker.add_history(your_requests)
        
        if "message" in xxx:
            if "message" in xxx["message"]:
                flash(xxx["message"]["message"],xxx["message"]["type"])

            
        return render_template("handle_add_history.html",classes0=selector.get_lookup_content("classes0"), user=user)
        
        
        
# Add history, authorized only
@app.route("/add/calibration", methods=["GET"])
def add_calibration():
    logger.debug("Add calibration page")
    username = None
    userroles = None
    if not 'username' in session:
        message = "Sorry, this page is session restricted, please login first"
        logger.info(message)
        flash(message, 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        user=fhelper.get_signed_user(username)
        if not user["access"] == "readwrite":
            referrer_url = request.referrer
            flash('Sorry, this page is user access readwrite only restricted', 'info')
            return redirect(url_for(referrer))
        else:
            your_requests = request.args.to_dict()
            
            # init device tracker record(s)
            uuid_calibrations = None
            uuid_calibration_key = None
            
            # if uui was provided
            if "uuid" in your_requests:
                
                # look for uuid calibration device(s)
                uuid_calibrations=selector.select_calibration( {"uuid" : your_requests["uuid"] } ).replace([np.nan], [None], regex=False).to_dict()
                
                if uuid_calibrations:
                    if (len(uuid_calibrations)>1):
                        message = "Your request returned multiple calibration records with uuid: " + your_requests["uuid"]
                        logger.warning(message)
                        exit()
                    uuid_calibration_key = list(uuid_calibrations.keys())[0]
                else:
                    message = "No calibration uuid detected: " + your_requests["uuid"]
                    logger.info(message)
                    flash(message)
                    
            # load schema
            with open("../config/schema_calibration.json", "r+") as file:
                try:
                    history_schema = json.load(file)
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON syntax at schema calibration:", e)
                    
            devices = selector.get_lookup_content("devices")
            return render_template("add_calibration.html",devices=devices, uuid_calibrations=uuid_calibrations, uuid_calibration_key=uuid_calibration_key ,your_requests=your_requests,user=user)
            

# Handle add calibration
@app.route("/handle/add/calibration", methods=["GET"])
def handle_add_calibration():
    logger.debug("Handle add calibration page")
    username = None
    userroles = None
    if not 'username' in session:
        message = "Sorry, this page is session restricted, please login first"
        logger.info(message)
        flash(message, 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        user=fhelper.get_signed_user(username)
        
        your_requests = request.args.to_dict()
        
        if ("calibration.performed_period_dates" in your_requests):
            #print(type(request.args.getlist('date')))
            your_requests["calibration.performed_period_dates"] = request.args.getlist('calibration.performed_period_dates')
        if ("calibration.valid_period_dates" in your_requests):
            #print(type(request.args.getlist('date')))
            your_requests["calibration.valid_period_dates"] = request.args.getlist('calibration.valid_period_dates')
            
        # remove empty key value sets
        your_requests=fhelper.purify_dict_v2(your_requests)
        
        
        xxx=update_device_tracker.add_calibration(your_requests)
        if "message" in xxx:
            if "message" in xxx["message"]:
                flash(xxx["message"]["message"],xxx["message"]["type"])
        
        return render_template("handle_add_calibration.html")


###################################### LOGIN STUFF
# Route for the login page (GET only)
@app.route('/login', methods=['GET'])
def login():
    logger.debug("Login page")
    return render_template('login.html')

# Route for handling login form submission (POST only)
@app.route('/login', methods=['POST'])
def handle_login():
    logger.debug("Handle login page")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate input
        if not username or not password:
            message = 'Please provide both username and password'
            error = message
            logger.info(message)
            return render_template('login.html', error=error)
        
        # Find user in JSON file
        user = fhelper.find_user(username)
        
        if user and fhelper.verify_password(password, user['password_hash']):
            # Successful authentication
            logger.debug(session)
            session['username'] = username
            session['user_id'] = username  # Use username as user_id
            flash('Login successful!', 'info')
            
            username = session['username']
            return render_template('index.html', user=fhelper.get_signed_user(username))
        else:
            # Failed authentication
            message = 'Invalid username or password'
            error = message
            logger.info(message)
            return render_template('login.html', error=error)
    
    return render_template('login.html')

# Dashboard route (non-protected)
@app.route("/")
def index():
    logger.debug("Index page")
    if 'username' in session:
        username = session['username']
        return render_template('index.html', user=fhelper.get_signed_user(username))
    else:
        #flash('Please login first', 'error')
        #return redirect(url_for('login'))
        return render_template('index.html')

# Logout route
@app.route('/logout')
def logout():
    logger.debug("Logout page")
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return render_template('index.html')

# Registration route (optional)
@app.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug("Register page")
    # handle only admin is allowed for that
    if 'username' in session:
        username = session['username']
        if not username == "admin":
            return "Please login as admin to use that feature!"
    else:
        return "Please login as admin to use that feature!"
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate input
        if not username or not password:
            message = 'Please provide both username and password'
            error = message
            logger.info(message)
            return render_template('register.html', error=error)
        
        if password != confirm_password:
            message = 'Passwords do not match'
            error = message
            logger.info(message)
            return render_template('register.html', error=error)
        
        # Check if username already exists
        if fhelper.username_exists(username):
            message = 'Username already exists'
            error = message
            logger.info(message)
            return render_template('register.html', error=error)
        
        # Add new user
        success, message = fhelper.add_user(username, password)
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            error = message
            return render_template('register.html', error=error)
    
    return render_template('register.html')


    

if __name__ == "__main__":
  app.run(HOST_NAME, HOST_PORT,debug=True)
