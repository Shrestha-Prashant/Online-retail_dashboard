import pandas as pd
import numpy as np
import dask.dataframe as dd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import os


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailDataLoader:
    """
    Optimized data loader for retail dashboard with caching and efficient data processing
    """
    
    def __init__(self, file_path: str, cache_dir: str = 'data/processed'):
        """
        Initialize the data loader with file paths and configurations
        
        Args:
            file_path (str): Path to the Excel file
            cache_dir (str): Directory for storing processed data
        """
        self.file_path = Path(file_path)
        self.cache_dir = Path(cache_dir)
        self.parquet_path = self.cache_dir / 'retail_data.parquet'
        self.processed_data = None
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure chunk size for processing
        self.chunk_size = 100000

    # Modify get_initial_data method
    def get_initial_data(self) -> tuple:
        """Get initial data and date range"""
        try:
            df = self.load_data()
            if df is None or df.empty:
                logger.warning("No data loaded")
                return pd.DataFrame(), datetime.now(), datetime.now()
                
            start_date = df['InvoiceDate'].min()
            end_date = df['InvoiceDate'].max()
            
            return df, start_date, end_date
            
        except Exception as e:
            logger.error(f"Error getting initial data: {str(e)}")
            return pd.DataFrame(), datetime.now(), datetime.now()

    # def load_data(self, use_dask: bool = False) -> Optional[pd.DataFrame]:
    #     """
    #     Load data efficiently with caching
        
    #     Args:
    #         use_dask (bool): Whether to use Dask for large datasets
            
    #     Returns:
    #         Optional[pd.DataFrame]: Loaded DataFrame or None if loading fails
    #     """
    #     try:
    #         logger.info("Loading data...")
            
    #         # If parquet doesn't exist, load from Excel
    #         if not self.parquet_path.exists():
    #             logger.info("Parquet file not found. Loading from Excel...")
    #             df = pd.read_excel(self.file_path)
    #             df = self._process_data(df)
    #             self.processed_data = df
    #             return df
                
    #         # Load from parquet
    #         logger.info("Loading from parquet file...")
    #         if use_dask:
    #             ddf = dd.read_parquet(self.parquet_path)
    #             df = ddf.compute()
    #         else:
    #             df = pd.read_parquet(self.parquet_path)
            
    #         self.processed_data = df
    #         return df
                
    #     except Exception as e:
    #         logger.error(f"Error loading data: {str(e)}")
    #         return None 
    # Modify load_data method in RetailDataLoader class
    def load_data(self) -> pd.DataFrame:
        """Load and process data from Excel file"""
        try:
            logger.info(f"Loading data from {self.file_path}")
            df = pd.read_excel(self.file_path, parse_dates=['InvoiceDate'])
            
            # Basic cleaning
            df = df.dropna(subset=['InvoiceNo', 'Quantity', 'UnitPrice'])
            df = df[df['Quantity'] > 0]
            
            # Calculate total amount
            df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
            
            # Add date features
            df['Year'] = df['InvoiceDate'].dt.year
            df['Month'] = df['InvoiceDate'].dt.month
            df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
            df['Hour'] = df['InvoiceDate'].dt.hour
            
            self.processed_data = df
            logger.info(f"Data loaded successfully: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw data with cleaning and feature engineering
        
        Args:
            df (pd.DataFrame): Raw DataFrame
            
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        try:
            logger.info("Processing data...")
            
            # Basic cleaning
            df = df.dropna(subset=['InvoiceNo', 'Quantity', 'UnitPrice'])
            df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
            df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
            
            # Data type conversions
            df['InvoiceNo'] = df['InvoiceNo'].astype(str)
            df['StockCode'] = df['StockCode'].astype(str)
            df['CustomerID'] = pd.to_numeric(df['CustomerID'], errors='coerce')
            
            # Calculate total amount
            df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
            
            # Add date features
            df['Year'] = df['InvoiceDate'].dt.year
            df['Month'] = df['InvoiceDate'].dt.month
            df['Day'] = df['InvoiceDate'].dt.day
            df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
            df['Hour'] = df['InvoiceDate'].dt.hour
            
            # Save to parquet for future use
            logger.info("Saving processed data to parquet...")
            df.to_parquet(self.parquet_path, engine='pyarrow', index=False)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise

    def get_filtered_data(self, start_date: datetime, end_date: datetime,
                         countries: Optional[List[str]] = None,
                         categories: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get filtered data based on various criteria
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            countries (List[str], optional): List of countries
            categories (List[str], optional): List of categories
            
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        try:
            if self.processed_data is None:
                self.processed_data = self.load_data()
                
            if self.processed_data is None:
                return pd.DataFrame()
            
            df = self.processed_data.copy()
            
            # Apply filters
            mask = (df['InvoiceDate'] >= start_date) & (df['InvoiceDate'] <= end_date)
            
            if countries:
                mask &= df['Country'].isin(countries)
                
            if categories and 'Category' in df.columns:
                mask &= df['Category'].isin(categories)
                
            return df[mask]
            
        except Exception as e:
            logger.error(f"Error filtering data: {str(e)}")
            return pd.DataFrame()

    def get_unique_values(self, column: str) -> List[Any]:
        """
        Get unique values for a specific column
        
        Args:
            column (str): Column name
            
        Returns:
            List[Any]: List of unique values
        """
        try:
            if self.processed_data is None:
                self.processed_data = self.load_data()
                
            if self.processed_data is None or column not in self.processed_data.columns:
                return []
                
            return sorted(self.processed_data[column].unique().tolist())
            
        except Exception as e:
            logger.error(f"Error getting unique values for {column}: {str(e)}")
            return []

    def get_summary_metrics(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Calculate summary metrics from the data
        
        Args:
            df (pd.DataFrame, optional): DataFrame to calculate metrics from
            
        Returns:
            Dict[str, Any]: Dictionary of summary metrics
        """
        try:
            if df is None:
                df = self.processed_data
                
            if df is None or df.empty:
                return {}
                
            metrics = {
                'total_revenue': df['TotalAmount'].sum(),
                'total_orders': df['InvoiceNo'].nunique(),
                'total_customers': df['CustomerID'].nunique(),
                'avg_order_value': df['TotalAmount'].sum() / df['InvoiceNo'].nunique(),
                'total_products': df['StockCode'].nunique(),
                'time_range': {
                    'start': df['InvoiceDate'].min(),
                    'end': df['InvoiceDate'].max()
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}

# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = RetailDataLoader("Online Retail.xlsx")
    
    # Get initial data
    df, start_date, end_date = loader.get_initial_data()
    
    if df is not None and not df.empty:
        # Print summary metrics
        metrics = loader.get_summary_metrics()
        print("\nSummary Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
        
        # Print unique countries
        countries = loader.get_unique_values('Country')
        print(f"\nAvailable Countries: {len(countries)}")