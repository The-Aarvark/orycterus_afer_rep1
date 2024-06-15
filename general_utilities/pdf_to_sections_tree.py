import tempfile
import re
from collections import defaultdict
import requests
import fitz  # PyMuPDF

# Function to download PDF from a URL to a temporary file
def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(temp_pdf.name, 'wb') as f:
        f.write(response.content)
    return temp_pdf.name

# Function to extract text from a section starting at a given page
def extract_section_text(doc, start_page, end_page):
    text = ""
    for page_num in range(start_page - 1, end_page):
        text += doc[page_num].get_text()
    return clean_text(text.strip())

# Clean up text to remove extra spaces and newlines
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text
# Function to extract text from the PDF and get sections based on TOC links
def extract_text_and_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    
    sections = defaultdict(lambda: {'subsections': [], 'text': ''})
    page_numbers = [item[2] for item in toc]
    current_h1 = None

    for i, item in enumerate(toc):
        level, title, page_num = item
        next_page_num = page_numbers[i + 1] if i + 1 < len(page_numbers) else len(doc)
        
        if level == 1:
            current_h1 = title
            sections[current_h1]['text'] = extract_section_text(doc, page_num, next_page_num)
        elif level == 2:
            if current_h1:
                sections[current_h1]['subsections'].append(title)
                sections[current_h1]['text'] += f"\n\n{title}\n{extract_section_text(doc, page_num, next_page_num)}"

    return sections

# get subsection dictionary from the sections dictionary
def get_subsection_dict(sections):
    subsections = {}
    subs = sections['Housing Variables']['subsections']
    for h1 in sections.keys():
        subs = sections[h1]['subsections']
        for i in range(len(subs)):
            sub = subs[i]
            sub_text = sections[h1]['text'].split(sub)[-1].split(subs[i+1])[0] if i+1 < len(subs) else sections['Housing Variables']['text'].split(sub)[-1]
            subsections[sub] = clean_text(sub_text)
    return subsections

# Function to start at a url and get a sections object
def get_sections_from_url(url):
    pdf_path = download_pdf(url)
    sections = extract_text_and_sections_from_pdf(pdf_path)

    return sections

if __name__ == "__main__":
    # URL of the PDF
    url = 'https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2022_ACSSubjectDefinitions.pdf'

    # Extract text and sections from the PDF
    sections = get_sections_from_url(url)

    # Print the "Contract Rent" section specifically
    for h1, data in sections.items():
        if h1.lower() == "housing variables":
            for h2 in data['subsections']:
                if "Contract Rent" in h2:
                    print(f"Contract Rent Section:\n{h2}\n{data['text'][data['text'].find(h2):data['text'].find(h2)+1000]}...")
