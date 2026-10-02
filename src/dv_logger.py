import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name: str = "lucky_logger") -> logging.Logger:
    """
    Configures and returns a logger instance with:
    - STDOUT Handler (Format: Datetime, Level, Message)
    - File Handler (lucky.log) (Format: Datetime, Level, Message, Module, Line)
    """
    
    # 1. Create the logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers if the logger was already configured
    if logger.handlers:
        return logger

    # 2. Set the global log level
    logger.setLevel(logging.DEBUG)

    # 3. FORMATTER FOR FILE (Detailed: Datetime, Level, Message, Module, Line)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s | %(name)s | Line:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 4. FORMATTER FOR STDOUT (Simple: Datetime, Level, Message)
    stdout_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s | %(name)s | Line:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 5. Create STDOUT Handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)  # Show INFO and above on console
    stdout_handler.setFormatter(stdout_formatter)  # Apply the simple formatter
    logger.addHandler(stdout_handler)

    # 6. Create File Handler (Rotates daily, keeps 7 days)
    file_handler = TimedRotatingFileHandler(
        filename="lucky.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Save everything to file
    file_handler.setFormatter(file_formatter)  # Apply the detailed formatter
    logger.addHandler(file_handler)


    return logger
