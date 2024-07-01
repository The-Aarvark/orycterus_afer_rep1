import os
import json
import hashlib
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    filename='parse_html_files.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ParseObject:
    @staticmethod
    def get_html_links(soup, base_url):
        links = []
        common_file_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'txt', 'json', 
            'xml', 'zip', 'tar', 'gz', '7z', 'rar', 'tar.gz', 'tar.bz2', 'tar.xz', 
            'tar.zst', 'tar.lz', 'tar.lzma', 'tar.lz4', 'tar.sz', 'tar.zstd', 'tar.z'
        ]
        parsed_base_url = urlparse(base_url)
        
        for link in soup.find_all('a'):
            href = link.get('href')
            link_text = link.get_text(strip=True)
            if href:
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                is_internal = parsed_url.netloc == parsed_base_url.netloc
                is_non_html = any(full_url.lower().endswith(ext) for ext in common_file_extensions)
                is_api = '/api/' in full_url or 'api.' in full_url

                link_type = 'html'
                if is_non_html:
                    link_type = full_url.split('.')[-1].lower()
                elif is_api:
                    link_type = 'api'

                link_data = {
                    'text': link_text,
                    'url': full_url,
                    'internal': is_internal,
                    'type': link_type
                }
                links.append(link_data)
        return links

    @staticmethod
    def get_html_tables(soup):
        tables = soup.find_all('table')
        return tables

    @staticmethod
    def get_html_forms_and_permitted_values_and_options(soup):
        forms = []
        for form in soup.find_all('form'):
            form_data = {'action': form.get('action'), 'method': form.get('method'), 'fields': []}
            for input_tag in form.find_all('input'):
                field_data = {'name': input_tag.get('name'), 'type': input_tag.get('type'), 'value': input_tag.get('value')}
                form_data['fields'].append(field_data)
            for select_tag in form.find_all('select'):
                field_data = {
                    'name': select_tag.get('name'),
                    'type': 'select',
                    'options': [option.get('value') for option in select_tag.find_all('option')]
                }
                form_data['fields'].append(field_data)
            forms.append(form_data)
        return forms

    @staticmethod
    def get_html_images(soup, base_url):
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                images.append(full_url)
        return images

def hash_url(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def parse_html_file(file_path, output_dir):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = os.path.dirname(file_path)  # Use the file's directory as base URL
        
        parser = ParseObject()
        links = parser.get_html_links(soup, base_url)
        tables = parser.get_html_tables(soup)
        forms = parser.get_html_forms_and_permitted_values_and_options(soup)
        images = parser.get_html_images(soup, base_url)

        data = {
            'links': links,
            'tables': tables,
            'forms': forms,
            'images': images,
            'soup': soup.prettify()
        }

        file_hash = hash_url(file_path)
        output_file_name = f"{file_hash}.json"
        output_file_path = os.path.join(output_dir, output_file_name)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        logging.info(f'Successfully parsed and saved: {file_path}')
        
        # Delete the original file after successful parsing and saving
        os.remove(file_path)
        logging.info(f'Successfully deleted: {file_path}')
    except Exception as e:
        logging.error(f'Error parsing {file_path}: {e}')

def parse_html_files(input_dir='output/responses', output_dir='web_scraping/staging', file_name=None):
    # Ensure the staging directory exists
    os.makedirs(output_dir, exist_ok=True)

    if file_name:
        # Parse a single file
        file_path = os.path.join(input_dir, file_name)
        if os.path.exists(file_path):
            parse_html_file(file_path, output_dir)
        else:
            logging.error(f"File {file_path} does not exist.")
    else:
        # Parse all files
        for filename in os.listdir(input_dir):
            if filename.endswith('.html'):
                file_path = os.path.join(input_dir, filename)
                parse_html_file(file_path, output_dir)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse HTML files.')
    parser.add_argument('--file', type=str, help='Specific HTML file to parse.')
    args = parser.parse_args()

    if args.file:
        parse_html_files(file_name=args.file)
    else:
        parse_html_files()
