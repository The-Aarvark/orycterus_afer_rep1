import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def parse_html_files(input_dir='output/responses', output_dir='web_scraping/staging', num_workers=10):
    html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
    total_files = len(html_files)
    
    def process_file(file):
        # Your existing parsing logic here
        try:
            # Example parsing logic
            with open(os.path.join(input_dir, file), 'r') as f:
                content = f.read()
            # Process the content and save to output_dir
            output_path = os.path.join(output_dir, file.replace('.html', '.txt'))
            with open(output_path, 'w') as f:
                f.write(content)  # Replace with actual processing logic
            return file
        except Exception as e:
            return None

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_file, file): file for file in html_files}
        with tqdm(total=total_files, desc="Processing HTML files") as pbar:
            for future in as_completed(futures):
                result = future.result()
                pbar.update(1)

# Run the function
parse_html_files()
