import pandas as pd

def check_correlation_safety(asset_a_prices: pd.Series, asset_b_prices: pd.Series, max_correlation: float = 0.70) -> bool:
    """
    Ensures algorithms are not buying highly correlated assets, preventing sector double-exposure.
    """
    correlation = asset_a_prices.corr(asset_b_prices)
    print(f"Asset Correlation: {correlation:.2f}")
    
    if correlation > max_correlation:
        print("WARNING: Assets are highly correlated. Trade Blocked.")
        return False
    return True
