#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json 
from jsonschema import validate, Draft7Validator, FormatChecker, ValidationError
import uuid
import datetime

import pandas as pd



device_record_arielle = {
    "metadata": {
        "name":"arielle",
        "classification": {
            "class":"lidar",
            "subclass": "pollyxt"
        },
        "device_manufacturer" : { 
            "name" : "TROPOS", 
            "address": "", 
            "contact":""
        },
        "device_model" : {
            "name": "PollyXT", 
            "description": "multiwavelength Raman polarization lidar",
            "purchased":"2016-01-21T12:00:00Z",
            "serial":"JHA399OO",
            "pid":"https://instrumentdb.out.ocp.fmi.fi/instrument/31c4f71c-f1a7-4e03-a66d-ecdbcaab0253"
        },
        "owner" : {"name" : "TROPOS", 
            "address":"", 
            "contact": "re@t.de"
        },
        "created" : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    },
    
    "history":[],
    "calibration":[]
}



device_record_ms80 = {
    "metadata": {
        "name":"MS-80_SNABCD22",
        "classification": {
            "class":"radiation",
            "subclass": "pyranometer"
        },
        "device_manufacturer" : { 
            "name" : "EKO", 
            "address": "EKO Instruments Europe B.V. Lulofsstraat 55, Unit 28 2521 AL, Den Haag Netherlands", 
            "contact":""
        },
        "device_model" : {
            "name": "MS-80", 
            "description": "An ISO9060:2018 Class A solar sensor in the top tier ‘fast-response and ‘spectrally flat’ sub-categories, with unprecedented low zero-offset behaviour, and a 5-year recalibration interval.",
            "purchased":"2024-01-21T12:00:00Z",
            "serial":"SNABCD22"
        },
        "owner" : {"name" : "TROPOS", 
            "address":"", 
            "contact": "x@tropos.de"
        },
        "created" : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    },
    
    "history":[],
    "calibration":[]
}

    
device_record_ms21 = {

    "metadata": {
        "name": "MS-21_SN445566A",
        "classification": {
            "class": "radiation",
            "subclass": "pygeometer"
        },
        "device_manufacturer": {
            "name": "EKO",
            "address": "EKO Instruments Europe B.V. Lulofsstraat 55, Unit 28 2521 AL, Den Haag Netherlands",
            "contact": ""
        },
        "device_model": {
            "name": "MS-21",
            "description": "Research-grade, accurate, and robust, the MS-21 measures longwave downwelling radiation and longwave net radiation in a wide spectral band and delivers superior stability independent of the sensors\u2019 operating temperature.",
            "purchased": "2012-01-01T12:00:00Z",
            "serial": "SN445566A"
        },
        "owner": {
            "name": "TROPOS",
            "address": "",
            "contact": "x@tropos.de"
        },
        "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    },
    "history": [],
    "calibration":[]
}



history_arielle11={
    "startdate": "2012-10-27T12:12:12Z",
    "stopdate": "2012-11-26T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "Polarstern", "OCEANET"
    ],
    "campaign": "PS81",
    "location": {
        "name": "xyz",       
        "description"       : "Master tracks",           
        "track_url"         : "https://doi.pangaea.de/10.1594/PANGAEA.841009?format=textfile",
        "track_desc"        : "https://doi.pangaea.de/10.1594/PANGAEA.841009",
        "is_mobile": True
    }
}
history_arielle12={
    "startdate": "2018-05-01T12:12:12Z",
    "stopdate": "2018-06-10T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "Polarstern", "OCEANET"
    ],
    "campaign": "PS113",
    "location": {
        "name": "Punta Arenas - Bremerhaven",       
        "description"       : "Master tracks: Punta Arenas - Bremerhaven",           
        "track_url"         : "https://doi.pangaea.de/10.1594/PANGAEA.891753?format=textfile",
        "track_desc"        : "https://doi.pangaea.de/10.1594/PANGAEA.891753",
        "is_mobile": True
    }
}

history_arielle13={
    "startdate": "2023-01-01T12:12:12Z",
    "stopdate": "2023-12-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "Polarstern", "OCEANET"
    ],
    "campaign": "PS113",
    "location": {
        "name": "Neumayer III",
        "lat": -70,
        "lon": -8,
        "is_mobile": False
    }
}

history_arielle14={
    "startdate": "2024-03-05T12:12:12Z",
    "stopdate": "2024-10-21T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "location": {
        "name": "Leipzig",
        "country":"Germany",
        "lat": 51,
        "lon": 12,
        "is_mobile": False
    }
}

history_11={
    "startdate": "2024-09-24T12:12:12Z",
    "stopdate": "2024-12-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "TARO"
    ],
    "location": {
        "name": "Melpitz",
        "country": "Germany",
        "lat": 50,
        "lon": 12,
        "is_mobile": False
    }
}
history_12 = {
    "startdate": "2025-01-24T12:12:12Z",
    "stopdate": "2025-05-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "campaign": "C3SAR",
    "location": {
        "name": "Falkenberg",
        "country": "Germany",
        "lat": 50,
        "lon": 12,
        "is_mobile": False
    }
}


history_AA={
    "startdate": "2023-09-24T12:12:12Z",
    "stopdate": "2023-12-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "TARO"
    ],
    "location": {
        "name": "Mindelo",
        "country": "Cabo Verde",
        "lat": -5,
        "lon": -5,
        "is_mobile": False
    }
}

history_AB={
    "startdate": "2024-01-24T12:12:12Z",
    "stopdate": "2024-12-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "TARO"
    ],
    "location": {
        "name": "Melpitz",
        "country": "Germany",
        "lat": 50,
        "lon": 13,
        "is_mobile": False
    }
}

history_AC={
    "startdate": "2025-01-01T12:12:12Z",
    "stopdate": "2025-12-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "platform": [
        "TARO"
    ],
    "location": {
        "name": "Mindelo",
        "country": "Cabo Verde",
        "lat": -5,
        "lon": -5,
        "is_mobile": False
    }
}

history_AD={
    "startdate": "2025-12-15T12:12:12Z",
    "stopdate": "2026-02-02T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "campaign": "PS127",
    "platform": [
        "Polarstern", "OCEANET"
    ],
    "location": {
        "name": "POLARSTERN cruise PS152",       
        "description"       : "Master tracks in different resolutions of POLARSTERN cruise PS152",           
        "track_url"         : "https://doi.pangaea.de/10.1594/PANGAEA.993941?format=textfile",
        "track_desc"        : "",
        "is_mobile": True
    }
}

history_AE={
    "startdate": "2026-05-01T12:12:12Z",
    "stopdate": "2026-08-01T00:12:12Z",
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "uuid": str(uuid.uuid1()),
    "campaign":"C3SAR",
    "location": {
        "name": "Falkenberg",
        "country": "Germany",
        "lat": 53,
        "lon": 12,
        "is_mobile": False
    }
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
            
            
            




def add_history(device, history_record):
    # load schema
    with open("../config/schema_history.json", "r+") as file:
        try:
            history_schema = json.load(file)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)
        
        
        
    
    # old valiadation without format checker
    validate(
        instance=history_record,
        schema=history_schema,
    )




    validator = Draft7Validator(
            history_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(history_record))
    
    if not errors:
        print("✓ Validation Successful: The JSON instance is valid.")
        print(history_record)
        
        
        json_file= "../config/device_tracker.json"
        with open(json_file, "r+") as file:
            device_tracker = json.load(file)
            
            print("Update json_file: " + json_file )
            
            if device in device_tracker.keys():
                if "history" in device_tracker[device].keys():
                    device_tracker[device]["history"].append(history_record)
                   # print(device_tracker)
                    file.seek(0)
                    json.dump(device_tracker, file, indent=4)
                    
                    
                    
                    
                else:
                    print("no key2")
            else:
                print("-- no device in json file detected: " + device + ", no validation")
                # device_tracker.update({"MS21-A987": { "name" : "xyz", "history":[]}})
                # print(device_tracker)
                # file.seek(0)
                # json.dump(device_tracker, file, indent=4)
                
            #data = pd.DataFrame.from_dict(device_tracker)
            #print(data)
            #print(data["MS21-A123"]["history"][0])
            #sorted_nested_dict = dict(sorted(data["MS21-A123"]["history"], key=lambda x: (x[1]['created'])))
        
    else:
        print("✗ Validation Failed: The JSON instance is invalid.")
        print(history_record)

        for error in errors:
            # error.message usually contains the specific reason
            print(f"  - Error: {error.message}")
            print(f"    Path: {list(error.path)}")
            print(f"    Validator: {error.validator}")
            
            
            

        
        
def add_device(device_record):
    # load schema
    with open("../config/schema_device.json", "r+") as file:
        device_schema = json.load(file)
        
    
    
    #validate(instance=device_record, schema=device_schema)
    
    validator = Draft7Validator(
            device_schema,
            format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(device_record))
    
   
    
    if errors:
        print("✗ Validation Failed: The JSON instance is invalid.")
        print(device_record)

        for error in errors:
            # error.message usually contains the specific reason
            print(f"  - Error: {error.message}")
            print(f"    Path: {list(error.path)}")
            print(f"    Validator: {error.validator}")
            
    else :
        print("✓ Validation Successful: The JSON instance is valid.")
        print(device_record)
        
        # add instance record to json
        json_file= "../config/device_tracker.json"
        with open(json_file, "r+") as file:
            device_tracker = json.load(file)
            
            print("Try to update json_file: " + json_file )
            
            if not device_record["metadata"]["name"] in device_tracker.keys():
                print("Add device record")
                device_tracker[device_record["metadata"]["name"]] = device_record
                file.seek(0)
                json.dump(device_tracker, file, indent=4)
            else:
                print("Device " + device_record["metadata"]["name"] + " already exists at json_file, skip record")






#add_history("MS-21_SN445566A",history_11)
#add_history("MS-21_SN445566A",history_12)
#add_calibration("MS-21_SN445566A",{"calibration_link":"http://mycalibration.info"})

# add_history("MS-80_SNABCD22",history_AA)
# add_history("MS-80_SNABCD22",history_AB)
# add_history("MS-80_SNABCD22",history_AC)
# add_history("MS-80_SNABCD22",history_AD)
# add_history("MS-80_SNABCD22",history_AE)
add_calibration("MS-80_SNABCD22",
{
    "calibration_description" : "",
    "calibration_performed_by" : "Ak Hein",
    "calibration_performed_at" :"DWD",
    "calibration_performed_period" : ["2023-07-03T12:12:12Z","2023-07-13T12:12:12Z"],
    "calibration_record_created" : "2024-08-03T12:12:12Z",
    "calibration_used_method" : "Kletter et al.",
    "calibration_used_reference" : "CPC",
    "calibration_valid_period": ["2023-08-03T00:12:12Z", "2024-08-03T12:12:12Z"],
    "calibration_values": [0.11992, -22.3, 0.3]
})
add_calibration("MS-80_SNABCD22",
{
    "calibration_description" : "",
    "calibration_performed_by" : "Dore Hwaptist",
    "calibration_performed_at" :"DWD",
    "calibration_performed_period" : ["2024-09-03T12:12:12Z","2024-09-13T12:12:12Z"],
    "calibration_record_created" : "2026-08-03T12:12:12Z",
    "calibration_used_method" : "Kletter et al.",
    "calibration_used_reference" : "CPC",
    "calibration_valid_period": ["2024-10-03T00:12:12Z", "2026-10-03T12:12:12Z"],
    "calibration_values": [0.11972, -22.0, 0.27]
})




# add_history("arielle",history_arielle11)
# add_history("arielle",history_arielle12)
# add_history("arielle",history_arielle13)
# add_history("arielle",history_arielle14)

add_calibration("arielle",
{
    "calibration_description" : "",
    "calibration_performed_by" : "Bonnie Nengeldrenn",
    "calibration_performed_at" :"TROPOS",
    "calibration_performed_period" : ["2023-07-03T12:12:12Z","2023-07-13T12:12:12Z"],
    "calibration_record_created" : "2024-08-03T12:12:12Z",
    "calibration_used_method" : "Nengeldren et al.",
    "calibration_used_reference" : "ColiDrom",
    "calibration_valid_period": ["2023-08-03T00:12:12Z", "2024-08-03T12:12:12Z"],
    "calibration_values": [2.11992, 22.3, 0.3]
})







#add_device(device_record_ms21)
#add_device(device_record_ms80)
#add_device(device_record_arielle)
