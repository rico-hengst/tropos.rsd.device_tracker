#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json 
from jsonschema import validate, Draft7Validator, FormatChecker, ValidationError
import uuid
import datetime
import requests
import re
import logging
logging.basicConfig(level=logging.WARNING)


import pandas as pd

def main():
    uri = "http://rsd2.tropos.de/device-tracking/api?device=arielle"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
       return "Connection Error"  
    Jresponse = uResponse.text
    data = json.loads(Jresponse)
    
    
    # load schema
    with open("../config/schema_device.json", "r+") as file:
        try:
            device_schema = json.load(file)
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON syntax at schema device:", e)
    
    # load schema
    with open("../config/schema_history.json", "r+") as file:
        try:
            history_schema = json.load(file)
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON syntax at schema history:", e)
            
            #scheinbar schema nach einfügen pylarda nicht korrekt
    
    imported_devices = {}
    
    for device, device_dict in data.items():
        
        if "history" in device_dict:

            logging.info("New Device: " + device)
            
            new_history = get_device_history(history_schema, device_dict["history"])
            new_device_dict = get_device_record(device_schema, device_dict)
            
            new_device_dict["history"] = new_history
            
            
            logging.debug(str(new_device_dict))
            
            imported_devices[device] = new_device_dict
            
    # add instance record to json
    json_file= "../config/device_tracker_imported.json"
    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
        
        logging.info("Try to update json file: " + json_file)
        
        
        for device, imported_device_record in imported_devices.items():
        
            if not device in device_tracker.keys():
                
                logging.info("Add device reord: " + device)
                device_tracker[device] = imported_device_record
                file.seek(0)
                json.dump(device_tracker, file, indent=4)
            else:
                logging.warning("Skip device record: " + device + ", record already exists")

    return Jresponse
    
    
def get_device_history(history_schema, history):
    
    enum_countries = history_schema["$defs"]["location"]["oneOf"][0]["properties"]["country"]["enum"]
    
    # create empty array of history records
    new_history = []
    
    # loop all "old" history items and import to the new schema and add ne instance
    for key, history_record in history.items():
        logging.debug(history_record)
        
        # extract location
        if not history_record["location"]:
            logging.error("No location provided: " + str(history_record))
            exit()
        else:
            pattern = r"^(.+?)\s*\((.+?)\)\s*,\s*\[(.+?)\]"


            match = re.match(pattern, history_record["location"])

            if match:
                city    = match.group(1).strip()
                country = match.group(2).strip()
                koordinaten_str = match.group(3).strip()
                
                # Optional: Koordinaten in float umwandeln
                lat, lon = map(float, [x.strip() for x in koordinaten_str.split(',')])
                
                logging.info("Location pattern correct: " + city + " " + country)
                
            else:
                logging.warning("Location pattern not correct: " + str(history_record["location"]))
                #exit()
                continue
                
        # replace nan
        history_record["campaign"]  = re.sub(r"^nan$", "", history_record["campaign"] )
        
        # set elevation
        elevations = {
            "Cabau":-1,
            "Hyytiala":150,
            "Jülich":111,
            "Leipzig":126,
            "Lindenberg":104,
            "Melpitz":86,
            "Mindelo":13,
            "Neumayer III":43,
            "Warsaw":111,
            "Davos":1630,
            "Eriswil":921,
            "Evora":293,
            "Falkenberg":73,
            "Finokalia":297,
            "Invercargill":5,
            "Punta Arenas":9,
            "Antikythera":193,
            "Athens":212,
            "Dushanbe":864,
            "Hohenpeissenberg":974,
            "Manaus":109,
            "Nicosia":180,
            "Tel_Aviv":5,
            "Thessaloniki":50,
            "Limassol":10
        }
        
        new_history_record = {
            "uuid":         history_record["uuid"],
            "startdate":    history_record["startdate"] + "T00:00:01Z",
            "stopdate":     history_record["enddate"] + "T00:00:01Z",
            "created":      datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "campaign":     history_record["campaign"],
            "location": {
                "name":     city,
                "lat":      lat,
                "lon":      lon
            }
            
        }
        
        # add elevation
        if city:
            if city in elevations:
                new_history_record["location"]["elevation"] = elevations[city]
                
        # add country
        if country in enum_countries:
            new_history_record["location"]["country"] = country
        else:
            subst_countries = {
                "Cape Verde":"Cabo Verde",
                "Czech":"Czech Republic",
                "United Arab Emirates, UAE":"United Arab Emirates"
            }
            
            if country in subst_countries:
                country_substituted = subst_countries[country]
                new_history_record["location"]["country"] = country_substituted
                logging.warning("Country name substituted: " + country + " to " + country_substituted)
            else:
                logging.warning("Country not valid: " + country)
            
        
        if len(history_record["pylarda_camp"])>1 or len(history_record["pylarda_system"])>1 or len(history_record["pylarda_connectorfile"])>1:
             new_history_record["pylarda"] = {
                "camp"          : history_record["pylarda_camp"],
                "system"        : history_record["pylarda_system"],
                "connectorfile" : history_record["pylarda_connectorfile"]
             }
        
        
        # validation
    
        # old valiadation without format checker
        validate(
            instance=new_history_record,
            schema=history_schema,
        )

        validator = Draft7Validator(
                history_schema,
                format_checker=FormatChecker()
        )
        errors = list(validator.iter_errors(new_history_record))
        
        if not errors:
           # print(new_history_record)
            
            logging.info("✓ Validation History Successful: The JSON instance is valid.")
            new_history.append(new_history_record)
           
            
        else:
            logging.warning("✗ Validation History Failed: The JSON instance is invalid.")

            for error in errors:
                # error.message usually contains the specific reason
                print(f"  - Error: {error.message}")
                print(f"    Path: {list(error.path)}")
                print(f"    Validator: {error.validator}")
                
            else:
                print("not ok")
                exit()
        
        
    return(new_history)
        
    
    
def get_device_record(device_schema, device_dict):
    
    # distinguish between device and platform
    is_platform = False
    if re.match("taro_", device_dict["device"] , re.IGNORECASE) or re.match("mordor_", device_dict["device"] , re.IGNORECASE):
        is_platform = True
        
    # create new record
    new_device_record = {
        "metadata": {
            "name"                      : device_dict["device"],  
            "description"               : "",  
            "is_platform"               : is_platform,
            "created"                   : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "class"                     : [ device_dict["class"],  device_dict["type"] ],
            "device_manufacturer"       : { "name" : "" },
            "device_model"              : { 
                "name"  : "",
                "pid"   : device_dict["pid"],
                "serial": {}
             },
            "owner"                     : { 
                "name" : "",
                "inv"  : {}
            }
        },
        "history": [],
        "calibration" : []
    }
    #print(new_device_record)
    
    # validation
    
    # old valiadation without format checker
    validate(
        instance=new_device_record,
        schema=device_schema,
    )




    validator = Draft7Validator(
            device_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(new_device_record))
    
    if not errors:
        logging.info("✓ Validation Device Successful: The JSON instance is valid.")
        logging.debug(new_device_record)
        
        return new_device_record
       
        
    else:
        logging.warning("✗ Validation Device Failed: The JSON instance is invalid.")
        logging.warning(new_device_record)

        for error in errors:
            # error.message usually contains the specific reason
            print(f"  - Error: {error.message}")
            print(f"    Path: {list(error.path)}")
            print(f"    Validator: {error.validator}")
            
        else:
            print("not ok")
            exit()
            

main()

