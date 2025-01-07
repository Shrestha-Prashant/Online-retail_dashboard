import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Application Settings
APP_NAME = "Online Retail Dashboard"
APP_VERSION = "1.0.0"
DEBUG_MODE = True
CACHE_TIMEOUT = 300  # 5 minutes

# File Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ASSETS_DIR = BASE_DIR / "assets"
CACHE_DIR = BASE_DIR / "cache-directory"

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, ASSETS_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data Settings
DEFAULT_EXCEL_FILE = "Online Retail.xlsx"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cache Configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': str(CACHE_DIR),
    'CACHE_DEFAULT_TIMEOUT': CACHE_TIMEOUT,
    'CACHE_THRESHOLD': 500
}

# Chart Settings
CHART_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': [
        'zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
        'autoScale2d', 'resetScale2d', 'hoverClosestCartesian',
        'hoverCompareCartesian', 'toggleSpikelines'
    ],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'chart_export',
        'height': 500,
        'width': 700,
        'scale': 2
    }
}

# Theme Settings
THEME = {
    'colors': {
        'primary': '#2C3E50',    # Dark Blue
        'secondary': '#E74C3C',  # Red
        'accent': '#3498DB',     # Light Blue
        'background': '#F8F9FA', # Light Gray
        'text': '#2C3E50',       # Dark Blue
        'success': '#2ECC71',    # Green
        'warning': '#F1C40F',    # Yellow
        'danger': '#E74C3C',     # Red
        'info': '#3498DB'        # Light Blue
    },
    'chart_colors': [
        '#2C3E50', '#E74C3C', '#3498DB', '#2ECC71', '#F1C40F',
        '#9B59B6', '#34495E', '#16A085', '#27AE60', '#D35400'
    ],
    'fonts': {
        'primary': 'Arial, sans-serif',
        'secondary': 'Helvetica, sans-serif'
    },
    'font_sizes': {
        'small': '12px',
        'normal': '14px',
        'large': '16px',
        'title': '24px',
        'subtitle': '18px'
    }
}

# Plot Template
PLOT_TEMPLATE = {
    'layout': {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'font': {
            'family': THEME['fonts']['primary'],
            'color': THEME['colors']['text']
        },
        'title': {
            'font': {
                'size': 24,
                'color': THEME['colors']['primary']
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        'legend': {
            'font': {
                'size': 12,
                'color': THEME['colors']['text']
            },
            'bgcolor': 'rgba(255, 255, 255, 0.8)'
        },
        'xaxis': {
            'gridcolor': '#eee',
            'zerolinecolor': '#eee'
        },
        'yaxis': {
            'gridcolor': '#eee',
            'zerolinecolor': '#eee'
        }
    }
}

# Component Styles
COMPONENT_STYLES = {
    'card': {
        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'border-radius': '5px',
        'margin-bottom': '1rem'
    },
    'header': {
        'background-color': THEME['colors']['primary'],
        'color': 'white',
        'padding': '1rem'
    },
    'tab': {
        'background-color': THEME['colors']['background'],
        'border-radius': '5px 5px 0 0',
        'padding': '0.5rem 1rem'
    },
    'button': {
        'border-radius': '4px',
        'font-weight': 'bold',
        'text-transform': 'uppercase'
    }
}

# Filter Settings
FILTER_CONFIG = {
    'date_picker': {
        'display_format': 'MMMM D, YYYY',
        'first_day_of_week': 1,  # Monday
        'show_outside_days': True
    },
    'dropdown': {
        'searchable': True,
        'clearable': True,
        'placeholder': 'Select...'
    }
}

# KPI Configuration
KPI_CONFIGS = {
    'revenue': {
        'title': 'Total Revenue',
        'icon': 'fas fa-pound-sign',
        'color': THEME['colors']['primary'],
        'format': '£{:,.2f}'
    },
    'orders': {
        'title': 'Total Orders',
        'icon': 'fas fa-shopping-cart',
        'color': THEME['colors']['accent'],
        'format': '{:,.0f}'
    },
    'customers': {
        'title': 'Total Customers',
        'icon': 'fas fa-users',
        'color': THEME['colors']['success'],
        'format': '{:,.0f}'
    },
    'avg_order': {
        'title': 'Average Order Value',
        'icon': 'fas fa-receipt',
        'color': THEME['colors']['secondary'],
        'format': '£{:,.2f}'
    }
}

# Chart Defaults
CHART_DEFAULTS = {
    'height': 400,
    'margin': {
        'l': 50,
        'r': 30,
        't': 50,
        'b': 50
    },
    'showlegend': True,
    'legend': {
        'orientation': 'h',
        'yanchor': 'bottom',
        'y': 1.02,
        'xanchor': 'right',
        'x': 1
    }
}

# RFM Analysis Settings
RFM_SETTINGS = {
    'recency_scores': {
        5: {'label': 'Champions', 'max_days': 30},
        4: {'label': 'Loyal', 'max_days': 90},
        3: {'label': 'Recent', 'max_days': 180},
        2: {'label': 'Inactive', 'max_days': 365},
        1: {'label': 'Lost', 'max_days': float('inf')}
    },
    'frequency_scores': {
        5: {'label': 'Champions', 'min_orders': 12},
        4: {'label': 'Loyal', 'min_orders': 6},
        3: {'label': 'Regular', 'min_orders': 3},
        2: {'label': 'Occasional', 'min_orders': 2},
        1: {'label': 'One-time', 'min_orders': 1}
    }
}

# Error Messages
ERROR_MESSAGES = {
    'data_load': "Error loading data. Please check the data file and try again.",
    'processing': "Error processing data. Please contact support if the issue persists.",
    'calculation': "Error performing calculations. Please try refreshing the page.",
    'filter': "Error applying filters. Please try different filter combinations."
}

# Function to get environment-specific settings
def get_env_settings() -> Dict[str, Any]:
    """Get environment-specific settings"""
    env = os.getenv('DASHBOARD_ENV', 'development')
    
    if env == 'production':
        return {
            'DEBUG_MODE': False,
            'CACHE_TIMEOUT': 3600,  # 1 hour
            'DATABASE_URI': os.getenv('DATABASE_URI'),
            'SECRET_KEY': os.getenv('SECRET_KEY')
        }
    else:
        return {
            'DEBUG_MODE': True,
            'CACHE_TIMEOUT': 300,  # 5 minutes
            'DATABASE_URI': 'sqlite:///dashboard.db',
            'SECRET_KEY': 'dev-secret-key'
        }

# Function to validate settings
def validate_settings() -> bool:
    """Validate critical settings and paths"""
    try:
        # Check required directories
        for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, ASSETS_DIR]:
            if not directory.exists():
                raise ValueError(f"Required directory not found: {directory}")

        # Check data file
        data_file = RAW_DATA_DIR / DEFAULT_EXCEL_FILE
        if not data_file.exists():
            raise ValueError(f"Data file not found: {data_file}")

        # Validate color schemes
        for color_set in [THEME['colors'], THEME['chart_colors']]:
            for color in color_set:
                if not isinstance(color, str) or not color.startswith('#'):
                    raise ValueError(f"Invalid color format: {color}")

        return True

    except Exception as e:
        print(f"Settings validation failed: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Validate settings
    if validate_settings():
        print("Settings validated successfully")
        
        # Print current environment settings
        env_settings = get_env_settings()
        print("\nCurrent Environment Settings:")
        for key, value in env_settings.items():
            print(f"{key}: {value}")
            
        # Print available color schemes
        print("\nAvailable Color Schemes:")
        for name, color in THEME['colors'].items():
            print(f"{name}: {color}")
    else:
        print("Settings validation failed")