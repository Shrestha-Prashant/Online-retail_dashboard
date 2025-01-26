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
#     with robust handling of edge cases and duplicate values
#     """
#     df = df.copy()
#     df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
#     today = df['InvoiceDate'].max()
    
#     # Calculate RFM metrics
#     rfm = df.groupby('CustomerID').agg({
#         'InvoiceDate': lambda x: (today - x.max()).days,  # Recency
#         'InvoiceNo': 'nunique',                           # Frequency
#         'TotalAmount': 'sum'                              # Monetary
#     }).reset_index()
    
#     rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    
#     def score_values(series: pd.Series, ascending: bool = True) -> pd.Series:
#         """
#         Score values from 1-5 using rank-based method to handle duplicate values
        
#         Args:
#             series: Series of values to score
#             ascending: Whether higher values should get higher scores
            
#         Returns:
#             Series of integer scores from 1-5
#         """
#         # Handle null values
#         if series.isna().any():
#             series = series.fillna(series.median())
            
#         # Use rank method to handle ties
#         ranks = series.rank(method='first', ascending=ascending, pct=True)
        
#         # Convert percentile ranks to scores 1-5
#         scores = pd.Series(1, index=series.index)  # Default score 1
#         scores[ranks > 0.2] = 2
#         scores[ranks > 0.4] = 3
#         scores[ranks > 0.6] = 4
#         scores[ranks > 0.8] = 5
        
#         return scores.astype(int)
    
#     # Calculate scores with proper handling of directionality
#     rfm['R_Score'] = score_values(rfm['Recency'], ascending=False)  # Lower recency is better
#     rfm['F_Score'] = score_values(rfm['Frequency'], ascending=True)  # Higher frequency is better
#     rfm['M_Score'] = score_values(rfm['Monetary'], ascending=True)   # Higher monetary is better
    
#     # Calculate RFM Score
#     rfm['RFM_Score'] = rfm['R_Score'].astype(str) + \
#                        rfm['F_Score'].astype(str) + \
#                        rfm['M_Score'].astype(str)
    
#     # Segment customers
#     def segment_customers(row):
#         r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        
#         if r >= 4 and f >= 4 and m >= 4:
#             return 'Champions'
#         elif r >= 3 and f >= 3 and m >= 3:
#             return 'Loyal Customers'
#         elif r >= 3 and f >= 1 and m >= 2:
#             return 'Active Customers'
#         elif r >= 2 and f >= 2 and m >= 2:
#             return 'Regular Customers'
#         elif r >= 2 and f >= 1:
#             return 'New Customers'
#         else:
#             return 'At Risk'
    
#     rfm['Customer_Segment'] = rfm.apply(segment_customers, axis=1)
    
#     # Add original metrics for reference
#     rfm['Recency_Days'] = rfm['Recency']
#     rfm['Purchase_Frequency'] = rfm['Frequency']
#     rfm['Total_Revenue'] = rfm['Monetary']
    
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
    
    def robust_scoring(series: pd.Series, ascending: bool = True) -> pd.Series:
        """
        More nuanced scoring method using quantile-based approach
        
        Args:
            series: Series of values to score
            ascending: Whether higher values should get higher scores
            
        Returns:
            Series of integer scores from 1-5
        """
        # Handle null values
        if series.isna().any():
            series = series.fillna(series.median())
        
        # Use quantile-based method for more granular scoring
        if ascending:
            # For metrics where higher is better (Frequency, Monetary)
            quartiles = series.quantile([0.2, 0.4, 0.6, 0.8])
            conditions = [
                series <= quartiles[0.2],
                (series > quartiles[0.2]) & (series <= quartiles[0.4]),
                (series > quartiles[0.4]) & (series <= quartiles[0.6]),
                (series > quartiles[0.6]) & (series <= quartiles[0.8]),
                series > quartiles[0.8]
            ]
            choices = [1, 2, 3, 4, 5]
        else:
            # For Recency, where lower values are better
            quartiles = series.quantile([0.2, 0.4, 0.6, 0.8])
            conditions = [
                series >= quartiles[0.8],
                (series < quartiles[0.8]) & (series >= quartiles[0.6]),
                (series < quartiles[0.6]) & (series >= quartiles[0.4]),
                (series < quartiles[0.4]) & (series >= quartiles[0.2]),
                series < quartiles[0.2]
            ]
            choices = [1, 2, 3, 4, 5]
        
        return pd.Series(np.select(conditions, choices, default=3), index=series.index)
    
    # Calculate scores with proper handling of directionality
    rfm['R_Score'] = robust_scoring(rfm['Recency'], ascending=False)  # Lower recency is better
    rfm['F_Score'] = robust_scoring(rfm['Frequency'], ascending=True)  # Higher frequency is better
    rfm['M_Score'] = robust_scoring(rfm['Monetary'], ascending=True)   # Higher monetary is better
    
    # Calculate RFM Score
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + \
                       rfm['F_Score'].astype(str) + \
                       rfm['M_Score'].astype(str)
    
    # Segment customers (keep previous segmentation logic)
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

def create_rfm_distribution_chart(rfm_df: pd.DataFrame, customer_metrics: pd.DataFrame) -> dbc.Card:
    """
    Create comprehensive RFM distribution visualization
    """
    # Convert categorical scores to numeric
    rfm_df = rfm_df.copy()
    rfm_df['R_Score'] = rfm_df['R_Score'].astype(int)
    rfm_df['F_Score'] = rfm_df['F_Score'].astype(int)
    rfm_df['M_Score'] = rfm_df['M_Score'].astype(int)
    
    # Create subplots with 2 rows and 2 columns
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribution of Customer Segments',  
            'Average RFM Component Scores',       
            'Segment Analysis: Size vs Sales Value',
            'Customer Lifecycle Analysis'
        ),
        vertical_spacing=0.2,
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
    
    # 3. Segment Size vs Sales Value
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
            hovertemplate='Segment: %{text}<br>Customers: %{x:,.0f}<br>Avg Sales: £%{y:,.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Customer Lifecycle Analysis
    # Create age groups using rank-based method
    ranks = customer_metrics['Age'].rank(method='dense')
    max_rank = ranks.max()
    
    def get_percentile_label(rank):
        pct = (rank - 1) / (max_rank - 1) * 100
        if pct <= 20: return '0-20%'
        elif pct <= 40: return '20-40%'
        elif pct <= 60: return '40-60%'
        elif pct <= 80: return '60-80%'
        else: return '80-100%'
    
    customer_metrics['AgeBin'] = ranks.map(get_percentile_label)
    
    # Calculate metrics by age bin for sales
    lifecycle_data = customer_metrics.groupby('AgeBin').agg({
        'Revenue': ['mean', 'count']
    }).reset_index()
    
    # Sort the bins in correct order
    bin_order = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    lifecycle_data['AgeBin'] = pd.Categorical(
        lifecycle_data['AgeBin'], 
        categories=bin_order, 
        ordered=True
    )
    lifecycle_data = lifecycle_data.sort_values('AgeBin')
    
    # Add bars for sales values (primary Y-axis)
    fig.add_trace(
        go.Bar(
            x=lifecycle_data['AgeBin'],
            y=lifecycle_data[('Revenue', 'mean')],
            name='Average Sales',
            marker_color=chart_colors[0],
            yaxis='y3',
            hovertemplate='Age Group: %{x}<br>Avg Sales: £%{y:,.2f}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Add line for customer count (secondary Y-axis)
    fig.add_trace(
        go.Scatter(
            x=lifecycle_data['AgeBin'],
            y=lifecycle_data[('Revenue', 'count')],
            name='Customer Count',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y4',
            hovertemplate='Age Group: %{x}<br>Customers: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text='Customer Analysis Overview',
        template=plot_template,
        showlegend=False,
        height=800,
        margin=dict(l=60, r=40, t=100, b=60),
        yaxis3=dict(
            title='Average Sales (£)',
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0]),
            anchor='x4'
        ),
        yaxis4=dict(
            title='Number of Customers',
            titlefont=dict(color=chart_colors[1]),
            tickfont=dict(color=chart_colors[1]),
            anchor='x4',
            overlaying='y3',
            side='right'
        )
    )
    
    # Update axes labels
    fig.update_xaxes(title_text='Customer Segment', row=1, col=1)
    fig.update_yaxes(title_text='Number of Customers', row=1, col=1)
    
    fig.update_xaxes(title_text='RFM Component', row=1, col=2)
    fig.update_yaxes(title_text='Average Score', row=1, col=2)
    
    fig.update_xaxes(title_text='Number of Customers', row=2, col=1)
    fig.update_yaxes(title_text='Average Sales by Customer (£)', row=2, col=1)
    
    fig.update_xaxes(title_text='Customer Age Group', row=2, col=2)
    fig.update_yaxes(title_text='No of Orders', row=2, col=2)
    
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_customer_lifecycle_chart(customer_metrics: pd.DataFrame) -> go.Figure:
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
    
    # Calculate metrics by age bin for sales
    lifecycle_data = customer_metrics.groupby('AgeBin').agg({
        'Revenue': ['mean', 'count']
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
    
    # Add bars for sales values (primary Y-axis)
    fig.add_trace(
        go.Bar(
            x=lifecycle_data['AgeBin'],
            y=lifecycle_data[('Revenue', 'mean')],
            name='Average Sales',
            marker_color=chart_colors[0],
            yaxis='y1',
            hovertemplate='Age Group: %{x}<br>Avg Sales: £%{y:,.2f}<extra></extra>'
        )
    )
    
    # Add line for customer count (secondary Y-axis)
    fig.add_trace(
        go.Scatter(
            x=lifecycle_data['AgeBin'],
            y=lifecycle_data[('Revenue', 'count')],
            name='Customer Count',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Age Group: %{x}<br>Customers: %{y:,.0f}<extra></extra>'
        )
    )
    
    # Update layout with dual Y-axes
    fig.update_layout(
        yaxis1=dict(
            title='Average Sales (£)',
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
        )
    )
    
    return fig

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
        'Revenue': 'Revenue by Cohort',
        'frequency': 'Purchase Frequency by Cohort'
    }.get(metric, 'Cohort Analysis')
    
    # fig.update_layout(
    #     title=title_text,
    #     template=plot_template,
    #     xaxis_title='Months Since First Purchase',
    #     yaxis_title='Cohort',
    #     margin=dict(l=80, r=40, t=80, b=60),
    #     height=600
    # )
    fig.update_layout(
    title=title_text,
    template=plot_template,
    xaxis_title='Months Since First Purchase',
    yaxis_title='Customer Cohort',  # Changed from 'Cohort'
    margin=dict(l=80, r=40, t=100, b=60),  # Changed t=80 to t=100
    height=600
)
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )

def create_segment_chart(segment_metrics: pd.DataFrame, metric: str = 'Sales') -> dbc.Card:
    """
    Create customer segmentation analysis visualization with sales focus
    """
    if metric == 'Sales':
        y_values = segment_metrics['TotalAmount']
        y_title = 'Sales (£)'
        hover_template = 'Segment: %{x}<br>Sales: £%{y:,.2f}<extra></extra>'
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
            name=f'Average Sales per Customer',
            mode='lines+markers',
            line=dict(color=chart_colors[1], width=2),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Segment: %{x}<br>Avg Sales per Customer: £%{y:.2f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'Customer Segment Analysis by Sales',
        template=plot_template,
        xaxis_title='Customer Segment',
        yaxis=dict(
            title=y_title,
            titlefont=dict(color=chart_colors[0]),
            tickfont=dict(color=chart_colors[0])
        ),
        yaxis2=dict(
            title='Average Sales per Customer',
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
    """Calculate cohort analysis data"""
    # Ensure datetime
    df = df.copy()
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Get first purchase month for each customer
    customer_first_purchase = df.groupby('CustomerID')['InvoiceDate'].min().reset_index()
    customer_first_purchase['CohortMonth'] = customer_first_purchase['InvoiceDate'].dt.strftime('%Y-%m')
    
    # Merge cohort month back to main df
    df = df.merge(customer_first_purchase[['CustomerID', 'CohortMonth']], on='CustomerID')
    
    # Calculate difference in months
    df['PurchaseMonth'] = df['InvoiceDate'].dt.strftime('%Y-%m')
    df['MonthIndex'] = ((pd.to_datetime(df['PurchaseMonth']) - 
                        pd.to_datetime(df['CohortMonth'])).dt.days // 30)
    
    # Create cohort matrix
    cohort_matrix = pd.crosstab(
        df['CohortMonth'],
        df['MonthIndex'],
        values=df['CustomerID'],
        aggfunc='nunique'
    )
    
    # Calculate retention percentages
    cohort_sizes = cohort_matrix[0]
    cohort_data = cohort_matrix.div(cohort_sizes, axis=0) * 100
    
    return cohort_data

def get_segment_metrics(df: pd.DataFrame, rfm_data: pd.DataFrame) -> pd.DataFrame:
    return df.merge(
        rfm_data[['CustomerID', 'Customer_Segment']], 
        on='CustomerID'
    ).groupby('Customer_Segment').agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
from io import StringIO

def score_percentile(series: pd.Series) -> pd.Series:
    ranks = series.rank(pct=True)
    scores = pd.Series(1, index=series.index)
    scores[ranks > 0.2] = 2
    scores[ranks > 0.4] = 3
    scores[ranks > 0.6] = 4
    scores[ranks > 0.8] = 5
    return scores

@cache.memoize(timeout=300)
def create_customer_summary(filtered_data: str) -> dbc.Container:
    """Create customer analysis dashboard"""
    df = pd.read_json(StringIO(filtered_data), orient='split')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    rfm_data = calculate_rfm_scores(df)
    
    customer_metrics = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (x.max() - x.min()).days,
        'InvoiceNo': 'nunique',
        'TotalAmount': 'sum'
    }).reset_index()
    
    customer_metrics.columns = ['CustomerID', 'Age', 'Orders', 'Revenue']
    customer_metrics['OrderFrequency'] = customer_metrics['Orders'] / customer_metrics['Age']
    
    # Use score_percentile instead of qcut
    customer_metrics['AgeBin'] = score_percentile(customer_metrics['Age']).map({
        1: '0-20%',
        2: '20-40%',
        3: '40-60%',
        4: '60-80%',
        5: '80-100%'
    })

    return dbc.Container([
        dbc.Row([
            dbc.Col([create_rfm_distribution_chart(rfm_data, customer_metrics)], md=12, className="mb-5")
        ]),
        dbc.Row([
            dbc.Col([create_segment_chart(get_segment_metrics(df, rfm_data))], md=12)
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