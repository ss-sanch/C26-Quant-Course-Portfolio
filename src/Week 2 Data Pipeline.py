import pandas as pd
import yfinance as yf
import numpy as np

class MarketDataCleaner:
    """
    A modular data preprocessing pipeline designed to handle missing data, 
    filter erroneous spikes, and adjust for corporate actions.
    """
    
    def __init__(self, spike_threshold: float = 0.10):
        # 10% threshold for single-tick anomalies based on Lesson 2
        self.spike_threshold = spike_threshold 

 def fetch_clean_data(self, ticker, start_date, end_date):
        """
        UPGRADED: Now fetches High and Low to support Week 5 ATR Stop Losses.
        """
        print(f"Fetching full OHLCV data for {ticker}...")
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        # Flatten MultiIndex if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        # WE MUST KEEP High, Low, Close, and Volume
        df = df[['High', 'Low', 'Close', 'Volume']].copy()
        
        # Apply Week 2 cleaning (Interpolate NaNs, remove 0s)
        df.replace(0, pd.NA, inplace=True)
        df.interpolate(method='linear', inplace=True)
        
        return df

    def apply_spike_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects and removes artificial price spikes > 10% that revert instantly.
        """
        clean_df = df.copy()
        
        # Calculate percentage change from the previous tick
        clean_df['Pct_Change'] = clean_df['Close'].pct_change()
        
        # Identify rows where the move exceeds the 10% threshold
        spike_condition = clean_df['Pct_Change'].abs() > self.spike_threshold
        
        # In a real environment, you might delete or smooth these. 
        # Here we replace the spike with a NaN, then interpolate to bridge the gap safely.
        clean_df.loc[spike_condition, 'Close'] = np.nan
        clean_df = self.resolve_nan_values(clean_df, method='interpolate')
        
        # Drop the temporary calculation column
        clean_df = clean_df.drop(columns=['Pct_Change'])
        
        return clean_df

    def calculate_adjusted_close(self, df: pd.DataFrame, split_ratio: float, split_date: str) -> pd.DataFrame:
        """
        A basic implementation to normalise historical prices before a stock split.
        Ensures the algorithm doesn't read a split as a mechanical crash.
        """
        clean_df = df.copy()
        clean_df.index = pd.to_datetime(clean_df.index)
        split_date = pd.to_datetime(split_date)
        
        # Adjust all historical close prices prior to the split date
        pre_split_mask = clean_df.index < split_date
        clean_df.loc[pre_split_mask, 'Close'] = clean_df.loc[pre_split_mask, 'Close'] / split_ratio
        
        # Conversely, volume must be increased to reflect the new share count
        if 'Volume' in clean_df.columns:
            clean_df.loc[pre_split_mask, 'Volume'] = clean_df.loc[pre_split_mask, 'Volume'] * split_ratio
            
        return clean_df

if __name__ == "__main__":
    # --- Testing the Week 2 Pipeline ---
    
    # Generating mock data with a NaN trap, a massive spike, and a stock split scenario
    dates = pd.date_range(start="2026-06-01", periods=6)
    mock_data = {
        'Close': [100.0, 102.0, np.nan, 106.0, 150.0, 25.0], # NaN on day 3, Spike on day 5, 4:1 Split on day 6
        'Volume': [1000, 1100, 1050, 1200, 1100, 4800]
    }
    
    df = pd.DataFrame(mock_data, index=dates)
    print("--- Original Raw Data ---")
    print(df)
    
    # Initialize the cleaner
    cleaner = MarketDataCleaner(spike_threshold=0.10)
    
    # 1. Resolve NaNs
    df = cleaner.resolve_nan_values(df, method='interpolate')
    
    # 2. Filter Spikes
    df = cleaner.apply_spike_filter(df)
    
    # 3. Adjust for the 4:1 split on 2026-06-06
    df = cleaner.calculate_adjusted_close(df, split_ratio=4.0, split_date="2026-06-06")
    
    print("\n--- Processed Clean Data ---")
    print(df)
