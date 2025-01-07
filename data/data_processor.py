import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailDataProcessor:
    """
    Class for processing and transforming retail data for analysis
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the data processor with a DataFrame
        
        Args:
            df (pd.DataFrame): Input DataFrame containing retail data
        """
        self.raw_data = df.copy()
        self.processed_data = None

    def process_transactions(self) -> pd.DataFrame:
        """
        Process transaction data with advanced transformations
        
        Returns:
            pd.DataFrame: Processed transaction data
        """
        df = self.raw_data.copy()
        
        # Calculate transaction-level metrics
        df['TransactionValue'] = df['Quantity'] * df['UnitPrice']
        df['ItemCount'] = df.groupby('InvoiceNo')['Quantity'].transform('sum')
        df['UniqueItems'] = df.groupby('InvoiceNo')['StockCode'].transform('nunique')
        
        # Calculate average item price per transaction
        df['AvgItemPrice'] = df.groupby('InvoiceNo')['UnitPrice'].transform('mean')
        
        # Flag high-value transactions (top 10%)
        value_threshold = df.groupby('InvoiceNo')['TransactionValue'].transform('sum').quantile(0.9)
        df['IsHighValue'] = df.groupby('InvoiceNo')['TransactionValue'].transform('sum') > value_threshold
        
        return df

    def calculate_product_metrics(self) -> pd.DataFrame:
        """
        Calculate product-level metrics and indicators
        
        Returns:
            pd.DataFrame: DataFrame with product metrics
        """
        df = self.processed_data if self.processed_data is not None else self.raw_data
        
        product_metrics = df.groupby('StockCode').agg({
            'Description': 'first',
            'Quantity': ['sum', 'mean', 'std'],
            'UnitPrice': 'mean',
            'TransactionValue': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        # Flatten column names
        product_metrics.columns = ['StockCode', 'Description', 'TotalQuantity', 
                                 'AvgQuantity', 'StdQuantity', 'AvgPrice',
                                 'TotalRevenue', 'TransactionCount', 'CustomerCount']
        
        # Calculate additional metrics
        product_metrics['RevenuePerCustomer'] = (product_metrics['TotalRevenue'] / 
                                               product_metrics['CustomerCount'])
        product_metrics['TransactionsPerCustomer'] = (product_metrics['TransactionCount'] / 
                                                    product_metrics['CustomerCount'])
        
        return product_metrics

    def analyze_customer_behavior(self) -> pd.DataFrame:
        """
        Perform detailed customer behavior analysis
        
        Returns:
            pd.DataFrame: DataFrame with customer behavior metrics
        """
        df = self.processed_data if self.processed_data is not None else self.raw_data
        
        # Calculate customer-level metrics
        customer_metrics = df.groupby('CustomerID').agg({
            'InvoiceNo': 'nunique',
            'TransactionValue': 'sum',
            'InvoiceDate': ['min', 'max'],
            'StockCode': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        # Flatten column names
        customer_metrics.columns = ['CustomerID', 'TransactionCount', 'TotalSpend',
                                  'FirstPurchase', 'LastPurchase', 'UniqueProducts',
                                  'TotalItems']
        
        # Calculate customer lifecycle metrics
        customer_metrics['CustomerAge'] = (customer_metrics['LastPurchase'] - 
                                         customer_metrics['FirstPurchase']).dt.days
        customer_metrics['AvgTransactionValue'] = (customer_metrics['TotalSpend'] / 
                                                 customer_metrics['TransactionCount'])
        customer_metrics['PurchaseFrequency'] = (customer_metrics['TransactionCount'] / 
                                               customer_metrics['CustomerAge'])
        
        return customer_metrics

    def calculate_temporal_metrics(self) -> Dict[str, pd.DataFrame]:
        """
        Calculate various time-based metrics
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing different temporal analyses
        """
        df = self.processed_data if self.processed_data is not None else self.raw_data
        
        # Daily metrics
        daily_metrics = df.groupby(df['InvoiceDate'].dt.date).agg({
            'TransactionValue': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        # Weekly metrics
        weekly_metrics = df.groupby(pd.Grouper(key='InvoiceDate', freq='W')).agg({
            'TransactionValue': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        # Monthly metrics
        monthly_metrics = df.groupby(pd.Grouper(key='InvoiceDate', freq='M')).agg({
            'TransactionValue': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        return {
            'daily': daily_metrics,
            'weekly': weekly_metrics,
            'monthly': monthly_metrics
        }

    def analyze_product_combinations(self) -> pd.DataFrame:
        """
        Analyze product combinations and calculate co-occurrence patterns
        
        Returns:
            pd.DataFrame: Product combination analysis results
        """
        df = self.processed_data if self.processed_data is not None else self.raw_data
        
        # Create transaction-product matrix
        transaction_matrix = pd.crosstab(df['InvoiceNo'], df['StockCode'])
        
        # Calculate product co-occurrence
        product_combinations = []
        products = transaction_matrix.columns
        
        for i in range(len(products)):
            for j in range(i + 1, len(products)):
                prod1, prod2 = products[i], products[j]
                co_occurrences = ((transaction_matrix[prod1] > 0) & 
                                (transaction_matrix[prod2] > 0)).sum()
                
                if co_occurrences > 0:
                    support = co_occurrences / len(transaction_matrix)
                    confidence = co_occurrences / (transaction_matrix[prod1] > 0).sum()
                    
                    product_combinations.append({
                        'Product1': prod1,
                        'Product2': prod2,
                        'CoOccurrences': co_occurrences,
                        'Support': support,
                        'Confidence': confidence
                    })
        
        return pd.DataFrame(product_combinations)

    def process_data(self) -> pd.DataFrame:
        """
        Execute the complete data processing pipeline
        
        Returns:
            pd.DataFrame: Fully processed DataFrame
        """
        logger.info("Starting advanced data processing pipeline")
        
        try:
            # Process transactions
            self.processed_data = self.process_transactions()
            logger.info("Transaction processing completed")
            
            # Add temporal features
            self.processed_data['DayOfWeek'] = self.processed_data['InvoiceDate'].dt.day_name()
            self.processed_data['Month'] = self.processed_data['InvoiceDate'].dt.month
            self.processed_data['Quarter'] = self.processed_data['InvoiceDate'].dt.quarter
            self.processed_data['Year'] = self.processed_data['InvoiceDate'].dt.year
            self.processed_data['Hour'] = self.processed_data['InvoiceDate'].dt.hour
            logger.info("Temporal features added")
            
            # Add transaction complexity indicators
            self.processed_data['IsComplexTransaction'] = (
                self.processed_data['UniqueItems'] > 
                self.processed_data['UniqueItems'].median()
            )
            
            # Add customer value indicators
            customer_metrics = self.analyze_customer_behavior()
            self.processed_data = self.processed_data.merge(
                customer_metrics[['CustomerID', 'CustomerAge', 'PurchaseFrequency']],
                on='CustomerID',
                how='left'
            )
            
            logger.info("Data processing pipeline completed successfully")
            return self.processed_data
            
        except Exception as e:
            logger.error(f"Error in data processing pipeline: {str(e)}")
            raise

    def get_summary_statistics(self) -> Dict[str, float]:
        """
        Calculate summary statistics for the processed data
        
        Returns:
            Dict[str, float]: Dictionary containing summary statistics
        """
        if self.processed_data is None:
            raise ValueError("Data not processed. Call process_data() first.")
            
        summary_stats = {
            'total_revenue': self.processed_data['TransactionValue'].sum(),
            'avg_transaction_value': self.processed_data.groupby('InvoiceNo')['TransactionValue'].sum().mean(),
            'total_transactions': self.processed_data['InvoiceNo'].nunique(),
            'total_customers': self.processed_data['CustomerID'].nunique(),
            'avg_items_per_transaction': self.processed_data.groupby('InvoiceNo')['Quantity'].sum().mean(),
            'total_quantity_sold': self.processed_data['Quantity'].sum()
        }
        
        return summary_stats

# Example usage
if __name__ == "__main__":
    from data_loader import RetailDataLoader
    
    # Load the actual retail data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    raw_df = loader.load_data()
    
    if raw_df is not None:
        # Initialize the processor with actual data
        processor = RetailDataProcessor(raw_df)
        
        # Process the data
        processed_df = processor.process_data()
        
        # Print summary statistics
        print("\nSummary Statistics:")
        for metric, value in processor.get_summary_statistics().items():
            print(f"{metric}: {value:,.2f}")
            
        # Print additional metrics
        product_metrics = processor.calculate_product_metrics()
        print("\nTop 5 Products by Revenue:")
        print(product_metrics.nlargest(5, 'TotalRevenue')[['Description', 'TotalRevenue', 'CustomerCount']])
        
        customer_metrics = processor.analyze_customer_behavior()
        print("\nCustomer Behavior Summary:")
        print(customer_metrics.describe())