Day 1 (27th July): Data Schema Issues
The live simulation finally started today. Didn't even get to place a trade. I was expecting the exchange API to stream simple price floats, but instead it sent nested order book JSON dictionaries for every 1-minute tick. My basic Moving Average trend model instantly threw a TypeError trying to calculate a mean on a dict.

I spent four hours writing a MarketDataCleaner to parse the underlying numeric price using the ['mid'] key. Also realised that every time I restarted the Colab kernel to fix a bug, the bot's 50-minute rolling window wiped itself to zero.
Ending Equity: $1,000,000. 0 trades executed.

Day 2 (28th July): The Whipsaw Massacre
Absolute bloodbath today. The market regime shifted into intense, non-trending chop. My 50-minute Trend Following strategy got slaughtered by false breakouts.

Specific example: At 14:15, the bot detected a breakout in AAPL.

Entry: Bought 340 shares at $215.30.

Exit: Ten minutes later, it mean-reverted and hit my static 1.5% stop-loss at $212.05.

Realised PnL on that single trade: -$1,105.

It did this repeatedly across the tech basket. To make things worse, the exchange servers crashed mid-afternoon. My terminal printed this:
[14:22:22] WARNING: Market Data Interruption or Server Error: 504 Server Error: Gateway Timeout

My try...except block caught it, so the kernel didn't die, but I still finished the day with my equity down to $993,920. My Sharpe ratio right now is a dismal 0.12. Like I noted back on the 12th of June, I promised myself I'd stick to a strict 70/30 out-of-sample split to avoid overfitting. Turns out, live market chop doesn't care about my pristine backtests.

Day 3 (29th July): Server Downtime & Shadow Book
Servers were down for a scheduled pause. Huge relief. I built a "Shadow Book" to paper-trade new strategies in the background without risking real capital. I also tried to fix the memory wipe issue by writing c26_bot_memory.json to the Colab drive.

I spent most of the afternoon trying to get the Cross-Sectional Momentum scanner working, but my hypothesis was completely wrong. I thought I could use it to rotate into Bonds (TLT), but the maths kept outputting NaN weights. Wasted three hours on it, couldn't figure out the matrix broadcast error, so I just commented the whole module out.

Day 4 (30th July): Earnings Volatility
Big tech earnings today (AAPL, AMZN). I didn't want to hold directional risk overnight into inflated Implied Volatility, so I coded an EarningsCatalystFilter to flatten AAPL at 4:30 PM.

Day 5 (31st July): Flash Crashes and Broken Code
I genuinely hate Pandas right now. The simulation threw massive liquidity shocks at us. My IntradayFlashCrashDetector was supposed to catch it, but it completely crashed the execution loop. Terminal output:

🚨 FLASH CRASH DETECTED! Intraday Drop: -8.43%, Vol Spike Ratio: 0.32x
/usr/local/lib/python3.12/dist-packages/numpy/_core/fromnumeric.py:4006: FutureWarning: The behavior of DataFrame.var with axis...
ValueError: The truth value of a Series is ambiguous.

The AI passed a DataFrame into a NumPy variance calculator instead of a flat 1D array. I tried to patch it with np.ravel(). It fixed the crash detector, but somehow that fix completely broke my Fractional Kelly sizer further down the pipeline. It started trying to size trades at 0.0 shares. I got so frustrated that I just ripped the Kelly sizer out entirely and hardcoded size = 0.05 (5% of equity per trade) for the rest of the day just to get trades on the board.
Ending Equity: ~$880,400.

Day 6 - 7 (3rd - 4th August): The VIX Sensor Failure
More architecture issues. My market regime sensor flatlined. It turns out the bot was pulling real-world VIX data from Yahoo Finance (which was sitting quietly at 15.71) while our internal Colab simulation was violently crashing.

[09:11:22] [INTRADAY CHECK] Polling Macro Environment... 📊 SENSOR READINGS -> VIX: 15.81 | News Sentiment: 0.00
🏭 STRATEGY FACTORY: Regime unclear. Assembling default neutral matrix...

I had to completely unhook the bot from external APIs and code an internal tape reader to calculate volatility strictly off the simulated self.history['SPY']. Back in Week 5 I was so proud of my Calmar ratio. I recalculated it this weekend and it’s currently sitting at 0.15.

Day 8 - 10 (5th - 7th August): A Bitter End
Going into the final days, I tried running a 15-minute Lookback Mean-Reversion Scalper.
We finally caught some decent moves. Terminal excerpt from Day 9:
[10:06:10] 📉 Executing SHORT: 170 of MSFT
[15:38:48] 📉 FLATTENING SPY | Signal: 💰 Trailing Stop Triggered (Long) | Realised PnL: +1.98%

But it wasn't enough to offset the damage from Day 5. We finished the simulation on Friday with an ending equity of $753,412.

Looking back at my numbers, I realised my "hardcoded 5% sizing" fix on Day 5 actually exposed me to way more risk than I calculated because I forgot to adjust it for correlation (I was taking 5% on MSFT and AAPL at the same time).

Being down nearly 25% means I now need a 33% gain just to get back to breakeven (Volatility Drag in action). My Sharpe went from a theoretical 1.4 in backtesting down to 0.38 in live simulation. It was a brutal way to learn, but dealing with unresolved bugs, bad data feeds, and simulated crashes taught me more about real quantitative engineering than the lectures ever could.
