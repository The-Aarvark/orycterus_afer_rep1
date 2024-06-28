from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

class ParseObject:
    @staticmethod
    def check_content_type(response, allowed_content_types):
        # Check the content type of the response
        content_type = response.headers.get('Content-Type', '')
        if isinstance(content_type, bytes):
            content_type = content_type.decode('utf-8')
        content_type = content_type.split(';')[0].strip()

        if content_type not in allowed_content_types:
            return False
        return True
    
    def get_html_text(response):
        allowed_content_types = ['text/html', 'text/xml']
        # Check the content type of the response
        if not check_content_type(response, allowed_content_types):
            return None
        return response.text
    
    def get_html_links(response):
        allowed_content_types = ['text/html', 'text/xml']
        # Check the content type of the response
        if not check_content_type(response, allowed_content_types):
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        return links