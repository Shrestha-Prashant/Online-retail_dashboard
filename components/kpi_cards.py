import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
from typing import Dict, Any
import json
from app import cache, kpi_card_style

def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"£{value:,.2f}"

def format_number(value: float) -> str:
    """Format value with thousand separators"""
    return f"{value:,.0f}"

def calculate_percentage_change(current: float, previous: float) -> tuple:
    """Calculate percentage change and determine if it's an increase"""
    if previous == 0:
        return 0, True
    change = ((current - previous) / previous) * 100
    return change, change >= 0

def get_trend_arrow(is_increase: bool) -> html.I:
    """Return trend arrow icon based on increase/decrease"""
    if is_increase:
        return html.I(className="fas fa-arrow-up text-success")
    return html.I(className="fas fa-arrow-down text-danger")

def create_kpi_card(title: str, value: str, trend: float, icon_class: str) -> dbc.Card:
    """Create a KPI card with title, value, and trend indicator"""
    is_increase = trend >= 0
    
    return dbc.Card(
        dbc.CardBody(
            [
                # Icon and Title Row
                dbc.Row(
                    [
                        dbc.Col(
                            html.I(className=f"{icon_class} fa-2x text-primary"),
                            width="auto"
                        ),
                        dbc.Col(
                            html.H6(title, className="mb-0 text-muted"),
                            className="ps-2"
                        )
                    ],
                    className="align-items-center mb-2"
                ),
                # Value Row
                dbc.Row(
                    dbc.Col(
                        html.H4(value, className="mb-0"),
                    ),
                    className="mb-2"
                ),
                # Trend Row
                dbc.Row(
                    dbc.Col(
                        [
                            get_trend_arrow(is_increase),
                            html.Span(
                                f" {abs(trend):.1f}%",
                                className=f"ms-1 {'text-success' if is_increase else 'text-danger'}"
                            ),
                            html.Span(" vs previous period", className="text-muted small ms-1")
                        ],
                        className="d-flex align-items-center"
                    )
                )
            ]
        ),
        style=kpi_card_style
    )

@cache.memoize(timeout=300)  # Cache for 5 minutes
def calculate_kpi_metrics(current_data: str, previous_data: str = None) -> Dict[str, Any]:
    """Calculate KPI metrics from current and previous period data"""
    # Parse JSON data
    df_current = pd.read_json(current_data, orient='split')
    df_previous = pd.read_json(previous_data, orient='split') if previous_data else None
    
    # Calculate current period metrics
    current_metrics = {
        'total_revenue': df_current['TotalAmount'].sum(),
        'total_orders': df_current['InvoiceNo'].nunique(),
        'avg_order_value': df_current['TotalAmount'].sum() / df_current['InvoiceNo'].nunique(),
        'total_customers': df_current['CustomerID'].nunique()
    }
    
    # Calculate previous period metrics for comparison
    if df_previous is not None:
        previous_metrics = {
            'total_revenue': df_previous['TotalAmount'].sum(),
            'total_orders': df_previous['InvoiceNo'].nunique(),
            'avg_order_value': df_previous['TotalAmount'].sum() / df_previous['InvoiceNo'].nunique(),
            'total_customers': df_previous['CustomerID'].nunique()
        }
        
        # Calculate trends
        trends = {
            key: calculate_percentage_change(current_metrics[key], previous_metrics[key])[0]
            for key in current_metrics.keys()
        }
    else:
        trends = {key: 0 for key in current_metrics.keys()}
    
    return {
        'metrics': current_metrics,
        'trends': trends
    }

def create_kpi_cards(current_data: str, previous_data: str = None) -> dbc.Row:
    """Create all KPI cards with data"""
    # Get metrics and trends
    kpi_data = calculate_kpi_metrics(current_data, previous_data)
    metrics = kpi_data['metrics']
    trends = kpi_data['trends']
    
    # Define KPI configurations
    kpi_configs = [
        {
            'title': 'Total Revenue',
            'value': format_currency(metrics['total_revenue']),
            'trend': trends['total_revenue'],
            'icon': 'fas fa-pound-sign'
        },
        {
            'title': 'Total Orders',
            'value': format_number(metrics['total_orders']),
            'trend': trends['total_orders'],
            'icon': 'fas fa-shopping-cart'
        },
        {
            'title': 'Average Order Value',
            'value': format_currency(metrics['avg_order_value']),
            'trend': trends['avg_order_value'],
            'icon': 'fas fa-receipt'
        },
        {
            'title': 'Total Customers',
            'value': format_number(metrics['total_customers']),
            'trend': trends['total_customers'],
            'icon': 'fas fa-users'
        }
    ]
    
    # Create cards
    return dbc.Row(
        [
            dbc.Col(
                create_kpi_card(
                    config['title'],
                    config['value'],
                    config['trend'],
                    config['icon']
                ),
                md=3,
                sm=6,
                className="mb-4"
            )
            for config in kpi_configs
        ]
    )

# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load and process the data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.process_data()
    
    # Create the KPI cards
    kpi_cards = create_kpi_cards(df.to_json(date_format='iso', orient='split'))