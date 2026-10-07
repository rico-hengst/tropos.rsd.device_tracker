#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json 
import datetime
import pandas as pd
import numpy as np
import re

import dv_config
# set logger
logger = dv_config.setup_logger()
# get ENV variables
ENV = dv_config.get_env()


# test if nested dict has keys
# see https://stackoverflow.com/questions/43491287/elegant-way-to-check-if-a-nested-key-exists-in-a-dict
def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    #logger.debug("Start check nested key exists")
    
    if not isinstance(element, dict):
        logger.warning('keys_exists() expects dict as first argument.')
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        logger.warning('keys_exists() expects at least two arguments, one given.')
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            logger.warning("Nested key not exists: " + key)
            return False
            
    #logger.debug("All nested keys exists")
    return True


def sort_continuous_history():

    # read json file
    #json_file= "../config/device_tracker.json"
    json_file = ENV["device_tracker_file"]
    

    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()
    
    # create dataframe
    data = pd.DataFrame.from_dict(device_tracker)

    logger.info("# Start check continuous device history: " + json_file)
    
    for device in data.columns:

        logger.info("## Start check continuous history at device: " + device)
            
        # sort
        if device not in data.columns:
            logger.error("Device " + device + " not in json file!")
            exit()
        
        # sort history and check overlap
        # 1. loop of history
        l = len(data[device]["history"])
        if l > 0:
        
            logger.debug("Sort history")
            data[device]["history"].sort(key=lambda e: e['startdate'], reverse=False)
            
            # 2. loop (nested) in history
            logger.debug("Loop history to check in-consistencies")
            for i, x in enumerate(data[device]["history"]):
                if i == l-1:
                    break
                
                if(data[device]["history"][i+1]["startdate"] >= data[device]["history"][i]["stopdate"]):
                    logger.info("  ok - continuous, consistent history: " + device)
                else:
                    logger.warning("  error - non-continuous or in-consistent history: " + device)
                    logger.warning("  index " + str(i) + ": focus stopdate:  " + str(data[device]["history"][i]) )
                    logger.warning("  index " + str(i+1) + ": focus startdate: " + str(data[device]["history"][i+1]) )
            
        else:
            logger.info("Device " + device + " without history!")

        logger.info("## Stop check continuous history at device: " + device)
        
            
    with open('../config/device_tracker_sorted.json', 'w') as f:
        f.write(data.to_json(orient='columns', indent=2))
                
    logger.info("---")
    logger.info("# Stop check continuous device history: " + json_file)





# AI: Function to filter the 'fails' list inside a record
def filter_created(data,my_filter):

    # delete column 
    #   * if filter is device regex and device is unknown
    #   * if filter class/subclass is set and no match
    #   * if no history exists
    logger.info("Start filter created, check record headers")
    if ("device" in my_filter):
        for device_column_name in list(data.columns):
            if re.match(my_filter["device"], device_column_name, flags=re.IGNORECASE):
                logger.debug("Match device pattern: " + device_column_name)
            else:
                logger.debug("Non match device pattern: " + device_column_name, " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
    # search full array of class
    if("class" in my_filter):
        for device_column_name in list(data.columns):

            if ( keys_exists(data[device_column_name].to_dict(),"metadata","class") and re.search( my_filter["class"], " ".join( data[device_column_name]["metadata"]["class"] ), flags=re.IGNORECASE) ):
                logger.debug("Match class pattern: " + device_column_name + "matches the class pattern")
            else:
                logger.debug("Non match class pattern: " + device_column_name + " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
                
    if("class0" in my_filter):
        for device_column_name in list(data.columns):
            if (  keys_exists(data[device_column_name].to_dict(),"metadata","class") and re.match(my_filter["class0"], data[device_column_name]["metadata"]["class"][0], flags=re.IGNORECASE) ):
                logger.debug("Match subclass pattern: " + device_column_name)
            else:
                logger.debug("Non match subclass pattern: " + device_column_name + " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
                
    if("pid" in my_filter):
        for device_column_name in list(data.columns):
            if (  keys_exists(data[device_column_name].to_dict(),"metadata","device_model","pid") and re.match(my_filter["pid"], data[device_column_name]["metadata"]["device_model"]["pid"], flags=re.IGNORECASE) ):
                logger.debug("Match id pattern: " + device_column_name)
            else:
                logger.debug("Non match pid pattern: " + device_column_name + " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
 
    
    for device_column_name in list(data.columns):
        if (len(data[device_column_name]["history"])==0):
            data.drop(device_column_name, axis=1, inplace=True)
            logger.info("No history records exists: " + device_column_name + " - delete device column !!!!")

    logger.debug("Stop filter created, check record headers")
    
    # Create a shallow copy of the record to avoid modifying the original directly
    # Note: We only need to deep-copy the 'fails' list
    logger.debug("Create data copy from reduced data.")
    new_data = data.copy(deep=True)
    
    for device_column_name in data:
        logger.debug("Start device column " + device_column_name )
        reduced_history = []
        
        for history_record in data[device_column_name]["history"]:
                        
            number_of_requested_filters = 0
            matched_requests = []
            nonmatched_requests = []
            
            if("created" in my_filter):
                number_of_requested_filters += 1
                if my_filter["created"] >= history_record["created"]:
                    matched_requests.append({"created":history_record["created"]})
                    logger.debug("check created match: " + history_record["created"])
                else:
                    nonmatched_requests.append({"created":history_record["created"]})
                    logger.debug("check created no match: " + history_record["created"])
            
            if("date" in my_filter):
                number_of_requested_filters += 1
                
                if not (isinstance(my_filter["date"], list) ):
                    logger.error("Error date query must be a list: " + my_filter["date"])
                    exit()
                if not (len(my_filter["date"]) ==1 or len(my_filter["date"]) == 2):
                    logger.error("Error data query must be a instance of a list of 1 or 2 items: " + str(my_filter["date"]) + str(len(my_filter["date"])))
                    exit()
                    
                # sort
                my_filter["date"] = sorted(my_filter["date"], reverse=False)
                                
                # search explizit single date
                if len(my_filter["date"]) == 1:
                    if (history_record["startdate"] <= my_filter["date"][0] and history_record["stopdate"] >= my_filter["date"][0]):
                        matched_requests.append({"date datetime":history_record["startdate"]+history_record["stopdate"]})
                        logger.debug("check startdtopdate single match: ")
                    else:
                        nonmatched_requests.append({"date datetime":history_record["startdate"]+ " " +history_record["stopdate"] + " versus " + str(my_filter["date"])})
                        logger.debug("check startdtopdate single no match, delete")
                # search explizit timespan
                elif len(my_filter["date"]) == 2:
                    if (my_filter["date"][0] <= history_record["stopdate"] and my_filter["date"][1] >= history_record["startdate"]):
                        matched_requests.append({"date timespan":history_record["startdate"]+history_record["stopdate"]})
                        logger.debug("check startdtopdate timespan match")
                    else:
                        nonmatched_requests.append({"date timespan":history_record["startdate"]+ " " +history_record["stopdate"] + " versus " + str(my_filter["date"])})                
                        logger.debug("check startdtopdate timespan no match, delete")

            
            if("locationname" in my_filter):
                if ( keys_exists(history_record,"location","name") and re.match(my_filter["locationname"], history_record["location"]["name"], re.IGNORECASE) ):
                    matched_requests.append({"locationname":history_record["location"]["name"]})  
                    logger.debug("check locationname match: " + history_record["location"]["name"])
                  
                else:
                    nonmatched_requests.append({"locationname":my_filter["locationname"]})
                    logger.debug("check location no match, delete " + my_filter["locationname"])

                    
            if("country" in my_filter):
                if ( keys_exists(history_record,"location","country") and re.match(my_filter["country"], history_record["location"]["country"], re.IGNORECASE)) :
                    matched_requests.append({"country":history_record["location"]["country"]})
                    logger.debug("check country match: " + history_record["location"]["country"])
                else:
                    nonmatched_requests.append({"country":my_filter["country"]}) 
                    logger.debug("check country no match, delete " + my_filter["country"])
                    
            if("campaign" in my_filter):
                if ( keys_exists(history_record,"campaign") and re.match(my_filter["campaign"], history_record["campaign"], re.IGNORECASE)):
                    matched_requests.append({"campaign":history_record["campaign"]})
                    logger.debug("check campaign match: " + history_record["campaign"])
                else:
                    nonmatched_requests.append({"campaign":""}) 
                    logger.debug("check campaign no match, delete")
                    
            if("platform" in my_filter):
                flag_platform = False
                if "platform" in history_record:
                    for platform in history_record["platform"]:
                        if (re.match(my_filter["platform"], platform, re.IGNORECASE)):
                            flag_platform = True

                    if flag_platform:
                        matched_requests.append({"platform":my_filter["platform"]})
                        logger.debug("check platform match: " + history_record["platform"])
                    else:
                        nonmatched_requests.append({"platform":my_filter["platform"]})
                        logger.debug("check platform no match, delete " + my_filter["platform"])
                else:
                    nonmatched_requests.append({"platform":""})
                    logger.debug("check platform no match, delete")
            
            if("uuid" in my_filter):
                if my_filter["uuid"] == history_record["uuid"]:
                    matched_requests.append({"uuid":my_filter["uuid"]})
                    logger.debug("check uuid match: " + my_filter["uuid"])
                else:
                    nonmatched_requests.append({"uuid":""})
                    logger.debug("check uuid no match, delete")
                    
            logger.debug("... matched history records:    " + str(len(matched_requests)) + " returns, filter: " + str(matched_requests))
            logger.debug("... nonmatched history records: " + str(len(nonmatched_requests)) + " returns, filter: " + str(nonmatched_requests))
            
            # all request per history records returns a result, so nonmated_request should be len()=0: append history record
            if len(nonmatched_requests) == 0:
                reduced_history.append(history_record)
                logger.debug("-> append current history record")
            else:
                logger.debug("-> do not append current history record")
                        
        # set history
        # if reduced history exists: substitute history
        if len(reduced_history) > 0:
            #new_data[device_column_name]['history'] = reduced_history
            new_data.loc['history',device_column_name] = reduced_history
            logger.info("history record was appended")
        # if number_of_requested_filters > 0: keep original history, do nothing
        else:
            new_data.drop(device_column_name, axis=1, inplace=True)
        
        logger.info("Stop device " + device_column_name )
            
    if not(new_data.empty):
        logger.info("Final filtered data!")
        #print(new_data)
        #for device_column_name in new_data:
         #   print(new_data[device_column_name]["history"])
        
    else:
        logger.info("Final, empty data return")
    
    
    
    return new_data




def select_history(my_filter):
    # read json file
    
    json_file= "../config/device_tracker.json"
    json_file= "../config/device_tracker_imported.json"
    json_file = ENV["device_tracker_file"]

    logger.info("Start query from json_file: " + json_file)
    logger.info(" requested filter: " + str(my_filter))
    
    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()
    # device_tracker = dict( sorted(device_tracker.items()) )
    

    # create dataframe
    data = pd.DataFrame.from_dict(device_tracker)
    
    # Apply the function to every element in the array
    # This creates a new array with the cleaned structure
    filtered_data = filter_created(data,my_filter)

    logger.info("Stop query from json_file: " + json_file)
    
    #d = dict(sorted(filtered_data.items(), reverse=True, key=lambda item: item[0]))
    
    logger.debug("Filtered data " + str(filtered_data))
    return filtered_data


def select_calibration(my_filter):
    json_file= "../config/device_tracker.json"
    json_file= "../config/device_tracker_imported.json"
    json_file = ENV["device_tracker_file"]

    logger.info("Start query from json_file: " + json_file)
    logger.info(" requested filter: " + str(my_filter))
    
    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()
    
    # create dataframe
    data = pd.DataFrame.from_dict(device_tracker)
    
    # new data
    new_data = data.copy(deep=True)
    
    for device_column_name in data:
        logger.info("### Start device ", device_column_name )
        reduced_calibration = []
        for calibration_record in data[device_column_name]["calibration"]:
            
            number_of_requested_filters = 0
            matched_requests = []
            nonmatched_requests = []
            
            if("uuid" in my_filter):
                if ( keys_exists(calibration_record,"uuid") and my_filter["uuid"] == calibration_record["uuid"]) :
                    matched_requests.append({"uuid":calibration_record["uuid"]})
                    logger.info("check uuid match: " + calibration_record["uuid"])
                else:
                    nonmatched_requests.append({"uuid":my_filter["uuid"]})
                    logger.info("check uuid match, delete " + my_filter["uuid"])
                    
            
             # all request per calibration records returns a result, so nonmated_request should be len()=0: append calibration record
            if len(nonmatched_requests) == 0:
                reduced_calibration.append(calibration_record)
                logger.info("     -> append current calibration record")
            else:
                logger.info("     -> do not append current calibration record")
                
        # set calibration
        # if reduced calibration exists: substitute calibration
        if len(reduced_calibration) > 0:
            new_data.loc['calibration',device_column_name] = reduced_calibration
            logger.info("calibration record was appended " + device_column_name)
        # if number_of_requested_filters > 0: keep original history, do nothing
        else:
            logger.info("Drop device, cause no calibration matched: " + device_column_name)
            new_data.drop(device_column_name, axis=1, inplace=True)
  
    # logger.debug(new_data)
    
    return new_data
            
        


# get unique list of
# * locations (nested dict) -> scan of all history records
# * class(es) level0 -> scan of all metadata records
def get_lookup_content(keyword):
    json_file= "../config/device_tracker_imported.json"
    json_file = ENV["device_tracker_file"]

    logger.info("Start get_lookup_content of " + keyword + ": " + json_file)
    
    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()

    data = pd.DataFrame.from_dict(device_tracker)   
     
    logger.debug("get lookup content: " + keyword)
    
    if keyword == "locations":

        # store location in nested dict
        locations = {}
        
        for device_column_name in list(data.columns):
            for history_record in data[device_column_name]["history"]:
                
                if not keys_exists(history_record, "location","country"):
                    logger.info("Skip history part, no country")
                    continue
                if not keys_exists(history_record, "location","lat"):
                    logger.info("Skip history part, no lat")
                    continue
                if not keys_exists(history_record, "location","lon"):
                    logger.info("Skip history part, no lon")
                    continue
                
                # create tmp new history record: keep only name,country,lat,lon
                new_history_record = {
                    "name":history_record["location"]["name"],
                }
                for key in ["country","lat","lon"]:
                    if key in history_record["location"]:
                        new_history_record[key] = history_record["location"][key]
                        
                # check if location name exist
                if new_history_record["name"] in locations:
                    logger.info("location already exists: " + new_history_record["name"])
                    
                    # compare locations record and current history location record, stringify records and remove white space etc
                    condensed_location = re.sub(r"[\n\t\s]*", "", str(locations[new_history_record["name"]]) )
                    condensed_history_location = re.sub(r"[\n\t\s]*", "", str(new_history_record) )
                    if not condensed_location == condensed_history_location:
                        logger.warning("location can be different: " + new_history_record["name"])
                        logger.warning(condensed_location)
                        logger.warning(condensed_history_location)
                    else:
                        logger.info("... but it seem the records are equal")
                else:
                    locations[new_history_record["name"]] = new_history_record
                    logger.info("add location: " + new_history_record["name"])
        
        return dict( sorted(locations.items()) )

    elif keyword == "classes0":
        
        # store classes0 in nested dict
        classes0 = []
        for device_column_name in list(data.columns):
            class0 = data[device_column_name]["metadata"]["class"][0]
            
            if not class0 in classes0 and len(class0) > 0:
                classes0.append(class0)
                logger.info("add class: " + class0)
        classes0.sort()
                
        return classes0
        
    elif keyword == "devices":
        
        devices = dict(sorted( device_tracker.items() ))
        
        return devices
        
    logger.info("Stop get_lookup_content of " + keyword + ": " + json_file)


