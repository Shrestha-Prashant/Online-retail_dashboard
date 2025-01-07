from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import List, Optional
from components.header import create_header
from components.kpi_cards import create_kpi_cards
from components.sales_charts import create_sales_summary
from components.product_charts import create_product_summary
from components.customer_charts import create_customer_summary
from components.geographic_charts import create_geographic_summary

def create_tab_content(tab_id: str, filtered_data: str) -> html.Div:
    """
    Create content for each tab
    
    Args:
        tab_id (str): ID of the tab
        filtered_data (str): JSON string of filtered data
        
    Returns:
        html.Div: Tab content
    """
    if tab_id == 'overview-tab':
        return html.Div([
            # KPI Cards
            create_kpi_cards(filtered_data),
            
            # Main Overview Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Sales Trend"),
                        dbc.CardBody(id='sales-trend-chart')
                    ])
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Top Products"),
                        dbc.CardBody(id='top-products-chart')
                    ])
                ], md=4)
            ], className="mb-4"),
            
            # Secondary Overview Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Customer Segments"),
                        dbc.CardBody(id='customer-segments-chart')
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Geographic Distribution"),
                        dbc.CardBody(id='geographic-chart')
                    ])
                ], md=6)
            ])
        ])
    
    elif tab_id == 'sales-tab':
        return create_sales_summary(filtered_data)
    
    elif tab_id == 'products-tab':
        return create_product_summary(filtered_data)
    
    elif tab_id == 'customers-tab':
        return create_customer_summary(filtered_data)
    
    elif tab_id == 'geography-tab':
        return create_geographic_summary(filtered_data)
    
    return html.Div("Tab content not found")

def create_main_layout(start_date: datetime, end_date: datetime, 
                      countries: List[str], categories: List[str]) -> html.Div:
    """
    Create the main dashboard layout
    
    Args:
        start_date (datetime): Minimum date in the dataset
        end_date (datetime): Maximum date in the dataset
        countries (List[str]): List of available countries
        categories (List[str]): List of available product categories
        
    Returns:
        html.Div: Main dashboard layout
    """
    return html.Div([
        # Data Stores
        dcc.Store(id='filtered-data-store'),
        dcc.Store(id='selected-data-store'),
        
        # Header with Filters
        create_header(start_date, end_date, countries, categories),
        
        # Loading Component
        dcc.Loading(
            id="loading-component",
            type="default",
            children=[
                # Main Content Container
                dbc.Container([
                    # Navigation Tabs
                    dbc.Tabs(
                        id='main-tabs',
                        active_tab='overview-tab',
                        children=[
                            dbc.Tab(
                                label='Overview',
                                tab_id='overview-tab',
                                labelClassName='custom-tab',
                                activeLabelClassName='custom-tab-selected'
                            ),
                            dbc.Tab(
                                label='Sales Analysis',
                                tab_id='sales-tab',
                                labelClassName='custom-tab',
                                activeLabelClassName='custom-tab-selected'
                            ),
                            dbc.Tab(
                                label='Product Analysis',
                                tab_id='products-tab',
                                labelClassName='custom-tab',
                                activeLabelClassName='custom-tab-selected'
                            ),
                            dbc.Tab(
                                label='Customer Analysis',
                                tab_id='customers-tab',
                                labelClassName='custom-tab',
                                activeLabelClassName='custom-tab-selected'
                            ),
                            dbc.Tab(
                                label='Geographic Analysis',
                                tab_id='geography-tab',
                                labelClassName='custom-tab',
                                activeLabelClassName='custom-tab-selected'
                            )
                        ],
                        className="mb-4"
                    ),
                    
                    # Tab Content Container
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
            ]
        )
    ])

def create_error_layout(error_message: str) -> dbc.Container:
    """
    Create an error layout for when data loading fails
    
    Args:
        error_message (str): Error message to display
        
    Returns:
        dbc.Container: Error layout
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("Error Loading Dashboard", className="text-danger mb-4"),
                    html.P(error_message, className="lead"),
                    dbc.Button(
                        "Retry Loading",
                        id="retry-button",
                        color="primary",
                        className="mt-3"
                    )
                ], className="text-center py-5")
            ], md=8, className="offset-md-2")
        ])
    ], fluid=True, className="mt-5")

def create_loading_layout() -> dbc.Container:
    """
    Create a loading layout for initial data load
    
    Returns:
        dbc.Container: Loading layout
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Loading Dashboard...", className="mb-4"),
                    dbc.Spinner(size="lg", color="primary"),
                    html.P("Please wait while we load your data.", className="mt-4 text-muted")
                ], className="text-center py-5")
            ], md=8, className="offset-md-2")
        ])
    ], fluid=True, className="mt-5")

# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load the actual retail data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.load_data()
    
    if df is not None:
        # Get date range
        start_date = df['InvoiceDate'].min()
        end_date = df['InvoiceDate'].max()
        
        # Get unique values for filters
        countries = sorted(df['Country'].unique().tolist())
        categories = sorted(df['Category'].unique().tolist()) if 'Category' in df.columns else []
        
        # Create the layout
        layout = create_main_layout(start_date, end_date, countries, categories)
        print("Layout created successfully")