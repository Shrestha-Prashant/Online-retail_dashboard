import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailCalculations:
    """Class containing calculation methods for retail analytics"""
    
    @staticmethod
    def calculate_revenue_metrics(df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate key revenue metrics
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            Dict[str, float]: Dictionary of revenue metrics
        """
        try:
            metrics = {
                'total_revenue': df['TotalAmount'].sum(),
                'average_order_value': df.groupby('InvoiceNo')['TotalAmount'].sum().mean(),
                'median_order_value': df.groupby('InvoiceNo')['TotalAmount'].sum().median(),
                'revenue_per_customer': df.groupby('CustomerID')['TotalAmount'].sum().mean(),
                'total_orders': df['InvoiceNo'].nunique(),
                'total_customers': df['CustomerID'].nunique()
            }
            
            # Calculate growth metrics if data spans multiple periods
            if len(df['InvoiceDate'].dt.to_period('M').unique()) > 1:
                monthly_revenue = df.groupby(df['InvoiceDate'].dt.to_period('M'))['TotalAmount'].sum()
                metrics['mom_growth'] = ((monthly_revenue.iloc[-1] / monthly_revenue.iloc[-2]) - 1) * 100
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating revenue metrics: {str(e)}")
            raise

    @staticmethod
    def calculate_customer_metrics(df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate customer-related metrics
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            Dict[str, float]: Dictionary of customer metrics
        """
        try:
            # Customer purchase frequency
            customer_orders = df.groupby('CustomerID')['InvoiceNo'].nunique()
            customer_first_purchase = df.groupby('CustomerID')['InvoiceDate'].min()
            customer_last_purchase = df.groupby('CustomerID')['InvoiceDate'].max()
            customer_lifespan = (customer_last_purchase - customer_first_purchase).dt.days

            metrics = {
                'avg_purchase_frequency': customer_orders.mean(),
                'median_purchase_frequency': customer_orders.median(),
                'avg_customer_lifespan': customer_lifespan.mean(),
                'avg_items_per_customer': df.groupby('CustomerID')['Quantity'].sum().mean(),
                'customer_retention_rate': (len(customer_orders[customer_orders > 1]) / 
                                         len(customer_orders) * 100)
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating customer metrics: {str(e)}")
            raise

    @staticmethod
    def calculate_product_metrics(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calculate product performance metrics
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of product metric DataFrames
        """
        try:
            # Product performance
            product_metrics = df.groupby(['StockCode', 'Description']).agg({
                'Quantity': ['sum', 'mean'],
                'TotalAmount': 'sum',
                'CustomerID': 'nunique',
                'InvoiceNo': 'nunique'
            }).reset_index()

            # Flatten column names
            product_metrics.columns = ['StockCode', 'Description', 'TotalQuantity', 
                                     'AvgQuantity', 'TotalRevenue', 'UniqueCustomers',
                                     'TransactionCount']

            # Calculate additional metrics
            product_metrics['RevenuePerTransaction'] = (product_metrics['TotalRevenue'] / 
                                                      product_metrics['TransactionCount'])
            product_metrics['CustomerPenetration'] = (product_metrics['UniqueCustomers'] / 
                                                    df['CustomerID'].nunique() * 100)

            # Product correlations
            purchase_matrix = pd.crosstab(df['InvoiceNo'], df['StockCode'])
            correlation_matrix = purchase_matrix.corr()

            return {
                'product_metrics': product_metrics,
                'correlation_matrix': correlation_matrix
            }
        except Exception as e:
            logger.error(f"Error calculating product metrics: {str(e)}")
            raise

    @staticmethod
    def calculate_rfm_metrics(df: pd.DataFrame, reference_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) metrics
        
        Args:
            df (pd.DataFrame): Input DataFrame
            reference_date (datetime, optional): Reference date for recency calculation
            
        Returns:
            pd.DataFrame: RFM metrics DataFrame
        """
        try:
            if reference_date is None:
                reference_date = df['InvoiceDate'].max()

            # Calculate RFM metrics
            rfm = df.groupby('CustomerID').agg({
                'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
                'InvoiceNo': 'nunique',                                    # Frequency
                'TotalAmount': 'sum'                                       # Monetary
            }).reset_index()

            rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

            # Calculate RFM scores
            rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
            rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
            rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])

            # Calculate RFM Score and Segment
            rfm['RFM_Score'] = (rfm['R_Score'].astype(str) + 
                              rfm['F_Score'].astype(str) + 
                              rfm['M_Score'].astype(str))

            def get_segment(row):
                r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
                if r >= 4 and f >= 4 and m >= 4:
                    return 'Champions'
                elif r >= 3 and f >= 3 and m >= 3:
                    return 'Loyal Customers'
                elif r >= 3:
                    return 'Recent Customers'
                elif f >= 3:
                    return 'Regular Customers'
                elif m >= 3:
                    return 'Big Spenders'
                else:
                    return 'Lost Customers'

            rfm['Customer_Segment'] = rfm.apply(get_segment, axis=1)
            
            return rfm
        except Exception as e:
            logger.error(f"Error calculating RFM metrics: {str(e)}")
            raise

    @staticmethod
    def calculate_time_based_metrics(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calculate time-based performance metrics
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of time-based metric DataFrames
        """
        try:
            # Daily metrics
            daily_metrics = df.groupby(df['InvoiceDate'].dt.date).agg({
                'TotalAmount': 'sum',
                'InvoiceNo': 'nunique',
                'CustomerID': 'nunique',
                'Quantity': 'sum'
            }).reset_index()

            # Calculate moving averages
            daily_metrics['Revenue_MA7'] = daily_metrics['TotalAmount'].rolling(window=7).mean()
            daily_metrics['Orders_MA7'] = daily_metrics['InvoiceNo'].rolling(window=7).mean()

            # Hourly patterns
            hourly_metrics = df.groupby([df['InvoiceDate'].dt.dayofweek, 
                                       df['InvoiceDate'].dt.hour]).agg({
                'TotalAmount': ['sum', 'mean'],
                'InvoiceNo': 'nunique'
            }).reset_index()

            # Seasonal patterns
            seasonal_metrics = df.groupby([df['InvoiceDate'].dt.month, 
                                         df['InvoiceDate'].dt.day]).agg({
                'TotalAmount': ['sum', 'mean'],
                'InvoiceNo': 'nunique'
            }).reset_index()

            return {
                'daily_metrics': daily_metrics,
                'hourly_metrics': hourly_metrics,
                'seasonal_metrics': seasonal_metrics
            }
        except Exception as e:
            logger.error(f"Error calculating time-based metrics: {str(e)}")
            raise

    @staticmethod
    def calculate_basket_metrics(df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate basket analysis metrics
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            Dict[str, float]: Dictionary of basket metrics
        """
        try:
            # Calculate basket-level metrics
            basket_sizes = df.groupby('InvoiceNo').agg({
                'StockCode': 'nunique',
                'Quantity': 'sum',
                'TotalAmount': 'sum'
            })

            metrics = {
                'avg_basket_size': basket_sizes['StockCode'].mean(),
                'median_basket_size': basket_sizes['StockCode'].median(),
                'avg_basket_value': basket_sizes['TotalAmount'].mean(),
                'median_basket_value': basket_sizes['TotalAmount'].median(),
                'avg_items_per_basket': basket_sizes['Quantity'].mean(),
                'median_items_per_basket': basket_sizes['Quantity'].median()
            }

            return metrics
        except Exception as e:
            logger.error(f"Error calculating basket metrics: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load the actual retail data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.load_data()
    
    if df is not None:
        # Clean and prepare data
        df = df[df['Quantity'] > 0]  # Remove cancelled orders
        df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
        
        # Calculate various metrics
        print("\nRevenue Metrics:")
        revenue_metrics = RetailCalculations.calculate_revenue_metrics(df)
        for metric, value in revenue_metrics.items():
            print(f"{metric}: {value:,.2f}")
            
        print("\nCustomer Metrics:")
        customer_metrics = RetailCalculations.calculate_customer_metrics(df)
        for metric, value in customer_metrics.items():
            print(f"{metric}: {value:,.2f}")
            
        print("\nBasket Metrics:")
        basket_metrics = RetailCalculations.calculate_basket_metrics(df)
        for metric, value in basket_metrics.items():
            print(f"{metric}: {value:,.2f}")
            
        # Calculate RFM metrics
        rfm_metrics = RetailCalculations.calculate_rfm_metrics(df)
        print("\nCustomer Segments Distribution:")
        print(rfm_metrics['Customer_Segment'].value_counts())