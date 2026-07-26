8th July 2026

Today’s lecture on the ‘Implementation Shortfall’ fundamentally changed how I view my strategy. I spent the afternoon rewriting my Week 1 execution logic. Previously, the model would generate a 'Buy' signal and just dump the entire allocation into the market via a single limit order. I now realise that for a larger simulated portfolio, this would cause severe slippage and immediately alert high-frequency front-runners.

To combat this, I’ve built a basic Smart Order Router (SOR) using a Time-Weighted Average Price (TWAP) algorithm. Instead of placing one massive block trade, the SOR slices the parent order into smaller child orders and drip-feeds them across the session. It’s a crucial layer of camouflage.

10th July 2026

The continued chop in the UK market at the end of this week—particularly the unpredictable swings in the FTSE 100 as the new government tries to establish its fiscal policy—has made standard risk management obsolete.

Arbitrary stop-losses (like a hard 2% cut) are getting whipsawed out constantly. Today, I completely overhauled the risk module to implement Average True Range (ATR) stop-losses. By measuring the actual daily volatility of the asset, my stops are now dynamic. When the market is calm, they tighten to lock in profit. When it’s chaotic, they widen (e.g., 2.5x ATR) to give the trade enough room to breathe without being taken out by random noise. To support this, I had to go back to my Week 2 data pipeline and ensure it fetches High and Low prices, not just the Adjusted Close.

13th July 2026

Spent the start of this week focused on portfolio mechanics and sizing. The concept of 'Volatility Drag' was a harsh mathematical truth: a 50% loss requires a 100% gain just to break even. This makes controlling downside variance the absolute priority.

To address this, I’ve integrated a Fractional Kelly sizing model. Rather than risking a fixed percentage of capital on every trade, the Kelly Criterion uses the backtested win rate and expectancy to calculate the mathematically optimal bet size. However, because backtests degrade in live markets, I am strictly using a "Half-Kelly" approach to heavily suppress the variance.

Finally, I updated the Week 4 backtesting engine. I am no longer relying solely on the Sharpe Ratio, as it unfairly penalises upside volatility (i.e., making large profits quickly). I have added the Sortino Ratio to evaluate my downside risk and the Calmar Ratio to directly measure returns against my maximum drawdown. The architecture is finally starting to look like a cohesive, institutional-grade system.
