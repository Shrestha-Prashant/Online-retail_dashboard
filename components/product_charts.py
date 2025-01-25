import pandas as pd
import plotly.express as px
from typing import Dict, List, Any
import plotly.graph_objects as go
from dash import html, dcc
from datetime import datetime
import dash_bootstrap_components as dbc
from app import cache, chart_colors, plot_template
import numpy as np
import multiprocessing
from joblib import Parallel, delayed
import networkx as nx
import scipy
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64


def create_top_products_chart(filtered_data: str) -> dbc.Card:
    """
    Create a chart showing top products by revenue and quantity
    """
    df = pd.read_json(filtered_data, orient='split')
    
    # Aggregate product data
    product_metrics = df.groupby(['StockCode', 'Description']).agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    
    # Get top 10 products by revenue
    top_products = product_metrics.nlargest(10, 'TotalAmount')
    
    # Create the figure
    fig = go.Figure()
    
    # Add revenue bars
    fig.add_trace(
        go.Bar(
            y=top_products['Description'],
            x=top_products['TotalAmount'],
            name='Revenue',
            orientation='h',
            marker_color=chart_colors[0]
        )
    )
    
    # Add quantity line
    fig.add_trace(
        go.Scatter(
            y=top_products['Description'],
            x=top_products['Quantity'],
            name='Quantity',
            orientation='h',
            mode='markers+lines',
            marker=dict(color=chart_colors[1], size=10),
            xaxis='x2'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Top 10 Products by Revenue',
        template=plot_template,
        xaxis=dict(
            title='Revenue (£)',
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0]),
            side='bottom'
        ),
        xaxis2=dict(
            title='Quantity Sold',
            titlefont=dict(color=chart_colors[1]),
            tickfont=dict(color=chart_colors[1]),
            anchor='y',
            overlaying='x',
            side='top'
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=200, r=100, t=100, b=60),
        height=500
    )
    
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_product_trends_chart(filtered_data: str) -> dbc.Card:
    """
    Create a chart showing overall product sales trends over time
    """
    try:
        # Read the JSON data
        df = pd.read_json(filtered_data, orient='split')
        
        # Convert InvoiceDate to datetime
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Create MonthYear column
        df['MonthYear'] = df['InvoiceDate'].dt.strftime('%Y-%m')
        
        # Aggregate by month
        monthly_trends = df.groupby('MonthYear').agg({
            'TotalAmount': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        # Sort by MonthYear
        monthly_trends = monthly_trends.sort_values('MonthYear')
        
        # Create line chart
        fig = go.Figure()
        
        # Add Revenue line
        fig.add_trace(
            go.Scatter(
                x=monthly_trends['MonthYear'],
                y=monthly_trends['TotalAmount'],
                name='Revenue',
                line=dict(color=chart_colors[0], width=2),
                hovertemplate='Revenue: £%{y:,.2f}<extra></extra>'
            )
        )
        
        # Add Order Count line on secondary y-axis
        fig.add_trace(
            go.Scatter(
                x=monthly_trends['MonthYear'],
                y=monthly_trends['InvoiceNo'],
                name='Orders',
                line=dict(color=chart_colors[1], width=2),
                yaxis='y2',
                hovertemplate='Orders: %{y:,.0f}<extra></extra>'
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Monthly Sales and Order Trends',
            template=plot_template,
            xaxis_title='Month',
            yaxis=dict(
                title='Revenue (£)',
                titlefont=dict(color=chart_colors[0]),
                tickfont=dict(color=chart_colors[0])
            ),
            yaxis2=dict(
                title='Number of Orders',
                titlefont=dict(color=chart_colors[1]),
                tickfont=dict(color=chart_colors[1]),
                anchor='x',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            margin=dict(l=60, r=60, t=80, b=60),
            xaxis=dict(
                tickangle=45,
                type='category'
            ),
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        return dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig)
            ])
        )
        
    except Exception as e:
        print(f"Error creating product trends chart: {str(e)}")
        return dbc.Card(
            dbc.CardBody([
                html.H5("Unable to load product trends", className="text-danger"),
                html.P(f"Error: {str(e)}", className="text-muted")
            ])
        )

# def create_product_correlation_chart(filtered_data: str) -> dbc.Card:
#     """
#     Create a chart showing product correlations based on purchase patterns
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     # Create purchase matrix (which products are bought together)
#     purchase_matrix = pd.crosstab(
#         df['InvoiceNo'],
#         df['Description']
#     )
    
#     # Calculate correlation matrix
#     corr_matrix = purchase_matrix.corr()
    
#     # Get top correlated product pairs
#     correlations = []
#     for i in range(len(corr_matrix.columns)):
#         for j in range(i+1, len(corr_matrix.columns)):
#             correlations.append({
#                 'Product1': corr_matrix.index[i],
#                 'Product2': corr_matrix.columns[j],
#                 'Correlation': corr_matrix.iloc[i, j]
#             })
    
#     # Convert to DataFrame and get top correlations
#     corr_df = pd.DataFrame(correlations)
#     top_correlations = corr_df.nlargest(10, 'Correlation')
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add correlation bars
#     fig.add_trace(
#         go.Bar(
#             y=[f"{row['Product1']} & {row['Product2']}" for _, row in top_correlations.iterrows()],
#             x=top_correlations['Correlation'],
#             orientation='h',
#             marker_color=chart_colors[0]
#         )
#     )
    
#     # Update layout
#     fig.update_layout(
#         title='Top Product Correlations',
#         template=plot_template,
#         xaxis_title='Correlation Coefficient',
#         showlegend=False,
#         margin=dict(l=300, r=40, t=80, b=60),
#         height=500
#     )
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig)
#         ])
#     )


# def compute_product_correlations(purchase_matrix_chunk):
#     """
#     Compute correlations for a chunk of the purchase matrix
    
#     Args:
#         purchase_matrix_chunk (pd.DataFrame): A subset of the purchase matrix
    
#     Returns:
#         pd.DataFrame: Correlation matrix for the chunk
#     """
#     try:
#         return purchase_matrix_chunk.corr(method='pearson')
#     except Exception as e:
#         print(f"Error in correlation computation: {e}")
#         return pd.DataFrame()

def compute_product_correlations(purchase_matrix_chunk):
    """
    Compute correlations for a chunk of the purchase matrix
    
    Args:
        purchase_matrix_chunk (pd.DataFrame): A subset of the purchase matrix
    
    Returns:
        pd.DataFrame: Correlation matrix for the chunk
    """
    try:
        return purchase_matrix_chunk.corr(method='pearson')
    except Exception as e:
        print(f"Error in correlation computation: {e}")
        return pd.DataFrame()
    
def compute_product_correlations(purchase_matrix_chunk):
    """
    Compute correlations for a chunk of the purchase matrix
    
    Args:
        purchase_matrix_chunk (pd.DataFrame): A subset of the purchase matrix
    
    Returns:
        pd.DataFrame: Correlation matrix for the chunk
    """
    try:
        return purchase_matrix_chunk.corr(method='pearson')
    except Exception as e:
        print(f"Error in correlation computation: {e}")
        return pd.DataFrame()

def create_product_correlation_chart(filtered_data: str) -> dbc.Card:
    """
    Create a chart showing product correlations based on purchase patterns
    with parallel processing for improved performance
    
    Args:
        filtered_data (str): JSON-formatted purchase data
    
    Returns:
        dbc.Card: Plotly visualization of product correlations
    """
    try:
        # Load the data
        df = pd.read_json(filtered_data, orient='split')
        
        # Prepare purchase matrix
        # Group by InvoiceNo and Description, then pivot to create binary purchase matrix
        purchase_matrix = df.groupby(['InvoiceNo', 'Description']).size().unstack(fill_value=0)
        purchase_matrix = (purchase_matrix > 0).astype(int)
        
        # Parallel correlation computation
        num_cores = multiprocessing.cpu_count()
        
        # Split the purchase matrix into chunks for parallel processing
        matrix_chunks = np.array_split(purchase_matrix, num_cores)
        
        # Compute correlations in parallel
        correlation_results = Parallel(n_jobs=num_cores)(
            delayed(compute_product_correlations)(chunk) 
            for chunk in matrix_chunks
        )
        
        # Combine correlation results
        # Use the first result as a base and merge others
        corr_matrix = correlation_results[0]
        for result in correlation_results[1:]:
            corr_matrix = corr_matrix.combine_first(result)
        
        # Create a mask to remove self-correlations and redundant pairs
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        # Gather correlations, removing self and duplicate correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                correlations.append({
                    'Product1': corr_matrix.index[i],
                    'Product2': corr_matrix.columns[j],
                    'Correlation': corr_matrix.iloc[i, j]
                })
        
        # Convert to DataFrame and filter correlations
        corr_df = pd.DataFrame(correlations)
        
        # Filter out weak correlations 
        significant_correlations = corr_df[
            (corr_df['Correlation'].abs() > 0.3) & 
            (corr_df['Correlation'] != 1.0)
        ]
        
        # Sort by absolute correlation
        top_correlations = significant_correlations.sort_values(
            by='Correlation', 
            key=abs, 
            ascending=False
        ).head(15)
        
        # Create color scale that shows variation
        # Blue for positive, Red for negative correlations
        colors = top_correlations['Correlation'].apply(
            lambda x: 'blue' if x > 0 else 'red'
        )
        color_intensities = np.abs(top_correlations['Correlation'])
        
        # Create the figure
        fig = go.Figure()
        
        # # Add correlation bars with color intensity
        # fig.add_trace(
        #     go.Bar(
        #         y=[f"{row['Product1']} & {row['Product2']}" for _, row in top_correlations.iterrows()],
        #         x=top_correlations['Correlation'],
        #         orientation='h',
        #         marker=dict(
        #             color=[f'rgba({"0,0,255" if c=="blue" else "255,0,0"}, {intensity*0.8})' 
        #                    for c, intensity in zip(colors, color_intensities)],
        #         ),
        #         hovertemplate='Products: %{y}<br>Correlation: %{x:.2f}<extra></extra>'
        #     )
        # )
        
        # # Update layout
        # fig.update_layout(
        #     title={
        #         'text': 'Top Product Correlations',
        #         'x': 0.5,
        #         'xanchor': 'center'
        #     },
        #     template='plotly_white',
        #     xaxis_title='Correlation Coefficient',
        #     xaxis=dict(
        #         tickmode='linear',
        #         tick0=top_correlations['Correlation'].min(),
        #         dtick=(top_correlations['Correlation'].max() - top_correlations['Correlation'].min()) / 5
        #     ),
        #     showlegend=False,
        #     margin=dict(l=300, r=40, t=80, b=60),
        #     height=500
        # )
        # Add correlation bars with color intensity
        fig.add_trace(
            go.Bar(
                y=[f"{row['Product1']} & {row['Product2']}" for _, row in top_correlations.iterrows()],
                x=top_correlations['Correlation'],
                orientation='h',
                marker=dict(
                    color=[f'rgba({"0,0,255" if c=="blue" else "255,0,0"}, {intensity*0.8})' 
                        for c, intensity in zip(colors, color_intensities)],
                ),
                hovertemplate='Products: %{y}<br>Correlation: %{x:.2f}<extra></extra>',
                text=[f"{row['Correlation']:.2f}" for _, row in top_correlations.iterrows()],
                textposition='outside'
            )
        )

        # Update layout to improve readability
        fig.update_layout(
            title={
                'text': 'Top Product Correlations',
                'x': 0.5,
                'xanchor': 'center'
            },
            template='plotly_white',
            xaxis_title='Correlation Coefficient',
            xaxis=dict(
                tickmode='linear',
                tick0=top_correlations['Correlation'].min(),
                dtick=(top_correlations['Correlation'].max() - top_correlations['Correlation'].min()) / 5
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(top_correlations))),
                ticktext=[f"{row['Product1']} & {row['Product2']}" for _, row in top_correlations.iterrows()],
                tickangle=0
            ),
            showlegend=False,
            margin=dict(l=300, r=40, t=80, b=60),
            height=500
        )
        
        return dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig)
            ])
        )
    
    except Exception as e:
        return dbc.Card(
            dbc.CardBody([
                html.P(f"Error creating product correlation chart: {str(e)}", 
                       className="text-danger text-center")
            ])
        )


# def create_product_correlation_chart(filtered_data: str) -> dbc.Card:
#     """
#     Create a chart showing product correlations based on purchase patterns
#     with parallel processing for improved performance
    
#     Args:
#         filtered_data (str): JSON-formatted purchase data
    
#     Returns:
#         dbc.Card: Plotly visualization of product correlations
#     """
#     try:
#         # Load the data
#         df = pd.read_json(filtered_data, orient='split')
        
#         # Prepare purchase matrix
#         # Group by InvoiceNo and Description, then pivot to create binary purchase matrix
#         purchase_matrix = df.groupby(['InvoiceNo', 'Description']).size().unstack(fill_value=0)
#         purchase_matrix = (purchase_matrix > 0).astype(int)
        
#         # Parallel correlation computation
#         num_cores = multiprocessing.cpu_count()
        
#         # Split the purchase matrix into chunks for parallel processing
#         matrix_chunks = np.array_split(purchase_matrix, num_cores)
        
#         # Compute correlations in parallel
#         correlation_results = Parallel(n_jobs=num_cores)(
#             delayed(compute_product_correlations)(chunk) 
#             for chunk in matrix_chunks
#         )
        
#         # Combine correlation results
#         # Use the first result as a base and merge others
#         corr_matrix = correlation_results[0]
#         for result in correlation_results[1:]:
#             corr_matrix = corr_matrix.combine_first(result)
        
#         # Create a mask to remove self-correlations and redundant pairs
#         mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
#         # Gather correlations, removing self and duplicate correlations
#         correlations = []
#         for i in range(len(corr_matrix.columns)):
#             for j in range(i+1, len(corr_matrix.columns)):
#                 correlations.append({
#                     'Product1': corr_matrix.index[i],
#                     'Product2': corr_matrix.columns[j],
#                     'Correlation': corr_matrix.iloc[i, j]
#                 })
        
#         # Convert to DataFrame and filter correlations
#         corr_df = pd.DataFrame(correlations)
        
#         # Filter out weak correlations 
#         significant_correlations = corr_df[
#             (corr_df['Correlation'].abs() > 0.3) & 
#             (corr_df['Correlation'] != 1.0)
#         ]
        
#         # Sort by absolute correlation
#         top_correlations = significant_correlations.sort_values(
#             by='Correlation', 
#             key=abs, 
#             ascending=False
#         ).head(15)
        
#         # Create color scale that shows variation
#         # Blue for positive, Red for negative correlations
#         colors = top_correlations['Correlation'].apply(
#             lambda x: 'blue' if x > 0 else 'red'
#         )
#         color_intensities = np.abs(top_correlations['Correlation'])
        
#         # Create the figure
#         fig = go.Figure()
        
#         # Add correlation bars with color intensity
#         fig.add_trace(
#             go.Bar(
#                 y=[f"{row['Product1']} & {row['Product2']}" for _, row in top_correlations.iterrows()],
#                 x=top_correlations['Correlation'],
#                 orientation='h',
#                 marker=dict(
#                     color=[f'rgba({"0,0,255" if c=="blue" else "255,0,0"}, {intensity*0.8})' 
#                            for c, intensity in zip(colors, color_intensities)],
#                 ),
#                 hovertemplate='Products: %{y}<br>Correlation: %{x:.2f}<extra></extra>'
#             )
#         )
        
#         # Update layout
#         fig.update_layout(
#             title={
#                 'text': 'Top Product Correlations',
#                 'x': 0.5,
#                 'xanchor': 'center'
#             },
#             template='plotly_white',
#             xaxis_title='Correlation Coefficient',
#             xaxis=dict(
#                 tickmode='linear',
#                 tick0=top_correlations['Correlation'].min(),
#                 dtick=(top_correlations['Correlation'].max() - top_correlations['Correlation'].min()) / 5
#             ),
#             showlegend=False,
#             margin=dict(l=300, r=40, t=80, b=60),
#             height=500
#         )
        
#         return dbc.Card(
#             dbc.CardBody([
#                 dcc.Graph(figure=fig)
#             ])
#         )
    
#     except Exception as e:
#         return dbc.Card(
#             dbc.CardBody([
#                 html.P(f"Error creating product correlation chart: {str(e)}", 
#                        className="text-danger text-center")
#             ])
#         )
    
def create_category_performance_chart(category_metrics: pd.DataFrame, metric: str = 'revenue') -> dbc.Card:
    """
    Create a chart showing category performance analysis
    
    Args:
        category_metrics (pd.DataFrame): DataFrame with category metrics
        metric (str): Metric to display ('revenue', 'quantity', 'orders', 'customers')
        
    Returns:
        dbc.Card: Card containing the category performance chart
    """
    fig = go.Figure()
    
    if metric == 'revenue':
        y_values = category_metrics['TotalAmount']
        y_title = 'Revenue (£)'
        hover_template = 'Category: %{x}<br>Revenue: £%{y:,.2f}<extra></extra>'
    elif metric == 'quantity':
        y_values = category_metrics['Quantity']
        y_title = 'Quantity Sold'
        hover_template = 'Category: %{x}<br>Quantity: %{y:,.0f}<extra></extra>'
    elif metric == 'orders':
        y_values = category_metrics['InvoiceNo']
        y_title = 'Number of Orders'
        hover_template = 'Category: %{x}<br>Orders: %{y:,.0f}<extra></extra>'
    else:  # customers
        y_values = category_metrics['CustomerID']
        y_title = 'Number of Customers'
        hover_template = 'Category: %{x}<br>Customers: %{y:,.0f}<extra></extra>'

        # Update layout to improve readability
    fig.update_layout(
        title={
            'text': f'Category Performance - {y_title}',
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        xaxis_title='Category',
        yaxis=dict(
            title=y_title,
            titlefont=dict(color=chart_colors[0]),
            tickformat=',.2f',  # Ensures 2 decimal places
            range=[0, 1]  # Force y-axis from 0 to 1
        ),
        yaxis2=dict(
            title='Avg Order Value (£)',
            titlefont=dict(color=chart_colors[1]),
            overlaying='y',
            side='right',
            tickformat='£,.0f'
        ),
        hoverlabel=dict(
            bgcolor='grey',  # Grey background for hover text
            font_color='white'  # White text for better readability
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=500
    )

    # Modify the traces to normalize values between 0 and 1
    # For primary metric
    normalized_y_values = (y_values - y_values.min()) / (y_values.max() - y_values.min())

    # Update the bar trace
    fig.add_trace(
        go.Bar(
            x=category_metrics['Category'],
            y=normalized_y_values,
            name=y_title,
            marker_color=chart_colors[0],
            hovertemplate='Category: %{x}<br>Normalized Value: %{y:.3f}<extra></extra>'
        )
    )

    # Normalize Avg Order Value for secondary y-axis
    normalized_avg_order_value = (category_metrics['AvgOrderValue'] - category_metrics['AvgOrderValue'].min()) / \
                                (category_metrics['AvgOrderValue'].max() - category_metrics['AvgOrderValue'].min())

    # Update the line trace
    fig.add_trace(
        go.Scatter(
            x=category_metrics['Category'],
            y=normalized_avg_order_value,
            name='Avg Order Value',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Category: %{x}<br>Normalized Avg Order Value: %{y:.3f}<extra></extra>'
        )
    )
    
    # # Add primary metric bars
    # fig.add_trace(
    #     go.Bar(
    #         x=category_metrics['Category'],
    #         y=y_values,
    #         name=y_title,
    #         marker_color=chart_colors[0],
    #         hovertemplate=hover_template
    #     )
    # )
    
    # # Add average order value line
    # fig.add_trace(
    #     go.Scatter(
    #         x=category_metrics['Category'],
    #         y=category_metrics['AvgOrderValue'],
    #         name='Avg Order Value',
    #         mode='lines+markers',
    #         line=dict(color=chart_colors[1], width=2),
    #         marker=dict(size=8),
    #         yaxis='y2',
    #         hovertemplate='Category: %{x}<br>Avg Order Value: £%{y:,.2f}<extra></extra>'
    #     )
    # )
    
    # # Update layout
    # # Update layout to improve readability
    # fig.update_layout(
    #     title={
    #         'text': f'Category Performance - {y_title}',
    #         'x': 0.5,
    #         'xanchor': 'center'
    #     },
    #     template='plotly_white',
    #     xaxis_title='Category',
    #     yaxis=dict(
    #         title=y_title,
    #         titlefont=dict(color=chart_colors[0]),
    #         tickformat='£,.0f' if metric == 'revenue' else ',.0f'
    #     ),
    #     yaxis2=dict(
    #         title='Avg Order Value (£)',
    #         titlefont=dict(color=chart_colors[1]),
    #         overlaying='y',
    #         side='right',
    #         tickformat='£,.0f'
    #     ),
    #     legend=dict(
    #         orientation='h',
    #         yanchor='bottom',
    #         y=1.02,
    #         xanchor='right',
    #         x=1
    #     ),
    #     height=500
    # )
        
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_product_details_table(metrics: Dict[str, Any]) -> dbc.Card:
    """
    Create a table showing detailed product metrics
    
    Args:
        metrics (Dict[str, Any]): Dictionary containing product metrics
        
    Returns:
        dbc.Card: Card containing the product details table
    """
    def format_value(key: str, value: Any) -> str:
        """Format values based on metric type"""
        if 'revenue' in key.lower() or 'price' in key.lower() or 'value' in key.lower():
            return f'£{value:,.2f}'
        elif isinstance(value, (int, float)):
            return f'{value:,.0f}'
        elif isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        return str(value)
    
    table_rows = [
        html.Tr([
            html.Td(key.replace('_', ' ').title(), className='font-weight-bold'),
            html.Td(format_value(key, value))
        ]) for key, value in metrics.items()
    ]
    
    return dbc.Card(
        dbc.CardBody([
            html.H5('Product Details', className='mb-4'),
            dbc.Table(
                [html.Tbody(table_rows)],
                bordered=True,
                hover=True,
                responsive=True,
                className='mb-0'
            )
        ])
    )

@cache.memoize(timeout=300)
def create_product_summary(filtered_data: str) -> dbc.Container:
    """
    Create a container with all product-related charts
    
    Args:
        filtered_data (str): JSON string of filtered DataFrame
        
    Returns:
        dbc.Container: Container with product analysis charts
    """
    try:
        return dbc.Container([
            # Top Products Chart
            dbc.Row([
                dbc.Col([
                    create_top_products_chart(filtered_data)
                ], md=12, className="mb-4")
            ]),
            dbc.Row([
                dbc.Col([
                    create_product_trends_chart(filtered_data)
                ], md=12, className="mb-4"),
            ]),
            # Product Trends and Correlations
            dbc.Row([
                dbc.Col([
                    create_product_correlation_chart(filtered_data)
                ], md=12, className="mb-4")
            ], className="mb-4")
        ], fluid=True)
        
    except Exception as e:
        print(f"Error details: {str(e)}")  # For debugging
        return dbc.Container([
            dbc.Alert(
                [
                    html.H4("Error loading product analysis", className="alert-heading"),
                    html.P(f"Details: {str(e)}")
                ],
                color="danger",
                className="mb-3"
            )
        ], fluid=True)



# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load and process the data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.process_data()
    
    # Create the product summary
    product_charts = create_product_summary(df.to_json(date_format='iso', orient='split'))