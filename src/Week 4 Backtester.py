import pandas as pd
import numpy as np
import yfinance as yf

class AdvancedBacktester:
    """
    A professional backtesting engine that evaluates strategies with realistic 
    market frictions (slippage, commission) and Out-of-Sample validation.
    """
    def __init__(self, ticker: str, start_date: str, end_date: str, split_date: str, 
                 initial_capital: float = 10000.0, commission_per_trade: float = 2.0, slippage_pct: float = 0.0005):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.split_date = split_date # Date separating In-Sample (Train) and Out-of-Sample (Test)
        
        self.capital = initial_capital
        self.commission = commission_per_trade
        self.slippage = slippage_pct
        
        self.data = self._fetch_data()

    def _fetch_data(self):
        print(f"Fetching data for {self.ticker}...")
        df = yf.download(self.ticker, start=self.start_date, end=self.end_date, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        return df[['Close', 'Volume']].copy()

    def calculate_KAMA(self, window=10, fast_ema_constant=2, slow_ema_constant=30):
        """
        Calculates the Kaufman Adaptive Moving Average (KAMA) to reduce lag and adapt to volatility.
        """
        df = self.data
        
        # 1. Efficiency Ratio (ER)
        change = abs(df['Close'] - df['Close'].shift(window))
        volatility = abs(df['Close'] - df['Close'].shift(1)).rolling(window=window).sum()
        er = change / volatility
        
        # 2. Smoothing Constant (SC)
        fast_sc = 2 / (fast_ema_constant + 1)
        slow_sc = 2 / (slow_ema_constant + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        
        # 3. Calculate KAMA iteratively
        kama = np.zeros_like(df['Close'])
        kama[:] = np.nan
        
        # Start KAMA with a simple moving average for the first valid data point
        first_valid = window
        kama[first_valid] = df['Close'].iloc[first_valid - window : first_valid].mean()
        
        for i in range(first_valid + 1, len(df)):
            kama[i] = kama[i-1] + sc.iloc[i] * (df['Close'].iloc[i] - kama[i-1])
            
        self.data['KAMA'] = kama
        self.data['SMA_50'] = df['Close'].rolling(window=50).mean() # Baseline for crossover

    def generate_signals(self):
        """
        Generates +1 (Long) or 0 (Cash) based on KAMA crossing a baseline SMA.
        """
        self.calculate_KAMA()
        self.data['Signal'] = np.where(self.data['KAMA'] > self.data['SMA_50'], 1.0, 0.0)
        self.data['Position'] = self.data['Signal'].shift(1) # Prevent Lookahead Bias

    def run_backtest(self):
        """
        Calculates returns accounting for Slippage and Commission.
        """
        self.generate_signals()
        df = self.data.dropna().copy()
        
        # Calculate when a trade actually occurs (Position changes from 0 to 1, or 1 to 0)
        df['Trade_Trigger'] = df['Position'].diff().abs()
        
        # Gross Market Returns
        df['Market_Returns'] = df['Close'].pct_change()
        df['Gross_Strategy_Returns'] = df['Market_Returns'] * df['Position']
        
        # Apply Slippage and Commission
        # Slippage: deducts a percentage of the return when entering/exiting
        # Commission: deducts a fixed dollar amount relative to the capital per trade
        trade_costs = (df['Trade_Trigger'] * self.slippage) + (df['Trade_Trigger'] * (self.commission / self.capital))
        
        df['Net_Strategy_Returns'] = df['Gross_Strategy_Returns'] - trade_costs
        
        self.data = df
        return self._evaluate_performance()

    def _evaluate_performance(self):
        """
        Splits data into In-Sample/Out-of-Sample and calculates Risk Metrics.
        """
        df = self.data
        train_data = df[:self.split_date]
        test_data = df[self.split_date:]
        
        def calc_metrics(data_slice, regime_name):
            returns = data_slice['Net_Strategy_Returns'].dropna()
            winning_trades = returns[returns > 0]
            losing_trades = returns[returns < 0]
            
            # Sharpe Ratio (Assuming 252 trading days, 0% risk free rate for simplicity)
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
            
            # Hit Rate & Expectancy
            hit_rate = len(winning_trades) / len(returns[returns != 0]) if len(returns[returns != 0]) > 0 else 0
            avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
            avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
            expectancy = (hit_rate * avg_win) + ((1 - hit_rate) * avg_loss)
            
            print(f"--- {regime_name} Performance ---")
            print(f"Sharpe Ratio: {sharpe:.2f}")
            print(f"Hit Rate:     {hit_rate*100:.2f}%")
            print(f"Expectancy:   {expectancy:.5f} per trade\n")

        print("\n=== STRATEGY EVALUATION REPORT ===")
        calc_metrics(train_data, "IN-SAMPLE (Training)")
        calc_metrics(test_data, "OUT-OF-SAMPLE (Testing)")

# --- RUN CONFIGURATION ---
if __name__ == "__main__":
    backtester = AdvancedBacktester(
        ticker="SPY",
        start_date="2010-01-01",
        end_date="2023-01-01",
        split_date="2019-01-01", # Splits the data exactly to check for overfitting
        initial_capital=50000.0,
        commission_per_trade=1.50, # $1.50 per trade
        slippage_pct=0.0005 # 0.05% slippage on market impact
    )
    backtester.run_backtest()
