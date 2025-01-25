import functools
import time
import traceback
import logging
import pandas as pd
from typing import Callable, Any, Dict
from datetime import datetime

class DashboardMonitor:
    """Utility class for monitoring dashboard operations and performance"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.operation_times: Dict[str, float] = {}
        self.error_counts: Dict[str, int] = {}
        
    def log_performance(self, operation: str, execution_time: float):
        """Log performance metrics for an operation"""
        self.operation_times[operation] = execution_time
        self.logger.info(f"Performance - {operation}: {execution_time:.2f}s")
        
    def log_error(self, operation: str, error: Exception):
        """Log error and update error counts"""
        self.error_counts[operation] = self.error_counts.get(operation, 0) + 1
        self.logger.error(f"Error in {operation}: {str(error)}\n{traceback.format_exc()}")
        
    def get_performance_summary(self) -> Dict[str, float]:
        """Get summary of operation performance"""
        return self.operation_times.copy()
        
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of error counts"""
        return self.error_counts.copy()

def monitor_callback(monitor: DashboardMonitor):
    """Decorator to monitor callback performance and errors"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            operation = func.__name__
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                monitor.log_performance(operation, execution_time)
                return result
            except Exception as e:
                monitor.log_error(operation, e)
                raise
        return wrapper
    return decorator

def validate_dataframe(df: 'pd.DataFrame', logger: logging.Logger) -> bool:
    """
    Validate DataFrame contents and log any issues
    
    Args:
        df: pandas DataFrame to validate
        logger: Logger instance
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        # Check for empty DataFrame
        if df.empty:
            logger.error("DataFrame is empty")
            return False
            
        # Check required columns
        required_columns = ['InvoiceDate', 'Quantity', 'UnitPrice', 'CustomerID', 'Country']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
            
        # Check for invalid values
        invalid_quantities = df['Quantity'] <= 0
        invalid_prices = df['UnitPrice'] <= 0
        
        if invalid_quantities.any():
            logger.warning(f"Found {invalid_quantities.sum()} rows with invalid quantities")
            
        if invalid_prices.any():
            logger.warning(f"Found {invalid_prices.sum()} rows with invalid prices")
            
        # Check date range
        date_range = df['InvoiceDate'].max() - df['InvoiceDate'].min()
        logger.info(f"Date range in data: {date_range.days} days")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating DataFrame: {str(e)}\n{traceback.format_exc()}")
        return False

def format_error_message(error: Exception, context: str = None) -> str:
    """
    Format error message with context and timestamp
    
    Args:
        error: Exception object
        context: Optional context information
        
    Returns:
        str: Formatted error message
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_message = [
        f"Timestamp: {timestamp}",
        f"Error Type: {type(error).__name__}",
        f"Message: {str(error)}"
    ]
    
    if context:
        error_message.insert(1, f"Context: {context}")
        
    error_message.append("Traceback:")
    error_message.append(traceback.format_exc())
    
    return "\n".join(error_message)

class CallbackDebugger:
    """Utility class for debugging callback executions"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.callback_history: Dict[str, list] = {}
        
    def log_callback_start(self, callback_id: str, inputs: Dict[str, Any]):
        """Log the start of a callback execution"""
        self.logger.debug(f"Starting callback {callback_id}")
        self.logger.debug(f"Inputs: {inputs}")
        
    def log_callback_end(self, callback_id: str, execution_time: float, output: Any):
        """Log the end of a callback execution"""
        self.logger.debug(f"Completed callback {callback_id} in {execution_time:.2f}s")
        self.callback_history.setdefault(callback_id, []).append({
            'timestamp': datetime.now(),
            'execution_time': execution_time,
            'success': True
        })
        
    def log_callback_error(self, callback_id: str, error: Exception):
        """Log callback error"""
        self.logger.error(f"Error in callback {callback_id}: {str(error)}")
        self.callback_history.setdefault(callback_id, []).append({
            'timestamp': datetime.now(),
            'error': str(error),
            'success': False
        })
        
    def get_callback_history(self, callback_id: str = None) -> Dict[str, list]:
        """Get callback execution history"""
        if callback_id:
            return {callback_id: self.callback_history.get(callback_id, [])}
        return self.callback_history.copy()

# Example usage
if __name__ == "__main__":
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Create monitor instance
    monitor = DashboardMonitor(logger)
    
    # Example monitored function
    @monitor_callback(monitor)
    def example_callback(input_value):
        time.sleep(1)  # Simulate some work
        return input_value * 2
    
    # Test the monitored callback
    try:
        result = example_callback(5)
        print(f"Result: {result}")
        print("\nPerformance Summary:")
        print(monitor.get_performance_summary())
    except Exception as e:
        print("\nError Summary:")
        print(monitor.get_error_summary())