import os
import json
import logging

# Configure logging
logging.basicConfig(
    filename='extract_soup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_and_save_soup_from_staging(staging_dir='web_scraping/staging', soups_dir='web_scraping/soups'):
    # Ensure the soups directory exists
    os.makedirs(soups_dir, exist_ok=True)

    # Process each JSON file in the staging directory
    for filename in os.listdir(staging_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(staging_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract the soup
                soup = data.get('soup')
                if soup:
                    # Save the soup to the soups directory
                    soup_filename = filename.replace('.json', '.html')
                    soup_file_path = os.path.join(soups_dir, soup_filename)
                    with open(soup_file_path, 'w', encoding='utf-8') as soup_file:
                        soup_file.write(soup)

                    logging.info(f'Successfully extracted and saved soup from: {file_path}')

                # Remove the processed file from the staging directory
                os.remove(file_path)
                logging.info(f'Successfully deleted: {file_path}')
            except Exception as e:
                logging.error(f'Error processing {file_path}: {e}')

if __name__ == "__main__":
    extract_and_save_soup_from_staging()
