#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json 

import datetime

import pandas as pd
import numpy as np
import re

import logging
logging.basicConfig(level=logging.WARNING)


import pprint
pp = pprint.PrettyPrinter(indent=4)

# test if nested dict has keys
# see https://stackoverflow.com/questions/43491287/elegant-way-to-check-if-a-nested-key-exists-in-a-dict
def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


def sort_continuous_history():

    
    # read json file
    json_file= "../config/device_tracker.json"
    

    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()
    
    # create dataframe
    data = pd.DataFrame.from_dict(device_tracker)
    
    # if no list take off columns from json
    #if not isinstance(devices, list):
    #devices = device_tracker.columns

    
    logging.info("# Start check continuous device history: " + json_file)
    
    for device in data.columns:

        logging.info("## Start check continuous device history: " + device)
            
        # sort
        if device not in data.columns:
            logging.error("  Device " + device + " not in json file!")
            exit()
        
        # sort history and check overlap
        # 1. loop of history
        l = len(data[device]["history"])
        if l > 0:
        
            # print("  unsorted")
            # pp.pprint(data[device]["history"])
            data[device]["history"].sort(key=lambda e: e['startdate'], reverse=False)
            # print("  sorted")
            # pp.pprint(data[device]["history"])
            
            # 2. loop (nested) in history
            for i, x in enumerate(data[device]["history"]):
                if i == l-1:
                    break
                
                if(data[device]["history"][i+1]["startdate"] >= data[device]["history"][i]["stopdate"]):
                    logging.info("  ok - continuous, consistent history: " + device)
                else:
                    logging.warning("  error - non-continuous or in-consistent history: " + device)
                    logging.warning("  index " + str(i) + ": focus stopdate:  " + str(data[device]["history"][i]) )
                    logging.warning("  index " + str(i+1) + ": focus startdate: " + str(data[device]["history"][i+1]) )
            
        else:
            logging.info("  Device " + device + " without history!")

        logging.info("## Stop check continuous device history: " + device)
        
        
    logging.info("---")
    logging.debug(data.to_json(orient='columns', indent=2) )
            
    with open('../config/device_tracker_sorted.json', 'w') as f:
        f.write(data.to_json(orient='columns', indent=2))
                
    logging.info("---")
    logging.info("# Stop check continuous device history: " + json_file)





# AI: Function to filter the 'fails' list inside a record
def filter_created(data,my_filter):

    # delete column 
    #   * if filter is device regex and device is unknown
    #   * if filter class/subclass is set and no match
    #   * if no history exists
    logging.info("### Start check record headers")
    if ("device" in my_filter):
        for device_column_name in list(data.columns):
            if re.match(my_filter["device"], device_column_name, flags=re.IGNORECASE):
                logging.info("#### Match device pattern: " + device_column_name)
            else:
                logging.info("#### Non match device pattern: " + device_column_name, " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
    # search full array of class
    if("class" in my_filter):
        for device_column_name in list(data.columns):


            if ( keys_exists(data[device_column_name].to_dict(),"metadata","class") and re.search( my_filter["class"], " ".join( data[device_column_name]["metadata"]["class"] ), flags=re.IGNORECASE) ):
                logging.info("#### Match class pattern: " + device_column_name, "matches the class pattern")
            else:
                logging.info("#### Non match class pattern: " + device_column_name + " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
            
            

                
    if("class0" in my_filter):
        for device_column_name in list(data.columns):
            if (  keys_exists(data[device_column_name].to_dict(),"metadata","class") and re.match(my_filter["class0"], data[device_column_name]["metadata"]["class"][0], flags=re.IGNORECASE) ):
                logging.info("#### Match subclass pattern: " + device_column_name)
            else:
                logging.info("#### Non match subclass pattern: " + device_column_name, " -- delete device column")
                data.drop(device_column_name, axis=1, inplace=True)
 
    
    for device_column_name in list(data.columns):
        if (len(data[device_column_name]["history"])==0):
            data.drop(device_column_name, axis=1, inplace=True)
            logging.info("#### No history records exists: " + device_column_name + " - delete device column !!!!")

    logging.info("### Stop check record headers")
    
    # Create a shallow copy of the record to avoid modifying the original directly
    # Note: We only need to deep-copy the 'fails' list
    new_data = data.copy(deep=True)
    
    
    for device_column_name in data:
        logging.info("### Start device ", device_column_name )
        reduced_history = []
        
        
        for history_record in data[device_column_name]["history"]:
            
            logging.info("#### check UUID ", history_record["uuid"])
            
            number_of_requested_filters = 0
            matched_requests = []
            nonmatched_requests = []
            
            if("created" in my_filter):
                number_of_requested_filters += 1
                if my_filter["created"] >= history_record["created"]:
                    matched_requests.append({"created":history_record["created"]})
                else:
                    nonmatched_requests.append({"created":history_record["created"]})
            
            if("date" in my_filter):
                number_of_requested_filters += 1
                
                if not (isinstance(my_filter["date"], list) ):
                    logging.error("Error date query must be a list")
                    exit()
                if not (len(my_filter["date"]) ==1 or len(my_filter["date"]) == 2):
                    logging.error("Error data query must be a instance of a list of 1 or 2 items: " + str(my_filter["date"]) + str(len(my_filter["date"])))
                    exit()
                    
                # sort
                my_filter["date"] = sorted(my_filter["date"], reverse=False)
                                
                # search explizit single date
                if len(my_filter["date"]) == 1:
                    if (history_record["startdate"] <= my_filter["date"][0] and history_record["stopdate"] >= my_filter["date"][0]):
                        matched_requests.append({"date datetime":history_record["startdate"]+history_record["stopdate"]})
                    else:
                        nonmatched_requests.append({"date datetime":history_record["startdate"]+ " " +history_record["stopdate"] + " versus " + str(my_filter["date"])})
                # search explizit timespan
                elif len(my_filter["date"]) == 2:
                    if (my_filter["date"][0] <= history_record["stopdate"] and my_filter["date"][1] >= history_record["startdate"]):
                        matched_requests.append({"date timespan":history_record["startdate"]+history_record["stopdate"]})
                    else:
                        nonmatched_requests.append({"date timespan":history_record["startdate"]+ " " +history_record["stopdate"] + " versus " + str(my_filter["date"])})                
            
            
            if("locationname" in my_filter):
                if ( keys_exists(history_record,"location","name") and re.match(my_filter["locationname"], history_record["location"]["name"], re.IGNORECASE) ):
                    matched_requests.append({"locationname":history_record["location"]["name"]})                    
                else:
                    nonmatched_requests.append({"locationname":my_filter["locationname"]})
                    
            if("country" in my_filter):
                if ( keys_exists(history_record,"location","country") and re.match(my_filter["country"], history_record["location"]["country"], re.IGNORECASE)) :
                    matched_requests.append({"country":history_record["location"]["country"]})
                else:
                    nonmatched_requests.append({"country":my_filter["country"]}) 
                    
            if("campaign" in my_filter):
                if ( keys_exists(history_record,"campaign") and re.match(my_filter["campaign"], history_record["campaign"], re.IGNORECASE)):
                    matched_requests.append({"campaign":history_record["campaign"]})
                else:
                    nonmatched_requests.append({"campaign":""}) 
                    
            if("platform" in my_filter):
                flag_platform = False
                if "platform" in history_record:
                    for platform in history_record["platform"]:
                        if (re.match(my_filter["platform"], platform, re.IGNORECASE)):
                            flag_platform = True

                    if flag_platform:
                        matched_requests.append({"platform":my_filter["platform"]})
                    else:
                        nonmatched_requests.append({"platform":my_filter["platform"]})
                else:
                    nonmatched_requests.append({"platform":""})
                    
                    
            logging.info("     matched history records:    " + str(len(matched_requests)) + " returns, filter: " + str(matched_requests))
            logging.info("     nonmatched history records: " + str(len(nonmatched_requests)) + " returns, filter: " + str(nonmatched_requests))
            
            # all request per history records returns a result, so nonmated_request should be len()=0: append history record
            if len(nonmatched_requests) == 0:
                reduced_history.append(history_record)
                logging.info("     -> append current history record")
            else:
                logging.info("     -> do not append current history record")
                        
        # set history
        # if reduced history exists: substitute history
        if len(reduced_history) > 0:
            #new_data[device_column_name]['history'] = reduced_history
            new_data.loc['history',device_column_name] = reduced_history
            logging.info("#### history record was appended")
        # if number_of_requested_filters > 0: keep original history, do nothing
        else:
            new_data.drop(device_column_name, axis=1, inplace=True)
        
        logging.info("### Stop device ", device_column_name )
            
    if not(new_data.empty):
        logging.info("Final filtered data!")
        #print(new_data)
        #for device_column_name in new_data:
         #   print(new_data[device_column_name]["history"])
        
    else:
        logging.info("empty data return")
    
    
    # Reversing the column order
    # cols = sorted( list(new_data.columns))
    
    # print(cols)

    # new_data = new_data[cols]
    
    
    return new_data




def select_history(my_filter):
    # read json file
    
    json_file= "../config/device_tracker.json"
    json_file= "../config/device_tracker_imported.json"
    logging.info("## Start query from json_file: " + json_file)
    logging.info(" requested filter: " + str(my_filter))
    
    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()
    # device_tracker = dict( sorted(device_tracker.items()) )
    
    # sorted_data_keys = json.dumps({k: device_tracker[k] for k in sorted(device_tracker)})
    # print(sorted_data_keys)
    # print(888)

    # for k in sorted(device_tracker):
        # print(k)
        
    # d= dict(sorted(device_tracker.items()))
    # for k in sorted(d):
        # print(k)
        
    # d = dict(sorted(device_tracker.items(), reverse=True, key=lambda item: item[0]))
    # for k in d:
        # print(k + "ddDW")
    # create dataframe
    data = pd.DataFrame.from_dict(device_tracker)
    logging.info("fef" + str(sorted(list(data.columns))))
    #filtered_values = np.where((data[query["device"]]) & (data[query["device"]]["history"][:]["created"] > "22" ))
    
    
    # Apply the function to every element in the array
    # This creates a new array with the cleaned structure
    filtered_data = filter_created(data,my_filter)

    
    logging.info("## Stop query from json_file: " + json_file)
    
    
    d = dict(sorted(filtered_data.items(), reverse=True, key=lambda item: item[0]))
    logging.info(d)


    logging.info(filtered_data)
    return filtered_data
    

# get unique list of
# * locations (nested dict) -> scan of all history records
# * class(es) level0 -> scan of all metadata records
def get_lookup_content(keyword):
    json_file= "../config/device_tracker_imported.json"
    logging.info("## Start get_lookup_content of " + keyword + ": " + json_file)
    
    with open(json_file, "r+") as file:
        device_tracker = json.load(file)
    file.close()

    data = pd.DataFrame.from_dict(device_tracker)
    logging.info("fefe" + str(sorted(list(data.columns))))
    
    
    if keyword == "locations":
        # store location in nested dict
        locations = {}
        
        
        
        for device_column_name in list(data.columns):
            for history_record in data[device_column_name]["history"]:
                
                if not keys_exists(history_record, "location","country"):
                    logging.info("Skip history part, no country")
                    continue
                if not keys_exists(history_record, "location","lat"):
                    logging.info("Skip history part, no lat")
                    continue
                if not keys_exists(history_record, "location","lon"):
                    logging.info("Skip history part, no lon")
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
                    logging.info("location already exists: " + new_history_record["name"])
                    
                    # compare locations record and current history location record, stringify records and remove white space etc
                    condensed_location = re.sub(r"[\n\t\s]*", "", str(locations[new_history_record["name"]]) )
                    condensed_history_location = re.sub(r"[\n\t\s]*", "", str(new_history_record) )
                    if not condensed_location == condensed_history_location:
                        logging.warning("location can be different: " + new_history_record["name"])
                        logging.warning(condensed_location)
                        logging.warning(condensed_history_location)
                    else:
                        logging.info("... but it seem the records are equal")
                else:
                    locations[new_history_record["name"]] = new_history_record
                    logging.info("add location: " + new_history_record["name"])
        
        return dict( sorted(locations.items()) )
       # print(type(locations))
        #print(locations)
        #return dict(sorted( new_history_record.items() ))
    elif keyword == "classes0":
        
        # store classes0 in nested dict
        classes0 = []
        for device_column_name in list(data.columns):
            class0 = data[device_column_name]["metadata"]["class"][0]
            
            if not class0 in classes0 and len(class0) > 0:
                classes0.append(class0)
                logging.info("add class: " + class0)
        classes0.sort()
                
        return classes0
    elif keyword == "devices":
        devices = []
        for device_column_name in list(data.columns):
            if not device_column_name in devices:
                devices.append(device_column_name)
                logging.info("add device: " + device_column_name)
        devices.sort()
        
        return devices
        
    logging.info("## Stop get_lookup_content of " + keyword + ": " + json_file)


my_filter = {
"#device":"MS21-",
"#date":["2023-08-30T12:12:12Z","2019-08-30T12:12:12Z"],
"#date":["2019-08-30T12:12:12Z"],
"#class":"radiation",
"#subclass":"Pygeometer",
"#locationname":"Mel",
"#country":"ger",
"campaign":"C3SAR",
"#platform":"taro"}


#select_history(my_filter)

#select_history({})

# sort_continuous_history(["MS21-A123", "MS21-A987"]) # positv
# sort_continuous_history(["MS21-A"]) # negativ, exit without save a new file
#sort_continuous_history() # positiv

