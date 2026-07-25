2nd July 2026

Today’s lecture on Backtesting and Strategy Evaluation was a massive eye-opener. I spent the afternoon playing with the standard SMA crossover backtester we built, and I quickly realised how flawed a basic Simple Moving Average can be.

The lag is horrendous. By the time the 50-day crosses the 200-day, the trend has often been running for weeks. We looked at alternatives today, and Kaufman’s Adaptive Moving Average (KAMA) caught my attention. The fact that it mathematically accounts for market volatility—slowing down in choppy markets to avoid false signals and speeding up when a clear trend emerges—makes it feel much safer for the current geopolitical climate.

4th July 2026

The market is an absolute mess right now. The political vacuum following Starmer’s sudden resignation last week has sent the FTSE 100 into a completely schizophrenic, sideways chop.

This volatility perfectly illustrated today's lesson on Commission, Slippage, and Market Impact. A lot of retail traders assume they will get filled exactly at the closing price their backtest shows. But trying to enter a large position in this UK market right now? The slippage is eating into my simulated profit margins instantly. I need to code a realistic transaction cost estimator into my Python pipeline, or my Sharpe ratio is going to be completely delusional.

7th July 2026

Spent the end of the week wrapping my head around model validation. The golden rule is brutal but true: if a strategy prints money in the In-Sample training data but completely falls apart on the Out-of-Sample testing data, it is overfitted.

It is so easy to fall into the trap of throwing polynomial regression at a dataset to minimise errors, creating a curve that perfectly hugs the past but has zero predictive power for tomorrow.

To combat this, I am going to implement Rolling Train Validation. We also touched on Monte Carlo simulations, which I definitely want to run. Throwing thousands of random variations at the model to see its absolute worst-case drawdown is the only way to eliminate my own gut feeling and trust the mathematics. Finally understood Markov Chains too—it’s just mapping out the probability of transitioning from a Bull to a Bear or Sideways market based only on where we are today. Simple, but incredibly effective for regime switching.
