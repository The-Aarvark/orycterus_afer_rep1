import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from response_scraper.response_scraper.spiders.custom_spider import CustomSpider

def run_spider(start_urls, tree_depth):
    process = CrawlerProcess(get_project_settings())
    process.crawl(CustomSpider, start_urls=start_urls, tree_depth=tree_depth)
    process.start()

if __name__ == "__main__":
    start_urls = sys.argv[1].split(",")
    tree_depth = int(sys.argv[2])
    run_spider(start_urls, tree_depth)
