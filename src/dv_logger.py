import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logger(name: str = "lucky_logger") -> logging.Logger:
    """
    Configures and returns a logger instance with:
    - Standard Output (STDOUT) handler
    - Daily Rotating File handler (lucky.log)
    - Logs older than 7 days are automatically deleted
    """
    
    # 1. Create the logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers if the logger was already configured
    if logger.handlers:
        return logger

    # 2. Set the global log level (Configure here only once)
    logger.setLevel(logging.DEBUG)  # Capture DEBUG and above

    # 3. Define the log format
    # Format: datetime, loglevel, message, module name, line number
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s | %(name)s | Line:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    stdout_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 4. Create STDOUT Handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)  # Usually, you only want INFO+ on console
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # 5. Create Rotating File Handler
    # backupCount=7 ensures logs older than 7 days are deleted
    file_handler = TimedRotatingFileHandler(
        filename="lucky.log",
        when="midnight",       # Rotate every day at midnight
        interval=1,            # Every 1 day
        backupCount=7,         # Keep logs for 7 days
        encoding="utf-8"       # Ensure proper character encoding
    )
    file_handler.setLevel(logging.DEBUG)  # Save everything to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
