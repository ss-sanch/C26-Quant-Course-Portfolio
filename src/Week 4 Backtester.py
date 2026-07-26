import pandas as pd
import numpy as np
import yfinance as yf
from week6_options_hedger import OptionPricingEngine

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
        self.split_date = split_date 
        
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
        # Efficiency Ratio (ER)
        change = abs(self.data['Close'] - self.data['Close'].shift(window))
        volatility = abs(self.data['Close'] - self.data['Close'].shift(1)).rolling(window=window).sum()
        er = change / volatility
        
        # Smoothing Constant (SC)
        fast_sc = 2 / (fast_ema_constant + 1)
        slow_sc = 2 / (slow_ema_constant + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        
        kama = np.zeros_like(self.data['Close'])
        kama[:] = np.nan
        
        first_valid = window
        kama[first_valid] = self.data['Close'].iloc[first_valid - window : first_valid].mean()
        
        for i in range(first_valid + 1, len(self.data)):
            kama[i] = kama[i-1] + sc.iloc[i] * (self.data['Close'].iloc[i] - kama[i-1])
            
        self.data['KAMA'] = kama
        self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()

    def generate_signals(self):
        self.calculate_KAMA()
        self.data['Signal'] = np.where(self.data['KAMA'] > self.data['SMA_50'], 1.0, 0.0)
        self.data['Position'] = self.data['Signal'].shift(1) # Prevent Lookahead Bias

    def run_backtest(self):
        self.generate_signals()
        df = self.data.dropna().copy()
        
        df['Trade_Trigger'] = df['Position'].diff().abs()
        df['Market_Returns'] = df['Close'].pct_change()
        df['Gross_Strategy_Returns'] = df['Market_Returns'] * df['Position']
        
        # Apply Slippage and Commission
        trade_costs = (df['Trade_Trigger'] * self.slippage) + (df['Trade_Trigger'] * (self.commission / self.capital))
        df['Net_Strategy_Returns'] = df['Gross_Strategy_Returns'] - trade_costs

        if 'Historical_Vol' not in df.columns:
            df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
            df['Historical_Vol'] = df['Log_Returns'].rolling(window=21).std() * np.sqrt(252)

        def price_protective_put(row):
            # Only calculate insurance cost on the exact day a trade OPENS 
            # (i.e., Position is 1 and a new Trade_Trigger occurs)
            if row.get('Position') == 1 and row.get('Trade_Trigger') == 1: 
                pricer = OptionPricingEngine()
                try:
                    put_price = pricer.black_scholes_price(
                        S=row['Close'], 
                        K=row['Close'] * 0.95, # 5% Out-of-The-Money Strike
                        T=30 / 365.0,          # 30-day expiry
                        r=0.05,                # Risk-Free Rate proxy
                        sigma=max(row.get('Historical_Vol', 0.20), 0.10), 
                        option_type="put"
                    )
                    # Return the cost of the option as a percentage of the stock price
                    return put_price / row['Close']
                except Exception:
                    return 0.0
            return 0.0

        # Apply pricing engine dynamically on trade days
        df['Hedge_Drag_Pct'] = df.apply(price_protective_put, axis=1)

        # Subtract the Volatility Drag from your Net Strategy Returns
        df['Net_Strategy_Returns'] = df['Net_Strategy_Returns'] - df['Hedge_Drag_Pct']
        # ---------------------------------------------------------
            
        self.data = df
        return self._evaluate_performance()

    def _evaluate_performance(self):
        """
        Splits data into In-Sample/Out-of-Sample and calculates Risk Metrics
        including Week 5 Sortino and Calmar ratios.
        """
        df = self.data
        train_data = df[:self.split_date]
        test_data = df[self.split_date:]
        
        def calc_metrics(data_slice, regime_name):
            returns = data_slice['Net_Strategy_Returns'].dropna()
            if len(returns) == 0:
                return
                
            winning_trades = returns[returns > 0]
            losing_trades = returns[returns < 0]
            
            # 1. Sharpe Ratio
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
            
            # --- WEEK 5 ADDITIONS START HERE ---
            annualised_return = returns.mean() * 252
            
            # 2. Sortino Ratio (Downside volatility only)
            downside_volatility = losing_trades.std() * np.sqrt(252)
            sortino = annualised_return / downside_volatility if downside_volatility != 0 else 0
            
            # 3. Calmar Ratio & Max Drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.cummax()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            calmar = annualised_return / max_drawdown if max_drawdown != 0 else 0
            # --- WEEK 5 ADDITIONS END HERE ---

            # Hit Rate & Expectancy
            hit_rate = len(winning_trades) / len(returns[returns != 0]) if len(returns[returns != 0]) > 0 else 0
            avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
            avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
            expectancy = (hit_rate * avg_win) + ((1 - hit_rate) * avg_loss)
            
            print(f"--- {regime_name} Performance ---")
            print(f"Sharpe Ratio:  {sharpe:.2f}")
            print(f"Sortino Ratio: {sortino:.2f} (Target: > 2.0)")
            print(f"Calmar Ratio:  {calmar:.2f} (Target: > 1.0)")
            print(f"Max Drawdown:  {max_drawdown*100:.2f}%")
            print(f"Hit Rate:      {hit_rate*100:.2f}%")
            print(f"Expectancy:    {expectancy:.5f} per trade\n")

        print("\n=== STRATEGY EVALUATION REPORT ===")
        calc_metrics(train_data, "IN-SAMPLE (Training)")
        calc_metrics(test_data, "OUT-OF-SAMPLE (Testing)")

# --- RUN CONFIGURATION ---
if __name__ == "__main__":
    backtester = AdvancedBacktester(
        ticker="SPY", start_date="2010-01-01", end_date="2023-01-01", split_date="2019-01-01", 
        initial_capital=50000.0, commission_per_trade=1.50, slippage_pct=0.0005
    )
    backtester.run_backtest()
