# scrapers/subpage_scraper.py

import scrapy
from scrapy.crawler import CrawlerProcess
import json
import hashlib
from urllib.parse import urlparse, urljoin
from scrapers.parsers.html_content_extractor import parse_params
from azure.storage.blob import BlobServiceClient

class SubpageSpider(scrapy.Spider):
    name = 'subpage_spider'

    def __init__(self, start_urls, parse, allowed_content_types=['text/html', 'application/xhtml+xml'], stay_within=None, blob_info=None, file_path=None, max_depth=5, *args, **kwargs):
        super(SubpageSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.parse_fn = parse
        self.allowed_content_types = allowed_content_types
        self.stay_within = stay_within
        self.blob_info = blob_info
        self.file_path = file_path
        self.non_html_links = []
        self.base_url = start_urls[0]
        self.max_depth = max_depth
        self.common_file_types = ('.pdf', '.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.zip', '.rar', '.tar', '.gz', '.mp3', '.mp4', '.avi', '.mov', '.mkv')
        self.scraped_hashes = set()

    def parse(self, response):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').split(';')[0].strip()
        if content_type not in self.allowed_content_types:
            self.non_html_links.append(response.url)
            return

        url_hash = hashlib.sha256(response.url.encode('utf-8')).hexdigest()
        if url_hash in self.scraped_hashes:
            return
        self.scraped_hashes.add(url_hash)

        data = self.parse_fn(response)

        # Add non-HTML links and API endpoints to the data
        data['non_html_links'] = self.non_html_links

        if self.file_path:
            file_path = f"{self.file_path}/{url_hash}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)
        elif self.blob_info:
            account, container, path = self.blob_info
            blob_service_client = BlobServiceClient.from_connection_string(account)
            blob_client = blob_service_client.get_blob_client(container=container, blob=f"{path}/{url_hash}.json")
            blob_client.upload_blob(json.dumps(data), overwrite=True)
        else:
            self.log(data)

        # Follow links on the page
        current_depth = response.meta.get('depth', 1)
        if current_depth < self.max_depth:
            for link in data['links']['internal'] + data['links']['external']:
                full_url = urljoin(response.url, link)
                if not self.is_common_file_type(full_url) and '?' not in full_url:
                    next_depth = current_depth + 1
                    if self.is_subpage(full_url) or current_depth == 1:  # Allow external links from the starting page
                        yield scrapy.Request(full_url, callback=self.parse, meta={'depth': next_depth})

    def is_subpage(self, url):
        parsed_base_url = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return parsed_url.netloc == parsed_base_url.netloc and parsed_url.path.startswith(parsed_base_url.path)

    def is_common_file_type(self, url):
        return url.lower().endswith(self.common_file_types)

def run_spider(start_urls, parse, stay_within=None, blob_info=None, file_path=None, allowed_content_types=['text/html', 'application/xhtml+xml'], max_depth=5):
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
    })

    spider = SubpageSpider(
        start_urls=start_urls,
        parse=parse,
        allowed_content_types=allowed_content_types,
        stay_within=stay_within,
        blob_info=blob_info,
        file_path=file_path,
        max_depth=max_depth
    )

    process.crawl(spider)
    process.start()

# main.py

# example usage 
"""
from scrapers.subpage_scraper import run_spider
from scrapers.parsers import html_content_extractor as parse_params

start_urls = ['http://example.com']
parse = parse_params.parse
stay_within = parse_params.stay_within('http://example.com')
blob_info = ('your_connection_string', 'your_container_name', 'your_blob_path')
file_path = 'output_directory'  # Ensure this directory exists

# Run spider and save to Azure Blob Storage with depth control
run_spider(start_urls, parse, stay_within, blob_info=blob_info, max_depth=5)

# Run spider and save to local file with depth control and hashed filenames
run_spider(start_urls, parse, stay_within, file_path=file_path, max_depth=5
"""