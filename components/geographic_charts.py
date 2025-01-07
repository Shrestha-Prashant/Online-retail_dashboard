# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from dash import html, dcc
# import dash_bootstrap_components as dbc
# from app import cache, chart_colors, plot_template

# def create_country_sales_map(filtered_data: str) -> dbc.Card:
#     """
#     Create a choropleth map showing sales by country
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     # Aggregate sales by country
#     country_sales = df.groupby('Country').agg({
#         'TotalAmount': 'sum',
#         'InvoiceNo': 'nunique',
#         'CustomerID': 'nunique'
#     }).reset_index()
    
#     # Create the choropleth map
#     fig = px.choropleth(
#         country_sales,
#         locations='Country',
#         locationmode='country names',
#         color='TotalAmount',
#         hover_data=['InvoiceNo', 'CustomerID'],
#         color_continuous_scale='Blues',
#         labels={
#             'TotalAmount': 'Revenue (£)',
#             'InvoiceNo': 'Orders',
#             'CustomerID': 'Customers'
#         },
#         title='Revenue Distribution by Country'
#     )
    
#     # Update layout
#     fig.update_layout(
#         template=plot_template,
#         margin=dict(l=0, r=0, t=40, b=0),
#         height=500,
#         coloraxis_colorbar_title='Revenue (£)'
#     )
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig)
#         ])
#     )

# def create_country_performance_chart(filtered_data: str) -> dbc.Card:
#     """
#     Create a detailed country performance analysis
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     # Calculate metrics by country
#     country_metrics = df.groupby('Country').agg({
#         'TotalAmount': 'sum',
#         'InvoiceNo': 'nunique',
#         'CustomerID': 'nunique',
#         'Quantity': 'sum'
#     }).reset_index()
    
#     # Calculate average order value
#     country_metrics['AvgOrderValue'] = country_metrics['TotalAmount'] / country_metrics['InvoiceNo']
    
#     # Sort by total amount
#     country_metrics = country_metrics.sort_values('TotalAmount', ascending=True)
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add revenue bars
#     fig.add_trace(
#         go.Bar(
#             y=country_metrics['Country'],
#             x=country_metrics['TotalAmount'],
#             name='Revenue',
#             orientation='h',
#             marker_color=chart_colors[0]
#         )
#     )
    
#     # Add average order value line
#     fig.add_trace(
#         go.Scatter(
#             y=country_metrics['Country'],
#             x=country_metrics['AvgOrderValue'],
#             name='Avg Order Value',
#             mode='markers+lines',
#             marker=dict(color=chart_colors[1], size=8),
#             xaxis='x2'
#         )
#     )
    
#     # Update layout
#     fig.update_layout(
#         title='Country Performance Analysis',
#         template=plot_template,
#         xaxis=dict(
#             title='Total Revenue (£)',
#             titlefont=dict(color=chart_colors[0]),
#             tickfont=dict(color=chart_colors[0]),
#             side='bottom'
#         ),
#         xaxis2=dict(
#             title='Average Order Value (£)',
#             titlefont=dict(color=chart_colors[1]),
#             tickfont=dict(color=chart_colors[1]),
#             anchor='y',
#             overlaying='x',
#             side='top'
#         ),
#         showlegend=True,
#         legend=dict(
#             orientation='h',
#             yanchor='bottom',
#             y=1.02,
#             xanchor='right',
#             x=1
#         ),
#         margin=dict(l=150, r=100, t=100, b=60),
#         height=600
#     )
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig)
#         ])
#     )

# def create_regional_time_analysis(filtered_data: str) -> dbc.Card:
#     """
#     Create time-based analysis by region
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     # Aggregate monthly sales by country
#     regional_time = df.groupby(['Country', 'MonthYear']).agg({
#         'TotalAmount': 'sum'
#     }).reset_index()
    
#     # Create line chart
#     fig = px.line(
#         regional_time,
#         x='MonthYear',
#         y='TotalAmount',
#         color='Country',
#         title='Regional Sales Trends',
#         labels={
#             'MonthYear': 'Month',
#             'TotalAmount': 'Revenue (£)',
#             'Country': 'Country'
#         },
#         template=plot_template,
#         color_discrete_sequence=chart_colors
#     )
    
#     # Update layout
#     fig.update_layout(
#         xaxis_title='Month',
#         yaxis_title='Revenue (£)',
#         legend_title='Country',
#         hovermode='x unified',
#         margin=dict(l=60, r=40, t=80, b=60),
#         showlegend=True,
#         legend=dict(
#             orientation='h',
#             yanchor='bottom',
#             y=1.02,
#             xanchor='right',
#             x=1
#         )
#     )
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig)
#         ])
#     )

# @cache.memoize(timeout=300)
# def create_geographic_summary(filtered_data: str) -> dbc.Container:
#     """
#     Create a container with all geography-related charts
#     """
#     return dbc.Container([
#         dbc.Row([
#             dbc.Col([
#                 create_country_sales_map(filtered_data)
#             ], md=12, className="mb-4")
#         ]),
#         dbc.Row([
#             dbc.Col([
#                 create_country_performance_chart(filtered_data)
#             ], md=12, className="mb-4")
#         ]),
#         dbc.Row([
#             dbc.Col([
#                 create_regional_time_analysis(filtered_data)
#             ], md=12)
#         ])
#     ], fluid=True)

# # Example usage
# if __name__ == "__main__":
#     from ..data.data_loader import RetailDataLoader
    
#     # Load and process the data
#     loader = RetailDataLoader("data/raw/Online Retail.xlsx")
#     df = loader.process_data()
    
#     # Create the geographic summary
#     geographic_charts = create_geographic_summary(df.to_json(date_format='iso', orient='split'))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import dash_bootstrap_components as dbc
from app import cache, chart_colors, plot_template
from typing import Optional

def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the dataframe to ensure all required columns are present and properly formatted
    """
    try:
        # Create MonthYear if it doesn't exist
        if 'MonthYear' not in df.columns and 'InvoiceDate' in df.columns:
            df['MonthYear'] = pd.to_datetime(df['InvoiceDate']).dt.strftime('%Y-%m')
        
        # Ensure TotalAmount exists
        if 'TotalAmount' not in df.columns and 'Quantity' in df.columns and 'UnitPrice' in df.columns:
            df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
        
        return df
    except Exception as e:
        raise ValueError(f"Error processing dataframe: {str(e)}")

def create_country_sales_map(filtered_data: str) -> dbc.Card:
    """
    Create a choropleth map showing sales by country
    """
    try:
        df = pd.read_json(filtered_data, orient='split')
        df = process_dataframe(df)
        
        # Aggregate sales by country
        country_sales = df.groupby('Country').agg({
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        # Create the choropleth map
        fig = px.choropleth(
            country_sales,
            locations='Country',
            locationmode='country names',
            color='TotalAmount',
            hover_data=['InvoiceNo', 'CustomerID'],
            color_continuous_scale='Blues',
            labels={
                'TotalAmount': 'Revenue (£)',
                'InvoiceNo': 'Orders',
                'CustomerID': 'Customers'
            },
            title='Revenue Distribution by Country'
        )
        
        # Update layout
        fig.update_layout(
            template=plot_template,
            margin=dict(l=0, r=0, t=40, b=0),
            height=500,
            coloraxis_colorbar_title='Revenue (£)'
        )
        
        return dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig)
            ])
        )
    except Exception as e:
        return dbc.Card(
            dbc.CardBody([
                html.H5("Error Loading Country Sales Map", className="text-danger"),
                html.P(f"Error details: {str(e)}")
            ])
        )

def create_country_performance_chart(filtered_data: str) -> dbc.Card:
    """
    Create a detailed country performance analysis
    """
    try:
        df = pd.read_json(filtered_data, orient='split')
        df = process_dataframe(df)
        
        # Calculate metrics by country
        country_metrics = df.groupby('Country').agg({
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        # Calculate average order value
        country_metrics['AvgOrderValue'] = country_metrics['TotalAmount'] / country_metrics['InvoiceNo']
        
        # Sort by total amount
        country_metrics = country_metrics.sort_values('TotalAmount', ascending=True)
        
        # Create the figure
        fig = go.Figure()
        
        # Add revenue bars
        fig.add_trace(
            go.Bar(
                y=country_metrics['Country'],
                x=country_metrics['TotalAmount'],
                name='Revenue',
                orientation='h',
                marker_color=chart_colors[0]
            )
        )
        
        # Add average order value line
        fig.add_trace(
            go.Scatter(
                y=country_metrics['Country'],
                x=country_metrics['AvgOrderValue'],
                name='Avg Order Value',
                mode='markers+lines',
                marker=dict(color=chart_colors[1], size=8),
                xaxis='x2'
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Country Performance Analysis',
            template=plot_template,
            xaxis=dict(
                title='Total Revenue (£)',
                titlefont=dict(color=chart_colors[0]),
                tickfont=dict(color=chart_colors[0]),
                side='bottom'
            ),
            xaxis2=dict(
                title='Average Order Value (£)',
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
            margin=dict(l=150, r=100, t=100, b=60),
            height=600
        )
        
        return dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig)
            ])
        )
    except Exception as e:
        return dbc.Card(
            dbc.CardBody([
                html.H5("Error Loading Country Performance Chart", className="text-danger"),
                html.P(f"Error details: {str(e)}")
            ])
        )

def create_regional_time_analysis(filtered_data: str) -> dbc.Card:
    """
    Create time-based analysis by region
    """
    try:
        # Parse the JSON data
        df = pd.read_json(filtered_data, orient='split')
        df = process_dataframe(df)
        
        if 'MonthYear' not in df.columns:
            raise ValueError("MonthYear column not found and could not be created from available data")
        
        # Aggregate monthly sales by country
        regional_time = df.groupby(['Country', 'MonthYear']).agg({
            'TotalAmount': 'sum'
        }).reset_index()
        
        # Sort by MonthYear to ensure proper timeline
        regional_time['MonthYear'] = pd.to_datetime(regional_time['MonthYear'].astype(str))
        regional_time = regional_time.sort_values('MonthYear')
        regional_time['MonthYear'] = regional_time['MonthYear'].dt.strftime('%Y-%m')
        
        # Create line chart
        fig = px.line(
            regional_time,
            x='MonthYear',
            y='TotalAmount',
            color='Country',
            title='Regional Sales Trends',
            labels={
                'MonthYear': 'Month',
                'TotalAmount': 'Revenue (£)',
                'Country': 'Country'
            },
            template=plot_template,
            color_discrete_sequence=chart_colors
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Revenue (£)',
            legend_title='Country',
            hovermode='x unified',
            margin=dict(l=60, r=40, t=80, b=60),
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
        return dbc.Card(
            dbc.CardBody([
                html.H5("Error Loading Regional Time Analysis", className="text-danger"),
                html.P(f"Error details: {str(e)}")
            ])
        )

@cache.memoize(timeout=300)
def create_geographic_summary(filtered_data: str) -> dbc.Container:
    """
    Create a container with all geography-related charts
    """
    try:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    create_country_sales_map(filtered_data)
                ], md=12, className="mb-4")
            ]),
            dbc.Row([
                dbc.Col([
                    create_country_performance_chart(filtered_data)
                ], md=12, className="mb-4")
            ]),
            dbc.Row([
                dbc.Col([
                    create_regional_time_analysis(filtered_data)
                ], md=12)
            ])
        ], fluid=True)
    except Exception as e:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Error Loading Geographic Summary", className="text-danger"),
                            html.P(f"Error details: {str(e)}")
                        ])
                    )
                ], md=12)
            ])
        ], fluid=True)

# Example usage
if __name__ == "__main__":
    from data.data_loader import RetailDataLoader
    
    # Load and process the data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.process_data()
    
    # Create the geographic summary
    geographic_charts = create_geographic_summary(df.to_json(date_format='iso', orient='split'))