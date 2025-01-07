import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
import dash_bootstrap_components as dbc
from app import cache, chart_colors, plot_template
import numpy as np
from datetime import datetime
from typing import Dict, Any

# def calculate_rfm_scores(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Calculate RFM (Recency, Frequency, Monetary) scores for customers
#     """
#     # Calculate metrics
#     today = df['InvoiceDate'].max()
    
#     rfm = df.groupby('CustomerID').agg({
#         'InvoiceDate': lambda x: (today - x.max()).days,  # Recency
#         'InvoiceNo': 'nunique',                           # Frequency
#         'TotalAmount': 'sum'                              # Monetary
#     }).reset_index()
    
#     rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    
#     # Create score quintiles
#     rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
#     rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=5, labels=[1, 2, 3, 4, 5])
#     rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
    
#     # Calculate RFM Score
#     rfm['RFM_Score'] = rfm['R_Score'].astype(str) + \
#                        rfm['F_Score'].astype(str) + \
#                        rfm['M_Score'].astype(str)
    
#     # Segment customers
#     def segment_customers(row):
#         if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >= 4:
#             return 'Champions'
#         elif row['R_Score'] >= 3 and row['F_Score'] >= 3 and row['M_Score'] >= 3:
#             return 'Loyal Customers'
#         elif row['R_Score'] >= 3 and row['F_Score'] >= 1 and row['M_Score'] >= 2:
#             return 'Active Customers'
#         elif row['R_Score'] >= 2 and row['F_Score'] >= 2 and row['M_Score'] >= 2:
#             return 'Regular Customers'
#         elif row['R_Score'] >= 2 and row['F_Score'] >= 1:
#             return 'New Customers'
#         else:
#             return 'At Risk'
    
#     rfm['Customer_Segment'] = rfm.apply(segment_customers, axis=1)
    
#     return rfm
def calculate_rfm_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for customers
    with robust handling of edge cases and duplicate values
    """
    df = df.copy()
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    today = df['InvoiceDate'].max()
    
    # Calculate RFM metrics
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (today - x.max()).days,  # Recency
        'InvoiceNo': 'nunique',                           # Frequency
        'TotalAmount': 'sum'                              # Monetary
    }).reset_index()
    
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    
    def score_values(series: pd.Series, ascending: bool = True) -> pd.Series:
        """
        Score values from 1-5 using percentile method with robust handling of duplicates
        """
        if len(series.unique()) < 5:
            # If we have fewer unique values than desired scores,
            # use a simpler ranking method
            ranks = series.rank(method='dense', ascending=ascending)
            max_rank = ranks.max()
            scores = (((ranks - 1) / (max_rank - 1)) * 4 + 1).round()
            return scores.clip(1, 5).astype(int)
        
        try:
            # Try regular percentile-based scoring
            if ascending:
                scores = pd.qcut(series, q=5, labels=[1, 2, 3, 4, 5])
            else:
                scores = pd.qcut(-series, q=5, labels=[5, 4, 3, 2, 1])
            return scores.astype(int)
        except ValueError:
            # If qcut fails due to duplicates, use rank-based method
            ranks = series.rank(pct=True, ascending=ascending)
            # Convert ranks to scores (1-5)
            scores = pd.qcut(ranks, q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
            # Fill any missing values with median score
            scores = scores.fillna(3)
            return scores.astype(int)
    
    # Calculate scores
    rfm['R_Score'] = score_values(rfm['Recency'], ascending=False)  # Lower recency is better
    rfm['F_Score'] = score_values(rfm['Frequency'], ascending=True)  # Higher frequency is better
    rfm['M_Score'] = score_values(rfm['Monetary'], ascending=True)   # Higher monetary is better
    
    # Calculate RFM Score
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + \
                       rfm['F_Score'].astype(str) + \
                       rfm['M_Score'].astype(str)
    
    # Segment customers
    def segment_customers(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 3 and f >= 1 and m >= 2:
            return 'Active Customers'
        elif r >= 2 and f >= 2 and m >= 2:
            return 'Regular Customers'
        elif r >= 2 and f >= 1:
            return 'New Customers'
        else:
            return 'At Risk'
    
    rfm['Customer_Segment'] = rfm.apply(segment_customers, axis=1)
    
    # Add original metrics for reference
    rfm['Recency_Days'] = rfm['Recency']
    rfm['Purchase_Frequency'] = rfm['Frequency']
    rfm['Total_Revenue'] = rfm['Monetary']
    
    return rfm


# def create_rfm_distribution_chart(rfm_df: pd.DataFrame) -> dbc.Card:
#     """
#     Create RFM distribution visualization
#     """
#     # Create subplots with 2 rows
#     fig = make_subplots(
#         rows=2, cols=2,
#         subplot_titles=(
#             'Customer Segments Distribution',
#             'RFM Score Distribution',
#             'Average Customer Value by Segment',
#             'Segment Size vs Value'
#         ),
#         vertical_spacing=0.15,
#         horizontal_spacing=0.1
#     )
    
#     # 1. Customer Segments Distribution
#     segment_dist = rfm_df['Customer_Segment'].value_counts()
#     fig.add_trace(
#         go.Bar(
#             x=segment_dist.index,
#             y=segment_dist.values,
#             name='Customers',
#             marker_color=chart_colors[0],
#             hovertemplate='Segment: %{x}<br>Customers: %{y:,.0f}<extra></extra>'
#         ),
#         row=1, col=1
#     )
    
#     # 2. RFM Score Distribution
#     rfm_scores = pd.DataFrame({
#         'Score': ['R', 'F', 'M'],
#         'Average': [
#             rfm_df['R_Score'].mean(),
#             rfm_df['F_Score'].mean(),
#             rfm_df['M_Score'].mean()
#         ]
#     })
#     fig.add_trace(
#         go.Bar(
#             x=rfm_scores['Score'],
#             y=rfm_scores['Average'],
#             name='Avg Score',
#             marker_color=chart_colors[1],
#             hovertemplate='Component: %{x}<br>Average Score: %{y:.2f}<extra></extra>'
#         ),
#         row=1, col=2
#     )
    
#     # 3. Average Value by Segment
#     avg_value = rfm_df.groupby('Customer_Segment')['Monetary'].mean().round(2)
#     fig.add_trace(
#         go.Bar(
#             x=avg_value.index,
#             y=avg_value.values,
#             name='Avg Value',
#             marker_color=chart_colors[2],
#             hovertemplate='Segment: %{x}<br>Average Value: £%{y:,.2f}<extra></extra>'
#         ),
#         row=2, col=1
#     )
    
#     # 4. Segment Size vs Value
#     segment_metrics = rfm_df.groupby('Customer_Segment').agg({
#         'CustomerID': 'count',
#         'Monetary': 'mean'
#     }).reset_index()
    
#     fig.add_trace(
#         go.Scatter(
#             x=segment_metrics['CustomerID'],
#             y=segment_metrics['Monetary'],
#             mode='markers+text',
#             name='Segments',
#             text=segment_metrics['Customer_Segment'],
#             textposition='top center',
#             marker=dict(
#                 size=15,
#                 color=chart_colors[3],
#                 line=dict(width=2, color='DarkSlateGrey')
#             ),
#             hovertemplate='Segment: %{text}<br>Customers: %{x:,.0f}<br>Avg Value: £%{y:,.2f}<extra></extra>'
#         ),
#         row=2, col=2
#     )
    
#     # Update layout
#     fig.update_layout(
#         title_text='RFM Analysis Overview',
#         template=plot_template,
#         showlegend=False,
#         height=800,
#         margin=dict(l=60, r=40, t=100, b=60)
#     )
    
#     # Update axes labels
#     fig.update_xaxes(title_text='Customer Segment', row=1, col=1)
#     fig.update_yaxes(title_text='Number of Customers', row=1, col=1)
    
#     fig.update_xaxes(title_text='RFM Component', row=1, col=2)
#     fig.update_yaxes(title_text='Average Score', row=1, col=2)
    
#     fig.update_xaxes(title_text='Customer Segment', row=2, col=1)
#     fig.update_yaxes(title_text='Average Customer Value (£)', row=2, col=1)
    
#     fig.update_xaxes(title_text='Number of Customers', row=2, col=2)
#     fig.update_yaxes(title_text='Average Customer Value (£)', row=2, col=2)
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig)
#         ])
#     )

def create_rfm_distribution_chart(rfm_df: pd.DataFrame) -> dbc.Card:
    """
    Create RFM distribution visualization
    """
    # Convert categorical scores to numeric
    rfm_df = rfm_df.copy()
    rfm_df['R_Score'] = rfm_df['R_Score'].astype(int)
    rfm_df['F_Score'] = rfm_df['F_Score'].astype(int)
    rfm_df['M_Score'] = rfm_df['M_Score'].astype(int)
    
    # Create subplots with 2 rows
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Customer Segments Distribution',
            'RFM Score Distribution',
            'Average Customer Value by Segment',
            'Segment Size vs Value'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Customer Segments Distribution
    segment_dist = rfm_df['Customer_Segment'].value_counts()
    fig.add_trace(
        go.Bar(
            x=segment_dist.index,
            y=segment_dist.values,
            name='Customers',
            marker_color=chart_colors[0],
            hovertemplate='Segment: %{x}<br>Customers: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. RFM Score Distribution
    rfm_scores = pd.DataFrame({
        'Score': ['R', 'F', 'M'],
        'Average': [
            rfm_df['R_Score'].astype(int).mean(),
            rfm_df['F_Score'].astype(int).mean(),
            rfm_df['M_Score'].astype(int).mean()
        ]
    })
    fig.add_trace(
        go.Bar(
            x=rfm_scores['Score'],
            y=rfm_scores['Average'],
            name='Avg Score',
            marker_color=chart_colors[1],
            hovertemplate='Component: %{x}<br>Average Score: %{y:.2f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Average Value by Segment
    avg_value = rfm_df.groupby('Customer_Segment')['Monetary'].mean().round(2)
    fig.add_trace(
        go.Bar(
            x=avg_value.index,
            y=avg_value.values,
            name='Avg Value',
            marker_color=chart_colors[2],
            hovertemplate='Segment: %{x}<br>Average Value: £%{y:,.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Segment Size vs Value
    segment_metrics = rfm_df.groupby('Customer_Segment').agg({
        'CustomerID': 'count',
        'Monetary': 'mean'
    }).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=segment_metrics['CustomerID'],
            y=segment_metrics['Monetary'],
            mode='markers+text',
            name='Segments',
            text=segment_metrics['Customer_Segment'],
            textposition='top center',
            marker=dict(
                size=15,
                color=chart_colors[3],
                line=dict(width=2, color='DarkSlateGrey')
            ),
            hovertemplate='Segment: %{text}<br>Customers: %{x:,.0f}<br>Avg Value: £%{y:,.2f}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text='RFM Analysis Overview',
        template=plot_template,
        showlegend=False,
        height=800,
        margin=dict(l=60, r=40, t=100, b=60)
    )
    
    # Update axes labels
    fig.update_xaxes(title_text='Customer Segment', row=1, col=1)
    fig.update_yaxes(title_text='Number of Customers', row=1, col=1)
    
    fig.update_xaxes(title_text='RFM Component', row=1, col=2)
    fig.update_yaxes(title_text='Average Score', row=1, col=2)
    
    fig.update_xaxes(title_text='Customer Segment', row=2, col=1)
    fig.update_yaxes(title_text='Average Customer Value (£)', row=2, col=1)
    
    fig.update_xaxes(title_text='Number of Customers', row=2, col=2)
    fig.update_yaxes(title_text='Average Customer Value (£)', row=2, col=2)
    
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_lifecycle_chart(customer_metrics: pd.DataFrame, metric: str = 'revenue') -> dbc.Card:
    """
    Create customer lifecycle visualization using rank-based grouping
    """
    # Create age groups using rank-based method
    ranks = customer_metrics['Age'].rank(method='dense')
    max_rank = ranks.max()
    
    # Create labels based on percentile ranges
    def get_percentile_label(rank):
        pct = (rank - 1) / (max_rank - 1) * 100
        if pct <= 20: return '0-20%'
        elif pct <= 40: return '20-40%'
        elif pct <= 60: return '40-60%'
        elif pct <= 80: return '60-80%'
        else: return '80-100%'
    
    customer_metrics['AgeBin'] = ranks.map(get_percentile_label)
    
    # Set up metric-specific variables
    if metric == 'orders':
        y_values = customer_metrics['Orders']
        y_title = 'Number of Orders'
        hover_template = 'Age Group: %{x}<br>Orders: %{y:,.0f}<extra></extra>'
    elif metric == 'revenue':
        y_values = customer_metrics['Revenue']
        y_title = 'Total Revenue (£)'
        hover_template = 'Age Group: %{x}<br>Revenue: £%{y:,.2f}<extra></extra>'
    else:  # frequency
        y_values = customer_metrics['OrderFrequency']
        y_title = 'Order Frequency (orders/day)'
        hover_template = 'Age Group: %{x}<br>Frequency: %{y:.2f}<extra></extra>'
    
    # Calculate metrics by age bin
    lifecycle_data = customer_metrics.groupby('AgeBin').agg({
        metric: ['mean', 'count']
    }).reset_index()
    
    # Sort the bins in correct order
    bin_order = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    lifecycle_data['AgeBin'] = pd.Categorical(
        lifecycle_data['AgeBin'], 
        categories=bin_order, 
        ordered=True
    )
    lifecycle_data = lifecycle_data.sort_values('AgeBin')
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars for metric values
    fig.add_trace(
        go.Bar(
            x=lifecycle_data['AgeBin'],
            y=lifecycle_data[(metric, 'mean')],
            name=y_title,
            marker_color=chart_colors[0],
            hovertemplate=hover_template
        )
    )
    
    # Add line for customer count
    fig.add_trace(
        go.Scatter(
            x=lifecycle_data['AgeBin'],
            y=lifecycle_data[(metric, 'count')],
            name='Customer Count',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Age Group: %{x}<br>Customers: %{y:,.0f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Customer Lifecycle Analysis',
        template=plot_template,
        xaxis_title='Customer Age Group',
        yaxis=dict(
            title=y_title,
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0])
        ),
        yaxis2=dict(
            title='Number of Customers',
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

def create_cohort_chart(cohort_data: pd.DataFrame, metric: str = 'retention') -> dbc.Card:
    """
    Create customer cohort analysis visualization
    """
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=cohort_data.values,
        x=cohort_data.columns,
        y=cohort_data.index,
        colorscale='Blues',
        hoverongaps=False
    ))
    
    # Update layout
    title_text = {
        'retention': 'Customer Retention by Cohort',
        'revenue': 'Revenue by Cohort',
        'frequency': 'Purchase Frequency by Cohort'
    }.get(metric, 'Cohort Analysis')
    
    fig.update_layout(
        title=title_text,
        template=plot_template,
        xaxis_title='Months Since First Purchase',
        yaxis_title='Cohort',
        margin=dict(l=80, r=40, t=80, b=60),
        height=600
    )
    
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_segment_chart(segment_metrics: pd.DataFrame, metric: str = 'revenue') -> dbc.Card:
    """
    Create customer segmentation analysis visualization
    """
    if metric == 'revenue':
        y_values = segment_metrics['TotalAmount']
        y_title = 'Revenue (£)'
        hover_template = 'Segment: %{x}<br>Revenue: £%{y:,.2f}<extra></extra>'
    elif metric == 'orders':
        y_values = segment_metrics['InvoiceNo']
        y_title = 'Number of Orders'
        hover_template = 'Segment: %{x}<br>Orders: %{y:,.0f}<extra></extra>'
    elif metric == 'customers':
        y_values = segment_metrics['CustomerID']
        y_title = 'Number of Customers'
        hover_template = 'Segment: %{x}<br>Customers: %{y:,.0f}<extra></extra>'
    else:  # quantity
        y_values = segment_metrics['Quantity']
        y_title = 'Total Quantity'
        hover_template = 'Segment: %{x}<br>Quantity: %{y:,.0f}<extra></extra>'
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars for primary metric
    fig.add_trace(
        go.Bar(
            x=segment_metrics['Customer_Segment'],
            y=y_values,
            name=y_title,
            marker_color=chart_colors[0],
            hovertemplate=hover_template
        )
    )
    
    # Add line for average value per customer
    avg_value = y_values / segment_metrics['CustomerID']
    fig.add_trace(
        go.Scatter(
            x=segment_metrics['Customer_Segment'],
            y=avg_value,
            name=f'Average {y_title} per Customer',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate=f'Segment: %{{x}}<br>Avg {y_title} per Customer: %{{y:.2f}}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'Customer Segment Analysis by {metric.title()}',
        template=plot_template,
        xaxis_title='Customer Segment',
        yaxis=dict(
            title=y_title,
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0])
        ),
        yaxis2=dict(
            title=f'Average {y_title} per Customer',
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

def create_customer_details_table(metrics: Dict[str, Any]) -> dbc.Card:
    """
    Create a table showing detailed customer metrics
    """
    def format_value(key: str, value: Any) -> str:
        """Format values based on metric type"""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        elif 'spend' in key.lower() or 'value' in key.lower():
            return f'£{value:,.2f}'
        elif isinstance(value, (int, float)):
            return f'{value:,.0f}' if value.is_integer() else f'{value:.2f}'
        return str(value)
    
    table_rows = [
        html.Tr([
            html.Td(key.replace('_', ' ').title(), className='font-weight-bold'),
            html.Td(format_value(key, value))
        ]) for key, value in metrics.items()
    ]
    
    return dbc.Card(
        dbc.CardBody([
            html.H5('Customer Details', className='mb-4'),
            dbc.Table(
                [html.Tbody(table_rows)],
                bordered=True,
                hover=True,
                responsive=True,
                className='mb-0'
            )
        ])
    )

def get_cohort_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cohort analysis data
    """
    # Ensure InvoiceDate is datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Get customer's first purchase month
    customer_first_purchase = df.groupby('CustomerID')['InvoiceDate'].min().reset_index()
    customer_first_purchase['CohortMonth'] = customer_first_purchase['InvoiceDate'].dt.to_period('M')
    
    # Merge with main dataframe
    df = df.merge(customer_first_purchase[['CustomerID', 'CohortMonth']], on='CustomerID')
    
    # Calculate months since first purchase
    df['MonthsFromFirstPurchase'] = ((df['InvoiceDate'].dt.to_period('M') - 
                                     df['CohortMonth']).astype(int))
    
    # Create cohort matrix
    cohort_data = pd.crosstab(df['CohortMonth'], 
                             df['MonthsFromFirstPurchase'],
                             values=df['CustomerID'],
                             aggfunc='nunique')
    
    # Calculate retention percentages
    cohort_sizes = cohort_data[0]
    cohort_data = cohort_data.div(cohort_sizes, axis=0) * 100
    
    return cohort_data

def get_segment_metrics(df: pd.DataFrame, rfm_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate segment-level metrics
    
    Args:
        df (pd.DataFrame): Input DataFrame
        rfm_data (pd.DataFrame): RFM analysis DataFrame
        
    Returns:
        pd.DataFrame: Segment metrics
    """
    return df.merge(
        rfm_data[['CustomerID', 'Customer_Segment']], 
        on='CustomerID'
    ).groupby('Customer_Segment').agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()

@cache.memoize(timeout=300)
def create_customer_summary(filtered_data: str) -> dbc.Container:
    """
    Create a container with all customer-related charts
    """
    df = pd.read_json(filtered_data, orient='split')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Calculate RFM scores and segments
    rfm_data = calculate_rfm_scores(df)
    
    # Calculate customer metrics with robust binning
    customer_metrics = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (x.max() - x.min()).days,  # Customer age
        'InvoiceNo': 'nunique',  # Number of orders
        'TotalAmount': 'sum',    # Total revenue
    }).reset_index()
    
    customer_metrics.columns = ['CustomerID', 'Age', 'Orders', 'Revenue']
    customer_metrics['OrderFrequency'] = customer_metrics['Orders'] / customer_metrics['Age']
    
    # Handle age binning explicitly here
    try:
        customer_metrics['AgeBin'] = pd.qcut(
            customer_metrics['Age'],
            q=5,
            labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
            duplicates='drop'
        )
    except ValueError:
        # Fallback to rank-based binning if qcut fails
        ranks = customer_metrics['Age'].rank(pct=True)
        customer_metrics['AgeBin'] = pd.qcut(
            ranks,
            q=5,
            labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
        )

    # Create summary container
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                create_rfm_distribution_chart(rfm_data)
            ], md=12, className="mb-4")
        ]),
        dbc.Row([
            dbc.Col([
                create_lifecycle_chart(customer_metrics)
            ], md=6),
            dbc.Col([
                create_cohort_chart(get_cohort_data(df))
            ], md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                create_segment_chart(get_segment_metrics(df, rfm_data))
            ], md=12)
        ])
    ], fluid=True)

# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load and process the data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.process_data()
    
    # Create the customer summary
    customer_charts = create_customer_summary(df.to_json(date_format='iso', orient='split'))