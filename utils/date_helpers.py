from datetime import datetime, timedelta
from typing import Tuple, List, Optional
import pandas as pd
from dateutil.relativedelta import relativedelta
import calendar

def get_date_range(df: pd.DataFrame) -> Tuple[datetime, datetime]:
    """
    Get the min and max dates from the DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame containing 'InvoiceDate' column
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    start_date = df['InvoiceDate'].min()
    end_date = df['InvoiceDate'].max()
    return start_date, end_date

def get_last_n_days(n: int, end_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    Get date range for last n days
    
    Args:
        n (int): Number of days to look back
        end_date (datetime, optional): End date, defaults to today
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    if end_date is None:
        end_date = datetime.now()
    start_date = end_date - timedelta(days=n)
    return start_date, end_date

def get_last_n_months(n: int, end_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    Get date range for last n months
    
    Args:
        n (int): Number of months to look back
        end_date (datetime, optional): End date, defaults to today
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    if end_date is None:
        end_date = datetime.now()
    start_date = end_date - relativedelta(months=n)
    return start_date, end_date

def get_year_to_date(year: Optional[int] = None) -> Tuple[datetime, datetime]:
    """
    Get date range from start of year to current date
    
    Args:
        year (int, optional): Year to get range for, defaults to current year
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    if year is None:
        year = datetime.now().year
    start_date = datetime(year, 1, 1)
    end_date = datetime.now()
    return start_date, end_date

def get_quarter_dates(year: int, quarter: int) -> Tuple[datetime, datetime]:
    """
    Get start and end dates for a specific quarter
    
    Args:
        year (int): Year
        quarter (int): Quarter (1-4)
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    if quarter < 1 or quarter > 4:
        raise ValueError("Quarter must be between 1 and 4")
        
    start_month = (quarter - 1) * 3 + 1
    end_month = quarter * 3
    
    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month, calendar.monthrange(year, end_month)[1])
    
    return start_date, end_date

def get_month_dates(year: int, month: int) -> Tuple[datetime, datetime]:
    """
    Get start and end dates for a specific month
    
    Args:
        year (int): Year
        month (int): Month (1-12)
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")
        
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, calendar.monthrange(year, month)[1])
    
    return start_date, end_date

def get_week_dates(date: datetime) -> Tuple[datetime, datetime]:
    """
    Get start and end dates for the week containing the given date
    
    Args:
        date (datetime): Date within the desired week
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates
    """
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=6)
    return start_date, end_date

def create_date_ranges(start_date: datetime, end_date: datetime, freq: str) -> List[Tuple[datetime, datetime]]:
    """
    Create a list of date ranges between start and end dates
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        freq (str): Frequency ('D' for daily, 'W' for weekly, 'M' for monthly, 'Q' for quarterly)
        
    Returns:
        List[Tuple[datetime, datetime]]: List of date ranges
    """
    ranges = []
    current_date = start_date
    
    while current_date < end_date:
        if freq == 'D':
            period_end = min(current_date + timedelta(days=1), end_date)
        elif freq == 'W':
            period_end = min(current_date + timedelta(days=7), end_date)
        elif freq == 'M':
            next_month = current_date + relativedelta(months=1)
            period_end = min(next_month, end_date)
        elif freq == 'Q':
            next_quarter = current_date + relativedelta(months=3)
            period_end = min(next_quarter, end_date)
        else:
            raise ValueError("Frequency must be one of: 'D', 'W', 'M', 'Q'")
            
        ranges.append((current_date, period_end))
        current_date = period_end
        
    return ranges

def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """
    Format a date range as a string
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        
    Returns:
        str: Formatted date range string
    """
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            if start_date.day == end_date.day:
                return start_date.strftime('%B %d, %Y')
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}"
        return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"

def get_relative_dates(reference_date: datetime = None) -> dict:
    """
    Get commonly used relative date ranges
    
    Args:
        reference_date (datetime, optional): Reference date, defaults to today
        
    Returns:
        dict: Dictionary of relative date ranges
    """
    if reference_date is None:
        reference_date = datetime.now()
        
    return {
        'today': (reference_date.replace(hour=0, minute=0, second=0, microsecond=0),
                 reference_date.replace(hour=23, minute=59, second=59, microsecond=999999)),
        'yesterday': get_last_n_days(1, reference_date.replace(hour=0, minute=0, second=0, microsecond=0)),
        'last_7_days': get_last_n_days(7, reference_date),
        'last_30_days': get_last_n_days(30, reference_date),
        'last_90_days': get_last_n_days(90, reference_date),
        'last_month': get_last_n_months(1, reference_date),
        'last_quarter': get_last_n_months(3, reference_date),
        'ytd': get_year_to_date(reference_date.year)
    }

# Example usage
if __name__ == "__main__":
    from ..data.data_loader import RetailDataLoader
    
    # Load the actual retail data
    loader = RetailDataLoader("data/raw/Online Retail.xlsx")
    df = loader.load_data()
    
    if df is not None:
        # Get dataset date range
        start_date, end_date = get_date_range(df)
        print(f"\nDataset Date Range: {format_date_range(start_date, end_date)}")
        
        # Create monthly date ranges
        monthly_ranges = create_date_ranges(start_date, end_date, 'M')
        print("\nMonthly Ranges:")
        for start, end in monthly_ranges[:3]:  # Print first 3 months
            print(format_date_range(start, end))
        
        # Get relative dates
        relative_dates = get_relative_dates(end_date)
        print("\nRelative Date Ranges (from end date):")
        for period, (start, end) in relative_dates.items():
            print(f"{period}: {format_date_range(start, end)}")