import scrapy
from scrapy.http import HtmlResponse
import os
import json
from datetime import datetime
import hashlib
from urllib.parse import urlparse, urljoin
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
import time

class CustomSpider(scrapy.Spider):
    name = "custom_spider"
    
    custom_settings = {
        'CLOSESPIDER_TIMEOUT': 300,  # 5 minutes
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': None,
        }
    }

    def __init__(self, start_urls=None, tree_depth=2, *args, **kwargs):
        super(CustomSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls if start_urls else ['https://example.com']
        self.allowed_domains = ['dhs.gov', 'uscis.gov', 'whitehouse.gov', 'myaccount.uscis.gov', 'travel.state.gov', 'cdc.gov', 'oig.dhs.gov', 'usa.gov']
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

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 429:
                self.logger.error('429 Too Many Requests on %s', response.url)
                # Retry logic: put the URL back at the end of the queue
                time.sleep(5)  # Optional: add a delay before retrying
                yield scrapy.Request(url=response.url, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
            else:
                self.logger.error('HTTPError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

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
        self.log(f"Current depth: {depth}, Tree depth: {self.tree_depth}")
        if depth < self.tree_depth:
            for link in response.css('a::attr(href)').getall():
                absolute_link = urljoin(response.url, link)
                if self.is_valid_link(absolute_link):
                    self.log(f"Following link: {absolute_link}")
                    yield response.follow(absolute_link, self.parse, meta={'depth': depth + 1})
                else:
                    self.log(f"Invalid link (skipping): {absolute_link}")

    def is_valid_link(self, link):
        parsed_link = urlparse(link)
        domain = parsed_link.netloc.replace("www.", "")
        self.log(f"Checking link: {link}, Domain: {domain}")

        invalid_extensions = (
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff',
            'mp3', 'mp4', 'avi', 'mov', 'zip', 'rar', '7z'
        )

        if any(link.lower().endswith(ext) for ext in invalid_extensions):
            return False

        # Allow links with empty domain (relative links) and links within allowed domains
        valid_link = domain == "" or domain in self.allowed_domains
        self.log(f"Link valid: {valid_link}")
        return valid_link

    def save_response(self, response, url):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        if not os.path.exists('output/responses'):
            os.makedirs('output/responses')

        # Convert headers to a JSON-serializable dictionary
        headers = {k.decode('utf-8'): [v.decode('utf-8') for v in value] if isinstance(value, list) else value.decode('utf-8') for k, value in response.headers.items()}

        # Add the URL and Headers to the response body
        response_body = f"<h1>{url}</h1>"
        response_body += "<h2>Headers</h2>"
        response_body += "<pre>"
        response_body += json.dumps(headers, indent=4)
        response_body += "</pre>"
        response_body += response.text
        response = response.replace(body=response_body)

        # Save the HTML content
        html_filepath = f'output/responses/{domain}-{url_hash}.html'
        with open(html_filepath, 'wb') as f:
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
            url_hash = hashlib.md5(url.encode()).hexdigest()
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace("www.", "")
            filepath = f'output/responses/{domain}-{url_hash}.html'

            if os.path.exists(filepath):
                self.log(f"Loading URL from file: {url}")
                with open(filepath, 'rb') as f:
                    content = f.read()
                    fake_response = HtmlResponse(url=url, body=content, encoding='utf-8')
                    yield self.parse(fake_response)
            else:
                self.log(f"Scraping URL from web: {url}")
                yield scrapy.Request(url=url, callback=self.parse, errback=self.errback_httpbin, dont_filter=True, meta={'depth': 0})
