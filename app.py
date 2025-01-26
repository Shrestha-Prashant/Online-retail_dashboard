import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_caching import Cache
import os
from datetime import datetime, timedelta

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)

# Initialize server
server = app.server

# Setup cache directory
CACHE_DIR = 'cache-directory'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': CACHE_DIR,
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default timeout
    'CACHE_THRESHOLD': 500  # Maximum number of items the cache will store
}

# Initialize cache
cache = Cache()
cache.init_app(server, config=CACHE_CONFIG)

# App title
app.title = "Online Retail Dashboard"

# Theme settings
color_schemes = {
    'primary': '#2C3E50',    # Dark Blue
    'secondary': '#E74C3C',  # Red
    'accent': '#3498DB',     # Light Blue
    'background': '#F8F9FA', # Light Gray
    'text': '#2C3E50',       # Dark Blue
    'success': '#2ECC71',    # Green
    'warning': '#F1C40F',    # Yellow
    'danger': '#E74C3C',     # Red
    'info': '#3498DB'        # Light Blue
}

# Chart colors for consistency
chart_colors = [
    '#2C3E50', '#E74C3C', '#3498DB', '#2ECC71', '#F1C40F',
    '#9B59B6', '#34495E', '#16A085', '#27AE60', '#D35400'
]

# Plot template
plot_template = {
    'layout': {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'font': {
            'family': 'Arial, sans-serif',
            'color': color_schemes['text']
        },
        'title': {
            'font': {
                'size': 24,
                'color': color_schemes['primary']
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        'legend': {
            'font': {
                'size': 12,
                'color': color_schemes['text']
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

# KPI card style
kpi_card_style = {
    'background-color': 'white',
    'border-radius': '5px',
    'padding': '15px',
    'margin': '10px',
    'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'height': '100%'
}

# Component Styles
component_styles = {
    'card': {
        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'border-radius': '5px',
        'margin-bottom': '1rem'
    },
    'header': {
        'background-color': color_schemes['primary'],
        'color': 'white',
        'padding': '1rem'
    },
    'tab': {
        'background-color': color_schemes['background'],
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
filter_config = {
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

# Configure chart defaults
chart_defaults = {
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

# Add loading spinner styles
loading_spinner_style = {
    'position': 'fixed',
    'top': '50%',
    'left': '50%',
    'transform': 'translate(-50%, -50%)',
    'z-index': '9999',
    'background': 'rgba(255, 255, 255, 0)',
    'width': '100%',
    'height': '100%',
    'display': 'flex',
    'justify-content': 'center',
    'align-items': 'center'
}

loading_spinner_config = {
    'type': 'circle',  
    'color': color_schemes['primary'],
    'fullscreen': True,
    'spinner_style': {
        'position': 'fixed',
        'top': '50%',
        'left': '50%',
        'transform': 'translate(-50%, -50%)',
        'width': '3rem', 
        'height': '3rem',
        'z-index': '9999'
    }
}

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
