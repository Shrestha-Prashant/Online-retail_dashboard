from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from typing import Tuple, List

def create_date_range_filter(start_date: datetime, end_date: datetime) -> dcc.DatePickerRange:
    """
    Create a date range picker component
    """
    return dcc.DatePickerRange(
        id='date-filter',
        min_date_allowed=start_date,
        max_date_allowed=end_date,
        start_date=start_date,
        end_date=end_date,
        display_format='MMMM D, YYYY',
        style={'zIndex': 1000}  # Ensure dropdown appears above other elements
    )

def create_country_filter(countries: List[str]) -> dcc.Dropdown:
    """
    Create a country selection dropdown
    """
    return dcc.Dropdown(
        id='country-filter',
        options=[{'label': country, 'value': country} for country in sorted(countries)],
        value=[],  # Default to all countries
        multi=True,
        placeholder='Select Countries...',
        style={'minWidth': '200px'}
    )

def create_category_filter(categories: List[str]) -> dcc.Dropdown:
    """
    Create a product category dropdown
    """
    return dcc.Dropdown(
        id='category-filter',
        options=[{'label': cat, 'value': cat} for cat in sorted(categories)],
        value=[],  # Default to all categories
        multi=True,
        placeholder='Select Categories...',
        style={'minWidth': '200px'}
    )

def create_header(start_date: datetime, end_date: datetime, 
                 countries: List[str], categories: List[str]) -> html.Div:
    """
    Create the main dashboard header with filters and navigation
    """
    return html.Div([
        # Top navigation bar
        dbc.Navbar(
            dbc.Container([
                # Logo and Title
                dbc.Row([
                    dbc.Col(
                        html.Img(
                            src="/assets/logo.png",
                            height="40px",
                            className="me-2"
                        ),
                        width="auto"
                    ),
                    dbc.Col(
                        html.H3(
                            "Online Retail Dashboard",
                            className="mb-0 text-white"
                        ),
                        width="auto"
                    )
                ], align="center"),

                # Navigation Links
                dbc.Row([
                    dbc.Nav([
                        dbc.NavLink("Overview", href="/", active="exact"),
                        dbc.NavLink("Sales Analysis", href="/sales", active="exact"),
                        dbc.NavLink("Products", href="/products", active="exact"),
                        dbc.NavLink("Customers", href="/customers", active="exact"),
                        dbc.NavLink("Geography", href="/geography", active="exact")
                    ], className="ml-auto")
                ])
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-3"
        ),

        # Filters section
        dbc.Container([
            dbc.Row([
                # Date Range Filter
                dbc.Col([
                    html.Label("Date Range", className="mb-2"),
                    create_date_range_filter(start_date, end_date)
                ], md=4, className="mb-3"),

                # Country Filter
                dbc.Col([
                    html.Label("Countries", className="mb-2"),
                    create_country_filter(countries)
                ], md=4, className="mb-3"),

                # Category Filter
                dbc.Col([
                    html.Label("Product Categories", className="mb-2"),
                    create_category_filter(categories)
                ], md=4, className="mb-3")
            ], className="g-3 mb-3"),

            # Quick Date Range Buttons
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Last 30 Days", id="last-30-days", color="secondary", size="sm", className="me-2"),
                        dbc.Button("Last Quarter", id="last-quarter", color="secondary", size="sm", className="me-2"),
                        dbc.Button("Year to Date", id="ytd", color="secondary", size="sm", className="me-2"),
                        dbc.Button("All Time", id="all-time", color="secondary", size="sm")
                    ])
                ])
            ], className="mb-4")
        ], fluid=True)
    ])

def create_loading_component() -> dcc.Loading:
    """
    Create a loading spinner for data loading states
    """
    return dcc.Loading(
        id="loading",
        type="default",
        children=html.Div(id="loading-output")
    )

# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load data to get date range and filter options
    loader = RetailDataLoader("data/raw/Online_Retail.xlsx")
    df = loader.process_data()
    
    # Get date range
    start_date = df['InvoiceDate'].min()
    end_date = df['InvoiceDate'].max()
    
    # Get unique countries and categories
    countries = df['Country'].unique().tolist()
    categories = df['Category'].unique().tolist() if 'Category' in df.columns else []
    
    # Create header component
    header = create_header(start_date, end_date, countries, categories)