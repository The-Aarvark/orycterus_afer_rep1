import os
import json
import logging

# Configure logging
logging.basicConfig(
    filename='extract_forms.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_and_save_forms_from_staging(staging_dir='web_scraping/staging', forms_dir='web_scraping/forms'):
    # Ensure the forms directory exists
    os.makedirs(forms_dir, exist_ok=True)

    # Process each JSON file in the staging directory
    for filename in os.listdir(staging_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(staging_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract the forms and URL
                forms = data.get('forms')
                url = data.get('url')

                if forms:
                    # Save each form to the forms directory
                    for i, form in enumerate(forms):
                        form_data = {
                            'url': url,
                            'form': form
                        }
                        form_filename = f"{filename.replace('.json', '')}_form_{i + 1}.json"
                        form_file_path = os.path.join(forms_dir, form_filename)
                        with open(form_file_path, 'w', encoding='utf-8') as form_file:
                            json.dump(form_data, form_file, indent=4)

                    logging.info(f'Successfully extracted and saved forms from: {file_path}')

                    # Remove the forms object from the data
                    del data['forms']

                    # Save the updated file back to the staging directory
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)

                    logging.info(f'Successfully updated: {file_path}')
            except Exception as e:
                logging.error(f'Error processing {file_path}: {e}')

if __name__ == "__main__":
    extract_and_save_forms_from_staging()
