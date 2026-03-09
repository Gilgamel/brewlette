"""
Nespresso Capsule Scraper using Playwright with advanced stealth mode
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

# URLs
ORIGINAL_URLS = [
    "https://www.nespresso.com/ca/en/order/capsules/original",
    "https://www.nespresso.com/us/en/order/capsules/original",
]
VERTUO_URLS = [
    "https://www.nespresso.com/ca/en/order/capsules/vertuo",
    "https://www.nespresso.com/us/en/order/capsules/vertuo",
]


def extract_intensity(text: str) -> int:
    """Extract intensity from text"""
    if not text:
        return None

    patterns = [
        r'intensity[:\s]*(\d+)',
        r'(\d+)\s*/\s*13',
        r'(\d+)\s*intensity',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def parse_product(product: dict, line: str) -> dict:
    """Parse product from JSON-LD data"""
    try:
        name = product.get('name', '')
        if not name:
            return None

        # Skip non-capsule products
        skip_words = ['machine', 'brewer', 'accessory', 'gift', 'bundle', '会员', '会员计划']
        if any(word in name.lower() for word in skip_words):
            return None

        description = product.get('description', '') or ''

        # Extract size
        size_ml = None
        offers = product.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        if offers:
            offer_desc = str(offers.get('description', ''))
            ml_match = re.search(r'(\d+)\s*ml', offer_desc, re.IGNORECASE)
            if ml_match:
                size_ml = int(ml_match.group(1))

        # Extract intensity
        intensity = extract_intensity(description) or extract_intensity(name)

        # Determine pod type
        pod_type = "espresso"
        if size_ml:
            if size_ml <= 50:
                pod_type = "espresso"
            elif size_ml <= 100:
                pod_type = "double"
            elif size_ml <= 180:
                pod_type = "lungo"
            else:
                pod_type = "coffee"

        return {
            "name": name,
            "name_en": name,
            "tasting_note": description[:300] if description else "",
            "tasting_note_en": description[:300] if description else "",
            "size_ml": size_ml,
            "pod_type": pod_type,
            "line": line,
            "intensity": intensity
        }
    except Exception as e:
        return None


async def scrape_page(page, url: str, line: str) -> list:
    """Scrape capsules from a specific page"""
    capsules = []

    print(f"Loading: {url}")

    try:
        # Try with longer timeout and wait for network idle
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)

        # Get page content
        content = await page.content()

        # Parse with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Find JSON-LD scripts
        scripts = soup.find_all('script', type='application/ld+json')
        print(f"Found {len(scripts)} JSON-LD scripts")

        for script in scripts:
            try:
                data = json.loads(script.string)

                # Handle different structures
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    # Check for @graph structure
                    if '@graph' in data:
                        items = data['@graph']
                    else:
                        items = [data]
                else:
                    continue

                for item in items:
                    if isinstance(item, dict) and item.get('@type') == 'Product':
                        capsule = parse_product(item, line)
                        if capsule:
                            capsules.append(capsule)

            except (json.JSONDecodeError, Exception):
                continue

        print(f"Extracted {len(capsules)} capsules from {line}")

    except Exception as e:
        print(f"Error loading {url}: {e}")

    return capsules


async def main():
    """Main function"""
    all_capsules = []

    # Stealth browser options
    stealth_options = {
        'args': [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
        ]
    }

    async with async_playwright() as p:
        # Launch with stealth settings
        browser = await p.chromium.launch(
            headless=True,
            **stealth_options
        )

        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
        )

        # Add stealth scripts to hide automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = { runtime: {} };
        """)

        page = await context.new_page()

        # Try Original Line
        for url in ORIGINAL_URLS:
            capsules = await scrape_page(page, url, "Original")
            if capsules:
                all_capsules.extend(capsules)
                break
            await asyncio.sleep(2)

        # Try Vertuo Line
        for url in VERTUO_URLS:
            capsules = await scrape_page(page, url, "Vertuo")
            if capsules:
                all_capsules.extend(capsules)
                break
            await asyncio.sleep(2)

        await browser.close()

    # Remove duplicates
    seen = set()
    unique_capsules = []
    for capsule in all_capsules:
        key = (capsule.get('name'), capsule.get('line'), capsule.get('size_ml'))
        if key not in seen:
            seen.add(key)
            unique_capsules.append(capsule)

    print(f"\nTotal unique capsules: {len(unique_capsules)}")

    # Save to file
    if unique_capsules:
        with open('data/capsules.json', 'w', encoding='utf-8') as f:
            json.dump(unique_capsules, f, indent=2, ensure_ascii=False)
        print(f"Saved to data/capsules.json")

        # Print sample
        print("\nSample capsules:")
        for c in unique_capsules[:10]:
            print(f"  - {c['name']} ({c['line']}, {c['size_ml']}ml)")
    else:
        print("No capsules extracted")

    return unique_capsules


if __name__ == "__main__":
    asyncio.run(main())
