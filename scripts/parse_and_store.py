# scripts/parse_and_store.py

import os
import json
import sqlite3
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
from general_utilities.embedder import TextEmbedder

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
logging.basicConfig(
    filename='logs/parse_and_store.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ParseObject:
    @staticmethod
    def get_html_links(soup, base_url):
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            link_text = link.get_text(strip=True)
            if href:
                full_url = urljoin(base_url, href)
                links.append({
                    'text': link_text,
                    'url': full_url
                })
        return links

    @staticmethod
    def get_html_images(soup, base_url):
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                images.append(full_url)
        return images

    @staticmethod
    def get_html_forms(soup):
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method'),
                'fields': []
            }
            for input_tag in form.find_all('input'):
                field_data = {
                    'name': input_tag.get('name'),
                    'type': input_tag.get('type'),
                    'value': input_tag.get('value')
                }
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

def hash_url(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def store_data(data, db_path='web_scraping/database/web_scraping.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Embed and store images
    for image in data['images']:
        cursor.execute('''
            INSERT INTO images (url, src)
            VALUES (?, ?)
        ''', (data['website_url'], image))

    # Embed and store forms
    for form in data['forms']:
        form_text = json.dumps(form)
        form_embedding = TextEmbedder.embed_form(form_text)
        cursor.execute('''
            INSERT INTO forms (url, action, method, embedding)
            VALUES (?, ?, ?, ?)
        ''', (data['website_url'], form['action'], form['method'], json.dumps(form_embedding.tolist())))
        form_id = cursor.lastrowid

        for field in form['fields']:
            cursor.execute('''
                INSERT INTO form_fields (form_id, name, type, value)
                VALUES (?, ?, ?, ?)
            ''', (form_id, field['name'], field['type'], field['value']))

    # Embed and store soup
    soup_embedding = TextEmbedder.embed_soup(data['soup'])
    cursor.execute('''
        INSERT OR IGNORE INTO soups (url, content, embedding)
        VALUES (?, ?, ?)
    ''', (data['website_url'], data['soup'], json.dumps(soup_embedding.tolist())))

    # Embed and store links
    for link in data['links']:
        link_hash = hash_url(link['url'])
        link_embedding = TextEmbedder.embed_link(link['url'], [link['text']])
        cursor.execute('''
            INSERT OR IGNORE INTO links (id, url, names, linked_to, linked_from, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (link_hash, link['url'], json.dumps([link['text']]), json.dumps([]), json.dumps([data['website_url']]), json.dumps(link_embedding.tolist())))

        # Update existing links
        cursor.execute('SELECT * FROM links WHERE id = ?', (link_hash,))
        row = cursor.fetchone()
        if row:
            existing_names = json.loads(row[2])
            if link['text'] not in existing_names:
                existing_names.append(link['text'])
            existing_linked_from = json.loads(row[4])
            if data['website_url'] not in existing_linked_from:
                existing_linked_from.append(data['website_url'])
            cursor.execute('''
                UPDATE links
                SET names = ?, linked_from = ?
                WHERE id = ?
            ''', (json.dumps(existing_names), json.dumps(existing_linked_from), link_hash))

    conn.commit()
    conn.close()

def parse_html_file(file_path, output_dir):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = soup.find('meta', attrs={'property': 'og:url'})['content'] if soup.find('meta', attrs={'property': 'og:url'}) else 'unknown'

        parser = ParseObject()
        images = parser.get_html_images(soup, base_url)
        forms = parser.get_html_forms(soup)
        links = parser.get_html_links(soup, base_url)

        data = {
            'website_url': base_url,
            'images': images,
            'forms': forms,
            'links': links,
            'soup': soup.prettify()
        }

        store_data(data)

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
