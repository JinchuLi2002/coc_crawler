# coc_spider.py

import scrapy
from bs4 import BeautifulSoup
from collections import Counter
import nltk
from nltk.corpus import stopwords
import re
import sqlite3
from scrapy.exceptions import CloseSpider
from urllib.parse import urlparse
import datetime
import sys


class CocSpider(scrapy.Spider):
    name = "coc"
    allowed_domains = ["cc.gatech.edu"]

    def __init__(self):
        self.count = 0
        self.keywords = set()
        self.connection = sqlite3.connect('coc.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS coc_pages (
                id INTEGER PRIMARY KEY,
                url TEXT,
                content TEXT,
                keywords TEXT,
                crawl_time TIMESTAMP
            )
        ''')
        self.connection.commit()

        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))
        self.start_time = datetime.datetime.now()
        self.crawl_stats = []

    def start_requests(self):
        self.urls = ['https://www.cc.gatech.edu/']
        self.pages_todo = len(self.urls)
        self.url_set = set(self.urls)
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def closed(self, reason):
        self.export_stats()
        self.connection.close()

    def parse(self, response):
        self.pages_todo -= 1
        self.count += 1
        if self.count >= 3000:
            raise CloseSpider('Reached 3000 pages')

        elapsed_time = (datetime.datetime.now() -
                        self.start_time).total_seconds()
        time_str = str(datetime.timedelta(seconds=int(elapsed_time)))
        max_url_length = 50  # Maximum length for displayed URL
        displayed_url = (response.url[:max_url_length - 3] + '...') if len(
            response.url) > max_url_length else response.url
        dynamic_line = f"Time: {time_str}, Pages Crawled: {self.count}, TODOs in Queue: {self.pages_todo}, Current Page: {displayed_url}"
        # Adjust the number 80 based on your console width
        sys.stdout.write("\r" + dynamic_line.ljust(80))
        sys.stdout.flush()

        # Extract and store new URLs
        for href in response.css('a::attr(href)').extract():
            url = response.urljoin(href)
            parsed_url = urlparse(url)
            if parsed_url.netloc.endswith('cc.gatech.edu'):
                if url not in self.url_set:
                    self.url_set.add(url)
                    self.pages_todo += 1
                    yield scrapy.Request(url, callback=self.parse)

        # Process page content
        soup = BeautifulSoup(response.body, 'html.parser')
        text = soup.get_text(separator=' ')
        words = [word.lower() for word in re.findall(r'\w+', text)
                 if word.lower() not in self.stop_words]

        # Extract keywords
        top_keywords = [word for word, count in Counter(words).most_common(5)]
        self.keywords.update(top_keywords)

        # Insert data into SQLite database
        crawl_time = datetime.datetime.now()
        self.cursor.execute('''
            INSERT INTO coc_pages (url, content, keywords, crawl_time) VALUES (?, ?, ?, ?)
        ''', (response.url, text, ', '.join(top_keywords), crawl_time))
        self.connection.commit()

        # Collect statistics
        # Time in minutes
        elapsed_time = (crawl_time - self.start_time).total_seconds() / 60
        self.crawl_stats.append(
            (elapsed_time, self.count, len(self.keywords), self.pages_todo))

    def export_stats(self):
        with open('crawl_stats.csv', 'w') as f:
            f.write('Time (Minutes),Pages Crawled,Keywords Extracted,Pages TODO\n')
            for stat in self.crawl_stats:
                f.write('{},{},{},{}\n'.format(*stat))
