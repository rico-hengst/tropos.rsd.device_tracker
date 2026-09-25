# fhelper.py - Helper functions for secure login application
import json
import hashlib
import os
import secrets
# Echoing password and masked with hashtag(#)
import maskpass  # importing maskpass library

import logging
logging.basicConfig(level=logging.INFO)

import selector

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

USER_CREDENTIALS = BASE_DIR + "/config/users.json"
if os.getenv("USER_CREDENTIALS_FILE"):
    USER_CREDENTIALS = BASE_DIR + "/" + os.getenv("USER_CREDENTIALS_FILE")

if not os.path.isfile(USER_CREDENTIALS):
    logging.error("File not exists: " + USER_CREDENTIALS)
    
# Function to generate salt
def generate_salt(length=64):
    """Generate a random salt for password hashing"""
    return secrets.token_hex(length // 2)

# Function to hash password with salt
def hash_password(password, salt):
    """Hash password using SHA256 with salt"""
    salted_password = password + salt
    password_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return f"sha256:{password_hash}:{salt}"

# Function to verify password
def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        # Parse the stored hash format: "sha256:hash:salt"
        parts = stored_hash.split(':')
        if len(parts) != 3 or parts[0] != 'sha256':
            return False
        
        stored_hash_value = parts[1]
        salt = parts[2]
        
        # Hash the provided password with the stored salt
        salted_password = password + salt
        computed_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        
        return computed_hash == stored_hash_value
    except Exception:
        logging.warning("Password or login doesnt match!")
        return False

# Function to load users from JSON file
def load_users():
    """Load users from JSON file"""
    try:
        with open(USER_CREDENTIALS, 'r') as file:
            data = json.load(file)
            return data.get('users', {})
    except FileNotFoundError:
        logging.warning("file not found " + USER_CREDENTIALS)
        return {}
    except json.JSONDecodeError:
        return {}

# Function to find user by username
def find_user(username):
    """Find user by username"""
    users = load_users()
    # Return user if exists, None otherwise
    logging.warning(username)
    logging.warning(users)
    return users.get(username)

# Function to check if username exists
def username_exists(username):
    """Check if username exists in the system"""
    users = load_users()
    return username in users

# Function to add a new user (for registration)
def add_user(username, password):
    """Add a new user to the system"""
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists"
    
    # Generate salt and hash password
    salt = generate_salt()
    password_hash = hash_password(password, salt)
    
    # Add new user
    users[username] = {
        "password_hash": password_hash,
        "salt": salt
    }
    
    # Save updated users back to JSON file
    try:
        with open(USER_CREDENTIALS, 'w') as file:
            json.dump({"users": users}, file, indent=2)
        return True, "User added successfully"
    except Exception as e:
        return False, f"Error adding user: {str(e)}"

# Initialize with some test users (optional - for first run)
def initialize_users():
    """Initialize users with secure password hashing"""
    if not os.path.exists(USER_CREDENTIALS):
        # Create initial users with secure passwords
        initial_users = {
            "admin": {"password": "admin123"},
            "user1": {"password": "password123"},
            "testuser": {"password": "test123"}
        }
        
        users_data = {"users": {}}
        for username, user_data in initial_users.items():
            salt = generate_salt()
            password_hash = hash_password(user_data['password'], salt)
            users_data["users"][username] = {
                "password_hash": password_hash,
                "salt": salt
            }
        
        with open(USER_CREDENTIALS, 'w') as file:
            json.dump(users_data, file, indent=2)
        logging.info("Users initialized with secure password hashing")


# admin tool to register user or reset password
def register_user_or_set_password(username):
    if not os.path.exists(USER_CREDENTIALS):
        print("No data about users!")
    else:
        user            = find_user(username)
        
        # set password_hash
        pwd             = maskpass.askpass(prompt="Enter your (new) password: ", mask="#")
        salt            = generate_salt()
        password_hash   = hash_password(pwd, salt)
        
        users           = None
        
        # open file to edit
        try:
            with open(USER_CREDENTIALS, 'r') as file:
                data = json.load(file)
                users = data.get('users', [])
        except FileNotFoundError:
            print("file not found")
            exit()
        except json.JSONDecodeError:
            print("decoding error")
            exit()
        
        # update dictionary
        success = 0
        if username in users:
            success = 1
            print("Reset password")
            users[username]["salt"] = salt
            users[username]["password_hash"] = password_hash
        
                
        if success == 0:
            print("Register user")
            users[username] = {
                "password_hash" : password_hash,
                "salt"          : salt
            }
        
        data["users"] = users
        
        # write to file
        with open(USER_CREDENTIALS, 'w') as file:
            json.dump(data, file, indent=2)
        print("User database updated: " + username)
        

# get roles from user
def get_roles(username):
    user = find_user(username)
    
    if not user:
        return None
    else:
        
        devices = selector.get_lookup_content("devices")
        return ({ 
            "username"          : username,
            "class_edit_roles"  : user["class_edit_roles"] if "class_edit_roles" in user else [] , 
            "access"            : user["access"] if "access" in user else None
        })
    
# get_signed_user
def get_signed_user(username):
    
    return get_roles(username)
    
    
############
#### input: dict (with values (list))
#### return dict, delete list elements with "", delete key if list will be empty
#### fhelper.purify_dict_v2({"key1":"value1","key2":"","date_a":["","2012-01-02"], "date_b":["","","",""]})
#### returns: {'key1': 'value1', 'date_a': ['2012-01-02']}
############
def purify_dict_v2(my_dict):
    my_dict2={}
    for my_key in my_dict:
        i=-1
        elements2pop = []
        
        if type(my_dict[my_key]) == list:
            for list_element in my_dict[my_key]:
                if(list_element.isspace() or list_element=="" ):
                    logging.info("Remove empty list element at key: " + my_key)
                else:
                    logging.info("Add/append value to key as list: " + my_key )
                    if my_key in my_dict2:
                        my_dict2[my_key].append(list_element)
                    else:
                        my_dict2[my_key] = [list_element]
        else:
            if my_dict[my_key] != "":
                my_dict2[my_key] = my_dict[my_key]
                logging.info("Add string at key: " + my_key)
            else:
                logging.info("Remove empty string at key: " + my_key)


    return my_dict2

############
