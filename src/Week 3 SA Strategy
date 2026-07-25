import pandas as pd
import numpy as np

class PairsTradingStrategy:
    """
    A Statistical Arbitrage (Pairs Trading) model that calculates the spread
    between two cointegrated assets and generates signals based on Z-scores.
    Designed to sit between the MarketDataCleaner and the Execution logic.
    """
    def __init__(self, asset_y: str, asset_x: str, window: int = 20, z_threshold: float = 2.0):
        self.asset_y = asset_y
        self.asset_x = asset_x
        self.window = window
        self.z_threshold = z_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the rolling Z-score of the spread and outputs directional signals.
        """
        # Calculate the spread 
        # (Assuming a simple 1:1 hedge ratio here for the baseline model. 
        # For advanced models, you would use linear regression to find beta).
        df['spread'] = df[self.asset_y] - df[self.asset_x]

        # Calculate rolling mean and standard deviation for the defined time window
        df['rolling_mean'] = df['spread'].rolling(window=self.window).mean()
        df['rolling_std'] = df['spread'].rolling(window=self.window).std()

        # Calculate the Z-score
        df['z_score'] = (df['spread'] - df['rolling_mean']) / df['rolling_std']

        # Initialize the Signal column to 0 (Flat/No action)
        df['signal'] = 0
        
        # RULE 1: If Z-score > Threshold (Spread is too wide)
        # Asset Y is expensive relative to Asset X. 
        # Signal -1 means: Short Y, Long X
        df.loc[df['z_score'] > self.z_threshold, 'signal'] = -1
        
        # RULE 2: If Z-score < -Threshold (Spread is too narrow)
        # Asset Y is cheap relative to Asset X. 
        # Signal 1 means: Long Y, Short X
        df.loc[df['z_score'] < -self.z_threshold, 'signal'] = 1

        return df

if __name__ == "__main__":
    # --- Testing the Week 3 Pairs Trading Strategy ---
    
    # Mock clean data (Simulating the output from your Week 2 MarketDataCleaner)
    # We use a small dataset to force a mean-reverting divergence on Day 4.
    mock_data = {
        'KO_Close': [60.0, 60.2, 60.1, 65.0, 60.3, 60.0],
        'PEP_Close': [170.0, 170.2, 170.1, 170.0, 170.5, 170.0]
    }
    test_df = pd.DataFrame(mock_data)
    
    # Initialize strategy with a short 3-day window for testing purposes
    pairs_model = PairsTradingStrategy(asset_y='KO_Close', asset_x='PEP_Close', window=3, z_threshold=1.5)
    
    # Generate signals
    results = pairs_model.generate_signals(test_df)
    
    # Display the mathematical breakdown
    print("Statistical Arbitrage Signal Output:")
    print(results[['spread', 'rolling_mean', 'z_score', 'signal']])
