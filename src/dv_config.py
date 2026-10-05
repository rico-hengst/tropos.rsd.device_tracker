import os
import json
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger() -> logging.Logger:
    """
    Configures and returns a logger instance with:
    - STDOUT Handler (Format: Datetime, Level, Message)
    - File Handler (lucky.log) (Format: Datetime, Level, Message, Module, Function, Line number)
    """
    
    # 0 logfile
    ENV = get_env()
    
    # 1. Create the logger
    logger = logging.getLogger()
    
    # Avoid adding handlers if the logger was already configured
    if logger.handlers:
        return logger

    # 2. Set the global log level
    logger.setLevel(logging.DEBUG)

    # 3. FORMATTER FOR FILE (Detailed: Datetime, Level, Message, Module, Line)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s | %(module)s | %(funcName)s:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 4. FORMATTER FOR STDOUT (Simple: Datetime, Level, Message)
    stdout_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s | %(module)s | %(funcName)s:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 5. Create STDOUT Handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)  # Show INFO and above on console
    stdout_handler.setFormatter(stdout_formatter)  # Apply the simple formatter
    logger.addHandler(stdout_handler)

    # 6. Create File Handler (Rotates daily, keeps 7 days)
    file_handler = TimedRotatingFileHandler(
        filename=ENV["logfile"],
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Save everything to file
    file_handler.setFormatter(file_formatter)  # Apply the detailed formatter
    logger.addHandler(file_handler)


    return logger
    

def get_env():
    if os.getenv("DV_ENV"):
        # read
        print("TRY to read config file, provided as ENV variable 'DV_ENV'")
        try:
            with open(os.getenv("DV_ENV"), 'r') as file:
                ENV = json.load(file)
                
            if "user_credentials" not in ENV or not os.path.isfile(ENV["user_credentials"]):
                print("user_credentials not exists: " + ENV["user_credentials"] )
                exit()
            if "logfile" not in ENV:
                print("logfile not exists: " + ENV["logfile"] )
                exit()
            elif not os.path.isfile(ENV["logfile"]):
                with open(ENV["logfile"], mode='w') as f:
                    f.write("")
            if "device_tracker_file" not in ENV or not os.path.isfile(ENV["device_tracker_file"]):
                print("device_tracker_file not exists: " + ENV["device_tracker_file"] )
                exit()
                
            return ENV
        except FileNotFoundError:
            print("Config file provided via ENV variable 'DV_ENV' not found " + os.getenv("DV_ENV"))
            exit()
        except json.JSONDecodeError:
            exit()
    else:
        print("ERROR: no ENV variable 'DV_ENV' provided!")
        exit()
    
    
