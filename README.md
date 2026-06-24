# Luxury-Brand-Perception-Performance-Analysis
<img width="1536" height="1024" alt="ChatGPT Image Jun 23, 2026 at 10_45_10 PM" src="https://github.com/user-attachments/assets/48317700-14f4-4b93-b33d-caf83a30a1f2" />



**Do consumers actually feel differently about LVMH brands vs. their competitors? And if so, does it show up in the financials?**

That's the question I set out to answer. I scraped 640 Reddit mentions across 7 communities, ran NLP sentiment analysis on all of them, then layered in financial data from LVMH, Kering, and Richemont annual reports to see if perception and performance are connected.

**Spoiler: they are just not in the way I expected.**

[View the Interactive Dashboard →](https://datastudio.google.com/reporting/e4a08aca-2d2c-47a4-b6bc-8a7296d11c63)

---

## The Story

I started this project thinking I'd find a clear gap between LVMH and its competitors in consumer sentiment. LVMH is the world's largest luxury conglomerate surely their brands would dominate the conversation, right?

They don't.

At the group level, LVMH and competitor sentiment is almost identical: **0.48 vs. 0.49**. If I'd stopped there, this would've been a boring project. But when I broke it down by individual brand, the real story came out, and it's one of visibility, not sentiment.

### The Visibility Problem

Rolex has **201 mentions** on Reddit. The most-discussed LVMH brand? Dior, with 27. TAG Heuer has 15. Bulgari has 9. LVMH doesn't have a perception problem it has an **awareness problem**. Their brands aren't being discussed enough for sentiment to even matter at scale.

Meanwhile, Rolex (201 mentions), Cartier (72 mentions), and Omega (62) completely own the luxury conversation on Reddit. These are all competitor brands.

### The Hublot Paradox

Here's where it gets interesting. Hublot has the **highest average engagement** of any brand 2,557 upvotes per mention. But its sentiment score is just 0.31, one of the lowest. With only 2 mentions, Hublot barely shows up in conversation but when it does, the posts go viral for the wrong reasons.

### The Quiet Winners

On the flip side, TAG Heuer (0.68 sentiment) and Bulgari (0.65) are LVMH's strongest brands by perception people who talk about them talk positively. But with only 15 and 9 mentions respectively, almost nobody is talking. These brands have the sentiment they just need the volume.

### Where It Gets Strategic

When I layered in financial data, the connection became clearer. Gucci maintained a 91% DTC share from 2021 through 2024. By the traditional playbook, that should protect the brand. But revenue dropped from €9.7 B to €7.7B anyway, and operating margins slid from 38.2% to 33.1% (and below reporting threshold in 2024). High DTC share didn't save Gucci from declining brand perception.

Compare that with Richemont Cartier's parent which grew DTC share from 55% to 71% over the same period while maintaining 33% operating margins. Cartier also scores 0.56 in sentiment with 72 mentions. The brands winning on perception are also winning on performance.

---

## What I Built

### Data Collection (Python)
Scraped Reddit's public JSON endpoints no API key needed :) Pulled posts and comments from r/Watches, r/luxury, r/fashion, r/femalefashionadvice, r/malefashionadvice, r/LuxuryLifeHabits, and r/Jewellery. Each post was matched against brand-specific keyword lists (catching both "Bulgari" and "Bvlgari," for example). The scraping script handles rate limiting, pagination, and comment threading automatically.

### Sentiment Analysis (VADER)
Ran every mention through VADER, a sentiment model built for social media text. It understands that "AMAZING" scores higher than "amazing" and "great!!!" beats "great." Each mention got a score from -1 to +1, then I classified them as Positive (≥0.05), Negative (≤-0.05), or Neutral.

### Financial Data (Public Sources)
Pulled revenue, channel mix, and margin data from:
- **Richemont** Five-Year Record — the most detailed channel breakdown in luxury (DTC Boutiques, Wholesale, Online separately)
- **Kering** annual press releases — brand-level DTC share and operating margins for Gucci, YSL, Bottega Veneta
- **LVMH** annual results — total revenue trends
- **Bain-Altagamma** Luxury Reports — industry benchmarks (€364B market in 2024, margins compressing from 23% peak to 15-16%)

### SQL Analysis (BigQuery)
Wrote 25+ queries covering everything from basic sentiment rankings to LAG window functions for YoY growth calculations to LEFT JOINs connecting sentiment data with financial performance. The most revealing query was the brand-level join mapping each brand's Reddit sentiment against its actual revenue and operating margin.

### Dashboard (Looker Studio — 5 Pages)

**Page 1: Which Luxury Brands Win Hearts Online?**
The overview. Scorecards set the context (640 mentions, 17 brands, 0.48 vs 0.49 group sentiment). The combo chart below is the most important visual in the whole dashboard — it ranks every brand by sentiment score while overlaying mention volume, so you can immediately see that Bottega Veneta tops sentiment at 0.79 but only has 6 mentions, while Rolex sits mid-pack at 0.50 but has 201.

**Page 2: LVMH's Visibility Challenge**
This is the strategic page. The data table sorted by mentions makes it painfully clear — the top 7 most-discussed brands are all competitors. Dior is the first LVMH brand to appear at #8. The stacked sentiment bars show that when LVMH brands ARE discussed, the sentiment distribution is actually comparable to competitors. The problem isn't what people say — it's that they're not saying enough.

**Page 3: Community Deep Dive**
A heatmap table breaking down every brand by subreddit with conditional formatting on sentiment and upvotes. The key insight: r/Watches drives 389 of 640 mentions, which explains why watch brands dominate the analysis. The interactive filters let you drill into any brand × subreddit combination.

**Page 4: The Business Behind the Buzz**
Financial context. The revenue trend line shows LVMH at €84.7B dwarfing Kering (€17.2B) and Richemont (€20.6B), but Kering's decline is steeper. The Richemont DTC shift chart shows DTC Boutiques growing while Wholesale shrinks. The Gucci table tells the cautionary tale — 91% DTC and still declining.

**Page 5: Strategic Recommendations**
The scatter chart is my signature visual. Sentiment (x-axis) vs. engagement (y-axis) with bubble size for volume creates four natural quadrants. Hublot sits alone in "Controversial" (top-left). Fendi sits in "At Risk" (bottom-left). TAG Heuer and Bulgari are "Loved but Quiet" (bottom-right). Rolex, Omega, and Cartier are "Strong & Visible" (top-right). The recommendations write themselves from this chart.

---

## Strategic Recommendations

1. **TAG Heuer & Bulgari** have the sentiment but not the volume. Invest in community engagement and content marketing to match competitor share of voice.

2. **Hublot** generates conversation but it's the wrong kind. The brand needs to understand what's driving criticism (pricing perception? design polarization?) and address it through targeted communication.

3. **Fendi** has both low visibility and low sentiment. This is a repositioning challenge in digital communities — the brand needs to build positive associations from the ground up.

4. **Rolex** is the model. Sustained community presence builds both volume and positive perception over time. LVMH watch brands should study this playbook.

5. **Channel strategy isn't enough.** Gucci proves that 91% DTC share doesn't protect against declining brand perception. Richemont (Cartier) shows that combining DTC growth with strong sentiment correlates with 33% operating margins — vs. Gucci's declining margins.

---

## Tech Stack

| Tool | What I Used It For |
|------|---------|
| Python | Reddit scraping, VADER sentiment analysis, data cleaning |
| BigQuery (SQL) | 25+ analytical queries including window functions and multi-table joins |
| Looker Studio | 5-page interactive dashboard with conditional formatting and filters |
| pandas / matplotlib | Data manipulation and initial chart exploration |
| Reddit JSON API | Data collection without authentication |

## Project Files

```
├── data/
│   ├── luxury_brand_sentiment_clean.csv     # 640 rows of sentiment data
│   ├── company_channel_revenue.csv          # Richemont, Kering, LVMH channel revenue
│   ├── brand_metrics.csv                    # Brand-level revenue, DTC %, margins
│   └── industry_benchmarks.csv              # Bain-Altagamma market data
│
├── scripts/
│   └── luxury_sentiment_no_api.py           # Full scraping + analysis pipeline
│
├── sql/
│   └── luxury_analysis_queries.sql          # All BigQuery queries
│
├── visualizations/
│   ├── chart1_brand_sentiment.png
│   ├── chart2_lvmh_vs_competitors.png
│   ├── chart3_sentiment_distribution.png
│   ├── chart4_mention_volume.png
│   ├── chart5_sentiment_vs_engagement.png
│   └── chart6_sentiment_over_time.png
│
└── README.md
```

## Limitations & What I'd Do Next

**Honest limitations:** Reddit skews toward watch enthusiasts and male-dominated communities — fashion brands are underrepresented. VADER is a solid starting point for sentiment but misses sarcasm and luxury-specific nuance ("understated" reads as neutral when it's actually a compliment in luxury). And LVMH doesn't publish channel-level data, so direct DTC comparisons across all three groups aren't possible.

**If I had more time:**
- Pull from Instagram, TikTok, and Xiaohongshu (RED) to capture the demographics Reddit misses
- Fine-tune a RoBERTa model on luxury-specific text for better sentiment accuracy
- Add Google Trends data to see if search interest correlates with Reddit sentiment
- Build an automated pipeline that refreshes the data weekly
- Layer in Chrono24 resale data to see if sentiment predicts value retention

---

## About Me

**Dinara Ibotova**

BBA in Data Analytics — Baruch College, Zicklin School of Business (GPA 3.7, May 2025)

Currently working as a Supply Chain Associate on the D2C Operational Excellence team at L'Oréal USA, where I build Power BI dashboards and manage O+O KPI tracking — so the DTC vs. wholesale analysis in this project comes from a place of hands-on experience, not just theory.

Certifications: Google Data Analytics | Bocconi/LVMH Fashion & Luxury Management | Bocconi/LVMH Operations & Supply Chain | Bocconi/LVMH Retail & Customer Experience | 17+ DataCamp Certificates

[LinkedIn](YOUR_LINKEDIN_URL) | [GitHub](https://github.com/Dinarauz)
