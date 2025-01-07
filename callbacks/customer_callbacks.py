from dash.dependencies import Input, Output, State
from dash import callback_context
import dash
from app import app, cache
import pandas as pd
import numpy as np
from components.customer_charts import (
    create_customer_summary,
    calculate_rfm_scores,
    create_rfm_distribution_chart,
    create_lifecycle_chart,
    create_cohort_chart,
    create_segment_chart,
    create_customer_details_table
)
from datetime import datetime, timedelta

@app.callback(
    Output('customer-tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filtered-data-store', 'data')]
)
def update_customer_tab(active_tab, filtered_data):
    """
    Update the customer tab content based on selected tab and filtered data
    
    Args:
        active_tab: Currently active tab
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Customer tab content if active, None otherwise
    """
    if active_tab == 'customers-tab':
        return create_customer_summary(filtered_data)
    return None

@app.callback(
    Output('rfm-distribution-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('rfm-segment-selector', 'value')]
)
def update_rfm_distribution(filtered_data, selected_segments):
    """
    Update RFM distribution chart based on selected segments
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        selected_segments: List of selected customer segments
        
    Returns:
        Updated RFM distribution chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Calculate RFM scores and segments
    rfm_df = calculate_rfm_scores(df)
    
    # Filter for selected segments if any
    if selected_segments and len(selected_segments) > 0:
        rfm_df = rfm_df[rfm_df['Customer_Segment'].isin(selected_segments)]
    
    return create_rfm_distribution_chart(rfm_df)

@app.callback(
    Output('customer-lifecycle-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('lifecycle-metric-selector', 'value')]
)
def update_customer_lifecycle(filtered_data, metric):
    """
    Update customer lifecycle chart based on selected metric
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        metric: Selected metric ('orders', 'revenue', 'frequency')
        
    Returns:
        Updated customer lifecycle chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Calculate customer age and metrics
    customer_metrics = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (x.max() - x.min()).days,  # Customer age
        'InvoiceNo': 'nunique',  # Number of orders
        'TotalAmount': 'sum',    # Total revenue
    }).reset_index()
    
    customer_metrics.columns = ['CustomerID', 'Age', 'Orders', 'Revenue']
    customer_metrics['OrderFrequency'] = customer_metrics['Orders'] / customer_metrics['Age']
    
    return create_lifecycle_chart(customer_metrics, metric)

@app.callback(
    Output('customer-cohort-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('cohort-metric-selector', 'value')]
)
def update_cohort_analysis(filtered_data, metric):
    """
    Update customer cohort analysis chart
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        metric: Selected metric ('retention', 'revenue', 'frequency')
        
    Returns:
        Updated cohort analysis chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Get customer's first purchase month
    customer_first_purchase = df.groupby('CustomerID')['InvoiceDate'].min().reset_index()
    customer_first_purchase['CohortMonth'] = customer_first_purchase['InvoiceDate'].dt.to_period('M')
    
    # Merge with main dataframe
    df = df.merge(customer_first_purchase[['CustomerID', 'CohortMonth']], on='CustomerID')
    
    # Calculate months since first purchase
    df['MonthsFromFirstPurchase'] = ((df['InvoiceDate'].dt.to_period('M') - 
                                     df['CohortMonth']).astype(int))
    
    # Create cohort matrix
    if metric == 'retention':
        cohort_data = pd.crosstab(df['CohortMonth'], 
                                 df['MonthsFromFirstPurchase'],
                                 values=df['CustomerID'],
                                 aggfunc='nunique')
    elif metric == 'revenue':
        cohort_data = pd.crosstab(df['CohortMonth'], 
                                 df['MonthsFromFirstPurchase'],
                                 values=df['TotalAmount'],
                                 aggfunc='sum')
    else:  # frequency
        cohort_data = pd.crosstab(df['CohortMonth'], 
                                 df['MonthsFromFirstPurchase'],
                                 values=df['InvoiceNo'],
                                 aggfunc='nunique')
    
    # Calculate retention percentages
    cohort_sizes = cohort_data[0]
    cohort_data = cohort_data.div(cohort_sizes, axis=0) * 100
    
    return create_cohort_chart(cohort_data, metric)

@app.callback(
    Output('customer-segments-chart', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('segmentation-metric-selector', 'value')]
)
def update_customer_segments(filtered_data, metric):
    """
    Update customer segmentation chart based on selected metric
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        metric: Selected metric for segmentation analysis
        
    Returns:
        Updated customer segmentation chart
    """
    if filtered_data is None:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    rfm_df = calculate_rfm_scores(df)
    
    # Calculate segment metrics
    segment_metrics = df.merge(
        rfm_df[['CustomerID', 'Customer_Segment']], 
        on='CustomerID'
    ).groupby('Customer_Segment').agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    return create_segment_chart(segment_metrics, metric)

@app.callback(
    Output('customer-details-table', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('customer-selector', 'value')]
)
def update_customer_details(filtered_data, selected_customer):
    """
    Update detailed customer metrics table for selected customer
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        selected_customer: Selected customer ID
        
    Returns:
        Updated customer details table
    """
    if filtered_data is None or not selected_customer:
        return None
        
    df = pd.read_json(filtered_data, orient='split')
    
    # Filter for selected customer
    customer_df = df[df['CustomerID'] == selected_customer]
    
    # Calculate customer metrics
    metrics = {
        'Total Spend': customer_df['TotalAmount'].sum(),
        'Number of Orders': customer_df['InvoiceNo'].nunique(),
        'Total Items Purchased': customer_df['Quantity'].sum(),
        'Average Order Value': customer_df['TotalAmount'].sum() / customer_df['InvoiceNo'].nunique(),
        'First Purchase Date': customer_df['InvoiceDate'].min(),
        'Last Purchase Date': customer_df['InvoiceDate'].max(),
        'Days Since Last Purchase': (df['InvoiceDate'].max() - customer_df['InvoiceDate'].max()).days,
        'Favorite Category': customer_df.groupby('Category')['Quantity'].sum().idxmax()
    }
    
    return create_customer_details_table(metrics)