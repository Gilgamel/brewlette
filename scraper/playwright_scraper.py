"""
Nespresso Capsule Scraper using Playwright
Scrapes capsule data from Nespresso Canada website with proper dynamic content loading
"""
import asyncio
import json
import re
import os
from datetime import datetime
from playwright.async_api import async_playwright

# URLs to scrape
ORIGINAL_CAPSULES_URL = "https://www.nespresso.com/ca/en/order/capsules/original"
VERTUO_CAPSULES_URL = "https://www.nespresso.com/ca/en/order/capsules/vertuo"

# Output paths
SCRAPER_DIR = os.path.dirname(os.path.abspath(__file__))
CAPSULES_FILE = os.path.join(os.path.dirname(SCRAPER_DIR), "data", "capsules.json")


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


def parse_size_from_text(text: str) -> int:
    """Extract size in ml from text"""
    if not text:
        return None
    # Match patterns like "40ml", "40 mL", "40 ML"
    match = re.search(r'(\d+)\s*(?:mL|ml|ML)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def parse_intensity_from_text(text: str) -> int:
    """Extract intensity from text"""
    if not text:
        return None
    # Match intensity patterns like "Intensity 9", "Intensity: 9"
    match = re.search(r'(?:intensity|intensidad)[:\s]*(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


async def scrape_capsules_from_page(page, url: str, line: str) -> list:
    """Scrape capsules from a specific Nespresso page"""
    capsules = []

    print(f"Loading {url}...")
    await page.goto(url, wait_until="networkidle", timeout=60000)

    # Wait for product grid to load
    try:
        await page.wait_for_selector('[class*="product"], .product-grid, .product-list, .product-tiles', timeout=30000)
    except Exception as e:
        print(f"Timeout waiting for products: {e}")

    # Scroll to load all dynamic content
    print("Scrolling to load all products...")
    for i in range(8):
        await page.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(0.8)

    # Scroll back to top
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)

    # Get all product card elements
    product_elements = await page.query_selector_all('[class*="product-card"], [class*="product-tile"], .product-item, [class*="capsule-product"], a[href*="/product/"]')

    print(f"Found {len(product_elements)} potential product elements")

    for elem in product_elements:
        try:
            # Get the href to check if it's a capsule product
            href = await elem.get_attribute('href')
            if href and 'capsule' not in href.lower() and 'coffee' not in href.lower():
                continue

            # Try to extract product name from various elements
            name = None

            # Try heading elements first
            for selector in ['h2', 'h3', 'h4', '[class*="name"]', '[class*="title"]', '[class*="product-name"]']:
                name_elem = await elem.query_selector(selector)
                if name_elem:
                    name = await name_elem.inner_text()
                    if name:
                        break

            if not name:
                # Try getting from title attribute
                title = await elem.get_attribute('title')
                if title:
                    name = title

            if not name:
                # Try from aria-label
                aria_label = await elem.get_attribute('aria-label')
                if aria_label:
                    name = aria_label

            if not name or len(name) < 3:
                continue

            name = name.strip()
            if any(skip in name.lower() for skip in ['add to cart', 'buy', 'price', 'quantity', 'qty']):
                continue

            # Extract size - look for size badge/text
            size_ml = None
            size_elem = await elem.query_selector('[class*="size"], [class*="volume"], [class*="ml"], [class*="format"]')
            if size_elem:
                size_text = await size_elem.inner_text()
                size_ml = parse_size_from_text(size_text)

            if not size_ml:
                # Try from parent elements
                parent = await elem.query_selector('..')
                if parent:
                    size_text = await parent.inner_text()
                    size_ml = parse_size_from_text(size_text)

            # Extract intensity
            intensity = None
            intensity_elem = await elem.query_selector('[class*="intensity"], [class*=" Intensity"]')
            if intensity_elem:
                intensity_text = await intensity_elem.inner_text()
                intensity = parse_intensity_from_text(intensity_text)

            # Extract tasting notes
            tasting_note = ""
            for selector in ['[class*="note"]', '[class*="tasting"]', '[class*="flavor"]', '[class*="description"]']:
                note_elem = await elem.query_selector(selector)
                if note_elem:
                    tasting_note = await note_elem.inner_text()
                    if tasting_note:
                        break

            if not tasting_note:
                # Try description meta
                desc_elem = await elem.query_selector('meta[name="description"], [class*="description"]')
                if desc_elem:
                    tasting_note = await desc_elem.inner_text()
                    if tasting_note and len(tasting_note) > 200:
                        tasting_note = tasting_note[:200]

            # Determine pod type
            pod_type = determine_pod_type(size_ml, line)

            capsule = {
                "name": name,
                "name_en": name,
                "line": line,
                "size_ml": size_ml,
                "pod_type": pod_type,
                "intensity": intensity,
                "tasting_note": tasting_note.strip()[:200] if tasting_note else "",
                "tasting_note_en": tasting_note.strip()[:200] if tasting_note else ""
            }

            capsules.append(capsule)
        except Exception as e:
            continue

    # Also try JSON-LD as fallback
    if not capsules or len(capsules) < 5:
        print("Trying JSON-LD extraction...")
        content = await page.content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

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

    print(f"Found {len(capsules)} capsules from {url}")
    return capsules


def extract_product_data(data: dict, line: str) -> dict:
    """Extract product data from JSON-LD"""
    try:
        name = data.get('name', '')
        if not name:
            return None

        # Skip non-capsule products
        name_lower = name.lower()
        if 'capsule' not in name_lower and 'coffee' not in name_lower and 'espresso' not in name_lower:
            return None

        # Extract description for tasting notes
        description = data.get('description', '')

        # Extract size from offers
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        size_ml = None
        if offers:
            offer_desc = str(offers.get('description', ''))
            size_ml = parse_size_from_text(offer_desc)

            if not size_ml:
                price_spec = offers.get('priceSpecification', {})
                if price_spec:
                    size_value = price_spec.get('value')
                    if size_value:
                        size_ml = int(size_value) if isinstance(size_value, int) else None

        # Try to extract intensity from description
        intensity = parse_intensity_from_text(description)

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


async def scrape_all_capsules() -> list:
    """Scrape all capsules from Nespresso Canada"""
    all_capsules = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        # Navigate to homepage first
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
    return unique_capsules


async def update_capsules_json():
    """Main function to scrape and update capsules.json"""
    capsules = await scrape_all_capsules()

    # Create data directory if it doesn't exist
    data_dir = os.path.dirname(CAPSULES_FILE)
    os.makedirs(data_dir, exist_ok=True)

    # Add metadata
    data = {
        "last_updated": datetime.now().isoformat(),
        "source": "https://www.nespresso.com/ca/en/order/capsules",
        "capsules": capsules
    }

    # Save to JSON
    with open(CAPSULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(capsules)} capsules to {CAPSULES_FILE}")
    return capsules


def load_capsules() -> list:
    """Load capsules from JSON file"""
    if os.path.exists(CAPSULES_FILE):
        try:
            with open(CAPSULES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('capsules', [])
        except Exception as e:
            print(f"Error loading capsules: {e}")
    return []


if __name__ == "__main__":
    asyncio.run(update_capsules_json())
