"""
Nespresso Capsule Scraper using Session
"""
import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_with_session():
    """Scrape using session"""
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    
    session.headers.update(headers)
    
    # First visit homepage
    print("Visiting homepage...")
    r = session.get("https://www.nespresso.com", timeout=30)
    print(f"Homepage: {r.status_code}")
    
    # Then try the capsules page
    url = "https://www.nespresso.com/ca/en/order/capsules/original"
    print(f"Fetching {url}...")
    r = session.get(url, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')
        print(f"Found {len(scripts)} JSON-LD scripts")
        
        for i, script in enumerate(scripts):
            print(f"\n--- Script {i+1} ---")
            try:
                data = json.loads(script.string)
                print(f"Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {data.keys()}")
                    if '@type' in data:
                        print(f"@type: {data['@type']}")
            except Exception as e:
                print(f"Error: {e}")
    else:
        print(f"Response text: {r.text[:500]}")


if __name__ == "__main__":
    scrape_with_session()
