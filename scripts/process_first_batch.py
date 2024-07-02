import os
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
from urllib.parse import urlparse
import json
import subprocess

def setup_databases():
    # Run the setup_sql_database.py script
    subprocess.run(['python', 'scripts/setup_sql_database.py'], check=True)

def process_html_files(input_dir='output/responses', db_path='web_scraping/database/web_scraping.db', batch_size=4):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
    batch_files = files[:batch_size]

    for filename in batch_files:
        file_path = os.path.join(input_dir, filename)
        print(f"Processing file: {file_path}")  # Logging
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')

            url_hash = filename.split('.')[0]
            domain, _ = filename.split('-')

            # Extract headers
            headers = [header.get_text() for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

            # Save soup content with headers
            soup_data = {
                'url': f'https://{domain}.com',
                'headers': json.dumps(headers),
                'content': str(soup),
                'embedding': ''
            }
            print(f"Inserting into soups table: {soup_data}")  # Logging
            cursor.execute('''
            INSERT OR IGNORE INTO soups (url, headers, content, embedding)
            VALUES (:url, :headers, :content, :embedding)
            ''', soup_data)
            conn.commit()  # Ensure the insertion is saved

            # Save images
            for img in soup.find_all('img'):
                img_data = {
                    'url': f'https://{domain}.com',
                    'src': img.get('src')
                }
                cursor.execute('''
                INSERT OR IGNORE INTO images (url, src)
                VALUES (:url, :src)
                ''', img_data)
                conn.commit()  # Ensure the insertion is saved

            # Save forms and form fields
            for form in soup.find_all('form'):
                form_data = {
                    'url': f'https://{domain}.com',
                    'action': form.get('action'),
                    'method': form.get('method'),
                    'embedding': ''
                }
                cursor.execute('''
                INSERT INTO forms (url, action, method, embedding)
                VALUES (:url, :action, :method, :embedding)
                ''', form_data)
                form_id = cursor.lastrowid
                conn.commit()  # Ensure the insertion is saved

                for field in form.find_all(['input', 'select', 'textarea']):
                    field_data = {
                        'form_id': form_id,
                        'name': field.get('name'),
                        'type': field.get('type'),
                        'value': field.get('value')
                    }
                    cursor.execute('''
                    INSERT INTO form_fields (form_id, name, type, value)
                    VALUES (:form_id, :name, :type, :value)
                    ''', field_data)
                    conn.commit()  # Ensure the insertion is saved

            # Save links
            for link in soup.find_all('a', href=True):
                link_data = {
                    'id': hashlib.md5(link['href'].encode()).hexdigest(),
                    'url': f'https://{domain}.com',
                    'names': link.get_text(),
                    'linked_to': link['href'],
                    'linked_from': f'https://{domain}.com'
                }
                cursor.execute('''
                INSERT OR IGNORE INTO links (id, url, names, linked_to, linked_from, embedding)
                VALUES (:id, :url, :names, :linked_to, :linked_from, '')
                ''', link_data)
                conn.commit()  # Ensure the insertion is saved

    conn.close()

if __name__ == "__main__":
    setup_databases()
    process_html_files()
