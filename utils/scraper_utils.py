from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dbzoutpost.com"

def fetch_html(url):
    """
    Fetch the HTML content of a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def parse_sets(html_content):
    """
    Parse sets from the main page HTML content, including set names, URLs, and images.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    sets = []
    
    set_elements = soup.find_all("div", class_="grid-item small--one-half one-quarter")

    for idx, element in enumerate(set_elements):
        try:
            set_name_tag = element.find("span", class_="featured-box--title")
            set_name = set_name_tag.text.strip() if set_name_tag else f"Set {idx + 1}"

            # Extract set URL
            set_url_tag = element.find("a")
            raw_url = set_url_tag["href"] if set_url_tag else None
            set_url = urljoin(BASE_URL, raw_url) if raw_url else "URL not found"
            
            img_tag = element.find("img")
            if img_tag and "data-src" in img_tag.attrs:
                base_img_url = img_tag["data-src"]
                img_url = base_img_url.replace("{width}", "360")
                img_url = urljoin(BASE_URL, img_url)  # Convert relative URL to absolute
            else:
                img_url = "Image not found"

            # Generate set ID
            set_id = f"set-{idx + 1}"

            # Append the parsed set data
            sets.append({
                "setId": set_id,
                "setName": set_name,
                "setUrl": set_url,
                "setImage": img_url,
            })
        except Exception as e:
            print(f"Error parsing set at index {idx}: {e}")
    
    return sets

def get_pagination_urls(initial_url):
    """
    Fetch all pagination URLs for a given set.
    """
    pagination_urls = [initial_url]
    html_content = fetch_html(initial_url)
    soup = BeautifulSoup(html_content, "html.parser")

    pagination_elements = soup.select("ul.pagination-custom a")
    for element in pagination_elements:
        raw_url = element.get("href")
        if raw_url:
            full_url = urljoin(BASE_URL, raw_url)
            if full_url not in pagination_urls:
                pagination_urls.append(full_url)

    return pagination_urls

def parse_cards(html_content, set_id):
    """
    Parse cards from a set page's HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cards = []
    
    # Locate card containers (adjust the class to match the card's parent div)
    card_elements = soup.find_all("div", class_="grid-item small--one-half medium--one-fifth large--one-fifth")

    for element in card_elements:
        try:
            card_name_tag = element.find("p")
            card_name = card_name_tag.text.strip() if card_name_tag else "Unknown Card"

            card_url_tag = element.find("a", class_="product-grid-item")
            raw_card_url = card_url_tag["href"] if card_url_tag else None
            card_url = urljoin(BASE_URL, raw_card_url) if raw_card_url else None

            rarity, card_image, market_price = fetch_card_details(card_url) if card_url else ("Unknown Rarity", "Image not found", "Price not available")
            
            cards.append({
                "cardName": card_name,
                "cardImage": card_image,
                "cardSetId": set_id,
                "marketPrice": market_price,
                "rarityName": rarity,
            })
        except Exception as e:
            print(f"Error parsing card: {e}") 
    
    return cards

def fetch_card_details(card_url):
    """
    Fetch the rarity, image, and price of a card by scraping its individual page.
    """
    try:
        response = requests.get(card_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            rarity_tag = soup.find("small", string="Rarity:")
            rarity = rarity_tag.next_sibling.strip() if rarity_tag else "Unknown Rarity"
            
            img_tag = soup.find("img", id=True)
            card_image = img_tag["src"] if img_tag and "src" in img_tag.attrs else "Image not found"
            card_image = urljoin(BASE_URL, card_image)
            
            price_tag = soup.find("span", class_="visually-hidden")
            market_price = price_tag.text.strip("$").strip() if price_tag else "Price not available"

            return rarity, card_image, market_price
        return "Unknown Rarity", "Image not found", "Price not available"
    except Exception as e:
        print(f"Error fetching card details from {card_url}: {e}")
        return "Unknown Rarity", "Image not found", "Price not available"

def scrape_all_sets(base_url):
    """
    Scrape all sets and their cards across paginated pages.
    """
    html_content = fetch_html(base_url)
    sets = parse_sets(html_content)
    all_cards = []

    for set_data in sets:
        set_id = set_data["setId"]
        set_url = set_data["setUrl"]
        pagination_urls = get_pagination_urls(set_url)
        
        for page_url in pagination_urls:
            page_html = fetch_html(page_url)
            cards = parse_cards(page_html, set_id)
            all_cards.extend(cards)
    
    return all_cards

# Usage
BASE_URL = "https://dbzoutpost.com"
home_html = fetch_html(BASE_URL)
all_cards = scrape_all_sets(BASE_URL)
print(all_cards)