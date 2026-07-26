import pandas as pd
import numpy as np
from week6_options_hedger import OptionPricingEngine, OptionsStrategyBuilder

class DynamicRiskManager:
    """
    Week 5 Risk Architecture: Calculates precise position sizing and dynamic 
    stop-losses to protect compound growth and minimize volatility drag.
    """
    def __init__(self, initial_capital: float = 100000.0, max_account_risk_pct: float = 0.02):
        self.capital = initial_capital
        self.max_account_risk = max_account_risk_pct # Hard circuit breaker (e.g., never risk >2% of account)

    def calculate_atr(self, df: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calculates the Average True Range (ATR) to measure natural market noise.
        Requires 'High', 'Low', and 'Close' columns in the DataFrame.
        """
        # 1. Calculate the three true range components
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift(1))
        low_close = np.abs(df['Low'] - df['Close'].shift(1))
        
        # 2. The True Range is the maximum of the three
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # 3. Smooth it out over the window (Wilder's Smoothing/Rolling Mean)
        atr = true_range.rolling(window=window).mean()
        return atr

    def apply_atr_stop_loss(self, df: pd.DataFrame, entry_price_col: str, atr_multiplier: float = 2.0):
        """
        Calculates a dynamic stop-loss price based on current market volatility.
        If the market is choppy, the stop gets wider. If calm, it tightens.
        """
        if 'ATR' not in df.columns:
            df['ATR'] = self.calculate_atr(df)
            
        # Stop Loss = Entry Price - (ATR * Multiplier)
        df['Dynamic_Stop_Loss'] = df[entry_price_col] - (df['ATR'] * atr_multiplier)
        return df

    def fractional_kelly_sizing(self, win_rate: float, avg_win: float, avg_loss: float, fraction: float = 0.5) -> float:
        """
        Uses the Kelly Criterion to find the mathematically optimal position size, 
        then applies a 'Fractional' modifier to heavily reduce variance and volatility drag.
        """
        if avg_loss == 0:
            return self.max_account_risk # Prevent division by zero if no losses yet
            
        reward_risk_ratio = abs(avg_win / avg_loss)
        
        # Kelly Formula: W - ((1 - W) / R)
        kelly_pct = win_rate - ((1.0 - win_rate) / reward_risk_ratio)
        
        # Prevent algorithm from outputting negative sizes (which means 'do not trade')
        kelly_pct = max(0.0, kelly_pct)
        
        # Apply Fractional Kelly (Quants rarely use Full Kelly due to model degradation)
        fractional_size = kelly_pct * fraction
        
        # Hard cap the size to our circuit breaker (e.g., maximum 20% of buying power per trade)
        safe_size = min(fractional_size, 0.20) 
        
        return safe_size

    def volatility_targeted_sizing(self, current_volatility: float, target_volatility: float = 0.15) -> float:
        """
        Allocates capital based on market fear. If the VIX/asset variance spikes, 
        position size is scaled down.
        """
        if current_volatility == 0:
            return 0.0
            
        # If target vol is 15% and current is 30%, it cuts the position size in half (0.5 weight)
        vol_scalar = target_volatility / current_volatility
        
        # Cap the maximum leverage/weight at 1.0 (100% of allowed capital)
        return min(vol_scalar, 1.0)

    # Inside your RiskManager class:
    def check_hedge_cost(self, current_price, target_stop, days_to_expiry, hist_vol, risk_free_rate):
        pricer = OptionPricingEngine()
        builder = OptionsStrategyBuilder(pricer)
        
        # Calculate the cost to insure this position with a protective put
        put_premium = pricer.black_scholes_price(
            S=current_price, 
            K=target_stop, # Your stop-loss becomes the strike price
            T=days_to_expiry / 365.0, 
            r=risk_free_rate, 
            sigma=hist_vol, 
            option_type="put"
        )
    
        # If the insurance costs less than 2% of the trade value, it's a viable hedge
        max_acceptable_premium = current_price * 0.02
        
        if put_premium <= max_acceptable_premium:
            return True, put_premium
        else:
            return False, put_premium

# --- RUN CONFIGURATION (TESTING THE MANAGER) ---
if __name__ == "__main__":
    risk_desk = DynamicRiskManager(initial_capital=50000.0)
    
    # Simulating the metrics from a Week 4 Backtest
    backtest_win_rate = 0.55   # 55% Hit Rate
    backtest_avg_win = 250.0   # $250 average win
    backtest_avg_loss = -150.0 # $150 average loss
    
    recommended_allocation = risk_desk.fractional_kelly_sizing(
        win_rate=backtest_win_rate, 
        avg_win=backtest_avg_win, 
        avg_loss=backtest_avg_loss,
        fraction=0.5 # Half-Kelly
    )
    
    print(f"Optimal Fractional Kelly Allocation: {recommended_allocation*100:.2f}% of total capital per trade.")
    
    if recommended_allocation <= 0:
        print("WARNING: Kelly is zero or negative. The math says this strategy does not have a statistical edge. DO NOT TRADE.")
