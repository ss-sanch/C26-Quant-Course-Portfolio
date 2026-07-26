import pandas as pd
import numpy as np

class SmartOrderRouter:
    """
    UPGRADED WEEK 1 SCRIPT: Acts as a Smart Order Router to slice large parent 
    orders into tiny child orders to avoid market impact and slippage.
    """
    def __init__(self, target_allocation_pct: float, portfolio_value: float):
        self.target_capital = target_allocation_pct * portfolio_value

    def execute_twap(self, current_price: float, total_minutes: int = 390, chunks: int = 10):
        """
        Time-Weighted Average Price (TWAP) execution.
        Slices the total order into smaller chunks distributed evenly across the trading day.
        (390 minutes = standard 6.5 hour US trading day).
        """
        total_shares_needed = self.target_capital / current_price
        shares_per_chunk = total_shares_needed / chunks
        time_interval = total_minutes / chunks
        
        print(f"--- TWAP EXECUTION ROUTER ---")
        print(f"Parent Order: Buy {total_shares_needed:.2f} shares at roughly ${current_price:.2f}")
        print(f"Routing Strategy: Slicing into {chunks} child orders.")
        print(f"Action: Buying {shares_per_chunk:.2f} shares every {time_interval} minutes.")
        
        # In a live API environment, this would trigger a time.sleep() or async loop
        return shares_per_chunk, time_interval

# --- TEST THE CONNECTION TO WEEK 5 ---
if __name__ == "__main__":
    # Let's say the Week 5 Risk Manager told us to allocate 13.5% of our $50k account
    week5_recommended_allocation = 0.135 
    
    sor = SmartOrderRouter(target_allocation_pct=week5_recommended_allocation, portfolio_value=50000.0)
    
    # We pass it to the Week 1 router to execute safely without moving the market
    child_order_size, delay = sor.execute_twap(current_price=150.0)
