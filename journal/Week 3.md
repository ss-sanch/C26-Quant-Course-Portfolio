25th June 2026

Just finished the Week 3 lecture on Core Strategies. It really put things into perspective. An algorithmic strategy is basically just a strict formula: Conviction + Rules.

We contrasted this with discretionary trading, which relies on human-led decisions and leaves way too much room for emotion and panic—something I’m definitely guilty of when staring at live charts!

We looked at Trend Following and Moving Averages, specifically the simple case of comparing a short-term MA50 to a long-term MA200 to spot uptrends or downtrends. It sounds brilliant on paper, but I can already see how it would get completely chewed up in a sideways, ranging market with constant false breakouts.

RSI was also covered for measuring momentum. It’s useful for spotting overbought or oversold conditions, but again, if a trend is aggressively strong, fading it just because the RSI is over 70 is a fantastic way to lose money.

28th June 2026

What an absolutely mental week in the markets. Geopolitics is completely driving the wheel right now, and the macro noise is deafening.

First off, Keir Starmer has resigned! That makes it the seventh Prime Minister since the Brexit vote. UK domestic uncertainty is spiking, and inflation pressures are expected to rise again, so I’m definitely keeping my algorithms far away from the FTSE 250 for now.

Globally, all eyes are on the US-Iran peace talks in Switzerland for a potential MOU. There’s so much conflicting news—Iran's Revolutionary Guard claimed the Strait of Hormuz is closed, while the US insists commercial shipping is fine. Brent crude is swinging wildly around $89 a barrel as a result.

In the tech world, the hangover from the massive SpaceX IPO continues. Accenture just cut their revenue growth outlook, causing a sharp tech sell-off and hitting ADRs like Infosys. The S&P 500 is hovering around 7,500, but market leadership is definitely shifting away from the mega-caps into smaller semiconductor and hardware names.

30th June 2026

Given how choppy and news-driven the market is right now, I think a simple Trend Following strategy would get absolutely slaughtered. The trends simply aren't sustaining. Instead, I want to build out the Statistical Arbitrage (Pairs Trading) model we discussed.

The logic relies on cointegration—finding two assets where they might trend on their own, but the gap between them does not drift forever.

If the price spread diverges massively due to a news spike (like the Strait of Hormuz rumours temporarily impacting two correlated energy majors), I can turn that spread into a standard Z-score. If the Z-score gets too wide, I can bet that the spread will mean-revert and come back together.

The main risk here is a structural break. If the geopolitical situation actually escalates or a company fundamentally changes, the spread might never revert. I need to code strict stop-losses to prevent getting trapped.

We also touched on Market Making to capture the bid-ask spread, but honestly, latency and inventory limits feel way too risky for my current Colab setup. Pairs trading is definitely the most logical play for this week's regime!
