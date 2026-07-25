import pandas as pd
import numpy as np

class RSIStrategy:
    """
    A Momentum strategy that calculates the Relative Strength Index (RSI) 
    to identify overbought and oversold conditions.
    """
    def __init__(self, price_column: str, window: int = 14, overbought: float = 70.0, oversold: float = 30.0):
        self.price_column = price_column
        self.window = window
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the RSI and outputs a directional signal.
        """
        # Calculate daily price changes
        delta = df[self.price_column].diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()

        # Calculate Relative Strength (RS) and RSI
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Initialize the Signal column to 0
        df['signal'] = 0
        
        # RULE 1: Oversold (Price dropped too fast, expect bounce) -> Go Long (+1)
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1
        
        # RULE 2: Overbought (Price rose too fast, expect pullback) -> Go Short (-1)
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1

        return df
