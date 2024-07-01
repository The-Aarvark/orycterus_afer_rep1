import os
import json
from bs4 import BeautifulSoup
from datetime import datetime

class ParseObject:
    @staticmethod
    def get_html_links(soup):
        html_links = []
        non_html_links = []
        api_links = []
        non_api_links = []
        common_file_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'txt', 'json', 
            'xml', 'zip', 'tar', 'gz', '7z', 'rar', 'tar.gz', 'tar.bz2', 'tar.xz', 
            'tar.zst', 'tar.lz', 'tar.lzma', 'tar.lz4', 'tar.sz', 'tar.zstd', 'tar.z'
        ]
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if any(href.lower().endswith(ext) for ext in common_file_extensions):
                    non_html_links.append(href)
                elif '/api/' in href or 'api.' in href:
                    api_links.append(href)
                else:
                    html_links.append(href)
                    non_api_links.append(href)
        return {'html': html_links, 'non_html': non_html_links, 'api': api_links, 'non_api': non_api_links}

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
    def get_html_images(soup):
        images = []
        for img in soup.find_all('img'):
            images.append(img.get('src'))
        return images

    @staticmethod
    def get_html_meta_tags(soup):
        meta_tags = []
        for meta in soup.find_all('meta'):
            meta_tags.append(meta.attrs)
        return meta_tags

    @staticmethod
    def get_html_text_structure(soup):
        text_structure = []

        def traverse_dom(element):
            if element.name in ['table', 'form', 'img', 'a']:
                return
            if element.name and element.name.startswith('h'):
                text_structure.append({'tag': 'heading', 'text': element.get_text(strip=True)})
            elif element.name in ['p', 'div', 'span']:
                text_structure.append({'tag': element.name, 'text': element.get_text(strip=True)})
            else:
                for child in element.children:
                    if isinstance(child, str):
                        if child.strip():
                            text_structure.append({'tag': 'text', 'text': child.strip()})
                    else:
                        traverse_dom(child)

        traverse_dom(soup.body)
        return text_structure

    @staticmethod
    def get_data_visualization_tools(soup):
        scripts = soup.find_all('script')
        data_viz_tools = []
        
        libraries = [
            'Chart.js', 'D3.js', 'Plotly', 'Highcharts', 'Google Charts', 
            'FusionCharts', 'Chartist.js', 'ECharts', 'C3.js', 'CanvasJS',
            'Tableau', 'PowerBI', 'ArcGIS', 'AnyChart', 'amCharts', 'Flot', 'Dygraphs'
        ]
        
        for script in scripts:
            src = script.get('src')
            if src:
                for lib in libraries:
                    if lib.lower() in src.lower():
                        data_viz_tools.append(lib)
        
        return list(set(data_viz_tools))

    @staticmethod
    def get_iframes(soup):
        iframes = []
        for iframe in soup.find_all('iframe'):
            iframes.append(iframe.get('src'))
        return iframes

    @staticmethod
    def get_uncategorized_elements(soup, categorized_tags):
        uncategorized_elements = []
        all_elements = soup.find_all()
        for element in all_elements:
            if element.name not in categorized_tags:
                uncategorized_elements.append(str(element))
        return uncategorized_elements

def parse_html_file(file_path, output_dir):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    parser = ParseObject()
    links = parser.get_html_links(soup)
    tables = parser.get_html_tables(soup)
    forms = parser.get_html_forms_and_permitted_values_and_options(soup)
    images = parser.get_html_images(soup)
    meta_tags = parser.get_html_meta_tags(soup)
    text_structure = parser.get_html_text_structure(soup)
    data_visualization_tools = parser.get_data_visualization_tools(soup)
    iframes = parser.get_iframes(soup)

    categorized_tags = {
        'a', 'table', 'form', 'img', 'meta', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
        'p', 'div', 'span', 'script', 'iframe'
    }
    uncategorized_elements = parser.get_uncategorized_elements(soup, categorized_tags)

    data = {
        'links': links,
        'tables': tables,
        'forms': forms,
        'images': images,
        'meta_tags': meta_tags,
        'text_structure': text_structure,
        'data_visualization_tools': data_visualization_tools,
        'iframes': iframes,
        'uncategorized_elements': uncategorized_elements,
        'scraped_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    output_file_name = os.path.basename(file_path).split('.')[0] + '.json'
    output_file_path = os.path.join(output_dir, output_file_name)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def parse_html_files(input_dir='output/responses', output_dir='web_scraping/staging', file_name=None):
    # Ensure the staging directory exists
    os.makedirs(output_dir, exist_ok=True)

    if file_name:
        # Parse a single file
        file_path = os.path.join(input_dir, file_name)
        if os.path.exists(file_path):
            parse_html_file(file_path, output_dir)
        else:
            print(f"File {file_path} does not exist.")
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
