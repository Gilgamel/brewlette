"""
Nespresso Scraper Module
Scrapes capsule data from Nespresso official website (Canada)
Supports both Original Line and Vertuo Line
"""
import requests
from bs4 import BeautifulSoup
import json
import random
import re
from typing import List, Dict

# User agent to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-CA,en;q=0.9"
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
        
        description = data.get('description', '')
        
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        size_ml = None
        if offers:
            offer_desc = str(offers.get('description', ''))
            if 'ml' in offer_desc.lower():
                ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
                if ml_match:
                    size_ml = int(ml_match.group(1))
        
        pod_type = determine_pod_type(size_ml)
        
        return {
            "name": name,
            "name_en": name,
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
        name_elem = element.find(['h3', 'h4', 'span', 'a'], class_=lambda x: x and 'name' in x.lower())
        if not name_elem:
            name_elem = element.find(['h3', 'h4', 'span', 'a'])
        
        if not name_elem:
            return None
        
        name = name_elem.get_text(strip=True)
        if not name:
            return None
        
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
    Return sample capsules data for when scraping fails
    This provides a fallback with realistic Nespresso products
    """
    
    # Original Line - 经典款
    original_capsules = [
        {"name": "Arpeggio", "name_en": "Arpeggio", "tasting_note": "Cereal, honey, caramel", "tasting_note_en": "Cereal, honey, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 9},
        {"name": "Ristretto", "name_en": "Ristretto", "tasting_note": "Cereal, cocoa, caramel", "tasting_note_en": "Cereal, cocoa, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 10},
        {"name": "Livanto", "name_en": "Livanto", "tasting_note": "Caramel, biscuit, vanilla", "tasting_note_en": "Caramel, biscuit, vanilla", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Capriccio", "name_en": "Capriccio", "tasting_note": "Cereal, green apple", "tasting_note_en": "Cereal, green apple", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        {"name": "Kazaar", "name_en": "Kazaar", "tasting_note": "Intense, cocoa, spicy", "tasting_note_en": "Intense, cocoa, spicy", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 12},
        {"name": "Dharkan", "name_en": "Dharkan", "tasting_note": "Roasted, cocoa, smoky", "tasting_note_en": "Roasted, cocoa, smoky", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 11},
        {"name": "Roma", "name_en": "Roma", "tasting_note": "Roasted, cereal", "tasting_note_en": "Roasted, cereal", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Decaf Intenso", "name_en": "Decaf Intenso", "tasting_note": "Roasted, caramel", "tasting_note_en": "Roasted, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 7},
        
        # Original Line - Double
        {"name": "Doppio", "name_en": "Doppio", "tasting_note": "Roasted, caramel", "tasting_note_en": "Roasted, caramel", "size_ml": 80, "pod_type": "double", "line": "Original", "intensity": 9},
        
        # Original Line - Lungo
        {"name": "Vivalto Lungo", "name_en": "Vivalto Lungo", "tasting_note": "Roasted, floral, slight fruit", "tasting_note_en": "Roasted, floral, slight fruit", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 5},
        {"name": "Fortissio Lungo", "name_en": "Fortissio Lungo", "tasting_note": "Roasted, green apple, caramel", "tasting_note_en": "Roasted, green apple, caramel", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 7},
        {"name": "Linizio Lungo", "name_en": "Linizio Lungo", "tasting_note": "Cereal, malt", "tasting_note_en": "Cereal, malt", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 4},
    ]
    
    # Vertuo Line - 经典款 + 联名款
    vertuo_capsules = [
        # Vertuo Espresso (40ml)
        {"name": "Odacio", "name_en": "Odacio", "tasting_note": "Roasted, green apple, berries", "tasting_note_en": "Roasted, green apple, berries", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 8},
        {"name": "Melozio", "name_en": "Melozio", "tasting_note": "Roasted, caramel, creamy", "tasting_note_en": "Roasted, caramel, creamy", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Volcanic", "name_en": "Volcanic", "tasting_note": "Roasted, smoky, cocoa", "tasting_note_en": "Roasted, smoky, cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 10},
        {"name": "Nicaragua", "name_en": "Nicaragua", "tasting_note": "Roasted, fruity, wine", "tasting_note_en": "Roasted, fruity, wine", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 7},
        {"name": "Ethiopia", "name_en": "Ethiopia", "tasting_note": "Floral, citrus, jasmine", "tasting_note_en": "Floral, citrus, jasmine", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Colombia", "name_en": "Colombia", "tasting_note": "Roasted, caramel, nuts", "tasting_note_en": "Roasted, caramel, nuts", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        
        # Vertuo Double (80ml)
        {"name": "Double Espresso", "name_en": "Double Espresso", "tasting_note": "Roasted, caramel, cocoa", "tasting_note_en": "Roasted, caramel, cocoa", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 7},
        {"name": "Chiaro", "name_en": "Chiaro", "tasting_note": "Smooth, roasted, caramel", "tasting_note_en": "Smooth, roasted, caramel", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 4},
        {"name": "Scuro", "name_en": "Scuro", "tasting_note": "Dark roast, cocoa, smoky", "tasting_note_en": "Dark roast, cocoa, smoky", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 9},
        
        # Vertuo Gran Lungo (150ml)
        {"name": "Envivo Lungo", "name_en": "Envivo Lungo", "tasting_note": "Roasted, caramel, green apple", "tasting_note_en": "Roasted, caramel, green apple", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 9},
        {"name": "Intenso", "name_en": "Intenso", "tasting_note": "Roasted, cocoa, caramel", "tasting_note_en": "Roasted, cocoa, caramel", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 9},
        {"name": "Dolceo", "name_en": "Dolceo", "tasting_note": "Roasted, caramel, creamy", "tasting_note_en": "Roasted, caramel, creamy", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 6},
        
        # Vertuo Alto (230ml)
        {"name": "Rich Chocolate", "name_en": "Rich Chocolate", "tasting_note": "Rich chocolate, roasted", "tasting_note_en": "Rich chocolate, roasted", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 8},
        {"name": "Hazelnut", "name_en": "Hazelnut", "tasting_note": "Roasted, hazelnut", "tasting_note_en": "Roasted, hazelnut", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Caramel Cookie", "name_en": "Caramel Cookie", "tasting_note": "Caramel, biscuit", "tasting_note_en": "Caramel, biscuit", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Ice Coffee", "name_en": "Ice Coffee", "tasting_note": "Refreshing, fruity", "tasting_note_en": "Refreshing, fruity", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        
        # ===== VERTUO 联名款胶囊 (Starbucks 等) =====
        {"name": "Starbucks Blonde Espresso", "name_en": "Starbucks Blonde Espresso", "tasting_note": "Light roast, caramel, citrus", "tasting_note_en": "Light roast, caramel, citrus", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 5},
        {"name": "Starbucks Veranda Blend", "name_en": "Starbucks Veranda Blend", "tasting_note": "Light roast, malt, chocolate", "tasting_note_en": "Light roast, malt, chocolate", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 4},
        {"name": "Starbucks Pike Place", "name_en": "Starbucks Pike Place", "tasting_note": "Medium roast, caramel, cocoa", "tasting_note_en": "Medium roast, caramel, cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Starbucks Dark Roast", "name_en": "Starbucks Dark Roast", "tasting_note": "Dark roast, cocoa, smoky", "tasting_note_en": "Dark roast, cocoa, smoky", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 9},
        
        # Starbucks Alto (230ml)
        {"name": "Starbucks Caramel Macchiato", "name_en": "Starbucks Caramel Macchiato", "tasting_note": "Caramel, milk, vanilla", "tasting_note_en": "Caramel, milk, vanilla", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Starbucks Cappuccino", "name_en": "Starbucks Cappuccino", "tasting_note": "Roasted, creamy, caramel", "tasting_note_en": "Roasted, creamy, caramel", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        
        # NOLA - New Orleans Style (Vertuo 特有)
        {"name": "NOLA", "name_en": "NOLA", "tasting_note": "New Orleans style, caramel, vanilla", "tasting_note_en": "New Orleans style, caramel, vanilla", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        
        # Limited Editions
        {"name": "Fizzio", "name_en": "Fizzio", "tasting_note": "Fizzy, citrus, mint", "tasting_note_en": "Fizzy, citrus, mint", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        {"name": "Bianco", "name_en": "Bianco", "tasting_note": "Creamy, biscuit, vanilla", "tasting_note_en": "Creamy, biscuit, vanilla", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 5},
    ]
    
    return original_capsules + vertuo_capsules


def scrape_all_capsules() -> List[Dict]:
    """
    Scrape all Nespresso capsules (both Original and Vertuo)
    Falls back to sample data if scraping fails
    """
    all_capsules = []
    
    try:
        original = scrape_original_line()
        if original:
            all_capsules.extend(original)
            print(f"Scraped {len(original)} Original Line capsules")
    except Exception as e:
        print(f"Error scraping Original Line: {e}")
    
    try:
        vertuo = scrape_vertuo_line()
        if vertuo:
            all_capsules.extend(vertuo)
            print(f"Scraped {len(vertuo)} Vertuo Line capsules")
    except Exception as e:
        print(f"Error scraping Vertuo Line: {e}")
    
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
