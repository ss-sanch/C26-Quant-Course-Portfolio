import pandas as pd
import numpy as np

class MarketMakingStrategy:
    """
    A simplified Market Making framework that measures short-term volatility 
    and volume to determine if conditions are safe to provide liquidity.
    """
    def __init__(self, price_column: str, volume_column: str, lookback: int = 10, max_volatility: float = 0.02):
        self.price_column = price_column
        self.volume_column = volume_column
        self.lookback = lookback
        self.max_volatility = max_volatility # Maximum acceptable price variance

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluates risk parameters to output an active/inactive market making signal.
        """
        # Calculate short-term price volatility (percentage change standard dev)
        df['pct_change'] = df[self.price_column].pct_change()
        df['volatility'] = df['pct_change'].rolling(window=self.lookback).std()

        # Calculate a rolling volume average to detect spikes
        df['avg_volume'] = df[self.volume_column].rolling(window=self.lookback).mean()

        # Initialize the Signal column to 0 (Do not make a market)
        df['signal'] = 0
        
        # RULE: Only deploy market making orders if volatility is low 
        # (to avoid inventory risk during a massive directional move) 
        # and volume is steady.
        # Signal 1 here means "Active: Place Bid and Ask limit orders"
        condition_safe = (df['volatility'] < self.max_volatility) & (df[self.volume_column] >= df['avg_volume'])
        df.loc[condition_safe, 'signal'] = 1

        return df
