# ============================================================
# LUXURY BRAND SENTIMENT ANALYSIS - Google Colab Script
# NO API KEY NEEDED - Uses Reddit Public JSON Endpoints
# ============================================================


# ================== CELL 1: SETUP ==================

#pip install vaderSentiment pandas matplotlib seaborn wordcloud


# ================== CELL 2: IMPORTS & CONFIG ==================

import requests
import pandas as pd
import time
from datetime import datetime

# Reddit requires a user-agent header (any descriptive string works)
headers = {
    'User-Agent': 'LuxuryBrandAnalysis/1.0 (academic research project)'
}

# LVMH brands vs competitors
brands = {
    # LVMH Watch & Jewelry
    'Bulgari': ['bulgari', 'bvlgari'],
    'TAG Heuer': ['tag heuer', 'tagheuer'],
    'Hublot': ['hublot'],
    'Tiffany': ['tiffany'],

    # LVMH Fashion
    'Louis Vuitton': ['louis vuitton', 'vuitton'],
    'Dior': ['dior'],
    'Fendi': ['fendi'],

    # Competitors - Watches
    'Rolex': ['rolex'],
    'Omega': ['omega seamaster', 'omega speedmaster'],
    'Cartier': ['cartier'],
    'Patek Philippe': ['patek philippe', 'patek'],
    'Audemars Piguet': ['audemars piguet', 'royal oak'],

    # Competitors - Fashion
    'Gucci': ['gucci'],
    'Chanel': ['chanel'],
    'Hermes': ['hermes', 'hermès', 'birkin'],
    'Prada': ['prada'],
    'Bottega Veneta': ['bottega veneta', 'bottega'],
}

subreddits = ['Watches', 'luxury', 'fashion', 'malefashionadvice',
              'femalefashionadvice', 'Jewellery', 'LuxuryLifeHabits']

print(f"Tracking {len(brands)} brands across {len(subreddits)} subreddits")
print("No API key needed!")


# ================== CELL 3: SCRAPE FUNCTION ==================

def get_reddit_posts(subreddit, sort='top', time_filter='year', limit=100, after=None):
    """Fetch posts from a subreddit using public JSON endpoint"""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    params = {
        't': time_filter,
        'limit': min(limit, 100),  # Reddit max is 100 per request
    }
    if after:
        params['after'] = after

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"  Rate limited, waiting 60 seconds...")
            time.sleep(60)
            return get_reddit_posts(subreddit, sort, time_filter, limit, after)
        else:
            print(f"  Error {response.status_code} for r/{subreddit}")
            return None
    except Exception as e:
        print(f"  Request error: {e}")
        return None


def get_post_comments(permalink):
    """Fetch comments for a specific post"""
    url = f"https://www.reddit.com{permalink}.json"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                return data[1]['data']['children']
        return []
    except:
        return []


def check_brands(text):
    """Check which brands are mentioned in text"""
    text_lower = text.lower()
    found = []
    for brand, keywords in brands.items():
        if any(kw in text_lower for kw in keywords):
            found.append(brand)
    return found


print("Scraping functions ready!")


# ================== CELL 4: SCRAPE REDDIT ==================
# This takes ~10-15 minutes. Don't worry if some subreddits return fewer results.

all_posts = []

for sub_name in subreddits:
    print(f"\nScraping r/{sub_name}...")
    post_count = 0

    # Get posts from multiple sort types
    for sort_type in ['top', 'hot', 'new']:
        time_filters = ['year', 'month', 'all'] if sort_type == 'top' else [None]

        for tf in time_filters:
            after = None

            # Paginate to get more posts (3 pages x 100 = 300 per combo)
            for page in range(3):
                if sort_type == 'top':
                    data = get_reddit_posts(sub_name, sort=sort_type, time_filter=tf, after=after)
                else:
                    data = get_reddit_posts(sub_name, sort=sort_type, after=after)

                if not data or 'data' not in data:
                    break

                children = data['data']['children']
                if not children:
                    break

                for post in children:
                    p = post['data']
                    title = p.get('title', '')
                    selftext = p.get('selftext', '')
                    full_text = f"{title} {selftext}"

                    # Check for brand mentions in post
                    found_brands = check_brands(full_text)
                    for brand in found_brands:
                        all_posts.append({
                            'brand': brand,
                            'subreddit': sub_name,
                            'title': title,
                            'text': selftext[:500],
                            'full_text': full_text[:500],
                            'score': p.get('score', 0),
                            'num_comments': p.get('num_comments', 0),
                            'date': datetime.fromtimestamp(p.get('created_utc', 0)),
                            'type': 'post',
                        })
                        post_count += 1

                # Get comments from top-scored posts (first 5 per page)
                top_posts = sorted(children, key=lambda x: x['data'].get('score', 0), reverse=True)[:5]
                for post in top_posts:
                    permalink = post['data'].get('permalink', '')
                    if not permalink:
                        continue

                    time.sleep(2)  # be polite
                    comments = get_post_comments(permalink)

                    for comment in comments[:15]:
                        if comment['kind'] != 't1':
                            continue
                        c = comment['data']
                        body = c.get('body', '')

                        found_brands = check_brands(body)
                        for brand in found_brands:
                            all_posts.append({
                                'brand': brand,
                                'subreddit': sub_name,
                                'title': post['data'].get('title', ''),
                                'text': body[:500],
                                'full_text': body[:500],
                                'score': c.get('score', 0),
                                'num_comments': 0,
                                'date': datetime.fromtimestamp(c.get('created_utc', 0)),
                                'type': 'comment',
                            })
                            post_count += 1

                # Pagination
                after = data['data'].get('after')
                if not after:
                    break

                time.sleep(2)  # wait between requests to avoid rate limiting

    print(f"  Found {post_count} brand mentions")

# Create dataframe and remove duplicates
df = pd.DataFrame(all_posts)
df = df.drop_duplicates(subset=['full_text', 'brand'], keep='first')

print(f"\n{'='*50}")
print(f"Total unique brand mentions: {len(df)}")
print(f"\nMentions by brand:")
print(df['brand'].value_counts())


# ================== CELL 5: SENTIMENT ANALYSIS ==================

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    scores = analyzer.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= 0.05:
        label = 'Positive'
    elif compound <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'
    return compound, label

# Apply sentiment
df['sentiment_score'], df['sentiment_label'] = zip(*df['full_text'].apply(get_sentiment))

# Add brand group (LVMH vs Competitor)
lvmh_brands = ['Bulgari', 'TAG Heuer', 'Hublot', 'Tiffany',
               'Louis Vuitton', 'Dior', 'Fendi']
df['brand_group'] = df['brand'].apply(lambda x: 'LVMH' if x in lvmh_brands else 'Competitor')

# Add category
watch_brands = ['Bulgari', 'TAG Heuer', 'Hublot', 'Rolex',
                'Omega', 'Cartier', 'Patek Philippe', 'Audemars Piguet']
df['category'] = df['brand'].apply(lambda x: 'Watches & Jewelry' if x in watch_brands else 'Fashion')

print("Sentiment analysis complete!")
print(f"\nSentiment distribution:")
print(df['sentiment_label'].value_counts())
print(f"\nAverage sentiment by brand group:")
print(df.groupby('brand_group')['sentiment_score'].mean())


# ================== CELL 6: VISUALIZATIONS ==================

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
gold = '#C9A84C'
blue = '#4A90D9'

# --- CHART 1: Average Sentiment by Brand ---
fig, ax = plt.subplots(figsize=(14, 8))
brand_sentiment = df.groupby('brand')['sentiment_score'].mean().sort_values()
colors = [gold if b in lvmh_brands else blue for b in brand_sentiment.index]
brand_sentiment.plot(kind='barh', color=colors, ax=ax)
ax.set_title('Average Sentiment Score by Luxury Brand', fontsize=16, fontweight='bold')
ax.set_xlabel('Sentiment Score (negative ← → positive)')
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('chart1_brand_sentiment.png', dpi=150, bbox_inches='tight')
plt.show()

# --- CHART 2: LVMH vs Competitors ---
fig, ax = plt.subplots(figsize=(10, 6))
group_means = df.groupby('brand_group')['sentiment_score'].mean()
group_means.plot(kind='bar', color=[blue, gold], ax=ax)
ax.set_title('LVMH Brands vs Competitors: Average Sentiment', fontsize=16, fontweight='bold')
ax.set_ylabel('Average Sentiment Score')
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
plt.tight_layout()
plt.savefig('chart2_lvmh_vs_competitors.png', dpi=150, bbox_inches='tight')
plt.show()

# --- CHART 3: Sentiment Distribution by Brand (%) ---
fig, ax = plt.subplots(figsize=(14, 8))
sentiment_counts = df.groupby(['brand', 'sentiment_label']).size().unstack(fill_value=0)
cols_order = [c for c in ['Positive', 'Neutral', 'Negative'] if c in sentiment_counts.columns]
sentiment_pct = sentiment_counts[cols_order].div(sentiment_counts.sum(axis=1), axis=0) * 100
sentiment_pct.plot(kind='barh', stacked=True, color=['#2ecc71', '#95a5a6', '#e74c3c'], ax=ax)
ax.set_title('Sentiment Distribution by Brand (%)', fontsize=16, fontweight='bold')
ax.set_xlabel('Percentage')
plt.tight_layout()
plt.savefig('chart3_sentiment_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

# --- CHART 4: Mention Volume ---
fig, ax = plt.subplots(figsize=(14, 8))
mention_counts = df['brand'].value_counts()
colors_vol = [gold if b in lvmh_brands else blue for b in mention_counts.index]
mention_counts.plot(kind='barh', color=colors_vol, ax=ax)
ax.set_title('Brand Mention Volume on Reddit', fontsize=16, fontweight='bold')
ax.set_xlabel('Number of Mentions')
plt.tight_layout()
plt.savefig('chart4_mention_volume.png', dpi=150, bbox_inches='tight')
plt.show()

# --- CHART 5: Engagement vs Sentiment ---
fig, ax = plt.subplots(figsize=(12, 8))
brand_stats = df.groupby('brand').agg(
    avg_sentiment=('sentiment_score', 'mean'),
    avg_score=('score', 'mean'),
    count=('brand', 'size')
).reset_index()
brand_stats['is_lvmh'] = brand_stats['brand'].apply(lambda x: x in lvmh_brands)

for _, row in brand_stats.iterrows():
    color = gold if row['is_lvmh'] else blue
    ax.scatter(row['avg_sentiment'], row['avg_score'], s=row['count']*3,
              color=color, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax.annotate(row['brand'], (row['avg_sentiment'], row['avg_score']),
               fontsize=8, ha='center', va='bottom')

ax.set_title('Brand Sentiment vs Engagement (bubble size = mention volume)',
            fontsize=14, fontweight='bold')
ax.set_xlabel('Average Sentiment Score')
ax.set_ylabel('Average Post Score (Upvotes)')
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('chart5_sentiment_vs_engagement.png', dpi=150, bbox_inches='tight')
plt.show()

# --- CHART 6: Sentiment Over Time ---
fig, ax = plt.subplots(figsize=(14, 6))
df['month'] = df['date'].dt.to_period('M').astype(str)
monthly = df.groupby(['month', 'brand_group'])['sentiment_score'].mean().unstack()
if not monthly.empty:
    monthly.plot(ax=ax, color=[blue, gold], linewidth=2)
    ax.set_title('Sentiment Trend Over Time: LVMH vs Competitors', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Sentiment Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('chart6_sentiment_over_time.png', dpi=150, bbox_inches='tight')
    plt.show()

print("All charts saved!")


# ================== CELL 7: SUMMARY STATS ==================

print("=" * 60)
print("LUXURY BRAND SENTIMENT ANALYSIS - SUMMARY")
print("=" * 60)

print(f"\nTotal mentions collected: {len(df)}")
print(f"Brands tracked: {df['brand'].nunique()}")
print(f"Subreddits scraped: {df['subreddit'].nunique()}")

if len(df) > 0:
    print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")

    print(f"\n--- TOP 5 MOST POSITIVE BRANDS ---")
    top_pos = df.groupby('brand')['sentiment_score'].mean().sort_values(ascending=False).head()
    for brand, score in top_pos.items():
        group = "LVMH" if brand in lvmh_brands else "Competitor"
        count = len(df[df['brand'] == brand])
        print(f"  {brand} ({group}): {score:.3f}  [{count} mentions]")

    print(f"\n--- TOP 5 MOST NEGATIVE BRANDS ---")
    top_neg = df.groupby('brand')['sentiment_score'].mean().sort_values().head()
    for brand, score in top_neg.items():
        group = "LVMH" if brand in lvmh_brands else "Competitor"
        count = len(df[df['brand'] == brand])
        print(f"  {brand} ({group}): {score:.3f}  [{count} mentions]")

    print(f"\n--- LVMH vs COMPETITORS ---")
    for group, data in df.groupby('brand_group'):
        print(f"  {group}: avg sentiment {data['sentiment_score'].mean():.3f} | {len(data)} mentions")

    print(f"\n--- WATCHES vs FASHION ---")
    for cat, data in df.groupby('category'):
        print(f"  {cat}: avg sentiment {data['sentiment_score'].mean():.3f} | {len(data)} mentions")


# ================== CELL 8: SAVE CSV FOR BIGQUERY ==================

export_df = df[['brand', 'brand_group', 'category', 'subreddit',
                'title', 'text', 'score', 'num_comments',
                'date', 'sentiment_score', 'sentiment_label', 'type']].copy()

export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')

export_df.to_csv('luxury_brand_sentiment.csv', index=False)
print(f"Saved {len(export_df)} rows to luxury_brand_sentiment.csv")
print("Download this file, then upload to BigQuery")
export_df.head(10)


# ================== CELL 9: UPLOAD TO BIGQUERY ==================
# Uncomment and run after you verify the CSV looks good

# from google.colab import auth
# auth.authenticate_user()
#
# export_df['date'] = pd.to_datetime(export_df['date'])
# export_df.to_gbq(
#     destination_table='Luxury.brand_sentiment',
#     project_id='clothing-sales-analysis',
#     if_exists='replace'
# )
# print("Uploaded to BigQuery!")
