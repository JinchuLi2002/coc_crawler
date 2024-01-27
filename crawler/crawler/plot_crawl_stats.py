# plot_crawl_stats.py

import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV file
df = pd.read_csv('crawl_stats.csv')
print(df.columns)
# Plot Time vs. Pages Crawled
plt.figure(figsize=(10, 6))
plt.plot(df['Time (Minutes)'], df['Pages Crawled'], label='Pages Crawled')
plt.title('Time vs Pages Crawled')
plt.xlabel('Time (Minutes)')
plt.ylabel('Pages Crawled')
plt.grid(True)
plt.savefig('time_vs_pages_crawled.png')
plt.show()

# Plot Time vs. Keywords Extracted
plt.figure(figsize=(10, 6))
plt.plot(df['Time (Minutes)'], df['Keywords Extracted'],
         label='Keywords Extracted', color='orange')
plt.title('Time vs Keywords Extracted')
plt.xlabel('Time (Minutes)')
plt.ylabel('Keywords Extracted')
plt.grid(True)
plt.savefig('time_vs_keywords_extracted.png')
plt.show()

# Assuming total URLs are the sum of unique URLs found so far
# You might need to adjust this based on how you track total URLs in your spider
df['Total URLs Found'] = df['Pages Crawled'].cummax()
df['Crawled/Total Ratio'] = df['Pages Crawled'] / df['Total URLs Found']

# Plot Time vs. Ratio of Crawled URLs to Total URLs

# Ensure no division by zero
df['Pages TODO'] = df['Pages TODO'].replace(0, 1)

# Calculate the ratio of 'Pages Crawled' to 'Pages TODO'
df['Crawled/Todo Ratio'] = df['Pages Crawled'] / df['Pages TODO']
plt.figure(figsize=(10, 6))
plt.plot(df['Time (Minutes)'], df['Crawled/Todo Ratio'],
         label='Crawled/Todo Ratio', color='green')
plt.title('Time vs Ratio of Crawled Pages to Pages TODO')
plt.xlabel('Time (Minutes)')
plt.ylabel('Crawled/Todo Ratio')
plt.grid(True)
plt.savefig('time_vs_crawled_todo_ratio.png')
plt.show()
