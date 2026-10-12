import os
import json
import logging
from logging.handlers import TimedRotatingFileHandler

# helper to get loglevel from ENV
def _resolve_level(default=logging.INFO):
    raw = os.getenv(default, "").strip().upper()
    if not raw:
        return default
    # Handles both "DEBUG" and "10"
    level = logging.getLevelName(raw)
    return level if isinstance(level, int) else default


def setup_logger() -> logging.Logger:
    """
    Configures and returns a logger instance with:
    - STDOUT Handler (Format: Datetime, Level, Message)
    - File Handler (lucky.log) (Format: Datetime, Level, Message, Module, Function, Line number)
    """
    
    # 0 logfile
    APP_CONFIG_PATH_CONTENT = get_APP_CONFIG_PATH()
    
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
    #stdout_handler.setLevel(logging.DEBUG)  # Show INFO and above on console
    stdout_handler.setLevel(_resolve_level( APP_CONFIG_PATH_CONTENT["loglevel_STDOUT"]) )  # Show INFO and above on console
    stdout_handler.setFormatter(stdout_formatter)  # Apply the simple formatter
    logger.addHandler(stdout_handler)

    # 6. Create File Handler (Rotates daily, keeps 7 days)
    file_handler = TimedRotatingFileHandler(
        filename=APP_CONFIG_PATH_CONTENT["logfile"],
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(APP_CONFIG_PATH_CONTENT["loglevel_LOGFILE"])  # Save everything to file
    file_handler.setFormatter(file_formatter)  # Apply the detailed formatter
    logger.addHandler(file_handler)


    return logger
    

def get_APP_CONFIG_PATH():
    if os.getenv("APP_CONFIG_PATH"):
        # read
        print("TRY to read config file, provided as ENV variable 'APP_CONFIG_PATH': " + os.getenv("APP_CONFIG_PATH"))
        try:
            with open(os.getenv("APP_CONFIG_PATH"), 'r') as file:
                APP_CONFIG_PATH_CONTENT = json.load(file)
                
            if "user_credentials_file" not in APP_CONFIG_PATH_CONTENT or not os.path.isfile(APP_CONFIG_PATH_CONTENT["user_credentials_file"]):
                print("user_credentials_file not exists: " + APP_CONFIG_PATH_CONTENT["user_credentials_file"] )
                exit()
            if "logfile" not in APP_CONFIG_PATH_CONTENT:
                print("logfile not exists: " + APP_CONFIG_PATH_CONTENT["logfile"] )
                exit()
            elif not os.path.isfile(APP_CONFIG_PATH_CONTENT["logfile"]):
                with open(APP_CONFIG_PATH_CONTENT["logfile"], mode='w') as f:
                    f.write("")
            if "device_tracker_file" not in APP_CONFIG_PATH_CONTENT or not os.path.isfile(APP_CONFIG_PATH_CONTENT["device_tracker_file"]):
                print("device_tracker_file not exists: " + APP_CONFIG_PATH_CONTENT["device_tracker_file"] )
                exit()
                
            return APP_CONFIG_PATH_CONTENT
        except FileNotFoundError:
            print("Config file provided via APP_CONFIG_PATH_CONTENT variable 'APP_CONFIG_PATH' not found " + os.getenv("APP_CONFIG_PATH"))
            exit()
        except json.JSONDecodeError:
            exit()
    else:
        print("ERROR: no ENV variable 'APP_CONFIG_PATH' provided!")
        exit()
    
    
