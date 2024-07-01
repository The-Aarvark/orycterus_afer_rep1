from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from response_scraper.response_scraper.spiders.custom_spider import CustomSpider

def run_spider(start_urls, domain='example.com', tree_depth=3):
    process = CrawlerProcess(get_project_settings())
    process.crawl(CustomSpider, start_urls=start_urls, domain=domain, tree_depth=tree_depth)
    process.start()

if __name__ == "__main__":
    run_spider(start_urls=['https://example.com'], domain='example.com', tree_depth=2)

# import sys
# sys.path.append('/Users/robertstillwell/GovernmentInformant/my_workspace/response_scraper')

# import run_spider  # Import the module

# # List of URLs to start scraping
# start_urls = ['https://example.com']

# # Call the spider
# run_spider.run_spider(start_urls=start_urls, domain='example.com', tree_depth=3)
