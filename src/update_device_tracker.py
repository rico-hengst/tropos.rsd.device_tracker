#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json 
from jsonschema import validate, Draft7Validator, FormatChecker, ValidationError
import uuid
import datetime
import os
import re
import numpy as np


import pandas as pd
import logging
logging.basicConfig(level=logging.WARNING)


import selector


def json_file():
    json_file= "../config/device_tracker_imported.json"
    if not os.path.isfile(json_file):
        logging.error("JSON not exists: " + json_file)
        json_file = None
        
    return json_file


# push the user input into the expected format
def prepare_add_device(myrequests):

    devive_is_platform = True if "metadata.is_platform" in myrequests else False

    
    # detect serial keys
    pattern_serial      = re.compile(r"^(serial_key)_(\d+)$")
    pattern_inventory   = re.compile(r"^(inventory_key)_(\d+)$")
   
    # grep serial and inventory user input and put to dicts
    dict_serial = {}
    dict_inventory = {}
    index=-1
    for key_name in myrequests:
        index +=1
        match_serial    = pattern_serial.match(key_name)
        match_inventory = pattern_inventory.match(key_name)
        if match_serial:
            text_part = match_serial.group(1)
            int_part = match_serial.group(2)
            numeric_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
            key_serial = myrequests[key_name] + "#" + str(numeric_id) + str(index) + "#"
            value_serial = myrequests[ key_name.replace("serial_key", "serial_value") ] if key_name.replace("serial_key", "serial_value") in myrequests else False
            
            # set
            dict_serial[key_serial] = value_serial
            
        elif match_inventory:
            text_part = match_inventory.group(1)
            int_part = match_inventory.group(2)
            
            numeric_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
            key_inventory = myrequests[key_name] + "#" + str(numeric_id) + str(index) + "#"
            value_inventory = myrequests[ key_name.replace("inventory_key", "inventory_value") ] if key_name.replace("inventory_key", "inventory_value") in myrequests else False
            
            # set
            dict_inventory[key_inventory] = value_inventory
    
    #print(dict_serial)
    #print(dict_inventory)
    
    my_dict_new = {
        "metadata": {
            "name":             myrequests["metadata.name"],
            "description":      myrequests["metadata.description"] if "metadata.description" in myrequests else "",
            "is_platform":      devive_is_platform,
            "created":          datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "class": [
                myrequests["metadata.class0"],
                myrequests["metadata.class1"]
            ],
            "device_manufacturer" : { 
                "name" :        myrequests["metadata.device_manufacturer.name"] if "metadata.device_manufacturer.name" in myrequests else "", 
                "address":      myrequests["metadata.device_manufacturer.address"] if "metadata.device_manufacturer.address" in myrequests else "", 
                "contact":      myrequests["metadata.device_manufacturer.contact"] if "metadata.device_manufacturer.contact" in myrequests else ""
            },
            "device_model" : {
                "name":         myrequests["metadata.device_model.name"] if "metadata.device_model.name" in myrequests else "",  
                "description":  myrequests["metadata.device_model.description"] if "metadata.device_model.description" in myrequests else "",
                "purchased":    myrequests["metadata.device_model.purchased"] if "metadata.device_model.purchased" in myrequests else "",
                "pid":          myrequests["metadata.device_model.pid"] if "metadata.device_model.pid" in myrequests else "",
                "serial":       dict_serial
            },
            "owner" : {
                "name" :        myrequests["metadata.owner.name"] if "metadata.owner.name" in myrequests else "", 
                "address":      myrequests["metadata.owner.address"] if "metadata.owner.address" in myrequests else "", 
                "contact":      myrequests["metadata.owner.contact"] if "metadata.owner.contact" in myrequests else "",
                "inv":          dict_inventory
            },
        },
        "history":[],
        "calibration":[]
        
    }
    
    # update some parts if edit mode
    if "requested_mode" in myrequests:
       
        
        if myrequests["requested_mode"] == "edit" and "device_keyname" in myrequests:
            # load device
            
            device_keyname = myrequests["device_keyname"]
            
            devices = selector.get_lookup_content("devices")
            
            if device_keyname in devices:                
                
                # update timestamp
                my_dict_new["metadata"]["created"] = devices[device_keyname]["metadata"]["created"]
                
                # update calibration and history
                if "calibration" in devices[device_keyname]:
                    my_dict_new["calibration"] = devices[device_keyname]["calibration"]
                if "history" in devices[device_keyname]:
                    my_dict_new["history"] = devices[device_keyname]["history"]
            else:
                print("error")
                exit()
                
            
    #print(2222)
    #print(my_dict_new)
    
    return my_dict_new
    
    
# push the user input into the expected format
def prepare_add_history(myrequests):
    
    # check if request_mode is edit/add
    if "requested_mode" in myrequests and myrequests["requested_mode"] != "add" and myrequests["requested_mode"] != "edit":
        logging.warning("Form request_mode add/edit expected!")
        
        return { 
            "returned_record"   : 1,
            "message"           : {
                "type": "warning",
                "message": "Form request_mode add/edit expected!"
            } 
        }

    my_location = {
        "is_mobile": True if "history.location.is_mobile" in myrequests else False
    }
    
  
    for key_name in myrequests:
        print(key_name)
        
        # transform datetime objects
        if key_name == "history.startdate":
            date_object = datetime.datetime.strptime(myrequests["history.startdate"], '%Y-%m-%d %H:%M')
            myrequests["history.startdate"] = date_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        if key_name == "history.stopdate":
            date_object = datetime.datetime.strptime(myrequests["history.stopdate"], '%Y-%m-%d %H:%M')
            myrequests["history.stopdate"] = date_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # split to a list
        if key_name == "history.platform":
            platforms = myrequests["history.platform"].strip()
            if len(platforms)==0:
                myrequests["history.platform"] = []
            else:
                platforms = myrequests["history.platform"].split(",")
                myrequests["history.platform"] = [platform.strip() for platform in platforms]
                
        # split to a list
        if key_name == "history.pylarda.connectorfile":
            cfs = myrequests[key_name].strip()
            if len(cfs)==0:
                myrequests[key_name] = []
            else:
                cfs = myrequests[key_name].split(",")

                myrequests[key_name] = [l.strip() for l in cfs]

                
        # update location
        if not my_location["is_mobile"]:
            print("not mobile")
            if key_name == "history.location.name":
                locations = selector.get_lookup_content("locations")
                
                # take al location info from database
                if myrequests[key_name] in locations:
                    my_location["name"] = myrequests[key_name]
                    my_location["lat"] = locations[ myrequests[key_name] ][ "lat" ]
                    my_location["lon"] = locations[ myrequests[key_name] ][ "lon" ]
                    
                    if "elevation" in locations[ myrequests[key_name] ]:
                        my_location["elevation"] = locations[ myrequests[key_name] ]["elevation"]

        else:
            print("mobile")
            if key_name == "history.location.name":
                my_location["name"] = myrequests[key_name]
                print("set: wdeqwqwdrqw" + key_name)
            elif key_name == "history.location.track_url":
                my_location["track_url"] = myrequests[key_name]
                print("set: " + key_name)
            elif key_name == "history.location.track_desc":
                my_location["track_desc"] = myrequests[key_name]
                print("set: " + key_name)
                    
                
    # check if start => stop
    if myrequests["history.startdate"] > myrequests["history.stopdate"]:
        logging.warning("Start > Stop, exit")
        
        return { 
            "returned_record"   : 1,
            "message"           : {
                "type": "warning",
                "message": "Start > Stop, exit"
            } 
        }
        
    
    # check if dates are overlapped with further history records 
    #### exception if "edit" node and if both uuid are identical
    devices=selector.select_history( {"device":myrequests["device"]} ).replace([np.nan], [None], regex=False).to_dict()
   
    if bool(devices) and myrequests["device"] in devices and "history" in devices[myrequests["device"]]:
        for history in devices[myrequests["device"]]["history"]:
            if myrequests["history.stopdate"] > history["startdate"] and myrequests["history.startdate"] < history["stopdate"]:
                if "requested_mode" in myrequests and myrequests["requested_mode"] == "edit" and myrequests["history.uuid"] == history["uuid"]:
                    logging.info("Edit mode, overlapping history record between provided and the identical uuid record")
                
                else:
                    message = "On or multiple history record perios did intersect with start/stoptime of your record" + str(history) + " versus " + myrequests["history.startdate"] + " " + myrequests["history.stopdate"]
                    logging.warning(message)
                    return { 
                        "message"           : {
                            "type": "warning",
                            "message": message
                        } 
                    }
            
        
    
    my_history_new = {
        "startdate"     : myrequests["history.startdate"],
        "stopdate"      : myrequests["history.stopdate"],
        "created"       : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "uuid"          : myrequests["history.uuid"] if "history.uuid" in myrequests else str(uuid.uuid1()),
        "campaign"      : myrequests["history.campaign"],
        "platform"      : myrequests["history.platform"] if len(myrequests["history.platform"]) > 0 else [],
        "location"      : my_location,
        "pylarda"       : {
            "camp"          : myrequests["history.pylarda.camp"],
            "system"        : myrequests["history.pylarda.system"],
            "connectorfile" : myrequests["history.pylarda.connectorfile"]
        }

    }
    

    
    return {
        "return_ok"   : my_history_new
    }
    



def add_calibration(device, calibration_record):
    # load schema
    with open("../config/schema_calibration.json", "r+") as file:
        try:
            calibration_schema = json.load(file)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)
        
        
        
    
    # old valiadation without format checker
    validate(
        instance=calibration_record,
        schema=calibration_schema,
    )




    validator = Draft7Validator(
            calibration_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(calibration_record))
    
    if not errors:
        print("✓ Validation Successful: The JSON instance is valid.")
        print(calibration_record)
        
        
        json_file= "../config/device_tracker.json"
        with open(json_file, "r+") as file:
            device_tracker = json.load(file)
            
            print("Update json_file: " + json_file )
            
            if device in device_tracker.keys():
                if "calibration" in device_tracker[device].keys():
                    device_tracker[device]["calibration"].append(calibration_record)
                   # print(device_tracker)
                    file.seek(0)
                    json.dump(device_tracker, file, indent=4)
                    
                else:
                    print("no key2")
            else:
                print("-- no device in json file detected: " + device + ", no validation")

        
    else:
        print("✗ Validation Failed: The JSON instance is invalid.")
        print(calibration_record)

        for error in errors:
            # error.message usually contains the specific reason
            print(f"  - Error: {error.message}")
            print(f"    Path: {list(error.path)}")
            print(f"    Validator: {error.validator}")
            
            
            




def add_history(myrequests):
    
    logging.info("Start: Add history record")
    history_record_ready = prepare_add_history(myrequests)
    
    
    device=myrequests["device"]
    
    my_rr = {}
    
    if "message" in history_record_ready:
        my_rr["message"]= history_record_ready["message"]


    if not "return_ok" in history_record_ready:
        return my_rr
    
    # load schema
    with open("../config/schema_history.json", "r+") as file:
        try:
            history_schema = json.load(file)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)
        
        
        
    
    # old valiadation without format checker
    # validate(
        # instance=history_record_ready["return_ok"],
        # schema=history_schema,
    # )




    validator = Draft7Validator(
            history_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(history_record_ready["return_ok"]))
    
    if not errors:
        logging.info("✓ Validation Successful: The JSON instance is valid.")
        logging.debug(history_record_ready["return_ok"])
        
        
        my_json_file = json_file()
        with open(my_json_file, "r+") as file:
            device_tracker = json.load(file)
            
            logging.info("Update json_file: " + my_json_file )
            
            if device in device_tracker.keys():
                if "history" in device_tracker[device].keys():
                    if "history.uuid" in myrequests and myrequests["requested_mode"] == "edit":
                        for index in range(len(device_tracker[device]["history"])):
                            if device_tracker[device]["history"][index]["uuid"] == history_record_ready["return_ok"]["uuid"]:
                                device_tracker[device]["history"][index] = history_record_ready["return_ok"]
                                logging.info("Edit history record: " + str(history_record_ready))
                                break
                    else:
                        logging.info("Add history record: " + str(history_record_ready))
                        device_tracker[device]["history"].append(history_record_ready["return_ok"])

                   # print(device_tracker)
                    file.seek(0)
                    json.dump(device_tracker, file, indent=4)
                    
                    message = "Updated history at device: " + device
                    logging.info(message)
                    return {"message": {"type":"info","message":message}}
                    
                else:
                    message = "No history key at device detected: " + device
                    logging.warning(message)
                    return {"message": {"type":"warning","message":message}}
            else:
                message = "-- no device in json file detected: " + str(device) + ", no validation"
                logging.warning(message)
                return {"message": {"type":"warning","message":message}}

        
    else:
        message = "✗ Validation Failed: The JSON instance is invalid." + str(history_record_ready["return_ok"])
        logging.warning(message)
        logging.debug(history_record_ready["return_ok"])

        for error in errors:
            # error.message usually contains the specific reason
            print(f"  - Error: {error.message}")
            print(f"    Path: {list(error.path)}")
            print(f"    Validator: {error.validator}")
            
        return {"message": {"type":"warning","message":message}}
            
            
    logging.info("End: Add history record")
            
            
            

        
        
def add_device(myrequests):
    
    logging.info("Start: Add device record")
    device_record_ready = prepare_add_device(myrequests)
    

    # load schema
    with open("../config/schema_device.json", "r+") as file:
        device_schema = json.load(file)
        
    
    
    validate(instance=device_record_ready, schema=device_schema)
    
    validator = Draft7Validator(
            device_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(device_record_ready))
    
   
    
    if errors:
        logging.info("✗ Validation Failed: The JSON instance is invalid.")
        logging.debug(device_record_ready)

        for error in errors:
            # error.message usually contains the specific reason
            logging.debug(f"  - Error: {error.message}")
            logging.debug(f"    Path: {list(error.path)}")
            logging.debug(f"    Validator: {error.validator}")
            
    else :
        logging.info("✓ Validation Successful: The JSON instance is valid.")
        logging.debug(device_record_ready)
        
        # add instance record to json
        my_json_file = json_file()
        
        # 1. load file content to variable
        device_tracker = None
        with open(my_json_file, "r+") as file:
            device_tracker = json.load(file)
        file.close()
        
        # 2 open file to write the updated content to the file
        with open(my_json_file, "w+") as file:
            
            # substitute space by - and transform to lowwer all keynames
            device_keyname = re.sub(r"\s+", '-', device_record_ready["metadata"]["name"].lower() )
        
            # add or update
            device_tracker[ device_keyname  ] = dict( sorted(device_record_ready.items()) )
            
            print("RQ")
            print(myrequests)
            print("dict")
            print(dict( sorted(device_record_ready.items()) ))
            
            logging.warning("Try to update json_file: " + my_json_file )
            logging.info("Add device record")
            # delete content
            file.truncate()
            #file.seek(0)
            json.dump(device_tracker, file, indent=4)


    logging.info("End: Add device record")





#add_history("MS-21_SN445566A",history_11)
#add_history("MS-21_SN445566A",history_12)
#add_calibration("MS-21_SN445566A",{"calibration_link":"http://mycalibration.info"})

# add_history("MS-80_SNABCD22",history_AA)
# add_history("MS-80_SNABCD22",history_AB)
# add_history("MS-80_SNABCD22",history_AC)
# add_history("MS-80_SNABCD22",history_AD)
# add_history("MS-80_SNABCD22",history_AE)
# add_calibration("MS-80_SNABCD22",
# {
    # "calibration_description" : "",
    # "calibration_performed_by" : "Ak Hein",
    # "calibration_performed_at" :"DWD",
    # "calibration_performed_period" : ["2023-07-03T12:12:12Z","2023-07-13T12:12:12Z"],
    # "calibration_record_created" : "2024-08-03T12:12:12Z",
    # "calibration_used_method" : "Kletter et al.",
    # "calibration_used_reference" : "CPC",
    # "calibration_valid_period": ["2023-08-03T00:12:12Z", "2024-08-03T12:12:12Z"],
    # "calibration_values": [0.11992, -22.3, 0.3]
# })
# add_calibration("MS-80_SNABCD22",
# {
    # "calibration_description" : "",
    # "calibration_performed_by" : "Dore Hwaptist",
    # "calibration_performed_at" :"DWD",
    # "calibration_performed_period" : ["2024-09-03T12:12:12Z","2024-09-13T12:12:12Z"],
    # "calibration_record_created" : "2026-08-03T12:12:12Z",
    # "calibration_used_method" : "Kletter et al.",
    # "calibration_used_reference" : "CPC",
    # "calibration_valid_period": ["2024-10-03T00:12:12Z", "2026-10-03T12:12:12Z"],
    # "calibration_values": [0.11972, -22.0, 0.27]
# })




# add_history("arielle",history_arielle11)
# add_history("arielle",history_arielle12)
# add_history("arielle",history_arielle13)
# add_history("arielle",history_arielle14)

