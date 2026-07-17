10th June 2026

We had our first lecture today, focusing on the fundamentals of liquidity, volume, and order execution. It was a necessary refresher that made me reconsider my current approach to execution. When managing the family portfolio, I rarely worry about slippage due to the scale and longer time horizons, but in a live algorithmic environment, it is clearly a critical factor. To mitigate this, I will restrict my initial asset universe to highly liquid mega-caps like Apple and Nvidia to ensure tight bid-ask spreads on entry.



It was also a heavy macro day. US CPI data printed with core inflation at 2.6 percent, and Kevin Warsh held rates steady at his first FOMC meeting. Despite his hawkish tone regarding inflation targets, the market absorbed it well and the VIX actually fell. Given this resilient regime, I have finalised my order logic for the first model. I am avoiding market orders entirely to prevent poor fills during unexpected volatility spikes. Instead, the algorithm will rely strictly on limit orders for entries and hard stop-losses to cap maximum drawdowns.



12th June 2026

Spent this afternoon revisiting the problem of overfitting, which was the final topic from Wednesday's session. It is surprisingly easy to build a model that looks flawless on historical data but fails completely in live markets. To ensure the strategy remains robust, I am implementing a strict 70/30 split on the historical data from the outset. Reserving a pristine out-of-sample dataset for final testing should keep the model's performance grounded in reality before we reach the live simulation.

