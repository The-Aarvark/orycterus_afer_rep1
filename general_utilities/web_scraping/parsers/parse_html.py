# scrapers/parsers/html_content_extractor.py

from bs4 import BeautifulSoup
from urllib.parse import urlparse

class ParseParams:
    @staticmethod
    def parse(response, allowed_content_types=['text/html', 'application/xhtml+xml']):
        soup = BeautifulSoup(response.body, 'lxml')

        # Check the content type of the response
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').split(';')[0].strip()
        if content_type not in allowed_content_types:
            return {
                'non_html_links': [response.url]
            }

        # Capture and list tables
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for row in table.find_all('tr'):
                cols = [ele.get_text(strip=True) for ele in row.find_all(['td', 'th'])]
                rows.append(cols)
            tables.append(rows)

        # Capture and list images
        images = [img['src'] for img in soup.find_all('img', src=True)]# scrapers/parsers/html_content_extractor.py

from bs4 import BeautifulSoup
import re

class ParseParams:
    @staticmethod
    def detect_web_tools(soup):
        tools = []
        if soup.find_all(re.compile(r'tableau-viz|powerbi|arcgis', re.I)):
            tools.append('Tableau') if soup.find_all(re.compile(r'tableau', re.I)) else None
            tools.append('PowerBI') if soup.find_all(re.compile(r'powerbi', re.I)) else None
            tools.append('ArcGIS') if soup.find_all(re.compile(r'arcgis', re.I)) else None
        return tools

    @staticmethod
    def split_into_chunks(text, chunk_size=250, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = words[i:i + chunk_size]
            chunks.append(' '.join(chunk))
        return chunks

    @staticmethod
    def parse(response):
        soup = BeautifulSoup(response.body, 'lxml')

        # Detect web tools
        web_tools = ParseParams.detect_web_tools(soup)

        # Capture and list tables
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for row in table.find_all('tr'):
                cols = [ele.get_text(strip=True) for ele in row.find_all(['td', 'th'])]
                rows.append(cols)
            tables.append(rows)

        # Capture and list images
        images = [img['src'] for img in soup.find_all('img', src=True)]

        # Capture and categorize links and API endpoints
        links = {'internal': [], 'external': [], 'non_html': []}
        api_endpoints = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            if '?' in url:
                api_endpoints.append(url)
                continue
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            link_type = 'internal' if domain == urlparse(response.url).netloc else 'external'
            if link_type == 'external':
                links['external'].append(url)
            else:
                links['internal'].append(url)

        # Capture text and split into sections and paragraphs
        sections = []
        section_header = None
        paragraphs = []

        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                if section_header:
                    section_text = ' '.join(paragraphs)
                    chunks = ParseParams.split_into_chunks(section_text)
                    sections.append({
                        'header': section_header,
                        'chunks': chunks
                    })
                section_header = element.get_text(strip=True)
                paragraphs = []
            elif element.name == 'p':
                paragraphs.append(element.get_text(strip=True))

        if section_header:
            section_text = ' '.join(paragraphs)
            chunks = ParseParams.split_into_chunks(section_text)
            sections.append({
                'header': section_header,
                'chunks': chunks
            })

        return {
            'links': links,
            'tables': tables,
            'images': images,
            'sections': sections,
            'web_tools': web_tools,
            'api_endpoints': api_endpoints
        }

    @staticmethod
    def stay_within(domain):
        def _filter(url):
            return url.startswith(domain)
        return _filter

parse_params = ParseParams()


        # Capture and categorize links
        links = {'internal': [], 'external': [], 'non_html': []}
        for link in soup.find_all('a', href=True):
            url = link['href']
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            link_type = 'internal' if domain == urlparse(response.url).netloc else 'external'
            if link_type == 'external':
                links['external'].append(url)
            else:
                links['internal'].append(url)

        # Capture text and split into sections and paragraphs
        sections = []
        section_header = None
        paragraphs = []

        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                if section_header:
                    sections.append({
                        'header': section_header,
                        'text': paragraphs
                    })
                section_header = element.get_text(strip=True)
                paragraphs = []
            elif element.name == 'p':
                paragraphs.append(element.get_text(strip=True))

        if section_header:
            sections.append({
                'header': section_header,
                'text': paragraphs
            })

        return {
            'links': links,
            'tables': tables,
            'images': images,
            'sections': sections
        }

    @staticmethod
    def stay_within(domain):
        def _filter(url):
            return url.startswith(domain)
        return _filter

parse_params = ParseParams()
