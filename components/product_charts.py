import pandas as pd
import plotly.express as px
from typing import Dict, List, Any
import plotly.graph_objects as go
from dash import html, dcc
from datetime import datetime
import dash_bootstrap_components as dbc
from app import cache, chart_colors, plot_template
import numpy as np

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
    Create a chart showing product category trends over time
    """
    df = pd.read_json(filtered_data, orient='split')
    
    # Aggregate daily sales by category
    category_trends = df.groupby(['MonthYear', 'Category']).agg({
        'TotalAmount': 'sum'
    }).reset_index()
    
    # Create line chart
    fig = px.line(
        category_trends,
        x='MonthYear',
        y='TotalAmount',
        color='Category',
        title='Category Sales Trends',
        color_discrete_sequence=chart_colors,
        template=plot_template
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Revenue (£)',
        legend_title='Category',
        hovermode='x unified',
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_product_correlation_chart(filtered_data: str) -> dbc.Card:
    """
    Create a chart showing product correlations based on purchase patterns
    """
    df = pd.read_json(filtered_data, orient='split')
    
    # Create purchase matrix (which products are bought together)
    purchase_matrix = pd.crosstab(
        df['InvoiceNo'],
        df['Description']
    )
    
    # Calculate correlation matrix
    corr_matrix = purchase_matrix.corr()
    
    # Get top correlated product pairs
    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            correlations.append({
                'Product1': corr_matrix.index[i],
                'Product2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i, j]
            })
    
    # Convert to DataFrame and get top correlations
    corr_df = pd.DataFrame(correlations)
    top_correlations = corr_df.nlargest(10, 'Correlation')
    
    # Create the figure
    fig = go.Figure()
    
    # Add correlation bars
    fig.add_trace(
        go.Bar(
            y=[f"{row['Product1']} & {row['Product2']}" for _, row in top_correlations.iterrows()],
            x=top_correlations['Correlation'],
            orientation='h',
            marker_color=chart_colors[0]
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Top Product Correlations',
        template=plot_template,
        xaxis_title='Correlation Coefficient',
        showlegend=False,
        margin=dict(l=300, r=40, t=80, b=60),
        height=500
    )
    
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

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
    
    # Add primary metric bars
    fig.add_trace(
        go.Bar(
            x=category_metrics['Category'],
            y=y_values,
            name=y_title,
            marker_color=chart_colors[0],
            hovertemplate=hover_template
        )
    )
    
    # Add average order value line
    fig.add_trace(
        go.Scatter(
            x=category_metrics['Category'],
            y=category_metrics['AvgOrderValue'],
            name='Avg Order Value',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Category: %{x}<br>Avg Order Value: £%{y:,.2f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'Category Performance Analysis by {metric.title()}',
        template=plot_template,
        xaxis_title='Category',
        yaxis=dict(
            title=y_title,
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0])
        ),
        yaxis2=dict(
            title='Average Order Value (£)',
            titlefont=dict(color=chart_colors[1]),
            tickfont=dict(color=chart_colors[1]),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        height=500
    )
    
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
    
    # Add primary metric bars
    fig.add_trace(
        go.Bar(
            x=category_metrics['Category'],
            y=y_values,
            name=y_title,
            marker_color=chart_colors[0],
            hovertemplate=hover_template
        )
    )
    
    # Add average order value line
    fig.add_trace(
        go.Scatter(
            x=category_metrics['Category'],
            y=category_metrics['AvgOrderValue'],
            name='Avg Order Value',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Category: %{x}<br>Avg Order Value: £%{y:,.2f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'Category Performance Analysis by {metric.title()}',
        template=plot_template,
        xaxis_title='Category',
        yaxis=dict(
            title=y_title,
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0])
        ),
        yaxis2=dict(
            title='Average Order Value (£)',
            titlefont=dict(color=chart_colors[1]),
            tickfont=dict(color=chart_colors[1]),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        height=500
    )
    
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
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                create_top_products_chart(filtered_data)
            ], md=12, className="mb-4")
        ]),
        dbc.Row([
            dbc.Col([
                create_product_trends_chart(filtered_data)
            ], md=6),
            dbc.Col([
                create_product_correlation_chart(filtered_data)
            ], md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                create_category_performance_chart(
                    pd.read_json(filtered_data, orient='split').groupby('Category').agg({
                        'TotalAmount': 'sum',
                        'Quantity': 'sum',
                        'InvoiceNo': 'nunique',
                        'CustomerID': 'nunique'
                    }).reset_index()
                )
            ], md=12)
        ])
    ], fluid=True)



# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load and process the data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.process_data()
    
    # Create the product summary
    product_charts = create_product_summary(df.to_json(date_format='iso', orient='split'))