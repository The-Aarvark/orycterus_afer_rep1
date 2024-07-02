import os
import sqlite3
from bs4 import BeautifulSoup
import hashlib
import json
import subprocess

def setup_databases():
    # Run the setup_sql_database.py script
    subprocess.run(['python', 'scripts/setup_sql_database.py'], check=True)

def process_html_files(input_dir='output/responses', db_path='web_scraping/database/web_scraping.db',batch_size=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if not batch_size:
        batch_size = len([f for f in os.listdir(input_dir) if f.endswith('.html')])
    files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
    batch_files = files[:batch_size]

    for filename in batch_files:
        file_path = os.path.join(input_dir, filename)
        print(f"Processing file: {file_path}")  # Logging
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract the original URL from the file content (assuming it's stored in a <h1> tag)
            original_url_tag = soup.find('h1')
            if original_url_tag:
                original_url = original_url_tag.get_text(strip=True)
            else:
                # If not found, construct it based on the filename
                url_hash = filename.split('.')[0]
                domain, _ = filename.split('-', 1)
                original_url = f'https://{domain}.com/{url_hash}'

            # Compute URL hash
            url_hash = hashlib.md5(original_url.encode()).hexdigest()

            # Extract headers
            headers = [header.get_text() for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

            # Save soup content with headers
            soup_data = {
                'url': original_url,
                'headers': json.dumps(headers),
                'content': str(soup),
                'embedding': '',
                'url_hash': url_hash
            }
            print(f"Inserting into soups table: {soup_data}")  # Logging
            cursor.execute('''
            INSERT OR IGNORE INTO soups (url, headers, content, embedding, url_hash)
            VALUES (:url, :headers, :content, :embedding, :url_hash)
            ''', soup_data)

            # Save images
            for img in soup.find_all('img'):
                img_data = {
                    'url': original_url,
                    'src': img.get('src'),
                    'url_hash': url_hash
                }
                cursor.execute('''
                INSERT OR IGNORE INTO images (url, src, url_hash)
                VALUES (:url, :src, :url_hash)
                ''', img_data)

            # Save forms and form fields
            for form in soup.find_all('form'):
                form_data = {
                    'url': original_url,
                    'action': form.get('action'),
                    'method': form.get('method'),
                    'embedding': '',
                    'url_hash': url_hash
                }
                cursor.execute('''
                INSERT INTO forms (url, action, method, embedding, url_hash)
                VALUES (:url, :action, :method, :embedding, :url_hash)
                ''', form_data)
                form_id = cursor.lastrowid

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

            # Save links
            for link in soup.find_all('a', href=True):
                link_data = {
                    'id': hashlib.md5(link['href'].encode()).hexdigest(),
                    'url': original_url,
                    'names': link.get_text(),
                    'linked_to': link['href'],
                    'linked_from': original_url,
                    'url_hash': url_hash
                }
                cursor.execute('''
                INSERT OR IGNORE INTO links (id, url, names, linked_to, linked_from, embedding, url_hash)
                VALUES (:id, :url, :names, :linked_to, :linked_from, '', :url_hash)
                ''', link_data)

            # Save tables
            for table in soup.find_all('table'):
                table_data = {
                    'url': original_url,
                    'table_html': str(table),
                    'url_hash': url_hash
                }
                cursor.execute('''
                INSERT INTO tables (url, table_html, url_hash)
                VALUES (:url, :table_html, :url_hash)
                ''', table_data)

        conn.commit()  # Ensure the insertion is saved after processing each file

        # Delete the file after processing
        os.remove(file_path)
        print(f"Deleted file: {file_path}")  # Logging

    conn.close()

if __name__ == "__main__":
    setup_databases()
    process_html_files()
