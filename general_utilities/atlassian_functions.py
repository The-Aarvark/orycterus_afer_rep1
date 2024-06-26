import requests
from requests.auth import HTTPBasicAuth
from general_utilities.my_secrets import MySecrets

class ConfluenceJiraAPI:
    def __init__(self):
        self.confluence_api_key = MySecrets.get_secret('usafactsatlassian_api_key')
        self.jira_api_key = MySecrets.get_secret('usafactsatlassian_api_key')
        self.username = MySecrets.get_secret('usafactsemail')  # Assuming the username is stored in secrets
        self.atlassian_base_url = MySecrets.get_secret('usaf_atlassian_base_url')  # Assuming the base URL is stored in secrets
        
    # Confluence functions
    def get_confluence_page(self, url):
        headers = {
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(self.username, self.confluence_api_key))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

    def create_confluence_page(self, base_url, space_key, title, body):
        url = f"{base_url}/rest/api/content/"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage"
                }
            }
        }
        response = requests.post(url, json=data, headers=headers, auth=HTTPBasicAuth(self.username, self.confluence_api_key))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create the page. Status code: {response.status_code}")

    def update_confluence_page(self, base_url, page_id, title, body, version):
        url = f"{base_url}/rest/api/content/{page_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "id": page_id,
            "type": "page",
            "title": title,
            "version": {
                "number": version + 1
            },
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage"
                }
            }
        }
        response = requests.put(url, json=data, headers=headers, auth=HTTPBasicAuth(self.username, self.confluence_api_key))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update the page. Status code: {response.status_code}")

    # JIRA functions
    def get_jira_issue(self, base_url, issue_key):
        url = f"{base_url}/rest/api/2/issue/{issue_key}"
        headers = {
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(self.username, self.jira_api_key))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve the issue. Status code: {response.status_code}")

    def create_jira_issue(self, base_url, project_key, summary, issue_type, description):
        url = f"{base_url}/rest/api/2/issue"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
                "description": description
            }
        }
        response = requests.post(url, json=data, headers=headers, auth=HTTPBasicAuth(self.username, self.jira_api_key))
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create the issue. Status code: {response.status_code}")

    def update_jira_issue(self, base_url, issue_key, fields):
        url = f"{base_url}/rest/api/2/issue/{issue_key}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "fields": fields
        }
        response = requests.put(url, json=data, headers=headers, auth=HTTPBasicAuth(self.username, self.jira_api_key))
        if response.status_code == 204:
            return {"status": "Issue updated successfully"}
        else:
            raise Exception(f"Failed to update the issue. Status code: {response.status_code}")

# Example usage
if __name__ == "__main__":
    api = ConfluenceJiraAPI()

    # Confluence example
    confluence_url = "https://usafacts.atlassian.net/wiki/rest/api/content/{page_id}"
    try:
        page_content = api.get_confluence_page(confluence_url)
        print("Confluence Page Content:", page_content)
    except Exception as e:
        print(e)

    # JIRA example
    jira_url = "https://usafacts.atlassian.net"
    issue_key = "PROJ-123"
    try:
        issue_content = api.get_jira_issue(jira_url, issue_key)
        print("JIRA Issue Content:", issue_content)
    except Exception as e:
        print(e)
