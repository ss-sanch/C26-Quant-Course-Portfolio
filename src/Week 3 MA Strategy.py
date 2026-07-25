import pandas as pd
import numpy as np

class MovingAverageStrategy:
    """
    A Trend Following strategy that uses Simple Moving Average (SMA) crossovers
    to generate Long and Short signals.
    """
    def __init__(self, price_column: str, short_window: int = 50, long_window: int = 200):
        self.price_column = price_column
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the moving averages and outputs a directional signal.
        """
        # Calculate the short-term and long-term SMAs
        df['MA_Short'] = df[self.price_column].rolling(window=self.short_window).mean()
        df['MA_Long'] = df[self.price_column].rolling(window=self.long_window).mean()

        # Initialize the Signal column to 0
        df['signal'] = 0
        
        # RULE 1: Uptrend (Short MA crosses above Long MA) -> Go Long (+1)
        df.loc[df['MA_Short'] > df['MA_Long'], 'signal'] = 1
        
        # RULE 2: Downtrend (Short MA crosses below Long MA) -> Go Short (-1)
        df.loc[df['MA_Short'] < df['MA_Long'], 'signal'] = -1

        return df
