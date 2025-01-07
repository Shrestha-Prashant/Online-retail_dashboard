from dash.dependencies import Input, Output, State
from dash import callback_context
import dash
from app import app, cache
import pandas as pd
import numpy as np
from components.product_charts import (
    create_product_summary,
    create_top_products_chart,
    create_product_trends_chart,
    create_product_correlation_chart,
    create_category_performance_chart,
    create_product_details_table
)
from datetime import datetime, timedelta

@app.callback(
    Output('product-tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filtered-data-store', 'data')]
)
def update_product_tab(active_tab, filtered_data):
    """
    Update the product tab content based on selected tab and filtered data
    
    Args:
        active_tab: Currently active tab
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Product tab content if active, None otherwise
    """
    if active_tab == 'products-tab':
        return create_product_summary(filtered_data)
    return None

@app.callback(
    Output('top-products-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('product-metric-selector', 'value'),
     Input('top-n-selector', 'value')]
)
def update_top_products(filtered_data, metric, top_n):
    """
    Update top products chart based on selected metric and number of products
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        metric: Selected metric ('revenue', 'quantity', 'orders')
        top_n: Number of top products to display
        
    Returns:
        Updated top products chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Aggregate product metrics
    product_metrics = df.groupby(['StockCode', 'Description']).agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    # Sort based on selected metric
    if metric == 'revenue':
        product_metrics = product_metrics.nlargest(top_n, 'TotalAmount')
    elif metric == 'quantity':
        product_metrics = product_metrics.nlargest(top_n, 'Quantity')
    else:  # orders
        product_metrics = product_metrics.nlargest(top_n, 'InvoiceNo')
    
    return create_top_products_chart(product_metrics, metric)

@app.callback(
    Output('product-trends-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('selected-products', 'value'),
     Input('trend-type-selector', 'value')]
)
def update_product_trends(filtered_data, selected_products, trend_type):
    """
    Update product trends chart based on selected products and trend type
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        selected_products: List of selected product codes
        trend_type: Type of trend to display ('daily', 'weekly', 'monthly')
        
    Returns:
        Updated product trends chart
    """
    if filtered_data is None or not selected_products:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Filter for selected products
    df = df[df['StockCode'].isin(selected_products)]
    
    # Group by time period and product
    if trend_type == 'daily':
        grouped = df.groupby([pd.Grouper(key='InvoiceDate', freq='D'), 'StockCode'])
    elif trend_type == 'weekly':
        grouped = df.groupby([pd.Grouper(key='InvoiceDate', freq='W'), 'StockCode'])
    else:  # monthly
        grouped = df.groupby([pd.Grouper(key='InvoiceDate', freq='M'), 'StockCode'])
    
    trend_data = grouped.agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    return create_product_trends_chart(trend_data)

@app.callback(
    Output('product-correlation-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('correlation-threshold', 'value')]
)
def update_product_correlation(filtered_data, threshold):
    """
    Update product correlation chart based on purchase patterns
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        threshold: Correlation threshold for displaying relationships
        
    Returns:
        Updated product correlation chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Create purchase matrix (which products are bought together)
    purchase_matrix = pd.crosstab(
        df['InvoiceNo'],
        df['StockCode']
    )
    
    # Calculate correlation matrix
    corr_matrix = purchase_matrix.corr()
    
    # Filter correlations above threshold
    strong_correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) >= threshold:
                strong_correlations.append({
                    'Product1': corr_matrix.index[i],
                    'Product2': corr_matrix.columns[j],
                    'Correlation': corr_matrix.iloc[i, j]
                })
    
    correlation_df = pd.DataFrame(strong_correlations)
    
    return create_product_correlation_chart(correlation_df)

@app.callback(
    Output('category-performance-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('category-metric-selector', 'value')]
)
def update_category_performance(filtered_data, metric):
    """
    Update category performance chart based on selected metric
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        metric: Selected metric ('revenue', 'quantity', 'orders', 'customers')
        
    Returns:
        Updated category performance chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Calculate category metrics
    category_metrics = df.groupby('Category').agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    # Calculate additional metrics
    category_metrics['AvgOrderValue'] = (category_metrics['TotalAmount'] / 
                                       category_metrics['InvoiceNo'])
    category_metrics['ItemsPerOrder'] = (category_metrics['Quantity'] / 
                                       category_metrics['InvoiceNo'])
    
    return create_category_performance_chart(category_metrics, metric)

@app.callback(
    Output('product-details-table', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('product-selector', 'value')]
)
def update_product_details(filtered_data, selected_product):
    """
    Update detailed product metrics table for selected product
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        selected_product: Selected product code
        
    Returns:
        Updated product details table
    """
    if filtered_data is None or not selected_product:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Filter for selected product
    product_df = df[df['StockCode'] == selected_product]
    
    # Calculate detailed metrics
    metrics = {
        'Total Revenue': product_df['TotalAmount'].sum(),
        'Total Quantity Sold': product_df['Quantity'].sum(),
        'Number of Orders': product_df['InvoiceNo'].nunique(),
        'Unique Customers': product_df['CustomerID'].nunique(),
        'Average Order Quantity': product_df.groupby('InvoiceNo')['Quantity'].sum().mean(),
        'Average Unit Price': product_df['UnitPrice'].mean(),
        'First Sale Date': product_df['InvoiceDate'].min(),
        'Last Sale Date': product_df['InvoiceDate'].max()
    }
    
    return create_product_details_table(metrics)