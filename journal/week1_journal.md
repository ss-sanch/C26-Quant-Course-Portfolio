\# Algorithmic Trading Building Journal: Week 1 (June 8 – 12, 2026)



\*\*1. Market Regime \& Macroeconomic Context\*\*

Strategy design must be grounded in the prevailing market regime. During the week of June 8–12, 2026, the market operated in a "low-volatility bull" regime. Key macroeconomic data releases drove market mechanics this week:

\*   \*\*Inflation:\*\* The May CPI print showed headline inflation falling 0.4% from May. Core inflation printed at 2.6% YoY.

\*   \*\*Monetary Policy:\*\* At the June FOMC meeting, the newly appointed Federal Reserve Board Chairman Kevin Warsh held the target federal funds rate steady. Warsh delivered a hawkish message, emphasizing a commitment to bringing inflation back to the 2% target.

\*   \*\*Volatility \& Liquidity:\*\* Despite the hawkish Fed tone, the VIX fell 12.5% to 19.44. The tech sector maintained deep liquidity and high trading volumes, primarily driven by sustained capital expenditure in Artificial Intelligence.



\*\*2. Asset Selection \& Liquidity\*\*

Given the resilient tech sector and low broader market volatility, the initial strategy will target high-volume, large-cap technology equities (e.g., AAPL, NVDA, GOOGL). High liquidity in these assets ensures tight bid-ask spreads, which minimizes slippage—a critical factor when deploying algorithmic models in a live environment. 



\*\*3. Order Execution Strategy\*\*

To capitalize on current market conditions while strictly managing downside risk, the strategy will utilize a tiered order execution logic:

\*   \*\*Market Orders:\*\* Will be avoided to prevent execution at unfavorable prices during sudden volatility spikes.

\*   \*\*Limit Orders:\*\* Used for all trade entries. By setting a specific price ceiling (for buys) or floor (for sells), the model controls exact transaction costs. 

\*   \*\*Stop-Loss Orders:\*\* A hard stop-loss will be attached to every executed trade to cap maximum drawdown, neutralizing the risk of a sudden macro shock.

\*   \*\*Stop-Limit Orders:\*\* Used for breakout scenarios, ensuring the algorithm only enters a momentum trade if the price breaks a resistance level \*and\* can be filled within a strict price window.



\*\*4. Combating Overfitting in Model Development\*\*

A primary risk in algorithmic design is overfitting—creating a model that perfectly memorizes historical data but fails in live markets. To mitigate this, the strategy will strictly adhere to Out-of-Sample testing. Historical data will be split: 70% "in-sample" data used exclusively for optimizing parameters (like volume multipliers and moving averages), and 30% "out-of-sample" data used to validate the model's predictive power on unseen market conditions.

