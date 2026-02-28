"""
Nespresso Capsule Scraper using Requests
Scrapes capsule data from Nespresso Canada website
"""
import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

ORIGINAL_URL = "https://www.nespresso.com/ca/en/order/capsules/original"
VERTUO_URL = "https://www.nespresso.com/ca/en/order/capsules/vertuo"


def determine_pod_type(size_ml: int, line: str) -> str:
    """Determine pod type based on size and line"""
    if size_ml is None:
        return "espresso"
    
    if line == "Vertuo":
        if size_ml <= 30:
            return "espresso"
        elif size_ml <= 50:
            return "espresso"
        elif size_ml <= 100:
            return "double"
        elif size_ml <= 180:
            return "lungo"
        elif size_ml <= 280:
            return "coffee"
        else:
            return "alto"
    
    if size_ml <= 50:
        return "espresso"
    elif size_ml <= 100:
        return "double"
    elif size_ml <= 200:
        return "lungo"
    else:
        return "coffee"


def scrape_page(url: str, line: str) -> list:
    """Scrape capsules from a page"""
    capsules = []
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    print(f"Status: {response.status_code}, Length: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all JSON-LD scripts
    scripts = soup.find_all('script', type='application/ld+json')
    print(f"Found {len(scripts)} JSON-LD scripts")
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Product':
                        capsule = extract_product(item, line)
                        if capsule:
                            capsules.append(capsule)
            elif data.get('@type') == 'Product':
                capsule = extract_product(data, line)
                if capsule:
                    capsules.append(capsule)
            elif isinstance(data, dict):
                # Check for @graph structure
                graph = data.get('@graph', [])
                for item in graph:
                    if item.get('@type') == 'Product':
                        capsule = extract_product(item, line)
                        if capsule:
                            capsules.append(capsule)
        except Exception as e:
            continue
    
    print(f"Found {len(capsules)} capsules from {url}")
    return capsules


def extract_product(data: dict, line: str) -> dict:
    """Extract product data from JSON-LD"""
    try:
        name = data.get('name', '')
        if not name:
            return None
        
        # Skip non-capsule products
        name_lower = name.lower()
        if 'capsule' not in name_lower and 'coffee' not in name_lower and 'brewing' not in name_lower:
            # But include known capsule names
            pass
        
        # Extract description
        description = data.get('description', '')
        
        # Extract size from offers
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        size_ml = None
        if offers:
            offer_desc = str(offers.get('description', ''))
            # Look for ml pattern
            ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
            if ml_match:
                size_ml = int(ml_match.group(1))
            
            # Also check priceSpecification for volume
            if not size_ml:
                price_spec = offers.get('priceSpecification', {})
                if price_spec:
                    # Check for value reference or direct value
                    value_ref = price_spec.get('valueReference')
                    if value_ref == 'volume':
                        size_ml = price_spec.get('value')
                    elif 'value' in price_spec and isinstance(price_spec['value'], int):
                        size_ml = price_spec['value']
        
        # Extract intensity from description
        intensity = None
        int_match = re.search(r'intensity[:\s]*(\d+)', description, re.IGNORECASE)
        if int_match:
            intensity = int(int_match.group(1))
        
        # Also try to find intensity in name
        if not intensity:
            int_match = re.search(r'(\d+)\/13', name)
            if int_match:
                intensity = int(int_match.group(1))
        
        pod_type = determine_pod_type(size_ml, line)
        
        return {
            "name": name,
            "name_en": name,
            "line": line,
            "size_ml": size_ml,
            "pod_type": pod_type,
            "intensity": intensity,
            "tasting_note": description[:300] if description else "",
            "tasting_note_en": description[:300] if description else ""
        }
    except Exception as e:
        return None


def main():
    """Main function"""
    all_capsules = []
    
    # Scrape Original Line
    try:
        original_capsules = scrape_page(ORIGINAL_URL, "Original")
        all_capsules.extend(original_capsules)
    except Exception as e:
        print(f"Error scraping Original: {e}")
    
    # Scrape Vertuo Line
    try:
        vertuo_capsules = scrape_page(VERTUO_URL, "Vertuo")
        all_capsules.extend(vertuo_capsules)
    except Exception as e:
        print(f"Error scraping Vertuo: {e}")
    
    # Remove duplicates
    seen = set()
    unique_capsules = []
    for capsule in all_capsules:
        key = (capsule.get('name'), capsule.get('line'), capsule.get('size_ml'))
        if key not in seen:
            seen.add(key)
            unique_capsules.append(capsule)
    
    print(f"\nTotal unique capsules: {len(unique_capsules)}")
    
    # Show some examples
    print("\nSample capsules:")
    for c in unique_capsules[:10]:
        print(f"  - {c['name']} ({c['line']}, {c['size_ml']}ml, intensity: {c['intensity']})")
    
    # Save to JSON
    with open('nespresso_capsules_scraped.json', 'w', encoding='utf-8') as f:
        json.dump(unique_capsules, f, indent=2, ensure_ascii=False)
    
    print("\nSaved to nespresso_capsules_scraped.json")
    return unique_capsules


if __name__ == "__main__":
    main()
