# RadarCore — Complete Beginner's Guide
### From zero to understanding swing trading and how to use the software

> **Important Notice:** This document is exclusively educational. RadarCore is a learning and technical analysis tool. Nothing found here constitutes financial advice. Investing involves risk of capital loss. Always consult a regulated professional before making real financial decisions.

---

## How to use this guide

You don't need to read it all at once. It's structured as a journey: start from the beginning if you know nothing about finance, or go directly to the section that interests you if you already have some background. Every important concept appears in **bold** the first time it's mentioned and is immediately explained with real-world examples.

---

# PART 1 — The World of Investing, Explained from Zero

## Chapter 1: Why do people invest?

Imagine you have €1,000 kept under your mattress. After a year, it's still €1,000. But prices have gone up by 3% (bread, electricity, rent). In real terms, those €1,000 are now worth less: you can buy fewer things with them than a year ago.

This is called **inflation**: the loss of purchasing power of money over time. It's the silent enemy of idle savings.

People invest to try and make their money grow at a rate higher than inflation. Instead of a mattress, they put their money to work.

### The three major investment options

**1. Fixed Income (bonds, deposits):** You lend money to a bank or government in exchange for an agreed interest. Low risk, low return. Example: a 2% annual deposit.

**2. Variable Income (stocks/shares):** You buy a small part of a company. If the company does well, the value of your part goes up. If it does poorly, it goes down. Higher risk, but much higher return potential.

**3. Alternative Assets (real estate, gold, cryptocurrencies):** Each with its own rules.

RadarCore works exclusively with **variable income**, specifically with **stocks** of large companies listed on the stock exchange.

---

## Chapter 2: What is a stock and how does the stock market work?

### The stock as a piece of a company

When a large company wants to grow and needs money, instead of asking for a bank loan, it may decide to "sell pieces of itself" to the public. Each piece is a **stock** (also called a *share*).

**Real example:** Apple has approximately 15 billion shares in circulation. If you buy one, you own a fifteen-billionth part of Apple. A small amount? Yes. But if Apple is worth more tomorrow, your piece is also worth more.

### The ticker: the code name for each company

Every listed company has a unique abbreviated code used across the financial world. It's called a **ticker symbol** or simply a **ticker**.

| Company | Ticker |
|---|---|
| Apple Inc. | AAPL |
| Microsoft | MSFT |
| Visa Inc. | V |
| Inditex (IBEX) | ITX.MC |

In RadarCore, you'll always see the tickers in the **Symbol** column of the results table, and you can click them to go directly to Yahoo Finance.

### The stock market as a marketplace

The **stock market** (or stock exchange) is simply the place where buyers and sellers of shares meet. Today it's electronic: there's no physical room with people shouting. Every second, millions of buy and sell orders cross paths automatically.

The **price** of a stock at any given moment is simply the last price at which someone was willing to buy and another to sell. If more people want to buy Apple today than sell it, the price goes up. If there are more sellers than buyers, it goes down.

### OHLCV: the five data points of each day

For every stock and every market day, five fundamental data points are recorded. You'll find them on any professional chart and in RadarCore:

- **O (Open):** Opening price. The first price of the day.
- **H (High):** Maximum price reached during the session.
- **L (Low):** Minimum price of the session.
- **C (Close):** Closing price. The last price of the day. It's the most important and what RadarCore uses for most calculations.
- **V (Volume):** Number of shares that have changed hands that day.

**Why does volume matter?** A price movement with high volume is much more significant than the same movement with low volume. If a stock goes up 5% but very few people bought, it might be noise. If it goes up 5% with double the usual volume, it's a sign of real market conviction.

---

## Chapter 3: Benchmark Indices

Following 500 companies one by one would be impossible. That's why **market indices** exist: baskets of companies that represent a broader group.

### The main indices used by RadarCore

**S&P 500 (USA):** The 500 largest companies in the United States by market capitalization. It's the thermometer of the American economy and, by extension, the global economy. Includes Apple, Microsoft, Amazon, NVIDIA, JPMorgan, etc.

**NASDAQ 100 (USA):** The 100 largest non-financial companies on the NASDAQ, the American tech stock exchange. Highly tech-focused: Apple, Microsoft, NVIDIA, Meta, Alphabet, Tesla...

**IBEX 35 (Spain):** The 35 most liquid companies on the Spanish stock exchange. Santander, Inditex, BBVA, Iberdrola, Telefónica...

**DAX 40 (Germany):** The 40 top German companies. SAP, Siemens, Volkswagen, BMW, Allianz...

**EuroStoxx 50 (Europe):** The 50 largest companies in the Eurozone, across all sectors and countries.

**Nikkei 225 (Japan):** 225 leading Japanese companies. Toyota, Sony, SoftBank...

**Nifty 50 (India):** The 50 top companies on the Mumbai stock exchange.

### Why is the S&P 500 the "global thermometer"?

When the S&P 500 falls sharply, almost the entire financial world notices. Institutional investors (pension funds, banks, insurance companies) move trillions of dollars, and when they sell American stocks, they also sell in other markets to cover losses. That's why RadarCore always uses the S&P 500 as a reference to detect if a drop is global or specific to a company.

### Market Capitalization: the size of a company

**Market capitalization** (*market cap*) is the total value of a company on the stock exchange. It's calculated by multiplying the price of a share by all existing shares.

```
Market Cap = Price per share × Total number of shares
Example: Apple at $200 × 15,000M shares = ~$3 trillion
```

| Category | Market Cap | Examples |
|---|---|---|
| Mega-cap | > $200B | Apple, Microsoft, NVIDIA |
| Large-cap | $10B - $200B | Visa, McDonald's, Nike |
| Mid-cap | $2B - $10B | many solid companies |
| Small-cap | $300M - $2B | small companies |
| Micro-cap | < $300M | very speculative |

By default, RadarCore only analyzes companies with **Min Mkt Cap ≥ $10B** to avoid noise and manipulation from small companies.

---

# PART 2 — Investment Strategies: How Do People Win?

## Chapter 4: The Three Main Philosophies

### Buy & Hold
Warren Buffett's philosophy. You buy shares in excellent companies and keep them for years or decades without selling. It works very well for those with patience and a long horizon. The problem: it takes a lot of time and it's emotionally difficult to withstand 40-50% drops without selling.

### Day Trading
You buy and sell on the same day, taking advantage of movements lasting minutes or hours. It requires a lot of time, access to professional platforms, significant capital, and extreme risk tolerance. Studies show that the vast majority of day traders lose money in the long run.

### Swing Trading (RadarCore's Strategy)
The middle ground. **Swing trading** means taking advantage of the "swings" in a stock's price over a horizon of **days to weeks** (typically 2-6 weeks). You aren't in front of the screen all day, but you don't buy and forget for years either.

The central idea: stock prices don't move in a straight line. They go up, down, consolidate, then go up again. A swing trader tries to detect when a stock has dropped for temporary reasons and buy it before it goes back up.

---

## Chapter 5: RadarCore's "Buy the Recovery" Strategy

### The intuition behind the strategy

Imagine a solid company, say Visa (the credit card company). One quarter its results are slightly below analyst expectations, or there's a moment of general market pessimism. The price drops 20% in a few weeks.

But Visa is still processing billions of transactions every day. Its business hasn't fundamentally changed. That 20% drop is a **temporary opportunity** to buy a solid company at a discount price.

This is what RadarCore looks for: companies that have dropped for temporary reasons and already show signs of having hit rock bottom and recovering.

### Why "Buy the Recovery" and not "Buy the Dip"?

"Buy the Dip" would be buying while the stock is still falling. The problem is that no one knows when it will hit bottom. You could buy at -20% and have it keep falling to -60%.

"Buy the Recovery" waits for confirmation: the stock has already hit the minimum and has bounced a bit. You miss the first few centimeters of the recovery, but you confirm that the floor is here. It's less exciting but much more disciplined.

### The pattern we look for: the "V" or "L" shape

Visually, the strategy looks for two main patterns:

**V-Pattern (V-RECOVERY):**
```
     Peak
    /      \
   /        \         Recovery
  /          \       /
 /            \ Low /
```
Quick and strong drop followed by an equally quick recovery. High volatility. Can be very profitable but also risky.

**L-Pattern (L-BASE):**
```
     Peak
    /      \
   /        \___________  ← Side base (accumulation)
  /                       \
 /                         Slow but solid recovery
```
Drop followed by a period of horizontal consolidation. Institutional investors "accumulate" shares without rushing while the price remains stable. When it finally breaks higher, it's usually a more solid movement.

**For RadarCore, L-BASE is considered higher quality than V-RECOVERY** because the lateral base suggests large buyers are positioning themselves discreetly.

---

# PART 3 — Fundamental Technical Concepts

## Chapter 6: Drawdown, Rebound, and Recovery

### Drawdown: how much a stock has fallen

**Drawdown** is the percentage drop from a peak to a subsequent low. It's the measure of "pain" a stock has suffered.

```
Drawdown Calculation:
Recent peak: $100
Subsequent low: $75
Drawdown = (100 - 75) / 100 = 25%
```

In RadarCore, the **Drop %** column shows exactly this value: how much the stock has dropped from its peak in the last X days (configurable with the *Historical Window* parameter) to its minimum.

**For example:** If Visa had a peak of $360 and dropped to $290, the Drop % would be:
```
(360 - 290) / 360 = 19.4%
```

### Rebound: the first sign of life

**Rebound** measures how much the stock has risen from its minimum to the current price. It's the confirmation that the drop has stopped.

```
Rebound Calculation:
Minimum: $75
Current price: $82
Rebound = (82 - 75) / 75 = 9.3%
```

In RadarCore, the **Rebound %** column shows this value. The *Minimum Rebound (%)* parameter (default 2%) filters out stocks that haven't shown any sign of recovery yet.

### Why does RadarCore require a minimum rebound?

To avoid buying "falling knives." If a stock has dropped 30% but is still falling, the rebound is 0%. There's no confirmation of a turnaround. RadarCore waits for the price to demonstrate that the low is already behind us.

---

## Chapter 7: Idiosyncratic vs. Systemic Drop

This distinction is **the most important of the whole strategy**. Understanding it will triple the quality of your decisions.

### Systemic Drop: the market explains the drop

If the entire market (S&P 500) drops 20%, it's normal for many companies to drop 20-25%. In this case, the drop is not the company's fault: it's the global context. Buying in a general market drop environment is risky because there is no clear "floor."

### Idiosyncratic Drop: the company falls alone

If the market goes up 5% but a company drops 25%, that drop is **idiosyncratic** (meaning specific to that company). It could be due to disappointing results, a change in management, a temporary regulatory problem, or simply exaggerated investor fear.

These idiosyncratic drops in fundamentally solid companies are the **best swing trading opportunities** because:
1. The company didn't drop because the world is going poorly.
2. When the fear passes, the price tends to recover toward the previous level.

**In RadarCore you'll see:** `✅ Idiosyncratic drop (+16.6% vs SPY)` in the scan results. It means the company has dropped 16.6% MORE than the market, confirming its drop is specific to it.

### How does RadarCore calculate it?

```
Relative Drop = Company Drawdown - SPY Drawdown
                over the same time period

If Relative Drop > 5% → Idiosyncratic drop ✅
If Relative Drop ≤ 5% → Systemic drop ⚠️
```

---

## Chapter 8: Moving Averages (EMA)

### What is a moving average?

Imagine you want to know if someone has a fever. You don't just look at their temperature for one second: you measure it over time. **Moving averages** do the same with a stock's price: they smooth out daily noise to show the real trend.

An **EMA (Exponential Moving Average)** is an exponential moving average that gives more weight to recent prices than old ones. It reacts faster to changes than a simple moving average.

### EMA 50 and EMA 200: the most important ones

**EMA 50:** Average of the last 50 trading days. Represents the medium-term trend.

**EMA 200:** Average of the last 200 days. Represents the long-term trend. Many institutional investors consider a stock to be "in an uptrend" when it trades above its EMA 200.

### Golden Cross and Death Cross

**Golden Cross:** When the EMA 50 crosses above the EMA 200. A strong bullish signal. Many automatic algorithms buy at this moment.

**Death Cross:** When the EMA 50 falls below the EMA 200. A bearish signal.

```
Price > EMA50 > EMA200 → Solid uptrend (RISE)
Price < EMA50 < EMA200 → Downtrend (DESCENDING)
Price fluctuates around EMA50 → Possible SWING or LATERAL
```

---

## Chapter 9: RSI — Relative Strength Index

### What does RSI measure?

The **RSI (Relative Strength Index)** is an indicator that measures the speed and magnitude of recent price movements on a scale of 0 to 100. It was created in the 70s and remains one of the most widely used in the world.

**Classic Interpretation:**
- RSI > 70 → The stock might be **overbought** (risen too fast, possible correction)
- RSI < 30 → The stock might be **oversold** (dropped too fast, possible rebound)
- RSI between 40-60 → Neutral zone

**How RadarCore uses it:** RSI at the bottom of the floor is a quality confirmer. If a stock hits its minimum with RSI < 30 and then the RSI starts recovering toward 40-50, it's a sign that the overselling is exhausted and the rebound may have continuity.

**Important:** RSI alone is never enough to make decisions. It's a confirmer, not a predictor.

---

## Chapter 10: ATR — The real volatility of each stock

### What is ATR?

**ATR (Average True Range)** measures how much a stock moves on average each day. It doesn't tell the direction (up or down), just the typical magnitude of the movement.

**Example:**
- If Apple has an ATR of $5, it means that on average every day the price fluctuates $5 between its low and high.
- If a $10 company has an ATR of $2, it's enormously volatile (20% daily!).

### What is ATR for in RadarCore?

**To calculate the Stop Loss intelligently.** Instead of setting a fixed stop (e.g., "sell if it drops 8%"), we use ATR to adapt the stop to each stock's real volatility:

```
Stop Loss = Floor Minimum - (ATR × 1.5)
```

For a very volatile stock, the stop will be wider (to avoid being "splashed" by normal movements). For a quiet stock, the stop will be narrower.

---

## Chapter 11: The Concept of Pivot and the RDP Algorithm

### What is a pivot?

A **pivot** (or turning point) is a local high or local low on a stock chart. In a two-year chart, there might be dozens of movements, but pivots are the "key moments": the peaks and structural valleys of the price.

- **Peak (marked as P1, P2...):** A local high, from where the price turned down.
- **Trough (Valley, marked as T1, T2...):** A local low, from where the price turned up.

### RDP Algorithm: filtering market noise

The financial market is full of noise. Every day the price goes up and down for hundreds of trivial reasons. The challenge is separating meaningful movement (structural) from irrelevant noise.

**RDP (Ramer-Douglas-Peucker)** is a mathematical algorithm originally designed to simplify lines in digital cartography. If you have a coastline with a thousand tiny bays, RDP helps you draw it with 20 essential points instead of 1,000, maintaining the global shape.

RadarCore applies it to a stock's price: it simplifies two years of trading to between 6 and 16 key points (the pivots), removing the noise of specific days to reveal the real structure of the movement.

**Visually in RadarCore:** In the "Pivots" view of the chart, you see the white dashed line (the RDP pivots) over the gold line (real price). The white line shows you the stock's "narrative," without noise.

---

## Chapter 12: Eras — the price narrative

### Segments and Eras

Once the RDP algorithm has identified pivots, RadarCore classifies each segment between two consecutive pivots:

- **UP:** Segment goes up more than 3%.
- **DOWN:** Segment goes down more than 3%.
- **FLAT:** Change is less than 3% (side consolidation).

A sequence of segments is what RadarCore calls the **Eras** of a stock. The sequence of eras is the stock's "story" told in simple words.

**Example sequences:**
```
UP-UP-UP               → Clear uptrend (RISE)
DOWN-DOWN-UP-DOWN-UP   → Oscillation with swing potential (SWING)
DOWN-FLAT-FLAT-FLAT    → Drop and side base (L-BASE / LATERAL)
UP-DOWN-UP-DOWN        → Regular swing (SWING)
```

**In the UI you'll see:** `Last segment FLAT (-0.6%) · Second-to-last UP (+3.8%) · Recovery at 24% of peak-valley range · Valley 0 days ago`

This tells you: the last structural movement is sideways (consolidation), the previous one was a 3.8% rise, and the stock has recovered 24% of the path from its minimum to the previous peak.

---

# PART 4 — RadarCore's Classification System

## Chapter 13: The Five Buckets (Categories)

RadarCore classifies every stock into one of five structural categories. It's not a binary system (opportunity yes/no), but a classification of what "state" the stock is in.

### SWING 🔄
The stock shows an oscillation pattern: it has gone up, down, and potentially will go back up. This is the most sought-after pattern for swing trading. The essential condition is that it has dropped enough from a recent peak and demonstrated the low is behind us with an initial rebound.

**SWING Subtypes:**
- **SWING → BREAKOUT:** The stock just broke above its last significant local peak. A sign of strength, but watch out for traps.
- **SWING → PULLBACK:** After a breakout, the stock has pulled back slightly. If it stays above the support, it may be a second entry opportunity better than the original breakout.
- **SWING → RETEST:** The stock has returned to test its previous minimum level (without breaking it). If support holds, it's a very powerful confirmation.

### RISE 📈
The stock is in a clear and sustained uptrend. No big oscillations: it just goes up consistently. For pure swing trading it's less interesting (no previous drop), but it indicates a company with strong momentum that may continue rising.

**RISE Subtypes:**
- **RISE → BREAKOUT:** Surpassing new annual highs. Very strong, but might be "too expensive."
- **RISE → PULLBACK:** Pullback within an uptrend. Can be an entry point for those who believe in trend continuation.

### LATERAL 〰️
The stock is doing nothing: moving in a narrow range without clear trend up or down. It might be "accumulating" (getting ready to move up) or just sleeping. On its own not an action signal, but if preceded by a drop it's what RadarCore calls **L-BASE**.

### HIGHS 🔝
The stock trades near its recent peak. High risk of correction. RadarCore marks it for information but doesn't consider it a "Buy the Recovery" opportunity (no previous drop to recover from).

### DESCENDING 📉
The stock is in a clear downtrend. The market is turning its back on it. Avoid for purchases. It could be interesting for short selling, but that is an advanced strategy outside the scope of this guide.

---

## Chapter 14: Trazo Phases — Where are you in the journey?

Knowing a stock is SWING is useful, but it doesn't tell you if you're entering at the beginning of the recovery or after it has already moved a lot. **Phases** answer exactly this question.

### The Progress Formula

```
Progress % = (Current Price - Pivot Minimum) 
             / (3-Year ATH - Pivot Minimum) × 100
```

This formula measures how much of the possible journey has already been covered. If the 3-year high is $100 and the pivot minimum was $60, and the stock is now at $70:

```
Progress = (70 - 60) / (100 - 60) × 100 = 25%
```

The stock has covered 25% of the possible path between its minimum and previous high.

### The Four Phases

**🟢 VALLEY (< 20% progress)**
The stock just bounced from the low. You have the maximum distance to cover to the previous high (maximum possible upside). But also maximum risk: you don't know if the bounce is real or a dead cat bounce (temporary bounce before falling further).

*When it's a good option:* When the pattern is L-BASE, volume is accompanying, and the drop is idiosyncratic.

**🟡 MID (20%-65% progress)**
The recovery is already somewhat underway. The uptrend is starting to be confirmed by markets. You still have path to the previous high but have missed the initial part. This is the **"sweet spot"** that Trazo and RadarCore consider the best balance between risk and opportunity.

*When it's a good option:* Almost always. The risk/reward ratio is the best of these four.

**🟠 MATURE (65%-85% progress)**
The stock has recovered most of the lost ground. Remaining path to the peak is limited. Risk of a new correction is high because many investors who bought at high prices now have the chance to "get back what they lost" and sell.

*When to be careful:* Watch the volume. If the rise is on decreasing volume, it might be a trap.

**🔴 LATE (> 85% progress)**
The stock has already returned almost to the previous high. Little room for further rise, lots of selling pressure. RadarCore shows it for info but doesn't consider it a candidate for a new entry.

### Upside: how much is left to rise

In the results table you'll see **Upside 3Y** and **Upside 5Y**. These percentages indicate how much the stock could rise if it returned to its 3 or 5-year high.

```
Upside 3Y = (3-Year ATH - Current Price) / Current Price × 100
```

A stock with Phase VALLEY and Upside 3Y of 40% is much more interesting than one with Phase LATE and Upside 3Y of 5%.

---

## Chapter 15: Confidence — How is it calculated?

The **Confidence %** you see in the **Conf.** column is a composite score RadarCore calculates to rank opportunities from best to worst. It's not magic: it's the weighted sum of four factors.

### The Four Components of Confidence

**1. Quality of the Drop (30% of total)**
The closer the real drop (from peak to low) is to 40%, the higher the score. A 20% drop gets fewer points than a 35% one. Because larger drops imply larger "discounts" and higher recovery potential.

```
Score = min(Drop% / 40%, 1.0) × 0.30
```

**2. Quality of the Rebound (20% of total)**
A rebound between 5% and 10% from the bottom is most valued. Too little (<2%) doesn't confirm the turn. Too much (>15%) may mean we've missed the best entry.

```
Score = min(Rebound% / 10%, 1.0) × 0.20
```

**3. Pattern Shape (25% of total)**
- **L-BASE or LATERAL:** Maximum score (0.25). Lateral base suggests institutional accumulation.
- **V-RECOVERY or SWING:** Medium score (0.15). Quick recovery is less predictable.
- **EARLY:** Low score (0.05). Too incipient to trust.

**4. Market Context (25% of total)**
- **Confirmed idiosyncratic drop:** 0.25 points. Drop is company-specific.
- **Market data unavailable:** 0.10 points. Benefit of the doubt.
- **Systemic drop:** 0 points. The market explains it all.

**Practical example:**
```
MSFT: Drop 26% → 0.195 | Rebound 17% → 0.20 | 
      V-RECOVERY Pattern → 0.15 | Idiosyncratic ✅ → 0.25
      
Confidence = (0.195 + 0.20 + 0.15 + 0.25) × 100 = 79.5%
```

---

## Chapter 16: Stop Loss, Targets, and the R/R Ratio

### Stop Loss: protecting capital

**Stop Loss (SL)** is the automatic sell order we set to limit losses if we're wrong. It's not a defeat: it's an integral part of any professional strategy.

**Fundamental trading rule:** Preserving capital is top priority. A 50% loss requires a 100% gain to recover. A 10% loss only needs an 11% gain.

```
Stop Loss = Pivot Minimum - (ATR × 1.5)
```

We use 1.5 times ATR because the price can make normal movements within its usual volatility without the investment thesis being broken. If the stop were too tight, it would trigger on normal noise.

**Invalidation level:** If the price falls below Stop Loss, the "Buy the Recovery" thesis is no longer valid. The price has broken the support where the pattern had formed. Exit quickly and look for the next opportunity.

### Targets: Taking Profits

**T1 (Target 1 — Conservative Objective):**
The first profit-taking point. In RadarCore it's usually marked around 85% of the distance between minimum and previous peak. At this point, many swing traders sell half the position to lock in gains and let the rest "run" to T2.

**T2 (Target 2 — Ideal Objective):**
The previous peak before the drop. It's the natural goal of "Buy the Recovery": if the company recovers all lost ground, the price would return to where it was. In practice, many recoveries don't reach 100% but do get to 70-80%.

### The Risk/Reward (R/R) Ratio

This is the **most important** concept for long-term financial survival.

```
R/R Ratio = (Target - Entry) / (Entry - Stop Loss)
```

**Example:**
```
Entry: $100
Stop Loss: $92  → Risk = $8
Target (T2): $125 → Reward = $25
R/R Ratio = 25 / 8 = 3.1x
```

An R/R ratio of 3.1x means for every dollar you risk, you can win $3.1. RadarCore considers an R/R of 2.0x as the minimum acceptable.

**The magic of R/R:** Imagine you make 10 trades with R/R of 2x:
- 6 go wrong: you lose 6 × $1 = -$6
- 4 go right: you win 4 × $2 = +$8
- Net result: +$2 **without even being right half the time!**

With good R/R, you can be profitable even getting less than 50% of trades right.

---

## Chapter 17: Earnings — the biggest risk in swing trading

### What are Earnings?

Every quarter (four times a year), listed companies publish their official financial results. Revenue, profit, future outlook... This publication is called an **Earnings Report**.

The market usually has expectations about results. If the company beats them → price can go up 10-20% in a day. If they miss → it can drop 10-20% in a day.

### Why are Earnings dangerous for swing trading?

Because **movement direction is unpredictable until the last moment**, even for professionals. Neither technical analysis nor the chart pattern can tell you if results will be better or worse than expectations.

If you have an open position and Earnings come out while you hold it, you are gambling without knowing heads or tails. This is pure speculation, not swing trading.

### How RadarCore manages Earnings?

RadarCore shows a warning badge in the UI:
- **⚠️ EARN Xd (red):** Earnings in less than 14 days. Very high risk. Consider waiting.
- **📅 EARN Xd (yellow):** Earnings in 15-30 days. Warning. Watch your timing.
- **earn Xd (gray):** Earnings in 31-60 days. Info for planning.

**Recommended strategy:** If an opportunity has Earnings in less than 14 days, you have two options:
1. **Don't enter** until Earnings have passed (and price has stabilized).
2. **Enter with a very reduced position** (less than you normally would) to limit exposure to uncertainty.

---

# PART 5 — Using RadarCore Step by Step

## Chapter 18: The Sidebar — global configuration

The **sidebar** (left panel) contains global settings that affect how AI analyzes opportunities.

**AI Provider:** Choose between Google Gemini (default and recommended) or OpenAI (GPT-4o). Affects the quality and style of generated reports.

**Model:** The specific model within each provider. For regular use, the default model is enough.

**API Key Settings:** If you have your own API keys, you can enter them here. Not required for basic functions.

**AI Report Language:** The language in which AI will write reports: Catalan, Spanish, or English.

**Analysis Mode:**
- **Automatic mode (ON):** All detected opportunities automatically go through advanced pattern analysis. Recommended while learning.
- **Automatic mode (OFF):** Enables Watchlist Mode. Only tickers you manually select in the Watchlist tab are analyzed in depth.

**Pre-filter universe:** Enables an additional filter that removes zombie companies (no recovery history) and companies with insufficient liquidity. Recommended off while learning to see more results; turn on when you want higher quality results.

---

## Chapter 19: Market Scanner Tab — doing your first scan

This is the main screen. Here you configure parameters and launch the scan.

### Select Market (Market to Scan)

Choose among seven available markets:

| Market | Recommended for... |
|---|---|
| S&P 500 (USA) | First-time learning. Well-known companies. |
| NASDAQ 100 (USA) | Interested in tech |
| IBEX 35 (Spain) | Close-by Spanish companies |
| DAX 40 (Germany) | Industrial European companies |
| EuroStoxx 50 | European diversification |
| Nikkei 225 | Exposure to Japan |
| Nifty 50 | Emerging market, India |

**Beginner recommendation:** Starts with S&P 500. Companies will be familiar (Apple, Microsoft, Visa...) and there's plenty of information available to learn.

### Symbol Limit

Set to 0 to analyze all companies in the market, or a small number (20-50) for quick tests. With 0 and S&P 500, scanning might take 30-60 seconds.

### Strategy Parameters — the strategy sliders

**Minimum Drop (%) — default 15%:**
How much the stock must have dropped from its recent peak. At 15%, you look for companies that have lost at least 15% of their value. If set very high (>30%), you'll see few companies but in "big discount" situations. If set low (<10%), you'll see many companies but some with insignificant drops.

*Initial recommendation:* 15% is a good starting point. In bull markets you might need to lower to 10%. In bear markets, opportunities will appear naturally at 20-30%.

**Historical Window (Days) — default 60:**
How many days back we look for the reference peak. At 60 days, the peak is the highest of the last 2 months. At 252 days (one year), the peak is the annual one. Longer windows detect larger structural drops; short windows detect smaller recent drops.

*Initial recommendation:* 60 days for 2-6 week swing trading. 120-252 days for long-term recovery positions.

**Minimum Rebound (%) — default 2%:**
Minimum rebound from the floor that confirms the drop has stopped. At 2%, it's very permissive (any small turn). At 8-10%, you demand a recovery already underway but miss the initial entry.

*Initial recommendation:* 2-5% to capture opportunities in VALLEY phase. 5-10% if you prefer more confirmation and don't mind missing the initial movement.

**Min Mkt Cap (B $) — default $10B:**
Filters by minimum market capitalization. $10B removes most speculative small-caps. For those wanting to explore smaller companies (with more risk), it can be lowered to $2-5B.

**Min Avg Vol (M) — default 1M shares/day:**
Minimum average volume. Liquidity is essential: you need to be able to buy and sell without your order moving the price. 1M shares/day is the minimum reasonable for large-cap companies.

### The Run Scan button

When pressing **Run Scan**, RadarCore:
1. Downloads price data for each company in the selected market.
2. Applies the universe filter (if active).
3. Calculates Drop % and Rebound % for each company.
4. Applies Strategy Parameters filters.
5. For those that pass, runs the PatternClassifier (RDP + Eras + Buckets).
6. Calculates Phase (VALLEY, MID, MATURE, LATE).
7. Detects upcoming Earnings.
8. Saves results to the database and shows them in the UI.

---

## Chapter 20: History & Reports Tab — interpreting results

This is where you see, analyze, and manage detected opportunities.

### The results table

Each row is a company that passed all filters. Columns:

**Symbol:** Company code. Click to go to Yahoo Finance and see full info.

**Company:** Full company name.

**Drop %:** Real drop from recent peak to minimum. *Rule of thumb: more drop means more "discount" but also more risk thesis doesn't play out.*

**Rebound %:** How much it rose from bottom to today. *5-15% rebound in a VALLEY is ideal. Over 30% in VALLEY might be excessive (maybe we missed the entry).*

**Pattern:** Type of pattern detected. Quick reminder:
- SWING / L-BASE / V-RECOVERY → Candidates for Buy the Recovery
- RISE → Uptrend, not "Buy the Recovery" but can be interesting
- LATERAL → Possible accumulation, watch
- DESCENDING / HIGHS → Avoid for now

**Phase:** Where we are in the path. 🟢 VALLEY is the best moment, 🔴 LATE is too late.

**Upside 3Y:** How much it could rise if it returned to 3-year high. Over 20% is interesting.

**Conf.:** Composite quality score. Sort by this column descending to see the best opportunities first.

**Date:** When the opportunity was detected. Opportunities from many days ago may have changed situation.

### Charts

Select one or more rows and press **View Charts** to see visual representation.

**Mountain View:** Gold price line over black background. Ideal for clear global trend viewing.

**Eras View:** Colored areas showing each RDP algorithm segment:
- Green areas → UP segments
- Red areas → DOWN segments
- Gray areas → FLAT segments

**Pivots View:** White dashed line of key points (P1, P2... for peaks; T1, T2... for valleys) over the price line. Lets you see structure without noise.

**Candles View:** Traditional Japanese candlestick chart (full OHLCV). Each candle represents one day: green if price went up, red if down.

**Chart header** (small text above chart): Gives important contextual info like `Last segment UP (+3.8%) · Recovery at 24% of peak-valley range · Valley 0 days ago · RETEST`. Always read as your first summary.

**Trazo Phase Analysis panel:** Shows Phase, Progress %, Upside 3Y, Upside 5Y, and Pivot price (pattern floor). Use it to instantly understand where you are in the possible path.

---

## Chapter 21: Watchlist Tab — manually curating opportunities

**Watchlist** is the manual curation step that Trazo considers essential. It works like this:

1. Scan gives you, say, 25 opportunities.
2. Quickly look at charts for each (30 secs/chart = 12 mins).
3. Those that visually convince you (good pattern, good shape), add to Watchlist.
4. On Watchlist items, do deep analysis: generate AI report, look at fundamentals on Yahoo Finance, check sectoral context.

### Automatic Mode vs. Watchlist Mode

**Automatic Mode (recommended for beginners):** All opportunities go through full analysis. Ideal while learning and wanting to see how system works.

**Watchlist Mode (recommended with experience):** You separate detection (algorithm) from final selection (you). Warren (author of system that inspired part of RadarCore) says he spends 1 hour on Yahoo Finance on those his bucketer selects. Trazo does an initial visual manual choice. Both agree the human eye adds value over the algorithm.

---

## Chapter 22: Investor Knowledge Tab — customizing the AI

Here you can upload your own investment philosophy PDFs to train the AI. If you have a Warren Buffett book, an analysis article you liked, or your own investment notes, the AI will incorporate them into its reports to give you answers more aligned with your philosophy.

Examples of documents to upload:
- Swing trading strategy summaries
- Notes on sectors that interest you
- Personal entry and exit criteria
- Articles about specific companies

---

# PART 6 — Putting It All Together: The Full Trade Flow

## Chapter 23: From Scan to Decision

### Step 1: Configuration (5 minutes)

Open RadarCore. In sidebar, verify language is what you want and mode is Automatic. In Market Scanner, select S&P 500. Leave parameters at default for the first time.

### Step 2: The Scan (30-60 seconds)

Press Run Scan. Watch logs as it scans. You'll see companies passing or failing filters. When finished, go to History & Reports.

### Step 3: First table review (5-10 minutes)

Sort by Conf. descending. Look at the first 10 rows. Filter by SWING or LATERAL if you want to focus on recovery patterns.

Mentally eliminate:
- Anything with Phase LATE or MATURE (already rose too much)
- Those with ⚠️ EARN in less than 14 days (if you don't want the risk)
- DESCENDING ones (avoid for purchases)

### Step 4: Visual chart review (2 minutes per company)

For each remaining candidate, press View Charts. Look at:
1. Mountain View: General trend. Clean up or down?
2. Pivots View: Pattern clear? Can you see the V or L?
3. Header: What is the last segment? FLAT is good (base), DOWN is bad.
4. Trazo Phase Analysis: Where is Progress? Upside 3Y attractive?

### Step 5: Deep analysis of candidates (10-20 minutes)

For the 3-5 companies that passed visual review, generate an **AI report** (Generate Reports). AI will explain fundamental context, non-technical risks (debt, competition, regulation) and if there are reasons not to enter.

At the same time, click the Symbol in the table to go to Yahoo Finance. Look at:
- Recent news section: any clear reason for the drop?
- Page Summary: market cap, P/E ratio, dividend.
- Earnings: when is the next one? Does it match what RadarCore marked?

### Step 6: The decision (you, not the algorithm)

RadarCore detects. You decide. Ask yourself:
1. Do I understand why this company dropped?
2. Do I believe the reasons for the drop are temporary?
3. Will the company still exist and thrive 6 months from now? 2 years?
4. Does the R/R ratio (Stop Loss to Target) justify the risk?
5. If it drops to Stop Loss, will I be comfortable having lost it?

If answers to all are yes, you have a solid investment thesis. If you doubt any, better to wait.

---

## Chapter 24: The Golden Rule — Risk Management and Diversification

No detection system is perfect. RadarCore gives probabilities, not certainties. To survive (and thrive) long-term, risk management is more important than any specific signal.

### Rule 1: Never everything in one position

If you put all your capital in one company and it goes wrong, you lose everything. If you distribute over 10 trades and one goes wrong (and Stop Loss triggers), you lost 10% of part of capital.

**Recommendation:** Between 8 and 15 simultaneous positions. Maximum 10-15% of total capital in a single company.

### Rule 2: Define Stop Loss BEFORE entering

Decide where you'll exit if wrong BEFORE buying. If you don't, market psychology will make it impossible once you're in. "I'll wait for it to bounce" is the phrase that ruined many investors.

### Rule 3: Minimum R/R is 2x

If the trade doesn't have at least double the possible reward compared to the risk taken, it's not a good swing trade.

### Rule 4: Accept losses fast, let winners run

Stop Loss triggers? Exit without hesitation. The market never owes you a recovery. But if a position goes in your favor, don't close out of fear: let it reach T1 and decide then.

### Rule 5: Don't invest what you can't afford to lose

All previous concepts are worthless if capital you invest is what you need for next month's rent. Emotional pressure of needing the money takes the worst possible decisions.

---

## Quick Glossary

| Term | Simplified definition |
|---|---|
| Stock/Share | Piece of ownership in a listed company |
| ATH | All-Time High. Historic maximum price of a stock |
| ATR | Average True Range. Measure of typical daily volatility |
| Stock Market | Electronic market where shares are bought and sold |
| Bucket | Structural category of a stock (SWING, RISE, etc.) |
| Idiosyncratic drop | Drop specific to a company, not general market |
| Drawdown | Percentage drop from a peak to a subsequent low |
| Earnings | Official quarterly financial results of a company |
| EMA | Exponential Moving Average. Smoother average favoring recent prices |
| Era | Chart segment classified as UP, DOWN or FLAT |
| Index | Company basket representing a market (S&P 500, IBEX 35...) |
| Inflation | Loss of purchasing power of money over time |
| L-BASE | Drop pattern followed by side base. Sign of accumulation |
| Liquidity | Ease of buying or selling a stock without moving price |
| Market Cap | Market Capitalization. Total value of a company on stock exchange |
| OHLCV | Open, High, Low, Close, Volume. The five daily data points of a stock |
| Pivot | Key turning point on a chart (Peak or Trough) |
| R/R Ratio | Risk/Reward Ratio. Quantifies if a trade is worth it |
| RDP | Ramer-Douglas-Peucker. Algorithm to simplify chart by removing noise |
| Rebound | Price rise from its minimum. Confirms the turn |
| RSI | Relative Strength Index. Overbought/oversold indicator (0-100) |
| Stop Loss | Automatic sell order to limit losses |
| Swing Trading | Investment strategy over a horizon of days to weeks |

---

### Acknowledgments and Credits
This software has been developed thanks to the inspiration from the work of Dani S�nchez-Crespo (https://www.skool.com/decodecore) and David Bastidas (https://www.davidbastidas.com/) in addition to their collaboration.
This software has been programmed with a pedagogical intention and thanks to Gemini and Claude.
