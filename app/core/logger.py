import logging
import sys

def setup_logger():
    """Sets up a standardized logger for the application."""
    logger = logging.getLogger("pythagoras")
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        # Create handler to stream to stdout
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger.addHandler(handler)
        
    return logger

# Global logger instance
log = setup_logger()
