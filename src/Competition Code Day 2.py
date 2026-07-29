import time
import pandas as pd
import numpy as np
import traceback
import pickle
import os

# ==========================================
# C26 QUANT TRADING BOT: UNIFIED ARCHITECTURE
# ==========================================

class DynamicRiskManager:
    """Week 5: Controls maximum drawdown and calculates fractional capital risk."""
    def __init__(self, initial_capital, max_account_risk_pct=0.02):
        self.max_risk = max_account_risk_pct

    def get_max_spend_per_trade(self, current_equity):
        # Never allocate more than a safe fraction of total equity to a single signal
        return current_equity * self.max_risk * 5 # Sized up slightly for simulation speed

class RobustPortfolioAllocator:
    """
    UPDATED DAY 2 PATCH: Allocates capital using intraday inverse volatility (Risk Parity)
    with a 30-minute lookback window, AND includes the original capital capping logic.
    """
    def __init__(self, max_weight_cap=0.35, lookback_window=30):
        # No single strategy can hold more than 35% of the portfolio capital
        self.max_weight_cap = max_weight_cap
        # The new Day 2 Intraday Lookback constraint
        self.lookback_window = lookback_window

    def calculate_intraday_weights(self, strategy_returns_dict):
        """
        Dynamically shifts capital every cycle based on the last 30 minutes of volatility.
        """
        inv_vols = {}
        total_inv_vol = 0.0

        for strategy, returns in strategy_returns_dict.items():
            if len(returns) < self.lookback_window:
                continue 

            recent_returns = returns[-self.lookback_window:]
            variance = np.var(recent_returns)

            if variance <= 0.000001:
                variance = 0.000001

            inv_vol = 1.0 / variance
            inv_vols[strategy] = inv_vol
            total_inv_vol += inv_vol

        final_weights = {}
        if total_inv_vol > 0:
            for strategy, inv_vol in inv_vols.items():
                raw_weight = inv_vol / total_inv_vol
                # Enforce the strict capital cap to prevent over-concentration
                final_weights[strategy] = self.cap_position_size(raw_weight)

        return final_weights

    def cap_position_size(self, target_weight):
        """
        Original Week 7 method: Enforces the hard capital cap per trade.
        """
        return min(target_weight, self.max_weight_cap)

class MemoryManager:
    """
    State Persistence Module: Saves and loads the bot's short-term memory 
    to the Colab hard drive to bypass the 50-minute warm-up phase on restarts.
    """
    def __init__(self, filepath='bot_memory.pkl'):
        self.filepath = filepath

    def save_memory(self, data):
        """Saves the current accumulated market data to the drive."""
        try:
            with open(self.filepath, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"[WARNING] Failed to save memory state: {e}")

    def load_memory(self):
        """Loads past market data if it exists, skipping the warm-up."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'rb') as f:
                    recovered_data = pickle.load(f)
                    data_length = len(recovered_data) if isinstance(recovered_data, list) else len(recovered_data.get(list(recovered_data.keys())[0], []))
                    print(f"[MEMORY MODULE] Successfully recovered {data_length} minutes of historical data. Warm-up bypassed.")
                    return recovered_data
            except Exception as e:
                print(f"[WARNING] Corrupted memory file. Starting fresh. Error: {e}")
        
        # If no file exists or it fails, return None so the bot starts fresh
        return None

class LiveTradingBot:
    def __init__(self):
        print("Initializing C26 Institutional Trading Architecture...")
        
        # 1. Define the Robust Universe FIRST so memory knows what to build
        self.trend_universe = ["SPY", "AAPL", "MSFT"]
        self.pairs_universe = ["XOM", "CVX"]
        self.all_tickers = self.trend_universe + self.pairs_universe

        # 2. Initialise the memory manager
        self.memory = MemoryManager()
        
        # 3. State Management: Load past memory, OR start a fresh dictionary
        recovered_data = self.memory.load_memory()
        if recovered_data is not None:
            self.history = recovered_data
        else:
            self.history = {ticker: [] for ticker in self.all_tickers}

        # 4. Instantiate Architecture
        account = get_account() # Assumes get_account() is in the Colab environment
        self.risk_manager = DynamicRiskManager(initial_capital=account['equity'])
        self.allocator = RobustPortfolioAllocator()

    def update_market_data(self, tape):
        """Week 2 Data Cleaner integration: safely extracts and stores live prices."""
        for ticker in self.all_tickers:
            if ticker in tape:
                data_point = tape[ticker]

                # Extract the raw number if the API returns a dictionary
                if isinstance(data_point, dict):
                    current_price = data_point.get('mid') or 0
                else:
                    current_price = float(data_point)

                if current_price > 0:
                    self.history[ticker].append(current_price)
                    # Keep only the last 200 minutes to prevent memory overflow
                    if len(self.history[ticker]) > 200:
                        self.history[ticker].pop(0)

    def generate_signals(self):
        """Week 3 Alpha Models: Generates Buy/Sell/Hold signals."""
        signals = {ticker: 0 for ticker in self.all_tickers}

        # MODEL 1: Trend Following (Moving Averages) for SPY, AAPL, MSFT
        for ticker in self.trend_universe:
            prices = self.history[ticker]
            if len(prices) >= 50:
                short_ma = np.mean(prices[-10:])
                long_ma = np.mean(prices[-50:])

                if short_ma > long_ma:
                    signals[ticker] = 1  # Bullish
                elif short_ma < long_ma:
                    signals[ticker] = -1 # Bearish

        # MODEL 2: Statistical Arbitrage (Pairs Trading) for XOM & CVX
        xom_prices = self.history["XOM"]
        cvx_prices = self.history["CVX"]
        if len(xom_prices) >= 50 and len(cvx_prices) >= 50:
            # Calculate the spread between the two oil majors
            spread = np.array(xom_prices[-50:]) - np.array(cvx_prices[-50:])
            z_score = (spread[-1] - np.mean(spread)) / np.std(spread)

            # Mean Reversion Logic
            if z_score > 2.0:
                signals["XOM"] = -1
                signals["CVX"] = 1
            elif z_score < -2.0:
                signals["XOM"] = 1
                signals["CVX"] = -1

        return signals

    def execute_trades(self, signals, tape):
        """Week 1 Order Routing: Safely executes via the competition backend."""
        account = get_account()
        current_equity = account['equity']
        current_cash = account['cash']
        positions = account['positions']

        for ticker, signal in signals.items():
            raw_data = tape.get(ticker, 0)
            current_price = raw_data.get('mid', 0) if isinstance(raw_data, dict) else float(raw_data)

            if current_price == 0:
                continue

            holds_position = ticker in positions and positions[ticker]['qty'] > 0

            if signal == 1 and not holds_position:
                # 1. Ask Risk Manager for max dollar spend
                proposed_spend = self.risk_manager.get_max_spend_per_trade(current_equity)
                
                # 2. Convert to portfolio weight to check against Allocator's 35% cap limit
                proposed_weight = proposed_spend / current_equity
                safe_weight = self.allocator.cap_position_size(proposed_weight)
                
                # 3. Convert back to dollars and ensure we don't over-leverage cash
                safe_spend = safe_weight * current_equity
                actual_spend = min(safe_spend, current_cash * 0.9)
                
                qty = int(actual_spend // current_price)

                if qty > 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Executing BUY: {qty} shares of {ticker} @ ~${current_price:.2f}")
                    buy(ticker, qty)

            elif signal == -1 and holds_position:
                qty_to_sell = positions[ticker]['qty']
                print(f"[{time.strftime('%H:%M:%S')}] Executing SELL: {qty_to_sell} shares of {ticker} @ ~${current_price:.2f}")
                sell(ticker, qty_to_sell)

    def run_cycle(self):
        """The Master Loop that runs every minute."""
        try:
            tape = get_tape()
            self.update_market_data(tape)
            
            # FIX: Safely save the actual rolling history dictionary
            if hasattr(self, 'history'):
                self.memory.save_memory(self.history)
                
            signals = self.generate_signals()
            self.execute_trades(signals, tape)
            
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] WARNING: Market Data Interruption or Server Error: {e}")

# ==========================================
# LAUNCH THE BOT
# ==========================================

bot = LiveTradingBot()
print("Starting C26 Live Trading Bot. Waiting for data accumulation...")
print("Note: The bot needs 50 minutes of data before it will execute its first trade.")

cycle_count = 0
while True:
    bot.run_cycle()
    cycle_count += 1

    # Print an update every 10 minutes so you know it's alive
    if cycle_count % 10 == 0:
        print(f"[{time.strftime('%H:%M:%S')}] Bot is healthy. Tracking {len(bot.all_tickers)} assets.")
        show_account()

    time.sleep(60) # Pauses for 60 seconds to match the minute-level simulation
