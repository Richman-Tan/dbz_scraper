import json
from utils.scraper_utils import fetch_html, parse_sets, parse_cards, get_pagination_urls

# Base URL
BASE_URL = "https://dbzoutpost.com/pages/score"

# Output files
SETS_JSON = "data/sets.json"
CARDS_JSON = "data/cards.json"

def main():
    # Step 1: Fetch HTML of the main page
    html_content = fetch_html(BASE_URL)
    
    # Step 2: Parse sets
    sets = parse_sets(html_content)
    print(f"Found {len(sets)} sets.")
    
    # Save sets to JSON
    with open(SETS_JSON, "w") as sets_file:
        json.dump(sets, sets_file, indent=4)
    print(f"Sets saved to {SETS_JSON}")
    
    # Step 3: Parse cards for each set, including paginated pages
    cards = []
    for set_data in sets:
        print(f"Processing set: {set_data['setName']}")
        
        # Get all pagination URLs for the current set
        pagination_urls = get_pagination_urls(set_data['setUrl'])
        print(f"Found {len(pagination_urls)} pages for set: {set_data['setName']}")
        
        for page_url in pagination_urls:
            print(f"Processing page: {page_url}")
            page_html = fetch_html(page_url)
            set_cards = parse_cards(page_html, set_data['setId'])
            cards.extend(set_cards)
    
    # Save cards to JSON
    with open(CARDS_JSON, "w") as cards_file:
        json.dump(cards, cards_file, indent=4)
    print(f"Cards saved to {CARDS_JSON}")

if __name__ == "__main__":
    main()
