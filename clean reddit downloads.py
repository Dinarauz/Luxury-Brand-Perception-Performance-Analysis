Python 3.12.1 (v3.12.1:2305ca5144, Dec  7 2023, 17:23:38) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> cd ~/Downloads
... python3 -c "
... import pandas as pd
... 
... df = pd.read_csv('luxury_brand_sentiment.csv')
... 
... # Remove the messy text columns - you don't need them for the dashboard
... df = df.drop(columns=['title', 'text'])
... 
... # Save clean version
... df.to_csv('luxury_brand_sentiment_clean.csv', index=False)
... print(f'Saved {len(df)} rows - clean version')
... print(df.head())
