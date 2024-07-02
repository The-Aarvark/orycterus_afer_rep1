# response_scraper/response_scraper/spiders/custom_spider.py

import scrapy
from scrapy.http import HtmlResponse
import os
import json
from datetime import datetime
import hashlib
from urllib.parse import urlparse


class CustomSpider(scrapy.Spider):
    name = "custom_spider"
    
    def __init__(self, start_urls=None, tree_depth=2, *args, **kwargs):
        super(CustomSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls if start_urls else ['https://example.com']
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.tree_depth = tree_depth
        self.visited_urls = self.load_visited_urls()
        self.setup_logging()
        self.log(f"Loaded visited URLs: {self.visited_urls}")

    def setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.log_file = open('logs/scrapy_log.txt', 'a')
        self.log(f"Spider started at {datetime.now()}\n")

    def log(self, message):
        self.log_file.write(message + '\n')
        self.log_file.flush()

    def load_visited_urls(self):
        visited = set()
        if os.path.exists('logs/scrapy_log.txt'):
            with open('logs/scrapy_log.txt', 'r') as file:
                for line in file:
                    if "Scraped URL:" in line:
                        url_start = line.find("Scraped URL:") + len("Scraped URL:")
                        url_end = line.find(" - ", url_start)
                        if url_end == -1:  # Handle case where there's no timestamp
                            url_end = len(line)
                        url = line[url_start:url_end].strip()
                        visited.add(url)
        return visited

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return

        url = response.url
        self.visited_urls.add(url)
        self.log(f"Scraped URL: {url} - {datetime.now()}")

        # Save the response
        self.save_response(response, url)

        # Follow links and control depth
        depth = response.meta.get('depth', 0)
        if depth < self.tree_depth:
            for link in response.css('a::attr(href)').getall():
                if self.is_valid_link(link):
                    yield response.follow(link, self.parse, meta={'depth': depth + 1})

    def is_valid_link(self, link):
        if '?' in link:
            return False

        invalid_extensions = (
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff',
            'mp3', 'mp4', 'avi', 'mov', 'zip', 'rar', '7z'
        )
        
        if any(link.endswith(ext) for ext in invalid_extensions):
            return False
        
        return link.endswith(('html', 'htm', 'xml', '/'))

    def save_response(self, response, url):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        if not os.path.exists('output/responses'):
            os.makedirs('output/responses')
        filepath = f'output/responses/{domain}-{url_hash}.html'
        with open(filepath, 'wb') as f:
            f.write(response.body)

    def closed(self, reason):
        self.log(f"Spider closed at {datetime.now()} due to: {reason}")
        self.log_file.close()
        self.save_visited_urls()

    def save_visited_urls(self):
        with open('logs/visited_urls.json', 'w') as file:
            json.dump(list(self.visited_urls), file)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        url = response.url
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        filepath = f'output/responses/{domain}-{url_hash}.html'
        
        if os.path.exists(filepath):
            self.log(f"Loading URL from file: {url}")
            with open(filepath, 'rb') as f:
                content = f.read()
                fake_response = HtmlResponse(url=url, body=content, encoding='utf-8')
                return self.parse(fake_response)
        else:
            self.log(f"Scraping URL from web: {url}")
            return self.parse(response)
