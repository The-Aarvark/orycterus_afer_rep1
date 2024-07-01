import requests
from bs4 import BeautifulSoup
import webbrowser
import time

def get_wonder_session():
    # Create a session object
    session = requests.Session()

    # Common headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    # Step 1: Access the initial URL
    initial_url = 'https://wonder.cdc.gov/mcd-icd10-provisional.html'
    response = session.get(initial_url, headers=headers)

    # Step 2: Extract the correct form for the "I Agree" button
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the correct form with the action URL '/controller/datarequest/D176'
    form = soup.find('form', action='/controller/datarequest/D176')
    action_url = form.get('action') if form else None

    if not action_url:
        print("Failed to find the agreement form.")
        exit()

    agree_url = 'https://wonder.cdc.gov' + action_url

    # Prepare the payload for the form submission
    payload = {}
    for input_tag in form.find_all('input'):
        name = input_tag.get('name')
        value = input_tag.get('value')
        if name:
            payload[name] = value

    response = session.post(agree_url, headers=headers, data=payload, allow_redirects=True)

    # Check if the agreement was successful
    if response.status_code != 200:
        print(f"Failed to submit the agreement form. Status code: {response.status_code}")
        print("Response:", response.text)
        exit()
    return session, response

def get_tables(session, response, api_payload=None):
    # Parse the response to get the next form or desired content
    soup = BeautifulSoup(response.content, 'html.parser')
    cookies = session.cookies
    cookie_header = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies])

    # Locate the form with the action URL containing 'jsessionid'
    form = soup.find('form', action=lambda x: x and 'jsessionid' in x)
    if not form:
        print("Failed to find the next form with jsessionid.")
        exit()

    # Extract the action URL
    next_action_url = 'https://wonder.cdc.gov' + form['action']

    # Add cookies to your headers
    next_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': response.url,
        'Cookie': cookie_header  # Add the cookies here
    }

    # Use the provided payload or let the user submit the form
    if api_payload is None:
        # Open the URL for the user to make their selections
        webbrowser.open(response.url)
        print("Please make your selections on the website and press the Send button.")

        # Wait for the user to press the Send button
        input("Press Enter after you have made your selections and pressed the Send button on the website...")

        # Simulate user payload capture (since we cannot capture actual user interaction)
        payload = {
            # Populate with data as if captured from user's selections
        }
    else:
        payload = api_payload

    # Make the POST request to the next action URL
    response = session.post(next_action_url, headers=next_headers, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    return tables

def main():
    session, response = get_wonder_session()

    # Default payload
    default_payload = {
        "B_1": "D176.V9-level1",
        "B_2": "D176.V15",
        "B_3": "*None*",
        "B_4": "*None*",
        "B_5": "*None*",
        "F_D176.V1": "*All*",
        "F_D176.V10": "*All*",
        "F_D176.V100": "*All*",
        "F_D176.V13": "*All*",
        "F_D176.V2": "*All*",
        "F_D176.V25": "*All*",
        "F_D176.V26": "*All*",
        "F_D176.V27": "*All*",
        "F_D176.V77": "*All*",
        "F_D176.V79": "*All*",
        "F_D176.V80": "*All*",
        "F_D176.V9": "*All*",
        "I_D176.V1": "*All* (All Dates)",
        "I_D176.V10": "*All* (The United States)",
        "I_D176.V100": "*All* (All Dates)",
        "I_D176.V2": "*All* (All Causes of Death)",
        "I_D176.V25": "All Causes of Death",
        "I_D176.V27": "*All* (The United States)",
        "I_D176.V77": "*All* (The United States)",
        "I_D176.V79": "*All* (The United States)",
        "I_D176.V80": "*All* (The United States)",
        "I_D176.V9": "*All* (The United States)",
        "L_D176.V15": "*All*",
        "L_D176.V16": "*All*",
        "M_1": "D176.M1",
        "M_2": "D176.M2",
        "M_3": "D176.M3",
        "M_31": "D176.M31",
        "M_32": "D176.M32",
        "M_9": "D176.M9",
        "O_MMWR": "false",
        "O_V100_fmode": "freg",
        "O_V10_fmode": "freg",
        "O_V13_fmode": "fadv",
        "O_V15_fmode": "fadv",
        "O_V16_fmode": "fadv",
        "O_V1_fmode": "freg",
        "O_V25_fmode": "freg",
        "O_V26_fmode": "fadv",
        "O_V27_fmode": "freg",
        "O_V2_fmode": "freg",
        "O_V77_fmode": "freg",
        "O_V79_fmode": "freg",
        "O_V80_fmode": "freg",
        "O_V9_fmode": "freg",
        "O_aar": "aar_std",
        "O_aar_CI": "true",
        "O_aar_SE": "true",
        "O_aar_enable": "true",
        "O_aar_pop": "0000",
        "O_age": "D176.V5",
        "O_dates": "YEAR",
        "O_death_location": "D176.V79",
        "O_death_urban": "D176.V89",
        "O_javascript": "on",
        "O_location": "D176.V9",
        "O_mcd": "D176.V13",
        "O_oc-sect1-request": "close",
        "O_precision": "1",
        "O_race": "D176.V42",
        "O_rate_per": "100000",
        "O_show_totals": "true",
        "O_timeout": "600",
        "O_title": "",
        "O_ucd": "D176.V2",
        "O_urban": "D176.V19",
        "VM_D176.M6_D176.V10": "",
        "VM_D176.M6_D176.V17": "*All*",
        "VM_D176.M6_D176.V1_S": "*All*",
        "VM_D176.M6_D176.V42": "*All*",
        "VM_D176.M6_D176.V7": "*All*",
        "V_D176.V1": "",
        "V_D176.V10": "",
        "V_D176.V100": "",
        "V_D176.V11": "*All*",
        "V_D176.V12": "*All*",
        "V_D176.V13": "",
        "V_D176.V13_AND": "",
        "V_D176.V15": "",
        "V_D176.V15_AND": "",
        "V_D176.V16": "",
        "V_D176.V16_AND": "",
        "V_D176.V17": "*All*",
        "V_D176.V19": "*All*",
        "V_D176.V2": "",
        "V_D176.V20": "*All*",
        "V_D176.V21": "*All*",
        "V_D176.V22": "*All*",
        "V_D176.V23": "*All*",
        "V_D176.V25": "",
        "V_D176.V26": "",
        "V_D176.V26_AND": "",
        "V_D176.V27": "",
        "V_D176.V4": "*All*",
        "V_D176.V42": "*All*",
        "V_D176.V43": "*All*",
        "V_D176.V44": "*All*",
        "V_D176.V5": "*All*",
        "V_D176.V51": "*All*",
        "V_D176.V52": "*All*",
        "V_D176.V6": "00",
        "V_D176.V7": "*All*",
        "V_D176.V77": "",
        "V_D176.V79": "",
        "V_D176.V80": "",
        "V_D176.V81": "*All*",
        "V_D176.V89": "*All*",
        "V_D176.V9": "",
        "action-Send": "Send",
        "dataset_code": "D176",
        "dataset_label": "Provisional Mortality Statistics, 2018 through Last Week",
        "dataset_vintage": "June 15, 2024 as of June 23, 2024",
        "finder-stage-D176.V1": "codeset",
        "finder-stage-D176.V10": "codeset",
        "finder-stage-D176.V100": "codeset",
        "finder-stage-D176.V13": "codeset",
        "finder-stage-D176.V15": "",
        "finder-stage-D176.V16": "",
        "finder-stage-D176.V2": "codeset",
        "finder-stage-D176.V25": "codeset",
        "finder-stage-D176.V26": "codeset",
        "finder-stage-D176.V27": "codeset",
        "finder-stage-D176.V77": "codeset",
        "finder-stage-D176.V79": "codeset",
        "finder-stage-D176.V80": "codeset",
        "finder-stage-D176.V9": "codeset",
        "saved_id": "",
        "stage": "request"
    }

    # Get the tables
    tables = get_tables(session, response, default_payload)
    print(f"Number of tables found: {len(tables)}")

    # If you want to return the tables for further processing, you can add:
    return tables

if __name__ == "__main__":
    main()
