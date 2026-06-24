SELECT *
FROM `Luxury.brand_sentiment`
LIMIT 20

select *
FROM `Luxury.luxury_brand_metrics`
limit 20

select *
from `Luxury.luxury_chanel_revenue`
Limit 15

select *
from `Luxury.luxury_industry_benchmarks`
Limit 15

--Average sentiment score per brand (highest to lowest)
select 
brand,
brand_group,
category,
round(avg(sentiment_score),3) as avg_sentiment,
COUNT(*) as total_mentions
FROM `Luxury.brand_sentiment`
group by brand, brand_group, category
order by avg_sentiment DESC;

-- LVMH vs Competitors — who has better perception?
SELECT
  brand_group,
  ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
  COUNT(*) AS total_mentions,
  -- count how many are positive, negative, neutral
  COUNTIF(sentiment_label = 'Positive') AS positive_count,
  COUNTIF(sentiment_label = 'Neutral') AS neutral_count,
  COUNTIF(sentiment_label = 'Negative') AS negative_count
FROM `Luxury.brand_sentiment`
GROUP BY brand_group;

-- Watches vs Fashion — which category do people feel better about?
SELECT
  category,
  ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
  COUNT(*) AS total_mentions,
  COUNTIF(sentiment_label = 'Positive') AS positive_count,
  COUNTIF(sentiment_label = 'Negative') AS negative_count
FROM `Luxury.brand_sentiment`
GROUP BY category;

-- Sentiment breakdown by percentage for each brand
SELECT
  brand,
  brand_group,
  COUNT(*) AS total_mentions,
  ROUND(COUNTIF(sentiment_label = 'Positive') / COUNT(*) * 100, 1) AS positive_pct,
  ROUND(COUNTIF(sentiment_label = 'Neutral') / COUNT(*) * 100, 1) AS neutral_pct,
  ROUND(COUNTIF(sentiment_label = 'Negative') / COUNT(*) * 100, 1) AS negative_pct
FROM `Luxury.brand_sentiment`
GROUP BY brand, brand_group
ORDER BY positive_pct DESC;
-- Which subreddits talk about luxury brands the most?
SELECT
  subreddit,
  COUNT(*) AS total_mentions,
  ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
  COUNTIF(sentiment_label = 'Positive') AS positive_count,
  COUNTIF(sentiment_label = 'Negative') AS negative_count
FROM `Luxury.brand_sentiment`
GROUP BY subreddit
ORDER BY total_mentions DESC;


-- Top 10 most engaged posts (highest upvotes)
SELECT
  brand,
  brand_group,
  score AS upvotes,
  sentiment_score,
  sentiment_label,
  subreddit,
  date
FROM `Luxury.brand_sentiment`
ORDER BY score DESC
LIMIT 10;

--Sentiment by month — is perception changing over time?
SELECT
  FORMAT_DATE('%Y-%m', date) AS month,
  brand_group,
  ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
  COUNT(*) AS mentions
FROM `Luxury.brand_sentiment`
GROUP BY month, brand_group
ORDER BY month;

-- Brand engagement score (combines upvotes + sentiment)
-- Higher score = more popular AND more positively discussed
SELECT
  brand,
  brand_group,
  COUNT(*) AS mentions,
  ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
  ROUND(AVG(score), 1) AS avg_upvotes,
  -- engagement score: avg_sentiment * avg_upvotes * log of mentions
  ROUND(AVG(sentiment_score) * AVG(score) * LOG(COUNT(*)), 2) AS engagement_score
FROM `Luxury.brand_sentiment`
GROUP BY brand, brand_group
ORDER BY engagement_score DESC;

-- Revenue by company and channel (latest year)
SELECT
  company,
  channel,
  revenue_eur_millions,
  channel_share_pct
FROM `Luxury.luxury_chanel_revenue`
WHERE year = 2024
ORDER BY company, channel_share_pct DESC;

-- How has DTC share changed over time? (Richemont only)
SELECT
  year,
  channel,
  revenue_eur_millions,
  channel_share_pct
FROM `Luxury.luxury_chanel_revenue`
WHERE company = 'Richemont'
  AND channel != 'Total'
ORDER BY year, channel DESC;

-- Total revenue trend by company
SELECT
  year,
  company,
  revenue_eur_millions
FROM `Luxury.luxury_chanel_revenue`
WHERE channel = 'Total'
ORDER BY company, year;

-- Year-over-year growth calculated from revenue
-- This is the YoY growth we didn't include in the CSV
SELECT
  year,
  company,
  revenue_eur_millions,
  LAG(revenue_eur_millions) OVER (
    PARTITION BY company
    ORDER BY year
  ) AS prev_year_revenue,
  ROUND(
    (revenue_eur_millions - LAG(revenue_eur_millions) OVER (
      PARTITION BY company
      ORDER BY year
    )) / LAG(revenue_eur_millions) OVER (
      PARTITION BY company
      ORDER BY year
    ) * 100, 1
  ) AS yoy_growth_pct
FROM `Luxury.luxury_chanel_revenue`
WHERE channel = 'Total'
ORDER BY company, year;

-- Richemont DTC share growth (online vs boutiques vs wholesale)
SELECT
  year,
  channel,
  channel_share_pct,
  channel_share_pct - LAG(channel_share_pct) OVER (
    PARTITION BY channel
    ORDER BY year
  ) AS share_change_vs_prior_year
FROM `Luxury.luxury_chanel_revenue`
WHERE company = 'Richemont'
  AND channel != 'Total'
ORDER BY channel, year;

-- All brand metrics — latest year
SELECT
  company,
  brand,
  revenue_eur_millions,
  dtc_share_pct,
  operating_margin_pct
FROM `Luxury.luxury_brand_metrics`
WHERE year = 2024
ORDER BY revenue_eur_millions DESC;


-- Gucci's decline over time
SELECT
  year,
  revenue_eur_millions,
  dtc_share_pct,
  operating_margin_pct
FROM `Luxury.luxury_brand_metrics`
WHERE brand = 'Gucci'
ORDER BY year;


--Operating margin comparison across brands (latest data)
SELECT
  brand,
  company,
  year,
  operating_margin_pct
FROM `Luxury.luxury_brand_metrics`
WHERE operating_margin_pct IS NOT NULL
ORDER BY operating_margin_pct DESC;

-- Luxury market size over time
SELECT
  year,
  value,
  unit
FROM Luxury.luxury_industry_benchmarks
WHERE metric LIKE '%Personal Luxury%'
ORDER BY year;

-- Margin compression story (peak to now)
SELECT
  year,
  metric,
  value
FROM Luxury.luxury_industry_benchmarks
WHERE metric LIKE '%Margin%'
ORDER BY year;

-- All benchmarks — clean view
SELECT
  year,
  metric,
  value,
  unit,
  source
FROM Luxury.luxury_industry_benchmarks
ORDER BY metric, year;

-- Brand sentiment vs revenue (the key insight)
-- This joins sentiment data with financial data
SELECT
  s.brand,
  s.brand_group,
  s.category,
  ROUND(AVG(s.sentiment_score), 3) AS avg_sentiment,
  COUNT(*) AS mention_count,
  b.revenue_eur_millions,
  b.operating_margin_pct
FROM `Luxury.brand_sentiment` s
LEFT JOIN `Luxury.luxury_brand_metrics` b
  ON s.brand = b.brand
  AND b.year = 2024
GROUP BY
  s.brand,
  s.brand_group,
  s.category,
  b.revenue_eur_millions,
  b.operating_margin_pct
ORDER BY avg_sentiment DESC;


-- Company-level: sentiment vs total revenue
SELECT
  s.brand_group,
  ROUND(AVG(s.sentiment_score), 3) AS avg_sentiment,
  COUNT(*) AS total_mentions,
  r.company,
  r.revenue_eur_millions AS total_revenue_2024
FROM `Luxury.brand_sentiment` s
LEFT JOIN `Luxury.luxury_chanel_revenue` r
  ON s.brand_group = CASE
      WHEN r.company IN ('Kering') THEN 'Competitor'
      WHEN r.company IN ('LVMH') THEN 'LVMH'
      WHEN r.company IN ('Richemont') THEN 'Competitor'
      ELSE r.company
    END
  AND r.channel = 'Total'
  AND r.year = 2024
GROUP BY s.brand_group, r.company, r.revenue_eur_millions
ORDER BY avg_sentiment DESC;


SELECT
  brand,
  brand_group,
  category,
  subreddit,
  score AS upvotes,
  num_comments,
  date,
  sentiment_score,
  sentiment_label,
  type
FROM `Luxury.brand_sentiment`;


-- Create a summary view for scorecards
SELECT
  brand,
  brand_group,
  category,
  ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
  COUNT(*) AS mention_count,
  COUNTIF(sentiment_label = 'Positive') AS positive_count,
  COUNTIF(sentiment_label = 'Neutral') AS neutral_count,
  COUNTIF(sentiment_label = 'Negative') AS negative_count,
  ROUND(COUNTIF(sentiment_label = 'Positive') / COUNT(*) * 100, 1) AS positive_pct,
  ROUND(AVG(score), 1) AS avg_upvotes
FROM `Luxury.brand_sentiment`
GROUP BY brand, brand_group, category;
