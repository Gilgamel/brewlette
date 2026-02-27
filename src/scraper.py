"""
Nespresso Scraper Module
Scrapes capsule data from Nespresso official website
Supports both Original Line and Vertuo Line
"""
import requests
from bs4 import BeautifulSoup
import json
import random
from typing import List, Dict

# User agent to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Base URLs - Nespresso Canada
NESPRESSO_BASE_URL = "https://www.nespresso.com"


def scrape_original_line() -> List[Dict]:
    """
    Scrape Original Line capsules from Nespresso Canada website
    """
    capsules = []
    
    # Nespresso Canada URLs
    urls_to_try = [
        "https://www.nespresso.com/ca/en/order/capsules/original",
        "https://www.nespresso.com/ca/en/order/capsules",
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                # Parse the page to find capsule data
                capsules.extend(parse_original_capsules(soup))
                if capsules:
                    break
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    return capsules


def parse_original_capsules(soup: BeautifulSoup) -> List[Dict]:
    """
    Parse Original Line capsules from BeautifulSoup object
    """
    capsules = []
    
    # Try to find capsule data in JSON-LD script tags
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Product':
                        capsule = parse_product_json(item, 'Original')
                        if capsule:
                            capsules.append(capsule)
            elif data.get('@type') == 'Product':
                capsule = parse_product_json(data, 'Original')
                if capsule:
                    capsules.append(capsule)
        except:
            continue
    
    # If no JSON-LD found, try parsing from HTML elements
    if not capsules:
        # Look for product cards
        products = soup.find_all(['div', 'li'], class_=lambda x: x and ('product' in x.lower() or 'capsule' in x.lower()))
        for product in products:
            capsule = parse_product_html(product, 'Original')
            if capsule:
                capsules.append(capsule)
    
    return capsules


def parse_product_json(data: dict, line: str) -> Dict:
    """Parse product from JSON-LD data"""
    try:
        name = data.get('name', '')
        if not name:
            return None
        
        # Extract tasting notes from description
        description = data.get('description', '')
        
        # Extract size/type from offers
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        # Try to extract size from offers
        size_ml = None
        if offers:
            # Look for volume in offer
            offer_desc = str(offers.get('description', ''))
            if 'ml' in offer_desc.lower():
                import re
                ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
                if ml_match:
                    size_ml = int(ml_match.group(1))
        
        # Determine pod type from size
        pod_type = determine_pod_type(size_ml)
        
        return {
            "name": name,
            "name_en": name,  # Already English
            "tasting_note": description,
            "tasting_note_en": description,
            "size_ml": size_ml,
            "pod_type": pod_type,
            "line": line,
            "intensity": extract_intensity(description)
        }
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None


def parse_product_html(element, line: str) -> Dict:
    """Parse product from HTML element"""
    try:
        # Try to find name
        name_elem = element.find(['h3', 'h4', 'span', 'a'], class_=lambda x: x and 'name' in x.lower())
        if not name_elem:
            name_elem = element.find(['h3', 'h4', 'span', 'a'])
        
        if not name_elem:
            return None
        
        name = name_elem.get_text(strip=True)
        if not name:
            return None
        
        # Try to find other details
        description = element.get_text(strip=True)
        
        return {
            "name": name,
            "name_en": name,
            "tasting_note": description,
            "tasting_note_en": description,
            "size_ml": None,
            "pod_type": "espresso",
            "line": line,
            "intensity": None
        }
    except Exception as e:
        return None


def scrape_vertuo_line() -> List[Dict]:
    """
    Scrape Vertuo Line capsules from Nespresso Canada website
    """
    capsules = []
    
    # Nespresso Canada URLs
    urls_to_try = [
        "https://www.nespresso.com/ca/en/order/capsules/vertuo",
        "https://www.nespresso.com/ca/en/order/capsules",
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                capsules.extend(parse_vertuo_capsules(soup))
                if capsules:
                    break
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    return capsules


def parse_vertuo_capsules(soup: BeautifulSoup) -> List[Dict]:
    """
    Parse Vertuo Line capsules from BeautifulSoup object
    """
    capsules = []
    
    # Try JSON-LD first
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Product':
                        capsule = parse_product_json(item, 'Vertuo')
                        if capsule:
                            capsules.append(capsule)
            elif data.get('@type') == 'Product':
                capsule = parse_product_json(data, 'Vertuo')
                if capsule:
                    capsules.append(capsule)
        except:
            continue
    
    if not capsules:
        products = soup.find_all(['div', 'li'], class_=lambda x: x and ('product' in x.lower() or 'capsule' in x.lower()))
        for product in products:
            capsule = parse_product_html(product, 'Vertuo')
            if capsule:
                capsules.append(capsule)
    
    return capsules


def determine_pod_type(size_ml: int) -> str:
    """Determine pod type based on size"""
    if size_ml is None:
        return "espresso"
    
    if size_ml <= 50:
        return "espresso"
    elif size_ml <= 100:
        return "double"
    elif size_ml <= 180:
        return "lungo"
    elif size_ml <= 250:
        return "coffee"
    else:
        return "alto"


def extract_intensity(text: str) -> int:
    """Extract intensity from description"""
    if not text:
        return None
    
    import re
    # Look for intensity patterns
    patterns = [
        r'intensity[:\s]*(\d+)',
        r'(\d+)\/13 intensity',
        r'intensity (\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None


def get_sample_capsules() -> List[Dict]:
    """
    Return sample capsules data - scraped from Nespresso Canada website
    Updated: 2026-02-27
    """
    
    # Scraped data from Nespresso Canada
    capsules = [
        # Original Line - Espresso
        {"name": "Arpeggio", "name_en": "Arpeggio", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 9},
        {"name": "Ristretto", "name_en": "Ristretto", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 10},
        {"name": "Livanto", "name_en": "Livanto", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Capriccio", "name_en": "Capriccio", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        {"name": "Kazaar", "name_en": "Kazaar", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 12},
        {"name": "Ispirazione Roma", "name_en": "Ispirazione Roma", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Ispirazione Venezia", "name_en": "Ispirazione Venezia", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Ispirazione Napoli", "name_en": "Ispirazione Napoli", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 13},
        {"name": "Cosi", "name_en": "Cosi", "tasting_note": "Fruity", "tasting_note_en": "Fruity", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Volluto", "name_en": "Volluto", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        
        # Original Line - Lungo
        {"name": "Vienna Lungo", "name_en": "Vienna Lungo", "tasting_note": "Malted Cereal", "tasting_note_en": "Malted Cereal", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 6},
        {"name": "Cape Town Lungo", "name_en": "Cape Town Lungo", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 10},
        {"name": "Tokyo Lungo", "name_en": "Tokyo Lungo", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 6},
        {"name": "Stockholm Lungo", "name_en": "Stockholm Lungo", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 8},
        
        # Original Line - Single Origin
        {"name": "Ethiopia", "name_en": "Ethiopia", "tasting_note": "Fruity", "tasting_note_en": "Fruity", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Colombia", "name_en": "Colombia", "tasting_note": "Winey", "tasting_note_en": "Winey", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "India", "name_en": "India", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 11},
        {"name": "Nicaragua", "name_en": "Nicaragua", "tasting_note": "Sweet", "tasting_note_en": "Sweet", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        
        # Original Line - Decaf
        {"name": "Arpeggio Decaffeinato", "name_en": "Arpeggio Decaffeinato", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 9},
        {"name": "Volluto Decaffeinato", "name_en": "Volluto Decaffeinato", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Ristretto Decaffeinato", "name_en": "Ristretto Decaffeinato", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 10},
        
        # Original Line - Flavoured
        {"name": "Caramello", "name_en": "Caramello", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        {"name": "Vaniglia", "name_en": "Vaniglia", "tasting_note": "", "tasting_note_en": "", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        {"name": "Nocciola", "name_en": "Nocciola", "tasting_note": "Flavoured", "tasting_note_en": "Flavoured", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        
        # Vertuo Line - Espresso
        {"name": "Altissio", "name_en": "Altissio", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 9},
        {"name": "Double Espresso Scuro", "name_en": "Double Espresso Scuro", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 11},
        
        # Vertuo Line - Coffee (Alto)
        {"name": "Melozio", "name_en": "Melozio", "tasting_note": "", "tasting_note_en": "", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Odacio", "name_en": "Odacio", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "Stormio", "name_en": "Stormio", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 8},
        {"name": "Intenso", "name_en": "Intenso", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 9},
        {"name": "Alto Onice", "name_en": "Alto Onice", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "Alto Ambrato", "name_en": "Alto Ambrato", "tasting_note": "Honey", "tasting_note_en": "Honey", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        
        # Vertuo Line - Lungo
        {"name": "Fortado", "name_en": "Fortado", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 8},
        {"name": "Costa Rica", "name_en": "Costa Rica", "tasting_note": "Malted Cereal", "tasting_note_en": "Malted Cereal", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 7},
        
        # Vertuo Line - Double
        {"name": "Double Espresso Chiaro", "name_en": "Double Espresso Chiaro", "tasting_note": "", "tasting_note_en": "", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 8},
        {"name": "Double Espresso Dolce", "name_en": "Double Espresso Dolce", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 5},
        
        # Vertuo Line - Decaf
        {"name": "Altissio Decaffeinato", "name_en": "Altissio Decaffeinato", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 9},
        {"name": "Melozio Decaffeinato", "name_en": "Melozio Decaffeinato", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 6},
        {"name": "Fortado Decaffeinato", "name_en": "Fortado Decaffeinato", "tasting_note": "Woody", "tasting_note_en": "Woody", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 8},
        
        # Vertuo Line - Flavoured
        {"name": "Sweet Vanilla", "name_en": "Sweet Vanilla", "tasting_note": "Vanilla", "tasting_note_en": "Vanilla", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": None},
        {"name": "Rich Chocolate", "name_en": "Rich Chocolate", "tasting_note": "Chocolate", "tasting_note_en": "Chocolate", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": None},
        
        # Vertuo Line - Single Origin
        {"name": "Ethiopia", "name_en": "Ethiopia", "tasting_note": "", "tasting_note_en": "", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 4},
        {"name": "Mexico", "name_en": "Mexico", "tasting_note": "Spicy", "tasting_note_en": "Spicy", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "El Salvador", "name_en": "El Salvador", "tasting_note": "", "tasting_note_en": "", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
    ]
    
    return capsules


def scrape_all_capsules() -> List[Dict]:
    """
    Scrape all Nespresso capsules (both Original and Vertuo)
    Falls back to sample data if scraping fails
    """
    all_capsules = []
    
    # Try scraping Original Line
    try:
        original = scrape_original_line()
        if original:
            all_capsules.extend(original)
            print(f"Scraped {len(original)} Original Line capsules")
    except Exception as e:
        print(f"Error scraping Original Line: {e}")
    
    # Try scraping Vertuo Line
    try:
        vertuo = scrape_vertuo_line()
        if vertuo:
            all_capsules.extend(vertuo)
            print(f"Scraped {len(vertuo)} Vertuo Line capsules")
    except Exception as e:
        print(f"Error scraping Vertuo Line: {e}")
    
    # If no capsules scraped, use sample data
    if not all_capsules:
        print("Using sample capsule data")
        all_capsules = get_sample_capsules()
    
    return all_capsules


def get_capsules_by_size(capsules: List[Dict], size_ml: int) -> List[Dict]:
    """Filter capsules by size"""
    return [c for c in capsules if c.get('size_ml') == size_ml]


def get_capsules_by_type(capsules: List[Dict], pod_type: str) -> List[Dict]:
    """Filter capsules by type (espresso/double/lungo)"""
    return [c for c in capsules if c.get('pod_type', '').lower() == pod_type.lower()]


def get_capsules_by_line(capsules: List[Dict], line: str) -> List[Dict]:
    """Filter capsules by line (Original/Vertuo)"""
    return [c for c in capsules if c.get('line', '').lower() == line.lower()]
