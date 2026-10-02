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


import dv_config
# set logger
logger = dv_config.setup_logger(__name__)
# get ENV variables
ENV = dv_config.get_env()

import selector


def json_file():
    json_file= "../config/device_tracker_imported.json"
    json_file = dv_config.get_env()["device_tracker_file"]
    if not os.path.isfile(json_file):
        logger.error("JSON not exists: " + json_file)
        json_file = None
        
    return json_file


# push the user input into the expected format
def prepare_add_device(myrequests):
    logger.info("Start of device record prep")
    

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
    
    
    # load devices
    devices = selector.get_lookup_content("devices")
    
    
    # update some parts if edit mode
    if "requested_mode" not in myrequests or myrequests["requested_mode"] == "add":
        logger.info("Start to add a new device")
        
        # substitute space by - and transform to lower all keynames
        tmp_device_keyname = re.sub(r"\s+", '-', my_dict_new["metadata"]["name"].lower() )
        
        # reject if device already exists
        if tmp_device_keyname in devices:
            message = "Request mode add, but you want to add a device name that already exists: " + tmp_device_keyname
            logger.warning(message)
            
            return { 
                "message"           : {
                    "type": "warning",
                    "message": message
                } 
            }
        else:
            return {
                "returned_record"   : my_dict_new,
            }
        
    
        
    elif "requested_mode" in myrequests and myrequests["requested_mode"] == "edit":
        logger.info("Start to update a device")
        
    
            
        
        
        logger.info("Requested mode is edit, so calibration/history record will be collected")
        
        if "device_keyname" not in myrequests:
            message = "Edit mode device, but no device_keyname in get parameters"
            logger.warning(message)
            return { 
                "message"           : {
                    "type": "warning",
                    "message": message
                } 
            }
        else:
            device_keyname = myrequests["device_keyname"]
            
            if device_keyname in devices:                
                
                # update timestamp
                my_dict_new["metadata"]["created"] = devices[device_keyname]["metadata"]["created"]
                
                # update calibration and history
                if "calibration" in devices[device_keyname]:
                    my_dict_new["calibration"] = devices[device_keyname]["calibration"]
                    logger.debug("Update device, get existing calibration records")
                if "history" in devices[device_keyname]:
                    my_dict_new["history"] = devices[device_keyname]["history"]
                    logger.debug("Update device, get existing history records")
                    
                return {
                     "returned_record"   : my_dict_new,
                }
            else:
                message = "Device unknown: " + device_name
                logger.warning(message)
                return { 
                    "message"           : {
                        "type": "warning",
                        "message": message
                    } 
                }
                    
    logger.info("End of device record prep")
        
    
# push the user input into the expected format
def prepare_add_history(myrequests):
    
    # check if request_mode is edit/add
    if "requested_mode" in myrequests and myrequests["requested_mode"] != "add" and myrequests["requested_mode"] != "edit":
        logger.warning("Form request_mode add/edit expected!")
        
        return { 
            "message"           : {
                "type": "warning",
                "message": "Form request_mode add/edit expected!"
            } 
        }

    my_location = {
        "is_mobile": True if "history.location.is_mobile" in myrequests else False
    }
    
    my_location_is_add_static_location = None
    
    # decision tree about my_location_is_add_static_location
    if not bool(my_location["is_mobile"]) and "checkbox_use_existing_static_location" in myrequests and bool(myrequests["checkbox_use_existing_static_location"]):
        my_location_is_add_static_location = False
    elif bool(my_location["is_mobile"]):
        my_location_is_add_static_location = False
    elif not bool(my_location["is_mobile"]) and "checkbox_add_static_location" in myrequests and bool(myrequests["checkbox_add_static_location"]):
        my_location_is_add_static_location = True
        
  
    for key_name in myrequests:
        logger.info(key_name)
        
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
        # is static
        if not my_location["is_mobile"]:
            logger.info("is a non-mobile location")
            if key_name == "history.location.name":
                locations = selector.get_lookup_content("locations")
                
                # take al location info from database
                if not bool(my_location_is_add_static_location):
                    logger.warning("is false, take location from database")
                    
                    if myrequests[key_name] in locations:
                        my_location["name"] = myrequests[key_name]
                        my_location["country"] = locations[ myrequests[key_name] ][ "country" ] if "country" in locations[ myrequests[key_name] ] else ""
                        my_location["lat"] = float( locations[ myrequests[key_name] ][ "lat" ] )
                        my_location["lon"] = float( locations[ myrequests[key_name] ][ "lon" ] )
                        
                        if "elevation" in locations[ myrequests[key_name] ]:
                            my_location["elevation"] = float( locations[ myrequests[key_name] ]["elevation"] )
                # add all info from web form
                elif bool(my_location_is_add_static_location):
                    logger.warning("is true, take location from web form")
                    
                    my_location["name"]     = myrequests[key_name]
                    my_location["country"]  = myrequests["history.location.country" ]
                    my_location["lat"]      = float( myrequests["history.location.lat" ] )
                    my_location["lon"]      = float( myrequests["history.location.lon" ] )
                    if "history.location.elevation" in myrequests and len(myrequests["history.location.elevation"])>0:
                        my_location["elevation"] = float( myrequests["history.location.elevation" ] )
                    
        # is mobile
        else:
            logger.info("is a mobile location")
            logger.debug("add name, track_url, track_desc from web form")
            if key_name == "history.location.name":
                my_location["name"] = myrequests[key_name]
            elif key_name == "history.location.track_url":
                my_location["track_url"] = myrequests[key_name]
            elif key_name == "history.location.track_desc":
                my_location["track_desc"] = myrequests[key_name]
                    
                
    # check if start => stop
    if myrequests["history.startdate"] > myrequests["history.stopdate"]:
        logger.warning("provided dates: Start > Stop, exit")
        
        return { 
            "message"           : {
                "type": "warning",
                "message": "provided dates: Start > Stop, exit"
            } 
        }
        
    
    # check if dates are overlapped with further history records 
    #### exception if "edit" node and if both uuid are identical
    devices=selector.select_history( {"device":myrequests["device"]} ).replace([np.nan], [None], regex=False).to_dict()
   
    if bool(devices) and myrequests["device"] in devices and "history" in devices[myrequests["device"]]:
        for history in devices[myrequests["device"]]["history"]:
            if myrequests["history.stopdate"] > history["startdate"] and myrequests["history.startdate"] < history["stopdate"]:
                if "requested_mode" in myrequests and myrequests["requested_mode"] == "edit" and myrequests["history.uuid"] == history["uuid"]:
                    logger.debug("Edit mode, overlapping history record between provided and the identical uuid record")
                
                else:
                    message = "On or multiple history record periods did intersect with start/stoptime of your record" + str(history) + " versus " + myrequests["history.startdate"] + " " + myrequests["history.stopdate"]
                    logger.warning(message)
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
    



# push the user input into the expected format
def prepare_add_calibration(myrequests):
    # check if request_mode is edit/add
    if "requested_mode" in myrequests and myrequests["requested_mode"] != "add" and myrequests["requested_mode"] != "edit":
        logger.warning("Form request_mode add/edit expected!")
        
        return { 
            "message"           : {
                "type": "warning",
                "message": "Form request_mode add/edit expected!"
            } 
        }
        
    my_calibration_new = {
        	"calibration_coefficient_uncertainties" : [float(x) for x in myrequests["calibration.calibration_coefficient_uncertainties"].split(",")] if "calibration.calibration_coefficient_uncertainties" in myrequests else [],
            "calibration_coefficients"              : [float(x) for x in myrequests["calibration.calibration_coefficients"].split(",")] if "calibration.calibration_coefficients" in myrequests else [],
            "calibration_equation"                  : myrequests["calibration.calibration_equation"] if "calibration.calibration_equation" in myrequests else "",
            "certificate_id"                        : myrequests["calibration.certificate_id"] if "calibration.certificate_id" in myrequests else "",
            "certificate_issuance_date"             : datetime.datetime.strptime(myrequests["calibration.certificate_issuance_date"], '%Y-%m-%d %H:%M').strftime("%Y-%m-%dT%H:%M:%SZ") if "calibration.certificate_issuance_date" in myrequests else "",
            "description"                           : myrequests["calibration.description"] if "calibration.description" in myrequests else "",
            "performed_at"                          : myrequests["calibration.performed_at"] if "calibration.performed_at" in myrequests else "",
            "performed_by"                          : myrequests["calibration.performed_by"] if "calibration.performed_by" in myrequests else "",
            "performed_period_dates"                : [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M').strftime("%Y-%m-%dT%H:%M:%SZ") for x in myrequests["calibration.performed_period_dates"]] if "calibration.performed_period_dates" in myrequests else [],
            "record_created_date"                   : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "temperature_correction_coefficients"   : [float(x) for x in myrequests["calibration.temperature_correction_coefficients"].split(",")] if "calibration.temperature_correction_coefficients" in myrequests else [],
            "temperature_correction_equation"       : myrequests["calibration.temperature_correction_equation"] if "calibration.temperature_correction_equation" in myrequests else "",
            "used_method"                           : myrequests["calibration.used_method"] if "calibration.used_method" in myrequests else "",
            "used_reference"                        : myrequests["calibration.used_reference"] if "calibration.used_reference" in myrequests else "",
            "uuid"                                  : myrequests["calibration.uuid"] if "calibration.uuid" in myrequests else str(uuid.uuid1()),
            "valid_period_dates"                    : [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M').strftime("%Y-%m-%dT%H:%M:%SZ") for x in myrequests["calibration.valid_period_dates"]] if "calibration.valid_period_dates" in myrequests else [],
    }
    
    # do not store, cause integer is expected
    if "calibration.performed_repeats" in myrequests:
        my_calibration_new["performed_repeats"] = int(myrequests["calibration.performed_repeats"])
        logger.info("performed_repeats were set")
    # record_created_date: use date from edited record
    if "calibration.uuid" in myrequests and "requested_mode" in myrequests and myrequests["requested_mode"] != "edit":
        uuid_calibrations=selector.select_calibration( {"uuid" : myrequests["calibration.uuid"] } ).replace([np.nan], [None], regex=False).to_dict()
        my_calibration_new["record_created_date"] = uuid_calibrations[myrequests["device_keyname"]]["calibration"][0]["record_created_date"]

    
    # validation
    schema_file = "../config/schema_calibration.json"

        
    # load schema
    with open(schema_file, "r+") as file:
        try:
            calibration_schema = json.load(file)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON syntax:", e)
        
        
    # old valiadation without format checker
    validate(
        instance=my_calibration_new,
        schema=calibration_schema,
    )

    validator = Draft7Validator(
            calibration_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(my_calibration_new))
    
    
        
    if errors:
        mesaage = "✗ Validation Failed: The JSON instance is invalid."
        logger.error(message)

        for error in errors:
            # error.message usually contains the specific reason
            logger.error(f"  - Error: {error.message}")
            logger.error(f"    Path: {list(error.path)}")
            logger.error(f"    Validator: {error.validator}")
            
        return {"message": {"type":"warning","message":message}}
    else:
        logger.info("Validation ok")
            
    
    return {
        "returned_record"   : my_calibration_new,
        "message" : {"type":"warning","message":"Returned json ok"}
    }


def add_calibration(myrequests):
    
    logger.info("Start: Add history record")
    
    if "device_keyname" not in myrequests:
        logger.warning("device keyname is missing")
    

    
    calibration_record_ready = prepare_add_calibration(myrequests)
    my_rr = {}
    
    if not "returned_record" in calibration_record_ready:
        return my_rr
        
    logger.debug(calibration_record_ready["returned_record"])
    
    
    # add to device tracker
    my_json_file = json_file()

    # 1. load file content to variable
    device_tracker = None
    with open(my_json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()
        
    # 2 open file to write the updated content to the file
    with open(my_json_file, "w+") as file:
            
        logger.info("Update json_file: " + my_json_file )
        if myrequests["device_keyname"] in device_tracker.keys():
            # looking for calibrations in edit mode
            if "requested_mode" in myrequests and myrequests["requested_mode"] == "edit":
                ii = -1
                for c in device_tracker[myrequests["device_keyname"]]["calibration"]:
                    ii+=1
                    if device_tracker[myrequests["device_keyname"]]["calibration"][ii]["uuid"] == myrequests["calibration.uuid"]:
                        logger.info("Edit mode: edit calibration")
                        device_tracker[myrequests["device_keyname"]]["calibration"][ii] = calibration_record_ready["returned_record"]
                        break
            else:
                device_tracker[myrequests["device_keyname"]]["calibration"].append(calibration_record_ready["returned_record"])
                logger.info("Add mode: append calibration")
                
        file.truncate()
        json.dump(device_tracker, file, indent=4)
                    
        message = "Updated calibration at device: " + myrequests["device_keyname"]
        logger.info(message)
        return {"message": {"type":"info","message":message}}
    file.close()
    
    
    
    if "message" in calibration_record_ready:
        my_rr["message"]= calibration_record_ready["message"]
        return my_rr


    
        
    
            
            
            




def add_history(myrequests):
    
    logger.info("Start: Add history record")
    
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
            logger.warning("Invalid JSON syntax:", e)
        
        
        
    
    #old valiadation without format checker
    validate(
        instance=history_record_ready["return_ok"],
        schema=history_schema,
    )

    validator = Draft7Validator(
            history_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(history_record_ready["return_ok"]))
    
    if not errors:
        logger.info("✓ Validation Successful: The JSON instance is valid.")
        logger.debug(history_record_ready["return_ok"])
        
        my_json_file = json_file()
        
        # 1. load file content to variable
        device_tracker = None
        with open(my_json_file, "r+") as file:
            device_tracker = json.load(file)
        file.close()
        
        # 2 open file to write the updated content to the file
        with open(my_json_file, "w+") as file:
            
            logger.info("Update json_file: " + my_json_file )
            
            if device in device_tracker.keys():
                if "history" in device_tracker[device].keys():
                    if "history.uuid" in myrequests and myrequests["requested_mode"] == "edit":
                        for index in range(len(device_tracker[device]["history"])):
                            if device_tracker[device]["history"][index]["uuid"] == history_record_ready["return_ok"]["uuid"]:
                                device_tracker[device]["history"][index] = history_record_ready["return_ok"]
                                logger.info("Edit history record: " + str(history_record_ready))
                                break
                    else:
                        logger.info("Add history record: " + str(history_record_ready))
                        device_tracker[device]["history"].append(history_record_ready["return_ok"])

                   # print(device_tracker)
                    #file.seek(0)
                    file.truncate()
                    json.dump(device_tracker, file, indent=4)
                    
                    message = "Updated history at device: " + device
                    logger.info(message)
                    return {"message": {"type":"info","message":message}}
                    
                else:
                    message = "No history key at device detected: " + device
                    logger.warning(message)
                    return {"message": {"type":"warning","message":message}}
            else:
                message = "-- no device in json file detected: " + str(device) + ", no validation"
                logger.warning(message)
                return {"message": {"type":"warning","message":message}}

        
    else:
        message = "✗ Validation Failed: The JSON instance is invalid." + str(history_record_ready["return_ok"])
        logger.warning(message)
        logger.debug(history_record_ready["return_ok"])

        for error in errors:
            # error.message usually contains the specific reason
            logger.warning(f"  - Error: {error.message}")
            logger.warning(f"    Path: {list(error.path)}")
            logger.warning(f"    Validator: {error.validator}")
            
        return {"message": {"type":"warning","message":message}}
            
    logger.info("End: Add history record")
            
            
            

        
        
def add_device(myrequests):
    
    
    logger.info("Start: Add device record")
    device_record_ready = prepare_add_device(myrequests)
    
    logger.warning(device_record_ready)
    
    if not "returned_record" in device_record_ready:
        logger.warning("returned_record was missing")
        return device_record_ready
    

    # load schema
    with open("../config/schema_device.json", "r+") as file:
        device_schema = json.load(file)
        
    
    
    validate(instance=device_record_ready["returned_record"], schema=device_schema)
    
    validator = Draft7Validator(
            device_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(device_record_ready["returned_record"]))
    
   
    
    if errors:
        logger.info("✗ Validation Failed: The JSON instance is invalid.")
        logger.debug(device_record_ready["returned_record"])

        for error in errors:
            # error.message usually contains the specific reason
            logger.debug(f"  - Error: {error.message}")
            logger.debug(f"    Path: {list(error.path)}")
            logger.debug(f"    Validator: {error.validator}")
        
        return {
            "message" :{"type":"info","message":"Validation Failed"}
        }
            
    else :
        logger.info("✓ Validation Successful: The JSON instance is valid.")
        logger.debug(device_record_ready["returned_record"])
        
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
            device_keyname = re.sub(r"\s+", '-', device_record_ready["returned_record"]["metadata"]["name"].lower() )
        
            # add or update
            device_tracker[ device_keyname  ] = dict( sorted(device_record_ready["returned_record"].items()) )

            
            logger.warning("Try to update json_file: " + my_json_file )
            logger.info("Add device record")
            # delete content
            file.truncate()
            #file.seek(0)
            json.dump(device_tracker, file, indent=4)
            
            return {
                "message":{"message": "ok"}
            }


    logger.info("End: Add device record")



