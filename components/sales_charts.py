# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from dash import html, dcc
# import dash_bootstrap_components as dbc
# from typing import Dict, Any
# from app import cache, chart_colors, plot_template

# def create_sales_trend_chart(filtered_data: str) -> dbc.Card:
#     """
#     Create a sales trend chart showing daily, weekly, and monthly trends
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     # Aggregate daily sales
#     daily_sales = df.groupby('InvoiceDate').agg({
#         'TotalAmount': 'sum',
#         'InvoiceNo': 'nunique',
#         'CustomerID': 'nunique'
#     }).reset_index()
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add revenue line
#     fig.add_trace(
#         go.Scatter(
#             x=daily_sales['InvoiceDate'],
#             y=daily_sales['TotalAmount'],
#             name='Revenue',
#             line=dict(color=chart_colors[0], width=2),
#             hovertemplate='Date: %{x}<br>Revenue: £%{y:,.2f}<extra></extra>'
#         )
#     )
    
#     # Add order count line
#     fig.add_trace(
#         go.Scatter(
#             x=daily_sales['InvoiceDate'],
#             y=daily_sales['InvoiceNo'],
#             name='Orders',
#             line=dict(color=chart_colors[1], width=2),
#             yaxis='y2',
#             hovertemplate='Date: %{x}<br>Orders: %{y:,.0f}<extra></extra>'
#         )
#     )
    
#     # Update layout
#     fig.update_layout(
#         title='Daily Sales Trend',
#         template=plot_template,
#         hovermode='x unified',
#         yaxis=dict(
#             title='Revenue (£)',
#             titlefont=dict(color=chart_colors[0]),
#             tickfont=dict(color=chart_colors[0])
#         ),
#         yaxis2=dict(
#             title='Number of Orders',
#             titlefont=dict(color=chart_colors[1]),
#             tickfont=dict(color=chart_colors[1]),
#             anchor='x',
#             overlaying='y',
#             side='right'
#         ),
#         showlegend=True,
#         legend=dict(
#             orientation='h',
#             yanchor='bottom',
#             y=1.02,
#             xanchor='right',
#             x=1
#         ),
#         margin=dict(l=60, r=60, t=80, b=60)
#     )
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig, style={'height': '400px'})
#         ])
#     )

# def create_sales_by_category(filtered_data: str) -> dbc.Card:
#     """
#     Create a chart showing sales distribution by product category or description group
    
#     Args:
#         filtered_data (str): JSON string of filtered DataFrame
        
#     Returns:
#         dbc.Card: Card containing the sales distribution chart
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     try:
#         # If Category exists, use it
#         if 'Category' in df.columns:
#             group_by_field = 'Category'
#         else:
#             # Create a simplified category based on the first word of Description
#             df['Category'] = df['Description'].str.split().str[0]
#             group_by_field = 'Category'
        
#         # Group by category
#         category_sales = df.groupby(group_by_field).agg({
#             'TotalAmount': 'sum',
#             'InvoiceNo': 'nunique'
#         }).reset_index()
        
#         # Sort by total amount
#         category_sales = category_sales.sort_values('TotalAmount', ascending=True)
        
#         # Take top 10 categories
#         category_sales = category_sales.nlargest(10, 'TotalAmount')
        
#         # Create horizontal bar chart
#         fig = go.Figure()
        
#         # Add revenue bars
#         fig.add_trace(
#             go.Bar(
#                 y=category_sales[group_by_field],
#                 x=category_sales['TotalAmount'],
#                 name='Revenue',
#                 orientation='h',
#                 marker_color=chart_colors[0],
#                 hovertemplate='%{y}<br>Revenue: £%{x:,.2f}<extra></extra>'
#             )
#         )
        
#         # Update layout
#         fig.update_layout(
#             title='Top 10 Product Categories by Revenue',
#             template=plot_template,
#             xaxis_title='Revenue (£)',
#             showlegend=False,
#             margin=dict(l=160, r=40, t=80, b=60),
#             height=400
#         )
        
#         return dbc.Card(
#             dbc.CardBody([
#                 dcc.Graph(figure=fig)
#             ])
#         )
        
#     except Exception as e:
#         print(f"Error creating sales by category chart: {e}")
#         # Return empty card with message if there's an error
#         return dbc.Card(
#             dbc.CardBody([
#                 html.P("Unable to create category analysis chart", 
#                       className="text-muted text-center")
#             ])
#         )


# def create_hourly_sales_pattern(filtered_data: str) -> dbc.Card:
#     """
#     Create a heatmap showing hourly sales patterns by day of week
#     """
#     df = pd.read_json(filtered_data, orient='split')
    
#     # Create hour and day of week fields
#     hourly_pattern = df.groupby(['DayOfWeek', 'Hour']).agg({
#         'TotalAmount': 'sum'
#     }).reset_index()
    
#     # Pivot data for heatmap
#     pivot_data = hourly_pattern.pivot(
#         index='DayOfWeek',
#         columns='Hour',
#         values='TotalAmount'
#     )
    
#     # Create heatmap
#     fig = go.Figure(data=go.Heatmap(
#         z=pivot_data.values,
#         x=pivot_data.columns,
#         y=pivot_data.index,
#         colorscale='Blues',
#         hoverongaps=False,
#         hovertemplate='Day: %{y}<br>Hour: %{x}:00<br>Revenue: £%{z:,.2f}<extra></extra>'
#     ))
    
#     # Update layout
#     fig.update_layout(
#         title='Hourly Sales Pattern',
#         template=plot_template,
#         xaxis_title='Hour of Day',
#         yaxis_title='Day of Week',
#         margin=dict(l=120, r=40, t=80, b=60)
#     )
    
#     return dbc.Card(
#         dbc.CardBody([
#             dcc.Graph(figure=fig)
#         ])
#     )

# def create_metrics_table(metrics: Dict[str, float]) -> dbc.Table:
#     """
#     Create a table displaying sales metrics
#     """
#     return dbc.Table([
#         html.Thead([
#             html.Tr([
#                 html.Th('Metric'),
#                 html.Th('Value')
#             ])
#         ]),
#         html.Tbody([
#             html.Tr([
#                 html.Td(metric.replace('_', ' ').title()),
#                 html.Td(f'£{value:,.2f}' if 'revenue' in metric.lower() else f'{value:,.2f}')
#             ]) for metric, value in metrics.items()
#         ])
#     ], bordered=True, hover=True, responsive=True)


# @cache.memoize(timeout=300)
# def create_sales_summary(filtered_data: str) -> dbc.Container:
#     """
#     Create a container with all sales-related charts
#     """
#     try:
#         return dbc.Container([
#             dbc.Row([
#                 dbc.Col([
#                     create_sales_trend_chart(filtered_data)
#                 ], md=12, className="mb-4")
#             ]),
#             dbc.Row([
#                 dbc.Col([
#                     create_sales_by_category(filtered_data)
#                 ], md=6),
#                 dbc.Col([
#                     create_hourly_sales_pattern(filtered_data)
#                 ], md=6)
#             ])
#         ], fluid=True)
#     except Exception as e:
#         print(f"Error creating sales summary: {e}")
#         return dbc.Container([
#             html.Div("Error loading sales analysis", 
#                     className="text-center text-muted p-5")
#         ], fluid=True)

# # Example usage
# if __name__ == "__main__":
#     from ..data.data_loader import RetailDataLoader
    
#     # Load and process the data
#     loader = RetailDataLoader("data/raw/Online Retail.xlsx")
#     df = loader.process_data()
    
#     # Create the sales summary
#     sales_charts = create_sales_summary(df.to_json(date_format='iso', orient='split'))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any
from app import cache, chart_colors, plot_template
import logging

# Set up logging
logger = logging.getLogger(__name__)

def create_sales_trend_chart(filtered_data: str) -> dbc.Card:
    """
    Create a sales trend chart showing daily, weekly, and monthly trends
    """
    try:
        df = pd.read_json(filtered_data, orient='split')
        
        # Aggregate daily sales
        daily_sales = df.groupby('InvoiceDate').agg({
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        # Create the figure
        fig = go.Figure()
        
        # Add revenue line
        fig.add_trace(
            go.Scatter(
                x=daily_sales['InvoiceDate'],
                y=daily_sales['TotalAmount'],
                name='Revenue',
                line=dict(color=chart_colors[0], width=2),
                hovertemplate='Date: %{x}<br>Revenue: £%{y:,.2f}<extra></extra>'
            )
        )
        
        # Add order count line
        fig.add_trace(
            go.Scatter(
                x=daily_sales['InvoiceDate'],
                y=daily_sales['InvoiceNo'],
                name='Orders',
                line=dict(color=chart_colors[1], width=2),
                yaxis='y2',
                hovertemplate='Date: %{x}<br>Orders: %{y:,.0f}<extra></extra>'
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Daily Sales Trend',
            template=plot_template,
            hovermode='x unified',
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
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=60, r=60, t=80, b=60)
        )
        
        return dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig, style={'height': '400px'})
            ])
        )
    except Exception as e:
        logger.error(f"Error creating sales trend chart: {str(e)}")
        return dbc.Card(
            dbc.CardBody([
                html.P("Error creating sales trend chart", className="text-danger text-center")
            ])
        )

def create_sales_by_category(filtered_data: str) -> dbc.Card:
    """
    Create a chart showing sales distribution by product category or description group
    """
    try:
        df = pd.read_json(filtered_data, orient='split')
        
        # If Category exists, use it
        if 'Category' in df.columns:
            group_by_field = 'Category'
        else:
            # Create a simplified category based on the first word of Description
            df['Category'] = df['Description'].str.split().str[0]
            group_by_field = 'Category'
        
        # Group by category
        category_sales = df.groupby(group_by_field).agg({
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        # Sort by total amount
        category_sales = category_sales.sort_values('TotalAmount', ascending=True)
        
        # Take top 10 categories
        category_sales = category_sales.nlargest(10, 'TotalAmount')
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add revenue bars
        fig.add_trace(
            go.Bar(
                y=category_sales[group_by_field],
                x=category_sales['TotalAmount'],
                name='Revenue',
                orientation='h',
                marker_color=chart_colors[0],
                hovertemplate='%{y}<br>Revenue: £%{x:,.2f}<extra></extra>'
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Top 10 Product Categories by Revenue',
            template=plot_template,
            xaxis_title='Revenue (£)',
            showlegend=False,
            margin=dict(l=160, r=40, t=80, b=60),
            height=400
        )
        
        return dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig)
            ])
        )
        
    except Exception as e:
        logger.error(f"Error creating sales by category chart: {str(e)}")
        return dbc.Card(
            dbc.CardBody([
                html.P("Unable to create category analysis chart", 
                      className="text-danger text-center")
            ])
        )

# def create_hourly_sales_pattern(filtered_data: str) -> dbc.Card:
#     """
#     Create a heatmap showing hourly sales patterns by day of week
#     """
#     try:
#         df = pd.read_json(filtered_data, orient='split')
        
#         # Add DayOfWeek and Hour fields
#         df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
#         df['Hour'] = df['InvoiceDate'].dt.hour
        
#         # Group by DayOfWeek and Hour
#         hourly_pattern = df.groupby(['DayOfWeek', 'Hour']).agg({
#             'TotalAmount': 'sum'
#         }).reset_index()
        
#         # Ensure proper day of week order
#         day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#         hourly_pattern['DayOfWeek'] = pd.Categorical(hourly_pattern['DayOfWeek'], 
#                                                    categories=day_order, 
#                                                    ordered=True)
        
#         # Pivot data for heatmap
#         pivot_data = hourly_pattern.pivot(
#             index='DayOfWeek',
#             columns='Hour',
#             values='TotalAmount'
#         )
        
#         # Create heatmap
#         fig = go.Figure(data=go.Heatmap(
#             z=pivot_data.values,
#             x=pivot_data.columns,
#             y=pivot_data.index,
#             colorscale='Blues',
#             hoverongaps=False,
#             hovertemplate='Day: %{y}<br>Hour: %{x}:00<br>Revenue: £%{z:,.2f}<extra></extra>'
#         ))
        
#         # Update layout
#         fig.update_layout(
#             title='Hourly Sales Pattern',
#             template=plot_template,
#             xaxis_title='Hour of Day',
#             yaxis_title='Day of Week',
#             margin=dict(l=120, r=40, t=80, b=60)
#         )
        
#         return dbc.Card(
#             dbc.CardBody([
#                 dcc.Graph(figure=fig)
#             ])
#         )
#     except Exception as e:
#         logger.error(f"Error creating hourly sales pattern: {str(e)}")
#         return dbc.Card(
#             dbc.CardBody([
#                 html.P("Error creating hourly sales pattern", className="text-danger text-center")
#             ])
#         )

def create_hourly_sales_pattern(filtered_data: str) -> dbc.Card:
    """
    Create a heatmap showing hourly sales patterns by day of week
    """
    try:
        # Load the data and properly parse dates
        df = pd.read_json(filtered_data, orient='split')
        
        # Convert InvoiceDate to datetime explicitly
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='ISO8601')
        
        # Extract day of week and hour
        df['DayOfWeek'] = df['InvoiceDate'].dt.strftime('%A')  # Full day name
        df['Hour'] = df['InvoiceDate'].dt.hour
        
        # Define day order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Group by DayOfWeek and Hour, calculating total amount
        hourly_pattern = df.groupby(['DayOfWeek', 'Hour'])['TotalAmount'].sum().reset_index()
        
        # Convert DayOfWeek to categorical with proper order
        hourly_pattern['DayOfWeek'] = pd.Categorical(
            hourly_pattern['DayOfWeek'],
            categories=day_order,
            ordered=True
        )
        
        # Sort by the categorical order
        hourly_pattern = hourly_pattern.sort_values('DayOfWeek')
        
        # Create pivot table for heatmap
        pivot_table = hourly_pattern.pivot(
            index='DayOfWeek',
            columns='Hour',
            values='TotalAmount'
        )
        
        # Fill any missing hours with 0
        pivot_table = pivot_table.fillna(0)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=day_order,
            colorscale='Blues',
            hoverongaps=False,
            hovertemplate=(
                'Day: %{y}<br>' +
                'Hour: %{x}:00<br>' +
                'Revenue: £%{z:,.2f}' +
                '<extra></extra>'
            )
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Sales by Day and Hour',
                'x': 0.5,
                'xanchor': 'center'
            },
            template=plot_template,
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            xaxis=dict(
                tickmode='array',
                ticktext=[f'{h:02d}:00' for h in range(24)],
                tickvals=list(range(24))
            ),
            margin=dict(l=120, r=40, t=80, b=60),
            height=400
        )
        
        return dbc.Card([
            dbc.CardHeader("Hourly Sales Pattern"),
            dbc.CardBody([
                dcc.Graph(
                    figure=fig,
                    config={'displayModeBar': True}
                )
            ])
        ])
        
    except Exception as e:
        import traceback
        error_msg = f"Error creating hourly sales pattern: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        
        return dbc.Card([
            dbc.CardHeader("Hourly Sales Pattern"),
            dbc.CardBody([
                dbc.Alert(
                    [
                        html.H4("Error Creating Chart", className="alert-heading"),
                        html.P("An error occurred while creating the hourly sales pattern chart."),
                        html.Hr(),
                        html.P(str(e), className="mb-0")
                    ],
                    color="danger"
                )
            ])
        ])
        
def create_metrics_table(metrics: Dict[str, Any]) -> dbc.Table:
    """
    Create a table displaying sales metrics
    """
    try:
        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th('Metric'),
                    html.Th('Value')
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(metric.replace('_', ' ').title()),
                    html.Td(f'£{value:,.2f}' if 'revenue' in metric.lower() else f'{value:,.2f}')
                ]) for metric, value in metrics.items()
            ])
        ], bordered=True, hover=True, responsive=True)
    except Exception as e:
        logger.error(f"Error creating metrics table: {str(e)}")
        return html.P("Error creating metrics table", className="text-danger")

@cache.memoize(timeout=300)
def create_sales_summary(filtered_data: str) -> dbc.Container:
    """
    Create a container with all sales-related charts
    """
    try:
        # Load and validate data
        df = pd.read_json(filtered_data, orient='split')
        
        # Ensure datetime conversion
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='ISO8601')
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    create_sales_trend_chart(filtered_data)
                ], md=12, className="mb-4")
            ]),
            dbc.Row([
                dbc.Col([
                    create_sales_by_category(filtered_data)
                ], md=6),
                dbc.Col([
                    create_hourly_sales_pattern(filtered_data)
                ], md=6)
            ])
        ], fluid=True)
    except Exception as e:
        print(f"Error creating sales summary: {str(e)}")
        return dbc.Container([
            dbc.Alert(
                [
                    html.H4("Error Loading Sales Analysis", className="alert-heading"),
                    html.P("An error occurred while loading the sales analysis."),
                    html.Hr(),
                    html.P(str(e), className="mb-0")
                ],
                color="danger",
                className="m-4"
            )
        ], fluid=True)

# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample data
    try:
        from data.data_loader import RetailDataLoader
        
        # Load and process the data
        loader = RetailDataLoader("data/raw/Online Retail.xlsx")
        df = loader.load_data()
        
        if df is not None:
            # Create the sales summary
            sales_charts = create_sales_summary(df.to_json(date_format='iso', orient='split'))
            print("Sales charts created successfully")
    except Exception as e:
        logger.error(f"Error in test run: {str(e)}")