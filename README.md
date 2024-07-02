Aardvarks Know Everything

Overview
This application is designed to scrape websites, process the content, and store various components (such as links, images, forms, and tables) into dedicated databases for efficient indexing and retrieval. The goal is to create a structured dataset that captures relationships between URLs and the different elements found within web pages.

Features
Response Scraper

Scrape a website to a depth of 1-2 layers.
Capture the HTML content (soup) of the pages.
Save the captured soup for further processing.
Soup Processor

Process the captured soup to extract:
Links
Forms
Images
Tables
Soup Database

Store processed soups into a database.
Apply an index to each soup based on the URL of the page it was scraped from.
Image Database

Store extracted images into a database.
Apply an index to each image based on the source URL.
Link Database

Store extracted links into a database.
Each link URL serves as an index.
Capture and aggregate the different names (anchor texts) used to reference each link.
Track the URLs that referenced each link, capturing URL-to-URL relationships.
Getting Started
Prerequisites
Python 3.x
Required libraries: BeautifulSoup, requests, sqlite3 (or your preferred database library)
Installation
Clone the repository:
bash
Copy code
git clone <repository-url>
Install the required libraries:
bash
Copy code
pip install beautifulsoup4 requests sqlite3
Usage
Scraping a Website

Run the response scraper to capture the HTML content of a website up to the specified depth:
python
Copy code
from response_scraper import scrape_website
scrape_website('http://example.com', depth=2)
Processing the Soup

Process the captured soup to extract links, forms, images, and tables:
python
Copy code
from soup_processor import process_soup
process_soup('path/to/soup/file')
Storing in Databases

Store the processed soups, images, and links into their respective databases:
python
Copy code
from database_manager import store_soup, store_image, store_link
store_soup('path/to/processed/soup')
store_image('path/to/image/file', 'source_url')
store_link('link_url', ['list_of_anchor_texts'], ['list_of_referrer_urls'])
Contributing
Fork the repository.
Create a new branch: git checkout -b feature-branch.
Make your changes and commit them: git commit -m 'Add some feature'.
Push to the branch: git push origin feature-branch.
Open a pull request.
License
This project is licensed under the MIT License.

Contact
For any questions or issues, please open an issue in the repository or contact the maintainer at [email@example.com].