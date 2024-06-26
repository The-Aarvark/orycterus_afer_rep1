from googleapiclient.discovery import build
from my_secrets import MySecrets

class GoogleSearch:
    def __init__(self):
        self.api_key = MySecrets.get_secret('google_api_key')
        self.cse_id = MySecrets.get_secret('google_cse_id')
        self.service = build("customsearch", "v1", developerKey=self.api_key)

    def search(self, query, num_results=10, domain=None):
        if domain:
            query = f"{query} site:{domain}"
        res = self.service.cse().list(q=query, cx=self.cse_id, num=num_results).execute()
        return res.get('items', [])

    def search_titles(self, query, num_results=10, domain=None):
        results = self.search(query, num_results, domain)
        return [item['title'] for item in results]

    def search_snippets(self, query, num_results=10, domain=None):
        results = self.search(query, num_results, domain)
        return [item['snippet'] for item in results]

    def search_links(self, query, num_results=10, domain=None):
        results = self.search(query, num_results, domain)
        return [item['link'] for item in results]

# Example usage
if __name__ == "__main__":
    google_search = GoogleSearch()
    query = "OpenAI"
    
    # Full search results
    search_results = google_search.search(query, domain="census.gov")
    for result in search_results:
        print(result['title'], result['link'])

    # Only titles
    titles = google_search.search_titles(query, domain=".gov")
    print("Titles:", titles)

    # Only snippets
    snippets = google_search.search_snippets(query, domain=".gov")
    print("Snippets:", snippets)

    # Only links
    links = google_search.search_links(query, domain="census.gov")
    print("Links:", links)
