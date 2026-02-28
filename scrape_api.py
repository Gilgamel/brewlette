"""
Nespresso Capsule Scraper - Try API endpoints
"""
import requests
from bs4 import BeautifulSoup
import json
import re

def try_api():
    """Try different API endpoints"""
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nespresso.com/",
    }
    
    session.headers.update(headers)
    
    # Try API endpoints
    apis_to_try = [
        # Nespresso API endpoints
        "https://www.nespresso.com/api/catalog/products",
        "https://www.nespresso.com/api/v1/products",
        "https://www.nespresso.com/api/v1/capsules",
        "https://api.nespresso.com/v1/products",
        "https://api.nespresso.com/catalog/products",
        
        # GraphQL endpoints
        "https://www.nespresso.com/graphql",
        
        # Try fetching main page first to get API info
        "https://www.nespresso.com/ca/en",
    ]
    
    for url in apis_to_try:
        print(f"\nTrying: {url}")
        try:
            r = session.get(url, timeout=15)
            print(f"  Status: {r.status_code}, Length: {len(r.text)}")
            
            if r.status_code == 200 and len(r.text) > 100:
                # Try to parse as JSON
                try:
                    data = r.json()
                    print(f"  ✓ JSON response!")
                    print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                    
                    # Save to file
                    with open('nespresso_api_response.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print("  Saved to nespresso_api_response.json")
                    
                    return data
                except:
                    # Check for JSON in HTML
                    if 'application/json' in r.headers.get('Content-Type', ''):
                        print(f"  Content-Type suggests JSON but parsing failed")
                    else:
                        print(f"  Not JSON (Content-Type: {r.headers.get('Content-Type', 'unknown')})")
                        
        except Exception as e:
            print(f"  Error: {e}")
    
    # Try to find API URL from main page
    print("\n\nFetching main page to find API...")
    try:
        r = session.get("https://www.nespresso.com/ca/en", timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Look for API URLs in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                src = script.get('src', '')
                if 'api' in src.lower() or 'graphql' in src.lower():
                    print(f"Found API script: {src}")
                
                # Also check script content
                content = script.string or ''
                if 'api' in content.lower() and 'nespresso' in content.lower():
                    # Look for URL patterns
                    urls = re.findall(r'https?://[^\s"\'<>]+api[^\s"\'<>]*', content)
                    if urls:
                        print(f"Found API URL in script: {urls[:3]}")
            
            # Look for data attributes
            data_elements = soup.find_all(attrs={"data-api": True})
            for el in data_elements:
                print(f"Found data-api: {el.get('data-api')}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    return None


if __name__ == "__main__":
    try_api()
