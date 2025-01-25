import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from datetime import datetime

def setup_logging(log_dir: str = "logs"):
    """
    Set up logging configuration with both file and console handlers
    
    Args:
        log_dir (str): Directory to store log files
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s'
    )

    # Create handlers
    # Main application log - Rotating by size (10MB)
    main_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_handler.setFormatter(detailed_formatter)
    main_handler.setLevel(logging.INFO)

    # Error log - Rotating daily
    error_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    root_logger.handlers = []

    # Add handlers
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Create specific loggers
    loggers = {
        'data': setup_component_logger('data', log_dir),
        'callbacks': setup_component_logger('callbacks', log_dir),
        'ui': setup_component_logger('ui', log_dir)
    }

    return loggers

def setup_component_logger(component: str, log_dir: str) -> logging.Logger:
    """
    Set up logger for specific component with its own file
    
    Args:
        component (str): Component name
        log_dir (str): Directory to store log files
        
    Returns:
        logging.Logger: Configured logger for the component
    """
    logger = logging.getLogger(component)
    logger.setLevel(logging.INFO)
    
    # Create component directory
    component_dir = os.path.join(log_dir, component)
    Path(component_dir).mkdir(parents=True, exist_ok=True)
    
    # Component specific handler
    handler = RotatingFileHandler(
        filename=os.path.join(component_dir, f'{component}.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    ))
    
    logger.handlers = []  # Remove any existing handlers
    logger.addHandler(handler)
    
    return logger

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """
    Log error with full traceback and context
    
    Args:
        logger (logging.Logger): Logger instance
        error (Exception): Exception to log
        context (str, optional): Additional context information
    """
    import traceback
    error_msg = f"Error occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {str(error)}\n"
    error_msg += "Traceback:\n"
    error_msg += traceback.format_exc()
    logger.error(error_msg)

# Usage example for testing
if __name__ == "__main__":
    loggers = setup_logging()
    
    # Test logging
    logger = logging.getLogger(__name__)
    logger.info("Testing logging configuration")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error(logger, e, "test section")