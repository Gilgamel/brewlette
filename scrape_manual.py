"""
Nespresso Capsule Scraper - Manual Mode
Run this script with a visible browser to scrape capsules
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

# URLs to scrape
ORIGINAL_CAPSULES_URL = "https://www.nespresso.com/ca/en/order/capsules/original"
VERTUO_CAPSULES_URL = "https://www.nespresso.com/ca/en/order/capsules/vertuo"


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


async def scrape_with_browser():
    """Scrape capsules using visible browser"""
    capsules = []
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode (visible window)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("=" * 60)
        print("INSTRUCTIONS:")
        print("1. A browser window will open")
        print("2. Go to: https://www.nespresso.com/ca/en/order/capsules/original")
        print("3. Wait for the page to fully load")
        print("4. Scroll down to see all products")
        print("5. Press ENTER in this console when ready to extract data")
        print("=" * 60)
        
        input("Press ENTER after loading the Original capsules page...")
        
        # Extract data from current page
        content = await page.content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all JSON-LD scripts
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Product':
                            name = item.get('name', '')
                            if name and ('capsule' in name.lower() or 'coffee' in name.lower()):
                                desc = item.get('description', '')
                                offers = item.get('offers', {})
                                if isinstance(offers, list):
                                    offers = offers[0] if offers else {}
                                
                                size_ml = None
                                if offers:
                                    offer_desc = str(offers.get('description', ''))
                                    ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
                                    if ml_match:
                                        size_ml = int(ml_match.group(1))
                                
                                intensity = None
                                int_match = re.search(r'intensity[:\s]*(\d+)', desc, re.IGNORECASE)
                                if int_match:
                                    intensity = int(int_match.group(1))
                                
                                capsules.append({
                                    "name": name,
                                    "name_en": name,
                                    "line": "Original",
                                    "size_ml": size_ml,
                                    "pod_type": determine_pod_type(size_ml, "Original"),
                                    "intensity": intensity,
                                    "tasting_note": desc[:200] if desc else "",
                                    "tasting_note_en": desc[:200] if desc else ""
                                })
                elif data.get('@type') == 'Product':
                    name = data.get('name', '')
                    if name and ('capsule' in name.lower() or 'coffee' in name.lower()):
                        desc = data.get('description', '')
                        offers = data.get('offers', {})
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        
                        size_ml = None
                        if offers:
                            offer_desc = str(offers.get('description', ''))
                            ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
                            if ml_match:
                                size_ml = int(ml_match.group(1))
                        
                        intensity = None
                        int_match = re.search(r'intensity[:\s]*(\d+)', desc, re.IGNORECASE)
                        if int_match:
                            intensity = int(int_match.group(1))
                        
                        capsules.append({
                            "name": name,
                            "name_en": name,
                            "line": "Original",
                            "size_ml": size_ml,
                            "pod_type": determine_pod_type(size_ml, "Original"),
                            "intensity": intensity,
                            "tasting_note": desc[:200] if desc else "",
                            "tasting_note_en": desc[:200] if desc else ""
                        })
            except:
                continue
        
        print(f"Found {len(capsules)} Original capsules")
        
        # Now do the same for Vertuo
        print("\n" + "=" * 60)
        print("Now go to: https://www.nespresso.com/ca/en/order/capsules/vertuo")
        print("Wait for page to load, then press ENTER")
        print("=" * 60)
        
        input("Press ENTER after loading the Vertuo capsules page...")
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Product':
                            name = item.get('name', '')
                            if name and ('capsule' in name.lower() or 'coffee' in name.lower()):
                                desc = item.get('description', '')
                                offers = item.get('offers', {})
                                if isinstance(offers, list):
                                    offers = offers[0] if offers else {}
                                
                                size_ml = None
                                if offers:
                                    offer_desc = str(offers.get('description', ''))
                                    ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
                                    if ml_match:
                                        size_ml = int(ml_match.group(1))
                                
                                intensity = None
                                int_match = re.search(r'intensity[:\s]*(\d+)', desc, re.IGNORECASE)
                                if int_match:
                                    intensity = int(int_match.group(1))
                                
                                capsules.append({
                                    "name": name,
                                    "name_en": name,
                                    "line": "Vertuo",
                                    "size_ml": size_ml,
                                    "pod_type": determine_pod_type(size_ml, "Vertuo"),
                                    "intensity": intensity,
                                    "tasting_note": desc[:200] if desc else "",
                                    "tasting_note_en": desc[:200] if desc else ""
                                })
                elif data.get('@type') == 'Product':
                    name = data.get('name', '')
                    if name and ('capsule' in name.lower() or 'coffee' in name.lower()):
                        desc = data.get('description', '')
                        offers = data.get('offers', {})
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        
                        size_ml = None
                        if offers:
                            offer_desc = str(offers.get('description', ''))
                            ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
                            if ml_match:
                                size_ml = int(ml_match.group(1))
                        
                        intensity = None
                        int_match = re.search(r'intensity[:\s]*(\d+)', desc, re.IGNORECASE)
                        if int_match:
                            intensity = int(int_match.group(1))
                        
                        capsules.append({
                            "name": name,
                            "name_en": name,
                            "line": "Vertuo",
                            "size_ml": size_ml,
                            "pod_type": determine_pod_type(size_ml, "Vertuo"),
                            "intensity": intensity,
                            "tasting_note": desc[:200] if desc else "",
                            "tasting_note_en": desc[:200] if desc else ""
                        })
            except:
                continue
        
        print(f"Found {len(capsules)} Vertuo capsules")
        
        await browser.close()
    
    # Remove duplicates
    seen = set()
    unique_capsules = []
    for capsule in capsules:
        key = (capsule.get('name'), capsule.get('line'), capsule.get('size_ml'))
        if key not in seen:
            seen.add(key)
            unique_capsules.append(capsule)
    
    print(f"\nTotal unique capsules: {len(unique_capsules)}")
    
    # Save to JSON
    with open('nespresso_capsules_scraped.json', 'w', encoding='utf-8') as f:
        json.dump(unique_capsules, f, indent=2, ensure_ascii=False)
    
    print("Saved to nespresso_capsules_scraped.json")
    return unique_capsules


if __name__ == "__main__":
    asyncio.run(scrape_with_browser())
