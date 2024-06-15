import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
import os
import json
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import camelot
import pandas as pd
import mimetypes
import tempfile

def clean_text(text):
    """
    Cleans the given text by removing newline characters, tabs, carriage returns, and extra spaces.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text

class GenericSpider(scrapy.Spider):
    name = 'generic_spider'
    
    def __init__(self, start_url, depth, write_to, stay_within, *args, **kwargs):
        super(GenericSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.depth = int(depth)
        self.write_to = write_to
        self.stay_within = stay_within
        if stay_within:
            self.allowed_domains = [urlparse(start_url).netloc]
        else:
            self.allowed_domains = []

        if not os.path.exists(self.write_to):
            os.makedirs(self.write_to)
    
    def parse(self, response):
        content_type = response.headers.get('Content-Type').decode('utf-8').lower()
        page_data = {'url': response.url}

        if 'html' in content_type:
            page_data.update(self.parse_html(response))
        elif 'text' in content_type:
            page_data.update(self.parse_text(response))
        elif 'pdf' in content_type:
            page_data.update(self.parse_pdf(response))
        elif 'excel' in content_type or 'spreadsheetml' in content_type:
            page_data.update(self.parse_xlsx(response))
        elif 'csv' in content_type:
            page_data.update(self.parse_csv(response))
        elif 'json' in content_type:
            page_data.update({'json': response.text})
        elif content_type in page_data:
            page_data.update({'text': response.text})
            self.log(f"Unsupported content type: {content_type}")
        else:
            self.log(f"Unsupported content type: {content_type}")
            page_data[content_type] = response.text
            return
        
        # Save the collected data to a JSON file
        url_domain = urlparse(response.url).netloc
        if not os.path.exists(os.path.join(self.write_to, url_domain)):
            os.makedirs(os.path.join(self.write_to, url_domain))
        page_filename = os.path.join(self.write_to, f"{url_domain}/{urlparse(response.url).path.strip('/').replace('/', '_')}.json")
        with open(page_filename, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=4)
        
        # Continue crawling if depth limit is not reached
        if response.meta.get('depth', 0) < self.depth:
            for next_page in response.css('a::attr(href)').getall():
                if next_page is not None:
                    next_page = response.urljoin(next_page)
                    if self.is_valid_link(next_page):
                        if self.stay_within and urlparse(next_page).netloc != self.allowed_domains[0]:
                            continue
                        yield scrapy.Request(next_page, callback=self.parse)

    def parse_html(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [{'text': link.get_text(), 'url': response.urljoin(link.get('href'))} for link in soup.find_all('a', href=True)]
        text = ' '.join(soup.stripped_strings)
        tables = self.identify_tables(soup)

        return {'text': clean_text(text), 'links': links, 'tables': tables, 'web_tools': self.identify_web_tools(soup)}

    def parse_text(self, response):
        text = response.text.strip()
        return {'text': clean_text(text)}

    def parse_pdf(self, response):
        text, tables = self.extract_text_and_tables_from_pdf(response)
        return {'text': clean_text(text), 'tables': tables}

    def parse_xlsx(self, response):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_xlsx:
            temp_xlsx.write(response.body)
            temp_xlsx_path = temp_xlsx.name
        xlsx_data = pd.ExcelFile(temp_xlsx_path)
        sheets_data = {sheet_name: xlsx_data.parse(sheet_name).head(5).to_dict(orient='split') for sheet_name in xlsx_data.sheet_names}
        os.remove(temp_xlsx_path)
        return {'sheets': sheets_data}

    def parse_csv(self, response):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_csv:
            temp_csv.write(response.body)
            temp_csv_path = temp_csv.name
        csv_data = pd.read_csv(temp_csv_path).head(5).to_dict(orient='split')
        os.remove(temp_csv_path)
        return {'csv': csv_data}

    def extract_text_and_tables_from_pdf(self, response):
        text = ""
        tables = []

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(response.body)
                temp_pdf_path = temp_pdf.name
            
            pdf_document = fitz.open(temp_pdf_path)
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                page_text = page.get_text("text")
                text += f"Page {page_num + 1}:\n{page_text}\n\n"
            
            pdf_document.close()
            os.remove(temp_pdf_path)
            
            camelot_tables = camelot.read_pdf(temp_pdf_path, pages='all')
            for table in camelot_tables:
                table_dict = {
                    'page': table.page,
                    'data': table.df.to_dict(orient='split')
                }
                tables.append(table_dict)
                
        except Exception as e:
            self.log(f"Error extracting text and tables from PDF: {e}")
        
        return clean_text(text), tables

    def identify_tables(self, soup):
        tables = []
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                table_data.append(row_data)
            tables.append(table_data)
        return tables

    def identify_web_tools(self, soup):
        web_tools = []
        if soup.find('iframe', {'src': lambda x: x and 'tableau' in x.lower()}):
            web_tools.append('Tableau')
        if soup.find('iframe', {'src': lambda x: x and 'powerbi' in x.lower()}):
            web_tools.append('Power BI')
        if soup.find('script', {'src': lambda x: x and 'arcgis' in x.lower()}):
            web_tools.append('ArcGIS')
        return web_tools

    def is_valid_link(self, url):
        # Ensure the link starts with the seed URL
        if not url.startswith(self.seed_url):
            return False
        mimetype, _ = mimetypes.guess_type(url)
        if mimetype:
            return mimetype.startswith('text/html') or mimetype.startswith('application/xhtml+xml')
        return True

def run_spider(start_url, depth=1, stay_within=True, write_to = '/Users/robertstillwell/robcode/mapping_work/grab_it_all/generic_spider/'):
    domain = urlparse(start_url).netloc
    if not write_to.endswith('/'):
        write_to += '/'
    process = CrawlerProcess(settings={
        'DEPTH_LIMIT': int(depth),
        'LOG_ENABLED': False
    })
    process.crawl(GenericSpider, start_url=start_url, depth=depth, write_to=write_to, stay_within=stay_within)
    process.start()
    print(f"information being written to: {write_to + domain}")

# Example call to run the spider
if __name__ == "__main__":
    start_url = 'http://example.com'
    depth = 2
    stay_within = True
    run_spider(start_url, depth, stay_within)
