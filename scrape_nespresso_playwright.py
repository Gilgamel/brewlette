"""
Nespresso Capsule Scraper using Playwright
Scrapes capsule data from Nespresso Canada website with proper dynamic content loading
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
    
    # Vertuo sizes
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
    
    # Original sizes
    if size_ml <= 50:
        return "espresso"
    elif size_ml <= 100:
        return "double"
    elif size_ml <= 200:
        return "lungo"
    else:
        return "coffee"


async def scrape_capsules_from_page(page, url: str, line: str) -> list:
    """Scrape capsules from a specific Nespresso page"""
    capsules = []
    
    print(f"Loading {url}...")
    await page.goto(url, wait_until="networkidle", timeout=60000)
    
    # Wait for product grid to load
    await page.wait_for_selector('[class*="product"], .product-grid, .product-list', timeout=30000)
    
    # Scroll to load all dynamic content
    print("Scrolling to load all products...")
    for _ in range(5):
        await page.evaluate("window.scrollBy(0, 1000)")
        await asyncio.sleep(1)
    
    # Get page content
    content = await page.content()
    
    # Extract product data from JSON-LD
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
                        capsule = extract_product_data(item, line)
                        if capsule:
                            capsules.append(capsule)
            elif data.get('@type') == 'Product':
                capsule = extract_product_data(data, line)
                if capsule:
                    capsules.append(capsule)
        except:
            continue
    
    # Also try to extract from product cards
    if not capsules:
        print("No JSON-LD found, trying product cards...")
        product_cards = await page.query_selector_all('[class*="product"], .product-item, .capsule-product')
        
        for card in product_cards:
            try:
                # Try to get name
                name_elem = await card.query_selector('h3, h4, [class*="name"], [class*="title"]')
                name = await name_elem.inner_text() if name_elem else None
                
                if name:
                    name = name.strip()
                    capsules.append({
                        "name": name,
                        "name_en": name,
                        "line": line,
                        "size_ml": None,
                        "pod_type": "espresso",
                        "intensity": None,
                        "tasting_note": "",
                        "tasting_note_en": ""
                    })
            except:
                continue
    
    print(f"Found {len(capsules)} capsules from {url}")
    return capsules


def extract_product_data(data: dict, line: str) -> dict:
    """Extract product data from JSON-LD"""
    try:
        name = data.get('name', '')
        if not name or 'capsule' not in name.lower() and 'coffee' not in name.lower():
            # Skip non-capsule products
            pass
        
        # Extract description for tasting notes
        description = data.get('description', '')
        
        # Extract size from offers
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        size_ml = None
        if offers:
            offer_desc = str(offers.get('description', ''))
            # Look for ml in description
            ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
            if ml_match:
                size_ml = int(ml_match.group(1))
            
            # Also check price specification
            if not size_ml:
                price_spec = offers.get('priceSpecification', {})
                if price_spec:
                    size_value = price_spec.get('value')
                    if size_value:
                        size_ml = int(size_value) if isinstance(size_value, int) else None
        
        # Try to extract intensity from description
        intensity = None
        intensity_match = re.search(r'intensity[:\s]*(\d+)', description, re.IGNORECASE)
        if intensity_match:
            intensity = int(intensity_match.group(1))
        
        # Determine pod type
        pod_type = determine_pod_type(size_ml, line)
        
        return {
            "name": name,
            "name_en": name,
            "line": line,
            "size_ml": size_ml,
            "pod_type": pod_type,
            "intensity": intensity,
            "tasting_note": description[:200] if description else "",
            "tasting_note_en": description[:200] if description else ""
        }
    except Exception as e:
        print(f"Error extracting product: {e}")
        return None


async def main():
    """Main function to scrape all capsules"""
    all_capsules = []
    
    async with async_playwright() as p:
        # Launch with more options to avoid detection
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
            ]
        )
        
        # Create context with realistic browser settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Try to set HTTP/1.1 transport
        # Set extra HTTP headers
        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        })
        
        # Navigate to homepage first to establish connection
        print("Navigating to homepage first...")
        try:
            await page.goto("https://www.nespresso.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Homepage navigation failed: {e}")
        
        # Scrape Original Line with retry
        for attempt in range(3):
            try:
                original_capsules = await scrape_capsules_from_page(page, ORIGINAL_CAPSULES_URL, "Original")
                if original_capsules:
                    all_capsules.extend(original_capsules)
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} failed for Original: {e}")
                await asyncio.sleep(2)
        
        # Scrape Vertuo Line with retry
        for attempt in range(3):
            try:
                vertuo_capsules = await scrape_capsules_from_page(page, VERTUO_CAPSULES_URL, "Vertuo")
                if vertuo_capsules:
                    all_capsules.extend(vertuo_capsules)
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} failed for Vertuo: {e}")
                await asyncio.sleep(2)
        
        await browser.close()
    
    # Remove duplicates based on name + line + size
    seen = set()
    unique_capsules = []
    for capsule in all_capsules:
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
    asyncio.run(main())
