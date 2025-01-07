from dash.dependencies import Input, Output, State
from dash import callback_context
import dash
from app import app
import pandas as pd
from datetime import datetime, timedelta
from utils.date_helpers import get_last_n_days, get_last_n_months, get_year_to_date

@app.callback(
    Output('filtered-data-store', 'data'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('country-filter', 'value'),
     Input('category-filter', 'value'),
     Input('last-30-days', 'n_clicks'),
     Input('last-quarter', 'n_clicks'),
     Input('ytd', 'n_clicks'),
     Input('all-time', 'n_clicks')],
    [State('filtered-data-store', 'data')]
)
def update_filtered_data(start_date, end_date, countries, categories, 
                        last_30_days, last_quarter, ytd, all_time, current_data):
    """
    Update the filtered dataset based on selected filters
    
    Args:
        start_date: Selected start date
        end_date: Selected end date
        countries: List of selected countries
        categories: List of selected categories
        last_30_days: n_clicks for last 30 days button
        last_quarter: n_clicks for last quarter button
        ytd: n_clicks for year to date button
        all_time: n_clicks for all time button
        current_data: Current data in the store
        
    Returns:
        JSON string of filtered DataFrame
    """
    ctx = callback_context
    if not ctx.triggered:
        return current_data
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Load current data
    df = pd.read_json(current_data, orient='split')
    
    # Handle quick date range buttons
    if triggered_id == 'last-30-days':
        start_date, end_date = get_last_n_days(30, df['InvoiceDate'].max())
    elif triggered_id == 'last-quarter':
        start_date, end_date = get_last_n_months(3, df['InvoiceDate'].max())
    elif triggered_id == 'ytd':
        start_date, end_date = get_year_to_date()
    elif triggered_id == 'all-time':
        start_date = df['InvoiceDate'].min()
        end_date = df['InvoiceDate'].max()
    
    # Apply date filter
    mask = (df['InvoiceDate'] >= start_date) & (df['InvoiceDate'] <= end_date)
    
    # Apply country filter
    if countries and len(countries) > 0:
        mask &= df['Country'].isin(countries)
    
    # Apply category filter if exists
    if categories and len(categories) > 0 and 'Category' in df.columns:
        mask &= df['Category'].isin(categories)
    
    filtered_df = df[mask]
    
    return filtered_df.to_json(date_format='iso', orient='split')

@app.callback(
    [Output('date-filter', 'start_date'),
     Output('date-filter', 'end_date')],
    [Input('last-30-days', 'n_clicks'),
     Input('last-quarter', 'n_clicks'),
     Input('ytd', 'n_clicks'),
     Input('all-time', 'n_clicks')],
    [State('filtered-data-store', 'data')]
)
def update_date_picker(last_30_days, last_quarter, ytd, all_time, current_data):
    """
    Update date picker based on quick filter buttons
    
    Args:
        last_30_days: n_clicks for last 30 days button
        last_quarter: n_clicks for last quarter button
        ytd: n_clicks for year to date button
        all_time: n_clicks for all time button
        current_data: Current data in the store
        
    Returns:
        Tuple of (start_date, end_date)
    """
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    df = pd.read_json(current_data, orient='split')
    
    if triggered_id == 'last-30-days':
        start_date, end_date = get_last_n_days(30, df['InvoiceDate'].max())
    elif triggered_id == 'last-quarter':
        start_date, end_date = get_last_n_months(3, df['InvoiceDate'].max())
    elif triggered_id == 'ytd':
        start_date, end_date = get_year_to_date()
    elif triggered_id == 'all-time':
        start_date = df['InvoiceDate'].min()
        end_date = df['InvoiceDate'].max()
    else:
        return dash.no_update, dash.no_update
    
    return start_date, end_date

@app.callback(
    [Output('country-filter', 'options'),
     Output('category-filter', 'options')],
    [Input('filtered-data-store', 'data')]
)
def update_filter_options(filtered_data):
    """
    Update filter dropdown options based on filtered data
    
    Args:
        filtered_data: JSON string of filtered DataFrame
        
    Returns:
        Tuple of (country_options, category_options)
    """
    if filtered_data is None:
        return [], []
    
    df = pd.read_json(filtered_data, orient='split')
    
    # Get unique countries
    countries = sorted(df['Country'].unique())
    country_options = [{'label': country, 'value': country} for country in countries]
    
    # Get unique categories if they exist
    if 'Category' in df.columns:
        categories = sorted(df['Category'].unique())
        category_options = [{'label': cat, 'value': cat} for cat in categories]
    else:
        category_options = []
    
    return country_options, category_options