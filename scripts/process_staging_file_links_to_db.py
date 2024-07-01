import os
import json
import logging
from scripts.manage_links import LinkDatabase

# Configure logging
logging.basicConfig(
    filename='process_staging_file_links_to_db.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_file(file_path, db):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract URL relationships from data
        url = data.get('url')
        if not url:
            logging.error(f"No URL found in file: {file_path}")
            return

        links = data.get('links', [])
        if not links:
            logging.warning(f"No links found in file: {file_path}")

        linked_to_urls = [entry['url'] for entry in links if entry.get('url')]
        names = [entry['text'] for entry in links if entry.get('text')]

        logging.info(f"Processing URL: {url} with links: {linked_to_urls} and names: {names}")

        # Update URL relationships and names in the database
        url_id = db.add_url_with_relationships(url, found_on=[], links_to=linked_to_urls)
        if url_id:
            for name in names:
                db.add_name(url_id, name)

        logging.info(f'Successfully processed: {file_path}')
    except Exception as e:
        logging.error(f'Error processing {file_path}: {e}')

def process_staging_file_links_to_db(staging_dir='web_scraping/staging', db_path='scripts/links_database.db', file_name=None):
    db = LinkDatabase(db_path)
    
    if file_name:
        file_path = os.path.join(staging_dir, file_name)
        if os.path.exists(file_path):
            process_file(file_path, db)
        else:
            logging.error(f"File {file_path} does not exist.")
    else:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(staging_dir, filename)
                process_file(file_path, db)
    
    db.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process staging files and update URL relationships in the database.')
    parser.add_argument('--staging_dir', type=str, default='web_scraping/staging', help='Directory containing JSON files to process.')
    parser.add_argument('--db_path', type=str, default='scripts/links_database.db', help='Path to the SQLite database.')
    parser.add_argument('--file_name', type=str, help='Specific JSON file to process.')

    args = parser.parse_args()

    process_staging_file_links_to_db(args.staging_dir, args.db_path, args.file_name)
