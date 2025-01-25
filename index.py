from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash
from app import app, cache
import pandas as pd
from datetime import datetime
import os
from components.header import create_header
from components.kpi_cards import create_kpi_cards
from components.sales_charts import create_sales_summary
from components.product_charts import create_product_summary
from components.customer_charts import create_customer_summary
from components.geographic_charts import create_geographic_summary
from data.data_loader import RetailDataLoader
import logging
from logging_config import setup_logging, log_error
from monitor_utils import DashboardMonitor, monitor_callback, validate_dataframe
from error_handler import DashboardErrorHandler

# Set up logging
loggers = setup_logging()
logger = logging.getLogger(__name__)
data_logger = loggers['data']
callback_logger = loggers['callbacks']
ui_logger = loggers['ui']


# Create monitoring and error handling instances
monitor = DashboardMonitor(callback_logger)
error_handler = DashboardErrorHandler(logger)

# Initialize the data loader
DATA_PATH = '/Users/panda/Documents/data_mining/Online-Retail-Dashboard/Online_Retail.xlsx'
print(DATA_PATH)
CACHE_DIR = 'data/processed'
loader = RetailDataLoader(DATA_PATH, CACHE_DIR)
print("RetailDataLoader crossed")

def make_cache_key():
    """Generate a unique cache key based on the data file's modification time"""
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Online_Retail.xlsx')
    if os.path.exists(data_path):
        mtime = os.path.getmtime(data_path)
        return f'retail_data_{mtime}'
    return 'retail_data_default'

@cache.memoize(timeout=3600, make_name=make_cache_key)
def load_initial_data():
    try:
        logger.info("Loading initial data...")
        df = pd.read_excel(DATA_PATH)
        if not validate_dataframe(df, data_logger):
            raise ValueError("Data validation failed")
        if df is not None and not df.empty:
            df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
            logger.info(f"Data loaded successfully: {len(df)} rows")
            return df, df['InvoiceDate'].min(), df['InvoiceDate'].max()
    except Exception as e:
        log_error(data_logger, e, "initial data loading")
        return pd.DataFrame(), datetime.now(), datetime.now()

# Update where initial data is loaded
df, start_date, end_date = load_initial_data()

# Initialize store with full dataset
if not df.empty:
    initial_filtered_data = df.to_json(date_format='iso', orient='split')
else:
    initial_filtered_data = None

# Define the navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H3("Online Retail Dashboard", className="mb-0 text-white"),
                        width="auto",
                    )
                ],
                align="center",
                className="g-0",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.DatePickerRange(
                                id='date-filter',
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                                start_date=start_date,
                                end_date=end_date,
                                className="date-picker"
                            )
                        ]
                    )
                ]
            )
        ],
        fluid=True
    ),
    color="dark",
    dark=True,
    className="mb-4"
)

# Define the layout
app.layout = html.Div([
    # Data stores
    dcc.Store(id='filtered-data-store'),
    dcc.Store(id='selected-data-store'),
    
    # Header with filters
    create_header(
        start_date=start_date,
        end_date=end_date,
        countries=df['Country'].unique().tolist() if not df.empty else [],
        categories=df['Category'].unique().tolist() if 'Category' in df.columns else []
    ),
    
    # Main content
    dbc.Container([
        # Tabs for navigation
        dbc.Tabs(
            id='main-tabs',
            active_tab='overview-tab',
            children=[
                dbc.Tab(label='Overview', tab_id='overview-tab'),
                dbc.Tab(label='Sales Analysis', tab_id='sales-tab'),
                dbc.Tab(label='Product Analysis', tab_id='products-tab'),
                dbc.Tab(label='Customer Analysis', tab_id='customers-tab'),
                dbc.Tab(label='Geographic Analysis', tab_id='geography-tab')
            ],
            className="mb-3"
        ),
        
        # Tab content
        html.Div(id='tab-content'),
        
        # Footer
        html.Footer(
            dbc.Row([
                dbc.Col(
                    html.P(
                        "Online Retail Dashboard © 2024",
                        className="text-center text-muted"
                    )
                )
            ]),
            className="mt-4 pt-3 border-top"
        )
    ], fluid=True)
])

# Add this after app.layout definition
@app.callback(
    Output('filtered-data-store', 'data'),
    [Input('date-filter', 'start_date')],
    [State('filtered-data-store', 'data')]
)
def initialize_store(start_date, current_data):
    if current_data is None:
        return initial_filtered_data
    return current_data

# Unified callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filtered-data-store', 'data')]
)
@monitor_callback(monitor)
def update_tab_content(active_tab, filtered_data):
    try:
        logger.info(f"Updating tab content: {active_tab}")
        
        if filtered_data is None:
            logger.warning("No filtered data available")
            return html.Div("No data available. Please check data loading.")

        try:
            df = pd.read_json(filtered_data, orient='split')
            if active_tab == 'overview-tab':
                return dbc.Container([
                    create_kpi_cards(filtered_data),
                    dbc.Row([
                        dbc.Col(create_sales_summary(filtered_data), md=12)
                    ], className="mb-4")
                ], fluid=True)
            elif active_tab == 'sales-tab':
                return create_sales_summary(filtered_data)
            elif active_tab == 'products-tab':
                return create_product_summary(filtered_data)
            elif active_tab == 'customers-tab':
                return create_customer_summary(filtered_data)
            elif active_tab == 'geography-tab':
                return create_geographic_summary(filtered_data)
        except Exception as e:
            logger.error(f"Error updating tab content: {e}")
            return html.Div(f"Error loading content: {str(e)}")

    except Exception as e:
        return error_handler.handle_callback_error(e, 'update_tab_content', {
            'active_tab': active_tab,
            'filtered_data': 'data_available' if filtered_data else None
        })

@app.callback(
    Output('filtered-data-store', 'data', allow_duplicate=True),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('country-filter', 'value'),
     Input('last-30-days', 'n_clicks'),
     Input('last-quarter', 'n_clicks'),
     Input('ytd', 'n_clicks'),
     Input('all-time', 'n_clicks')],
     prevent_initial_call=True
)
def update_filtered_data(start_date, end_date, countries, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return initial_filtered_data if not df.empty else None

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'last-30-days':
        end_date = df['InvoiceDate'].max()
        start_date = end_date - pd.Timedelta(days=30)
    elif triggered_id == 'last-quarter':
        end_date = df['InvoiceDate'].max()
        start_date = end_date - pd.Timedelta(days=90)
    elif triggered_id == 'ytd':
        end_date = df['InvoiceDate'].max()
        start_date = end_date.replace(month=1, day=1)
    elif triggered_id == 'all-time':
        start_date = df['InvoiceDate'].min()
        end_date = df['InvoiceDate'].max()

    try:
        mask = (df['InvoiceDate'] >= start_date) & (df['InvoiceDate'] <= end_date)
        if countries and len(countries) > 0:
            mask &= df['Country'].isin(countries)
        filtered_df = df[mask]
        return filtered_df.to_json(date_format='iso', orient='split')
    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        return None

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)