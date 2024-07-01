# popest_scrape.py
import sys
sys.path.append('/Users/robertstillwell/GovernmentInformant/my_workspace')
sys.path.append('/Users/robertstillwell/GovernmentInformant/my_workspace/response_scraper/response_scraper')
from response_scraper.response_scraper.run_spider import run_spider

# List of URLs to start scraping
start_urls = ['https://www.census.gov/programs-surveys/popest.html']

# Call the spider
run_spider(start_urls=start_urls, domain='census.gov', tree_depth=1)

## TODO parse the results
## TODO excel and html tables with annotations, stubs and headers with multiple rows and merged cells