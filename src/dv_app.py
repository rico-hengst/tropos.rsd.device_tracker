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
import selector as selector


import hashlib
import secrets


import fhelper
import update_device_tracker



BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USER_CREDENTIALS = BASE_DIR + "/config/users.json"

# (A2) FLASK INIT
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"),)
app.secret_key = secrets.token_hex(32)  # Secure random secret key


# @app.route("/")
# def index():
    # return render_template("index.html")
    # return "<p>Hello, World!</p>"

# http://127.0.0.1:3000/select?date=2024-12-31T14:49:36Z,2024-12-31T14:49:36Z,

# DT API
@app.route("/select", methods=["GET"])
def select():
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
    your_requests = request.args.to_dict()
    
    if ("date" in your_requests):
        #print(type(request.args.getlist('date')))
        your_requests["date"] = request.args.getlist('date')
    
    devices=selector.select_history( your_requests ).replace([np.nan], [None], regex=False).to_json()
    
    
    
    username = None
    userroles = None
    if 'username' in session:
        username = session['username']
    
    return render_template("selectvis.html",devices=devices, your_requests=your_requests, user=fhelper.get_signed_user(username))


# DT API TAB
@app.route("/selecttab", methods=["GET"])
def selecttab():
    your_requests = request.args.to_dict()
    
    if ("date" in your_requests):
        #print(type(request.args.getlist('date')))
        your_requests["date"] = request.args.getlist('date')
    
    devices=selector.select_history( your_requests ).replace([np.nan], [None], regex=False).to_dict()
    
    username = None
    userroles = None
    if 'username' in session:
        username = session['username']
        

    return render_template("selecttab.html",devices=devices,your_requests=your_requests, user=fhelper.get_signed_user(username))
    


# Add device, authorized admin only
@app.route("/add/device", methods=["GET"])
def add_device():
    username = None
    userroles = None
    if not 'username' in session:
        flash('Sorry, this page is admin only restricted, please login first', 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        if not username == "admin":
            referrer_url = request.referrer
            print(request.headers.get("Referer"))
            flash('Sorry, this page is admin only restricted', 'info')
            return redirect(url_for(referrer))
        else:
            return render_template("add_device.html",classes0=selector.get_lookup_content("classes0"), user=fhelper.get_signed_user(username))
        
    
# Handle add device, authorized admin only
@app.route("/handle/add/device", methods=["GET"])
def handle_add_device():
    username = None
    userroles = None
    if not 'username' in session:
        flash('Sorry, this page is admin only restricted, please login first', 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        if not username == "admin":
            referrer_url = request.referrer
            print(request.headers.get("Referer"))
            flash('Sorry, this page is admin only restricted', 'info')
            return redirect(url_for(referrer))
        else:
            user=fhelper.get_signed_user(username)
            
            # requests
            your_requests = request.args.to_dict()
            # trim and delete empty form requests
            #your_requests = fhelper.purify_dict(your_requests)
            
            # check requests step by step
            if(your_requests["metadata.name"] in selector.get_lookup_content("devices")):
                flash('Sorry, name of instrument already exists: ' + your_requests["metadata.name"], 'info')
                exit()
            if not (your_requests["metadata.class0"] in user["class_edit_roles"]):
                flash('Sorry, you are not allowed to add devices with class: ' + your_requests["metadata.class0"], 'info')
                exit()
                
            
            update_device_tracker.add_device(your_requests)

            
            return render_template("handle_add_device.html",classes0=selector.get_lookup_content("classes0"), user=user)
            

# Add history, authorized admin only
@app.route("/add/history", methods=["GET"])
def add_history():
    username = None
    userroles = None
    if not 'username' in session:
        flash('Sorry, this page is admin only restricted, please login first', 'info')
        return redirect(url_for("login"))
    else:
        username = session['username']
        if not username == "admin":
            referrer_url = request.referrer
            print(request.headers.get("Referer"))
            flash('Sorry, this page is admin only restricted', 'info')
            return redirect(url_for(referrer))
        else:
            return render_template("add_history.html",classes0=selector.get_lookup_content("classes0"), user=fhelper.get_signed_user(username))
            

# Handle add device, authorized admin only
@app.route("/handle/add/history", methods=["GET"])
def handle_add_history():
    print(2)
    
###################################### LOGIN STUFF
# Route for the login page (GET only)
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Route for handling login form submission (POST only)
@app.route('/login', methods=['POST'])
def handle_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate input
        if not username or not password:
            error = 'Please provide both username and password'
            return render_template('login.html', error=error)
        
        # Find user in JSON file
        user = fhelper.find_user(username)
        
        if user and fhelper.verify_password(password, user['password_hash']):
            # Successful authentication
            print(session)
            session['username'] = username
            session['user_id'] = username  # Use username as user_id
            flash('Login successful!', 'info')
            
            username = session['username']
            return render_template('index.html', user=fhelper.get_signed_user(username))
        else:
            # Failed authentication
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

# Dashboard route (non-protected)
@app.route("/")
def index():
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
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return render_template('index.html')

# Registration route (optional)
@app.route('/register', methods=['GET', 'POST'])
def register():
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
            error = 'Please provide both username and password'
            return render_template('register.html', error=error)
        
        if password != confirm_password:
            error = 'Passwords do not match'
            return render_template('register.html', error=error)
        
        # Check if username already exists
        if fhelper.username_exists(username):
            error = 'Username already exists'
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
