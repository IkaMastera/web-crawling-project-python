import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def fetch_email(details_url):
    try:
        print(f"Fetching email from {details_url}")
        response = requests.get(details_url)
        response.raise_for_status() 

        details_soup = BeautifulSoup(response.text, 'html.parser')
        email_link = details_soup.select_one('a[href^="mailto:"]')
        if email_link:
            email_address = email_link['href'].replace('mailto:', '')  # Extract email
            return email_address
        else:
            return "No email found"
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {details_url}: {e}")
        return "Request failed"

    time.sleep(0.1)

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    table_rows = soup.find_all('tr')[1:]
    base_url = "https://www.bdh-online.de"

    data = []

    for row in table_rows:
        columns = row.find_all('td')
        if not columns:
            continue
        
        name = columns[0].get_text(strip=True).title()
        last_name, first_name = name.split(', ')
        plz = columns[2].get_text(strip=True)
        ort = columns[3].get_text(strip=True)

        detail_link = columns[5].find('a', href=True)
        if detail_link:
            detail_href = detail_link['href'].strip()

            details_url = detail_href if detail_href.startswith(('http://', 'https://')) else base_url + detail_href

            email = fetch_email(details_url)
        else:
            email = "No link found"

        data.append({
            'First Name': first_name,
            'Last Name': last_name,
            'PLZ': plz,
            'Ort': ort,
            'Email': email,
            'Gender': ''  # Placeholder for gender
        })

    return data

def save_to_csv(data, filename='therapists.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    base_url = 'https://www.bdh-online.de/patienten/therapeutensuche/'
    pages_to_fetch = 2

    all_data = []

    for page in range(1, pages_to_fetch + 1):
        url = f"{base_url}?seite={page}"
        print(f"Fetching data from: {url}")
        html = fetch_page(url)
        if html:
            data = parse_html(html)
            all_data.extend(data)
        else:
            print(f"Failed to retrieve page {page}")

    save_to_csv(all_data)

if __name__ == "__main__":
    main()