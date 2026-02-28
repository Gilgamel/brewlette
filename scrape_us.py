"""
Nespresso Capsule Scraper - US Website
"""
import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_us():
    """Scrape US Nespresso website"""
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    session.headers.update(headers)
    
    # Try US website
    urls_to_try = [
        "https://www.nespresso.com/us/en/order/capsules",
        "https://www.nespresso.com/us/en/order/coffee-capsules",
        "https://www.nespresso.com/us/en/orders/capsules",
    ]
    
    for url in urls_to_try:
        print(f"Trying: {url}")
        try:
            r = session.get(url, timeout=30)
            print(f"  Status: {r.status_code}, Length: {len(r.text)}")
            
            if r.status_code == 200 and len(r.text) > 10000:
                soup = BeautifulSoup(r.text, 'html.parser')
                scripts = soup.find_all('script', type='application/ld+json')
                print(f"  Found {len(scripts)} JSON-LD scripts")
                
                # Parse capsules
                capsules = []
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, list):
                            for item in data:
                                if item.get('@type') == 'Product':
                                    capsules.append(item)
                        elif data.get('@type') == 'Product':
                            capsules.append(data)
                    except:
                        continue
                
                if capsules:
                    print(f"  Found {len(capsules)} products!")
                    return capsules, url
        except Exception as e:
            print(f"  Error: {e}")
    
    return None, None


if __name__ == "__main__":
    result, url = scrape_us()
    if result:
        print(f"\nSuccess from: {url}")
        print(f"Products: {len(result)}")
        # Save to file
        with open('nespresso_us_capsules.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("Saved to nespresso_us_capsules.json")
    else:
        print("\nFailed to scrape US website")
