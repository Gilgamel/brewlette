"""
Nespresso Capsule Scraper using Markdown conversion approach
Similar to Firecrawl - convert page to Markdown, then extract data
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import html2text
import time

# Nespresso URLs to try
URLS = [
    "https://www.nespresso.com/ca/en/order/capsules/original",
    "https://www.nespresso.com/us/en/order/capsules/original",
    "https://www.nespresso.com/ca/en/order/capsules/vertuo",
    "https://www.nespresso.com/us/en/order/capsules/vertuo",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def html_to_markdown(html_content: str) -> str:
    """Convert HTML to Markdown using html2text"""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines

    markdown = h.handle(html_content)
    return markdown


def extract_capsules_from_markdown(markdown: str, line: str) -> list:
    """Extract capsule information from Markdown"""
    capsules = []

    # Patterns to find capsule info in markdown
    # Look for product names, descriptions, intensities, sizes

    # Split by lines
    lines = markdown.split('\n')

    for line_text in lines:
        line_text = line_text.strip()

        # Look for capsule-like entries
        # Patterns: name followed by intensity, size, description

        # Intensity pattern (e.g., "Intensity 9", "9/13")
        intensity_match = re.search(r'(\d+)\s*(?:/13)?\s*(?:intensity)?', line_text, re.IGNORECASE)

        # Size pattern (e.g., "40ml", "150 ml")
        size_match = re.search(r'(\d+)\s*ml', line_text, re.IGNORECASE)

        # Skip if too short or looks like navigation
        if len(line_text) < 5:
            continue

        # Skip navigation/UI elements
        skip_words = ['home', 'cart', 'search', 'menu', 'account', 'login', 'sign in', 'skip']
        if any(word in line_text.lower() for word in skip_words):
            continue

    return capsules


def scrape_with_markdown():
    """Main scraping function using markdown conversion"""
    all_capsules = []

    for url in URLS:
        print(f"\n{'='*50}")
        print(f"Scraping: {url}")
        print('='*50)

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                # Convert to Markdown
                markdown = html_to_markdown(response.text)
                print(f"Markdown length: {len(markdown)} chars")

                # Save markdown for inspection
                line = "Original" if "original" in url.lower() else "Vertuo"
                filename = f"nespresso_{line.lower()}_.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"Saved to {filename}")

                # Try to extract capsules
                capsules = extract_capsules_from_markdown(markdown, line)
                print(f"Extracted {len(capsules)} capsules")
                all_capsules.extend(capsules)

            else:
                print(f"Failed with status: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(2)  # Be polite

    return all_capsules


def try_alternative_extraction():
    """
    Alternative: Try to extract data from the structured data in the page
    Many modern sites embed JSON-LD or similar structured data
    """
    print("\n" + "="*50)
    print("Trying alternative extraction method...")
    print("="*50)

    capsules = []

    # Try different URLs
    for url in URLS:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for application/ld+json scripts
                scripts = soup.find_all('script', type='application/ld+json')

                for script in scripts:
                    try:
                        data = json.loads(script.string)

                        # Handle different data structures
                        if isinstance(data, list):
                            items = data
                        elif isinstance(data, dict):
                            items = [data]
                        else:
                            continue

                        for item in items:
                            if item.get('@type') == 'Product':
                                capsule = parse_product(item)
                                if capsule:
                                    capsules.append(capsule)

                        if capsules:
                            print(f"Found {len(capsules)} capsules!")
                            break

                    except json.JSONDecodeError:
                        continue

                if capsules:
                    break

        except Exception as e:
            print(f"Error: {e}")

    return capsules


def parse_product(product: dict) -> dict:
    """Parse a product from JSON-LD data"""
    try:
        name = product.get('name', '')
        if not name:
            return None

        # Skip non-capsule products
        name_lower = name.lower()
        if any(word in name_lower for word in ['machine', 'brewer', 'accessory', 'gift', 'bundle']):
            return None

        description = product.get('description', '')

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

        # Extract intensity from description or name
        intensity = None
        int_match = re.search(r'intensity[:\s]*(\d+)', description, re.IGNORECASE)
        if int_match:
            intensity = int(int_match.group(1))

        if not intensity:
            int_match = re.search(r'(\d+)\s*/\s*13', description)
            if int_match:
                intensity = int(int_match.group(1))

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

        # Determine line (Original or Vertuo)
        line = "Original"  # Default, would need URL context

        return {
            "name": name,
            "name_en": name,
            "tasting_note": description[:200] if description else "",
            "tasting_note_en": description[:200] if description else "",
            "size_ml": size_ml,
            "pod_type": pod_type,
            "line": line,
            "intensity": intensity
        }

    except Exception as e:
        print(f"Error parsing product: {e}")
        return None


def save_capsules(capsules: list, filename: str = "capsules_output.json"):
    """Save capsules to JSON file"""
    # Remove duplicates
    seen = set()
    unique_capsules = []

    for capsule in capsules:
        key = (capsule.get('name'), capsule.get('line'), capsule.get('size_ml'))
        if key not in seen:
            seen.add(key)
            unique_capsules.append(capsule)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(unique_capsules, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(unique_capsules)} unique capsules to {filename}")
    return unique_capsules


if __name__ == "__main__":
    print("Nespresso Capsule Scraper - Markdown Approach")
    print("="*50)

    # First try markdown conversion
    capsules = scrape_with_markdown()

    # If that didn't work well, try alternative
    if len(capsules) < 10:
        capsules = try_alternative_extraction()

    # Save results
    if capsules:
        save_capsules(capsules)
    else:
        print("\nNo capsules extracted. Check the .md files for content.")
