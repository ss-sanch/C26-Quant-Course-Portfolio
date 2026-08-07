Algorithmic Trading Building Journal: Competition Days (July 27 - August 7, 2026)
Day 1 (27th July): A Complete Data Mess
The live simulation finally started today, and honestly, it was an absolute headache right out of the gate. I was expecting the exchange API to stream simple price floats so my bot could get straight to work. Instead, it sent nested order book JSON dictionaries for every single 1-minute tick. My basic Moving Average trend model instantly crashed. I had to manually step in and write a MarketDataCleaner to parse the underlying numeric price using the 'mid' key.

To make matters worse, Gemini’s initial code design wiped the bot's short-term memory every time the Python kernel restarted. Because my trend model requires a 50-minute lookback window of 1-minute close prices to warm up, every time I stopped the bot to fix a bug, I had to wait nearly an hour before it would even think about trading again. No trades were executed today. Just purely fixing data preparation issues.

Day 2 (28th July): The Whipsaw Massacre
Today was brutal. The market regime shifted into intense, non-trending chop with violent volatility. My 50-minute Trend Following strategy got absolutely slaughtered. The algorithm would detect a sharp 5-minute price spike in AAPL, assume a breakout, and generate a LONG signal. Then the price would immediately mean-revert, triggering my static 1.5% stop-losses.

I’m bleeding capital to a thousand tiny cuts. It’s clear that relying on lagging trend indicators is completely useless in this regime.

Day 3 (29th July): Server Downtime & Shadow Book Testing
The exchange servers were down for a scheduled pause today, which was honestly a relief. It gave me a chance to completely rip apart the bot's architecture.

First, I fixed the memory issue. I wrote a script to save the 1-minute rolling price data to a local c26_bot_memory.json file on the Colab drive so I can bypass the 50-minute warm-up on restarts.

Second, I built a "Shadow Book". This is an extra testing methodology I researched outside the lectures. Instead of pushing un-backtested code straight into live capital, the bot now runs experimental strategies on a simulated paper-trading account in the background. If the shadow strategy works on the live tape, I promote it to the real portfolio.

Since trend following is killing my account, I’m using the Shadow Book to test a Pairs Trading (Statistical Arbitrage) strategy. It tracks the Z-score spread between correlated energy stocks (like Chevron and Exxon) using 15-minute intervals. If the spread stretches too far, it shorts the winner and buys the loser, betting on mean reversion.

Day 4 (30th July): Earnings Volatility and Qualitative Filters
Big tech earnings dropped today (AAPL, AMZN, MSFT, META). Rather than blindly trading the tape, I used qualitative data—specifically the scheduled earnings calendar—to manage risk.

Holding a directional stock position overnight into an earnings call is basically gambling because Implied Volatility (IV) is heavily inflated. I coded an EarningsCatalystFilter that automatically flattens all AAPL and AMZN positions at 4:30 PM before the close.

I also started backtesting a Dynamic Universe Scanner (Cross-Sectional Momentum). Instead of hard-coding which stocks to trade, I ran a backtest using our saved 1-minute JSON data to rank sector proxy ETFs. The idea is to dynamically drop losing sectors and rotate into safe havens like Gold (GLD) or Bonds (TLT) if equities collapse.

Day 5 (31st July): Flash Crashes and AI Frustrations
Just an awful day. The simulation threw massive liquidity shocks at us, with intraday flash crashes of up to -14% and 504 Gateway errors.

I actually built an IntradayFlashCrashDetector to trip the circuit breakers, but then the bot just crashed anyway because of a stupid code error from Gemini. The AI passed a Pandas DataFrame into a NumPy variance calculator instead of a flat 1D array, triggering a fatal truth value of a Series is ambiguous error. I lost precious time debugging this and had to wrap the data array in np.ravel() to fix it.

I also realised the bot was trying to catch falling knives during brief pauses in the crashes. To fix this, I added a 30-minute lockout timer. If a crash triggers, the bot is put in the penalty box for half an hour so it stops buying fake dips.

Day 6 - 7 (3rd - 4th August): The VIX Sensor Failure
More issues with the architecture. My market regime sensor flatlined and returned a "Regime unclear" state. It turns out the bot was pulling real-world VIX data from the Yahoo Finance API (which was sitting quietly at 15.71) while our internal Colab simulation was violently crashing.

I had to completely unhook the bot from external APIs. I coded an internal tape reader to calculate volatility strictly off the simulated self.history['SPY'].

To try and claw back some of the massive losses, I added a third distinct strategy to the portfolio: Statistical Dispersion. It’s an advanced concept where the bot goes long on highly volatile single tech stocks and shorts the Nasdaq ETF (QQQ). It doesn't care about market direction; it just bets that the volatility spread between single stocks and the index will mean-revert.

Day 8 - 10 (5th - 7th August): A Bitter End
Going into the final days, I ran a rapid Grid Search backtest on the Colab environment to test different timeframes (5, 10, 15, 30, and 60 minutes) for the mean-reversion scalper. I desperately shrunk the lookback window down to 15 minutes just to get the bot taking more trades before the competition ended.

It didn't work. We finished the week down almost 25%, which is incredibly frustrating given how much better other students did.

Despite the awful PnL, the mathematics of Volatility Drag really hit home for me. Being down 25% means I now need a 33% gain just to get back to breakeven. It proves that institutional trading is entirely about downside protection. I spent too much time trying to fix Gemini’s bugs and optimising alpha signals, and not enough time stress-testing the risk manager. It was a brutal way to learn, but dealing with bad data feeds, buggy code, and simulated crashes taught me more about real quantitative engineering than a textbook ever could.
