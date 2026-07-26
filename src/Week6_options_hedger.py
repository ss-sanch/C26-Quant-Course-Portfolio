import numpy as np
from scipy.stats import norm
import math

class OptionPricingEngine:
    """
    Core pricing engine utilizing Black-Scholes for European options
    and Binomial Trees for American execution.
    """
    
    @staticmethod
    def _calculate_d1_d2(S, K, T, r, sigma):
        """Calculates d1 and d2 for Black-Scholes."""
        # Add a tiny float to T and sigma to prevent division by zero
        T = max(T, 1e-5)
        sigma = max(sigma, 1e-5)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2

    @classmethod
    def black_scholes_price(cls, S, K, T, r, sigma, option_type="call"):
        """
        Calculates theoretical premium of a European option.
        S: Underlying Price
        K: Strike Price
        T: Time to Expiration (in years)
        r: Risk-free rate (decimal)
        sigma: Volatility (decimal)
        """
        d1, d2 = cls._calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type.lower() == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == "put":
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("Option type must be 'call' or 'put'")
            
        return price

    @classmethod
    def calculate_greeks(cls, S, K, T, r, sigma, option_type="call"):
        """Calculates the standard Option Greeks (Delta, Gamma, Vega, Theta, Rho)."""
        d1, d2 = cls._calculate_d1_d2(S, K, T, r, sigma)
        
        # Vega and Gamma are identical for both Calls and Puts
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% change
        
        if option_type.lower() == "call":
            delta = norm.cdf(d1)
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                     - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
            rho = (K * T * np.exp(-r * T) * norm.cdf(d2)) / 100
        else:
            delta = norm.cdf(d1) - 1
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
            rho = (-K * T * np.exp(-r * T) * norm.cdf(-d2)) / 100
            
        return {"Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta, "Rho": rho}

    @classmethod
    def implied_volatility(cls, market_price, S, K, T, r, option_type="call", tol=1e-4, max_iter=100):
        """
        Calculates Implied Volatility (IV) using the Newton-Raphson root-finding method.
        """
        sigma_est = 0.20 # Initial guess of 20%
        
        for i in range(max_iter):
            price_est = cls.black_scholes_price(S, K, T, r, sigma_est, option_type)
            diff = price_est - market_price
            
            if abs(diff) < tol:
                return sigma_est
                
            vega = cls.calculate_greeks(S, K, T, r, sigma_est, option_type)["Vega"] * 100
            
            # Avoid division by zero if Vega becomes too small
            if vega < 1e-6:
                break 
                
            sigma_est -= diff / vega 
            sigma_est = max(sigma_est, 1e-5) # Prevent negative volatility
            
        return sigma_est

    @staticmethod
    def binomial_tree_american(S, K, T, r, sigma, option_type="call", steps=100):
        """
        Prices American options using a Binomial Tree to account for early exercise.
        """
        dt = T / steps
        u = np.exp(sigma * np.sqrt(dt)) # Up factor
        d = 1 / u                       # Down factor
        p = (np.exp(r * dt) - d) / (u - d) # Risk-neutral probability
        
        # Initialize asset prices at maturity
        asset_prices = np.array([S * (u ** j) * (d ** (steps - j)) for j in range(steps + 1)])
        
        # Initialize option values at maturity
        if option_type.lower() == "call":
            option_values = np.maximum(0, asset_prices - K)
        else:
            option_values = np.maximum(0, K - asset_prices)
            
        # Step backwards through the tree
        for i in range(steps - 1, -1, -1):
            option_values = np.exp(-r * dt) * (p * option_values[1:i+2] + (1 - p) * option_values[0:i+1])
            asset_prices = asset_prices[:-1] / u # Step asset price back
            
            # Check for early exercise
            if option_type.lower() == "call":
                option_values = np.maximum(option_values, asset_prices - K)
            else:
                option_values = np.maximum(option_values, K - asset_prices)
                
        return option_values[0]


class OptionsStrategyBuilder:
    """
    Constructs multi-leg option strategies for the trading algorithm.
    """
    def __init__(self, pricing_engine):
        self.pricer = pricing_engine

    def build_straddle(self, S, K, T, r, sigma):
        """Buys a Call and a Put at the same ATM strike."""
        call_leg = self.pricer.black_scholes_price(S, K, T, r, sigma, "call")
        put_leg = self.pricer.black_scholes_price(S, K, T, r, sigma, "put")
        return {"Strategy": "Straddle", "Total_Premium": call_leg + put_leg, "Legs": [f"Long {K} Call", f"Long {K} Put"]}

    def build_strangle(self, S, K_call, K_put, T, r, sigma):
        """Buys an OTM Call and an OTM Put."""
        call_leg = self.pricer.black_scholes_price(S, K_call, T, r, sigma, "call")
        put_leg = self.pricer.black_scholes_price(S, K_put, T, r, sigma, "put")
        return {"Strategy": "Strangle", "Total_Premium": call_leg + put_leg, "Legs": [f"Long {K_call} Call", f"Long {K_put} Put"]}

    def build_collar(self, S, K_put, K_call, T, r, sigma):
        """
        Protective strategy: Long underlying (assumed), Long OTM Put, Short OTM Call.
        Calculates the net cost of the options legs.
        """
        put_cost = self.pricer.black_scholes_price(S, K_put, T, r, sigma, "put")
        call_credit = self.pricer.black_scholes_price(S, K_call, T, r, sigma, "call")
        net_premium = put_cost - call_credit
        return {"Strategy": "Collar", "Net_Options_Cost": net_premium, "Legs": [f"Long {K_put} Put", f"Short {K_call} Call"]}

# --- Quick Test Execution ---
if __name__ == "__main__":
    pricer = OptionPricingEngine()
    builder = OptionsStrategyBuilder(pricer)
    
    # Example Market Environment
    current_price = 100.0
    strike = 100.0
    expiry = 0.5 # 6 months
    risk_free = 0.05 # 5%
    vol = 0.20 # 20%
    
    print("--- Week 6 Options Module Initialized ---")
    bs_price = pricer.black_scholes_price(current_price, strike, expiry, risk_free, vol, "call")
    print(f"European Call Price (Black-Scholes): £{bs_price:.2f}")
    
    greeks = pricer.calculate_greeks(current_price, strike, expiry, risk_free, vol, "call")
    print(f"Call Delta: {greeks['Delta']:.4f}")
    
    collar = builder.build_collar(current_price, 90, 110, expiry, risk_free, vol)
    print(f"Collar Execution Net Options Premium: £{collar['Net_Options_Cost']:.2f}")
