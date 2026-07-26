15th July 2026
Moving from linear equities into derivatives this week felt like stepping up to a completely different tier of quantitative trading. Up until now, my backtester has been entirely directional—buying assets when trends or momentum look favourable, and relying on stop-losses to bail me out when things go south. But watching the relentless, sideways chop in the UK markets over the last few weeks made it obvious that a directional strategy alone is dangerously fragile. Overnight gap risks can easily blow right past a standard stop-loss due to slippage.

Today’s lecture on option fundamentals and the Black-Scholes model clicked into place. The realization that an option’s premium is a non-linear function split between Intrinsic Value and Time Value completely changes how you think about risk. We coded the Black-Scholes pricing engine and the Newton-Raphson method for Implied Volatility (IV) today. It’s fascinating how IV acts as the market's true forward-looking barometer, capturing the "skew" and "smile" where out-of-the-money puts trade at a rich premium because everyone is terrified of fat-tail crash events.

18th July 2026
Spent the weekend figuring out how to weave options and Greeks into my existing backtesting architecture without breaking the performance metrics we built in Weeks 4 and 5.

The Volatility Reality: Standard Black-Scholes assumes constant volatility and frictionless markets, which we know is completely detached from reality. To fix this in our Python pipeline, we integrated a rolling historical volatility calculation alongside a risk-free rate proxy so the algorithm can dynamically price synthetic option legs.

The Greek Integration: Delta gives us the true delta-adjusted exposure of our equity positions, while Vega and Theta remind us of the hidden cost of holding options over time (time decay is a brutal enemy if the market stays dead flat).

Hedging the Downside: Instead of relying solely on arbitrary ATR stop-losses that get whipsawed by market noise, I integrated a Protective Put / Collar logic into the backtester. By calculating the fractional cost of an Out-of-The-Money put option on trade entry days, the model now mathematically accounts for "Volatility Drag."

It’s satisfying to see the Calmar and Sortino ratios automatically penalise the strategy for the cost of insurance. It proves that institutional-grade safety isn't free—you have to pay a volatility tax to protect your capital against severe market shocks. Next week, we pivot into the final stretch before the live simulation starts on July 27th, and the system is finally starting to look resilient.
