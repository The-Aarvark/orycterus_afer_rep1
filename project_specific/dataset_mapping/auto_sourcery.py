import os
import json
import requests
import pandas as pd
import io
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from openai import ChatOpenAI, SystemMessage, HumanMessage
from my_secrets import MySecrets
api_key = MySecrets().openai
def parse_domain(url):
    domain = urlparse(url).netloc.replace('www.', '')
    return domain

def request_csv(url):
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_csv(io.StringIO(response.text)).to_dict(orient='records')

def get_CISA_MAP():
    if os.path.exists('CISA_MAP.json'):
        with open('CISA_MAP.json', 'r') as f:
            CISA_MAP = json.load(f)
    else:
        CISA_MAP = {}
        CISA = request_csv('https://github.com/cisagov/dotgov-data/blob/main/current-federal.csv?raw=true')
        for row in CISA:
            CISA_MAP[row['Domain name']] = row
        with open('CISA_MAP.json', 'w') as f:
            json.dump(CISA_MAP, f)
    return CISA_MAP

def cut_text_to_n_tokens(text, n=500):
    tokens = text.split()
    if len(tokens) > n:
        text = ' '.join(tokens[:n])
    return text

def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def short_soup(soup):
    for tag in soup.find_all(['script', 'style']):
        tag.decompose()
    return soup

def whosAgency(url, temperature=0.2):
    CISA_MAP = get_CISA_MAP()
    domain = parse_domain(url)
    if domain in CISA_MAP:
        agency_response = CISA_MAP[domain]
    # elif domain in USAF_already_determined_domains:
    #     do it right
    else:
        soup = get_soup(url)
        links = [{x['href']: x.text} for x in soup.find_all('a') if x.get('href') and x.get('href').startswith('http')]
        text = soup.get_text()
        link_json = json.dumps(links)
        token_cut = 1500
        text = cut_text_to_n_tokens(text, token_cut - len(link_json.split()))
        website_info = {url: {'text': text, 'links': links}}

        messages = [
            SystemMessage(content="""You are an AI assistant trained to analyze website content and determine the US federal agency that owns or is responsible for the website. You should focus on textual content, official logos, disclaimers, contact information, and any relevant metadata. All responses must be in this json format:  
                            {
                                'url': {dhs sub-bureau non-dot-gov url},
                                'Domain name': 'dhs.gov',
                                'Domain type': 'Federal - Executive',
                                'Agency': 'Department of Homeland Security',
                                'Organization name': 'Headquarters',
                                'City': 'Washington',
                                'State': 'DC',
                                'Security contact email': 'IS2OSecurity@hq.dhs.gov'
                            }
                                we want to union this information with the CISA MAP. If you can't determine the agency, please don't guess. simply fill in the field as "NONE FOUND" in the JSON response."""),
            HumanMessage(content=f"Please fill out the metadata json if you can determine the agency that is responsible for {website_info}? Please fill out the requested metadata json for this url. Also - make sure to use formal names, never abbreviations, nicknames, or monikers.")
        ]
        
        llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo", temperature=temperature)
        agency_response = llm(messages)
    messages = [
        SystemMessage(content="""You are an AI assistant trained to analyze website content and determine which US Program Office collected or published the data. You should focus on textual content, official logos, disclaimers, contact information, and any relevant metadata. All responses must be in this json format:  
                        {
                            'url': 'https://github.com/cisagov',
                            'program name': 'Cybersecurity and Infrastructure Security Agency (CISA)',
                            'program main url': 'https://www.cisa.gov/',
                            'Domain name': 'dhs.gov',
                            'Domain type': 'Federal - Executive',
                            'Agency': 'Department of Homeland Security',
                            'Organization name': 'Headquarters',
                            'City': 'Washington',
                            'State': 'DC',
                            'Security contact email': 'IS2OSecurity@hq.dhs.gov'
                        }
                            we want to union this information with the Federal Budget Database. If you can't determine the specific program office, look for the most prominent text on the page taht loooks like a title and use a derivation of that with a (prelim) note. please don't guess without providing evidence that the results are imperfect"."""),
        HumanMessage(content=f"Please fill out the metadata json if you can determine the program office that is responsible for {website_info}? Please fill out the requested metadata json for this url. Also - make sure to use formal names, never abbreviations, nicknames, or monikers.")
    ]
    
    llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo", temperature=temperature)
    source_response = llm(messages)
    
    return agency_response, source_response

def __main__():
    url = 'https://www.cisa.gov/'
    agency_response, source_response = whosAgency(url)
    print(agency_response)
    print(source_response)