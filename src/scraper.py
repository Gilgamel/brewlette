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
    Return comprehensive sample capsules data
    Based on official Nespresso Canada product listings
    Updated: 2026-02-27
    
    Note: Each capsule may have multiple sizes (e.g., Altissio Decaffeinato can be 40ml or 80ml)
    """
    
    capsules = [
        # ========== ORIGINAL LINE - ESPRESSO (40ml) ==========
        {"name": "Arpeggio", "name_en": "Arpeggio", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 9},
        {"name": "Ristretto", "name_en": "Ristretto", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 10},
        {"name": "Livanto", "name_en": "Livanto", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Capriccio", "name_en": "Capriccio", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        {"name": "Kazaar", "name_en": "Kazaar", "tasting_note": "Spicy", "tasting_note_en": "Spicy", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 12},
        {"name": "Dhorm", "name_en": "Dhorm", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Ispirazione Roma", "name_en": "Ispirazione Roma", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Ispirazione Venezia", "name_en": "Ispirazione Venezia", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Ispirazione Napoli", "name_en": "Ispirazione Napoli", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 13},
        {"name": "Ispirazione Firenze", "name_en": "Ispirazione Firenze", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 7},
        {"name": "Cosi", "name_en": "Cosi", "tasting_note": "Fruity", "tasting_note_en": "Fruity", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Volluto", "name_en": "Volluto", "tasting_note": "Sweet", "tasting_note_en": "Sweet", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Rosabaya", "name_en": "Rosabaya", "tasting_note": "Fruity", "tasting_note_en": "Fruity", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Dulsao", "name_en": "Dulsao", "tasting_note": "Sweet", "tasting_note_en": "Sweet", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Bukeela", "name_en": "Bukeela", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        
        # ========== ORIGINAL LINE - LUNGO (150ml) ==========
        {"name": "Vienna Lungo", "name_en": "Vienna Lungo", "tasting_note": "Malted Cereal", "tasting_note_en": "Malted Cereal", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 6},
        {"name": "Cape Town Lungo", "name_en": "Cape Town Lungo", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 10},
        {"name": "Tokyo Lungo", "name_en": "Tokyo Lungo", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 6},
        {"name": "Stockholm Lungo", "name_en": "Stockholm Lungo", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 8},
        {"name": "Shanghai Lungo", "name_en": "Shanghai Lungo", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 8},
        {"name": "Lisboa Lungo", "name_en": "Lisboa Lungo", "tasting_note": "Malted", "tasting_note_en": "Malted", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 5},
        {"name": "Baku Lungo", "name_en": "Baku Lungo", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 9},
        
        # ========== ORIGINAL LINE - SINGLE ORIGIN (40ml) ==========
        {"name": "Ethiopia", "name_en": "Ethiopia", "tasting_note": "Fruity", "tasting_note_en": "Fruity", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Colombia", "name_en": "Colombia", "tasting_note": "Winey", "tasting_note_en": "Winey", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "India", "name_en": "India", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 11},
        {"name": "Nicaragua", "name_en": "Nicaragua", "tasting_note": "Sweet", "tasting_note_en": "Sweet", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        {"name": "Brazil", "name_en": "Brazil", "tasting_note": "Nutty", "tasting_note_en": "Nutty", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        {"name": "Kenya", "name_en": "Kenya", "tasting_note": "Citrus", "tasting_note_en": "Citrus", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Guatemala", "name_en": "Guatemala", "tasting_note": "Spicy", "tasting_note_en": "Spicy", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 7},
        {"name": "Costa Rica", "name_en": "Costa Rica", "tasting_note": "Honey", "tasting_note_en": "Honey", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        
        # ========== ORIGINAL LINE - DECAF (40ml) ==========
        {"name": "Arpeggio Decaffeinato", "name_en": "Arpeggio Decaffeinato", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 9},
        {"name": "Volluto Decaffeinato", "name_en": "Volluto Decaffeinato", "tasting_note": "Sweet", "tasting_note_en": "Sweet", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 4},
        {"name": "Ristretto Decaffeinato", "name_en": "Ristretto Decaffeinato", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 10},
        {"name": "Livanto Decaffeinato", "name_en": "Livanto Decaffeinato", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        
        # ========== ORIGINAL LINE - FLAVOURED (40ml) ==========
        {"name": "Caramello", "name_en": "Caramello", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        {"name": "Vaniglia", "name_en": "Vaniglia", "tasting_note": "Vanilla", "tasting_note_en": "Vanilla", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        {"name": "Nocciola", "name_en": "Nocciola", "tasting_note": "Hazelnut", "tasting_note_en": "Hazelnut", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        {"name": "Cioccolino", "name_en": "Cioccolino", "tasting_note": "Chocolate", "tasting_note_en": "Chocolate", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": None},
        
        # ========== VERTUO LINE - ESPRESSO (40ml) ==========
        {"name": "Altissio", "name_en": "Altissio", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 9},
        {"name": "Diavolitto", "name_en": "Diavolitto", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 11},
        
        # ========== VERTUO LINE - DOUBLE ESPRESSO (80ml) ==========
        {"name": "Altissio", "name_en": "Altissio", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 9},
        {"name": "Diavolitto", "name_en": "Diavolitto", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 11},
        
        # ========== VERTUO LINE - BIANCO (80ml) ==========
        {"name": "Bianco", "name_en": "Bianco", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 8},
        {"name": "Bianco Odacio", "name_en": "Bianco Odacio", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 8},
        {"name": "Bianco Intensivo", "name_en": "Bianco Intensivo", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 11},
        
        # ========== VERTUO LINE - LUNGO (150ml) ==========
        {"name": "Fortado", "name_en": "Fortado", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 8},
        {"name": "Envivo", "name_en": "Envivo", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 9},
        {"name": "Istanbul", "name_en": "Istanbul", "tasting_note": "Spicy", "tasting_note_en": "Spicy", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 7},
        {"name": "Buenos Aires", "name_en": "Buenos Aires", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 6},
        
        # ========== VERTUO LINE - COFFEE/ALTO (230ml) ==========
        {"name": "Melozio", "name_en": "Melozio", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Odacio", "name_en": "Odacio", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "Stormio", "name_en": "Stormio", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 8},
        {"name": "Intenso", "name_en": "Intenso", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 9},
        {"name": "Alto Onice", "name_en": "Alto Onice", "tasting_note": "Intense Roasted", "tasting_note_en": "Intense Roasted", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "Alto Ambrato", "name_en": "Alto Ambrato", "tasting_note": "Honey", "tasting_note_en": "Honey", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        {"name": "Alto Dolce", "name_en": "Alto Dolce", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Voltesso", "name_en": "Voltesso", "tasting_note": "Light", "tasting_note_en": "Light", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        
        # ========== VERTUO LINE - DOUBLE ESPRESSO (80ml) ==========
        {"name": "Double Espresso Chiaro", "name_en": "Double Espresso Chiaro", "tasting_note": "Floral", "tasting_note_en": "Floral", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 8},
        {"name": "Double Espresso Dolce", "name_en": "Double Espresso Dolce", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 5},
        {"name": "Double Espresso Scuro", "name_en": "Double Espresso Scuro", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 11},
        
        # ========== VERTUO LINE - DECAFFEINATO ==========
        {"name": "Altissio Decaffeinato", "name_en": "Altissio Decaffeinato", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 9},
        {"name": "Melozio Decaffeinato", "name_en": "Melozio Decaffeinato", "tasting_note": "Cereal", "tasting_note_en": "Cereal", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Fortado Decaffeinato", "name_en": "Fortado Decaffeinato", "tasting_note": "Cocoa", "tasting_note_en": "Cocoa", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 8},
        
        # ========== VERTUO LINE - FLAVOURED (80ml) ==========
        {"name": "Sweet Vanilla", "name_en": "Sweet Vanilla", "tasting_note": "Vanilla", "tasting_note_en": "Vanilla", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": None},
        {"name": "Rich Chocolate", "name_en": "Rich Chocolate", "tasting_note": "Chocolate", "tasting_note_en": "Chocolate", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": None},
        {"name": "Caramel Creme", "name_en": "Caramel Creme", "tasting_note": "Caramel", "tasting_note_en": "Caramel", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": None},
        
        # ========== VERTUO LINE - SINGLE ORIGIN ==========
        {"name": "Ethiopia", "name_en": "Ethiopia", "tasting_note": "Floral", "tasting_note_en": "Floral", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 4},
        {"name": "Colombia", "name_en": "Colombia", "tasting_note": "Fruity", "tasting_note_en": "Fruity", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Mexico", "name_en": "Mexico", "tasting_note": "Spicy", "tasting_note_en": "Spicy", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "Brazil", "name_en": "Brazil", "tasting_note": "Nutty", "tasting_note_en": "Nutty", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Kenya", "name_en": "Kenya", "tasting_note": "Citrus", "tasting_note_en": "Citrus", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 6},
        {"name": "Indonesia", "name_en": "Indonesia", "tasting_note": "Earthy", "tasting_note_en": "Earthy", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 8},
        
        # ========== VERTUO LINE - BARISTA CREATIONS (230ml) ==========
        {"name": "Cortez", "name_en": "Cortez", "tasting_note": "Spicy", "tasting_note_en": "Spicy", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 9},
        {"name": "Napoli", "name_en": "Napoli", "tasting_note": "Intense", "tasting_note_en": "Intense", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 10},
        {"name": "Roma", "name_en": "Roma", "tasting_note": "Balanced", "tasting_note_en": "Balanced", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 8},
        {"name": "Milano", "name_en": "Milano", "tasting_note": "Sweet", "tasting_note_en": "Sweet", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
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
