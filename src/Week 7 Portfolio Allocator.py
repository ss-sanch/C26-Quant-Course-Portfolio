import numpy as np
import pandas as pd

class RobustPortfolioAllocator:
    """
    Allocates capital across multiple strategies using inverse volatility (Risk Parity)
    and strict capital caps to ensure survival during extreme market stress.
    """
    def __init__(self, max_weight_cap=0.35):
        # No single strategy can hold more than 35% of the portfolio capital
        self.max_weight_cap = max_weight_cap

    def calculate_inverse_volatility_weights(self, strategy_returns: pd.DataFrame) -> pd.Series:
        """
        Calculates weights inversely proportional to the strategy's historical volatility.
        Highly volatile strategies get smaller allocations.
        """
        # Calculate standard deviation (volatility) for each strategy
        volatilities = strategy_returns.std()
        
        # Prevent division by zero if a strategy has perfectly flat returns
        volatilities = volatilities.replace(0, 1e-6)
        
        # Calculate inverse volatility
        inv_vol = 1.0 / volatilities
        
        # Normalize so weights sum to 1.0
        raw_weights = inv_vol / inv_vol.sum()
        
        return raw_weights

    def apply_weight_caps(self, weights: pd.Series) -> pd.Series:
        """
        Enforces the maximum weight limit and redistributes excess capital 
        proportionally to the remaining strategies.
        """
        capped_weights = weights.copy()
        
        while any(capped_weights > self.max_weight_cap):
            # Find strategies exceeding the cap
            excess_mask = capped_weights > self.max_weight_cap
            
            # Calculate total excess weight to redistribute
            excess_weight = (capped_weights[excess_mask] - self.max_weight_cap).sum()
            
            # Cap the overweight strategies
            capped_weights[excess_mask] = self.max_weight_cap
            
            # Find strategies that can receive more weight
            receivers_mask = capped_weights < self.max_weight_cap
            receivers_total = capped_weights[receivers_mask].sum()
            
            if receivers_total > 0:
                # Redistribute excess proportionally
                capped_weights[receivers_mask] += (capped_weights[receivers_mask] / receivers_total) * excess_weight
            else:
                # If all are capped (rare, implies small number of strategies), break to avoid infinite loop
                break 
                
        return capped_weights

    def generate_target_allocations(self, strategy_returns: pd.DataFrame) -> pd.Series:
        """
        Master method to generate final, robust portfolio weights.
        """
        raw_weights = self.calculate_inverse_volatility_weights(strategy_returns)
        final_weights = self.apply_weight_caps(raw_weights)
        
        return final_weights
