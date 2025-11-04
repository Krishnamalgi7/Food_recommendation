import logging
import datetime

class CustomLogger:
    """
    A custom logger class for flexible logging.
    """

    def __init__(self, log_file="app.log", log_level=logging.INFO, format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
        """
        Initializes the custom logger.

        Args:
            log_file (str): The name of the log file.
            log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO).
            format_string (str): The format string for log messages.
        """
        self.logger = logging.getLogger(__name__)  # Get a logger for the current module
        self.logger.setLevel(log_level)

        # Create a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create a formatter
        formatter = logging.Formatter(format_string)
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(file_handler)


    def debug(self, message):
        """Logs a debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Logs an info message."""
        self.logger.info(message)

    def warning(self, message):
        """Logs a warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Logs an error message."""
        self.logger.error(message)

    def critical(self, message):
        """Logs a critical message."""
        self.logger.critical(message)