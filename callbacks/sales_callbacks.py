from dash.dependencies import Input, Output, State
from dash import callback_context
import dash
from app import app, cache
import pandas as pd
from components.sales_charts import (
    create_sales_summary,
    create_sales_trend_chart,
    create_sales_by_category,
    create_hourly_sales_pattern,
    create_metrics_table
)
from components.kpi_cards import create_kpi_cards
from datetime import datetime, timedelta

@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filtered-data-store', 'data')]
)
def update_sales_tab(active_tab, filtered_data):
    """
    Update the sales tab content based on selected tab and filtered data
    
    Args:
        active_tab: Currently active tab
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Sales tab content if active, None otherwise
    """
    if active_tab == 'sales-tab':
        return create_sales_summary(filtered_data)
    return None

@app.callback(
    Output('kpi-cards', 'children'),
    [Input('filtered-data-store', 'data')]
)
def update_kpi_cards(filtered_data):
    """
    Update KPI cards with current period vs previous period comparison
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Updated KPI cards component
    """
    if filtered_data is None:
        return []
    
    # Get current period data
    df = pd.read_json(filtered_data, orient='split')
    
    # Calculate date range for comparison
    date_range = (df['InvoiceDate'].max() - df['InvoiceDate'].min()).days
    end_date = df['InvoiceDate'].min()
    start_date = end_date - pd.Timedelta(days=date_range)
    
    # Get previous period data
    prev_mask = (df['InvoiceDate'] >= start_date) & (df['InvoiceDate'] < end_date)
    prev_data = df[prev_mask].to_json(date_format='iso', orient='split')
    
    return create_kpi_cards(filtered_data, prev_data)

@app.callback(
    Output('sales-trend-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('trend-interval-selector', 'value')]
)
def update_sales_trend(filtered_data, interval):
    """
    Update sales trend chart based on selected interval
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        interval: Selected time interval ('D', 'W', 'M')
        
    Returns:
        Updated sales trend chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Group data by selected interval
    if interval == 'D':
        grouped = df.groupby(df['InvoiceDate'].dt.date)
    elif interval == 'W':
        grouped = df.groupby(pd.Grouper(key='InvoiceDate', freq='W'))
    else:  # Monthly
        grouped = df.groupby(pd.Grouper(key='InvoiceDate', freq='M'))
    
    # Aggregate metrics
    trend_data = grouped.agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    return create_sales_trend_chart(trend_data)

@app.callback(
    Output('sales-by-category-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('category-metric-selector', 'value')]
)
def update_category_sales(filtered_data, metric):
    """
    Update sales by category chart based on selected metric
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        metric: Selected metric ('revenue', 'orders', 'customers')
        
    Returns:
        Updated category sales chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Group by category and calculate metrics
    category_metrics = df.groupby('Category').agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    return create_sales_by_category(category_metrics, metric)

@app.callback(
    Output('hourly-sales-pattern', 'children'),
    [Input('filtered-data-store', 'data')]
)
def update_hourly_pattern(filtered_data):
    """
    Update hourly sales pattern chart
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Updated hourly pattern chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Create hour and day of week fields
    hourly_pattern = df.groupby(['DayOfWeek', 'Hour']).agg({
        'TotalAmount': 'sum'
    }).reset_index()
    
    return create_hourly_sales_pattern(hourly_pattern)

@app.callback(
    Output('sales-metrics-table', 'children'),
    [Input('filtered-data-store', 'data')]
)
def update_sales_metrics(filtered_data):
    """
    Update detailed sales metrics table
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Updated sales metrics table
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Calculate detailed metrics
    metrics = {
        'Total Revenue': df['TotalAmount'].sum(),
        'Total Orders': df['InvoiceNo'].nunique(),
        'Average Order Value': df['TotalAmount'].sum() / df['InvoiceNo'].nunique(),
        'Total Customers': df['CustomerID'].nunique(),
        'Items per Order': df.groupby('InvoiceNo')['Quantity'].sum().mean(),
        'Revenue per Customer': df['TotalAmount'].sum() / df['CustomerID'].nunique()
    }
    
    return create_metrics_table(metrics)