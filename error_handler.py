from typing import Optional, Dict, Any
import traceback
import logging
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime

class DashboardErrorHandler:
    """Error handler for the dashboard application"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_history: Dict[str, list] = {}
        
    def handle_callback_error(self, error: Exception, callback_id: str, inputs: Dict[str, Any]) -> html.Div:
        """
        Handle callback errors and return appropriate UI component
        
        Args:
            error: The exception that occurred
            callback_id: ID of the callback where error occurred
            inputs: Callback inputs when error occurred
            
        Returns:
            html.Div: Error message component for display
        """
        # Log the error
        error_msg = self._format_error_details(error, callback_id, inputs)
        self.logger.error(error_msg)
        
        # Store in error history
        self.error_history.setdefault(callback_id, []).append({
            'timestamp': datetime.now(),
            'error': str(error),
            'traceback': traceback.format_exc(),
            'inputs': inputs
        })
        
        # Return user-friendly error component
        return self._create_error_component(error)
        
    def handle_data_error(self, error: Exception, operation: str) -> html.Div:
        """
        Handle data processing errors
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            
        Returns:
            html.Div: Error message component for display
        """
        # Log the error
        error_msg = f"Data Error in {operation}: {str(error)}\n{traceback.format_exc()}"
        self.logger.error(error_msg)
        
        # Return user-friendly error component
        return self._create_error_component(
            error,
            title="Data Processing Error",
            suggestion="Please try refreshing the page or contact support if the issue persists."
        )
        
    def _format_error_details(self, error: Exception, callback_id: str, 
                            inputs: Dict[str, Any]) -> str:
        """Format detailed error message for logging"""
        details = [
            f"Error in callback: {callback_id}",
            f"Timestamp: {datetime.now()}",
            f"Error Type: {type(error).__name__}",
            f"Error Message: {str(error)}",
            f"Callback Inputs: {inputs}",
            "Traceback:",
            traceback.format_exc()
        ]
        return "\n".join(details)
        
    def _create_error_component(self, error: Exception, title: str = "Error", 
                              suggestion: Optional[str] = None) -> html.Div:
        """Create user-friendly error message component"""
        return dbc.Alert(
            [
                html.H4(title, className="alert-heading"),
                html.P(str(error)),
                html.Hr(),
                html.P(
                    suggestion or "An error occurred while processing your request. "
                    "Please try again later.",
                    className="mb-0"
                )
            ],
            color="danger",
            className="mb-3"
        )
        
    def get_error_history(self, callback_id: Optional[str] = None) -> Dict[str, list]:
        """Get error history for analysis"""
        if callback_id:
            return {callback_id: self.error_history.get(callback_id, [])}
        return self.error_history.copy()
        
    def clear_error_history(self, callback_id: Optional[str] = None):
        """Clear error history"""
        if callback_id:
            self.error_history.pop(callback_id, None)
        else:
            self.error_history.clear()

def create_error_boundary(error: Exception) -> dbc.Container:
    """
    Create error boundary component for top-level errors
    
    Args:
        error: The exception that occurred
        
    Returns:
        dbc.Container: Error boundary component
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4("Dashboard Error", className="alert-heading"),
                    html.P("An unexpected error occurred in the dashboard."),
                    html.Hr(),
                    html.P([
                        "Error details: ",
                        html.Code(str(error))
                    ]),
                    html.Button(
                        "Reload Dashboard",
                        id="reload-button",
                        className="btn btn-primary mt-3",
                        n_clicks=0
                    )
                ], color="danger", className="mt-5")
            ], md=8, className="offset-md-2")
        ])
    ], fluid=True)

# Example usage
if __name__ == "__main__":
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Create error handler instance
    error_handler = DashboardErrorHandler(logger)
    
    # Example error handling
    try:
        raise ValueError("Example error")
    except Exception as e:
        error_component = error_handler.handle_callback_error(
            e,
            "example-callback",
            {"input1": "value1"}
        )
        print("Error logged and component created")