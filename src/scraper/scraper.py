import time
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_google_maps():
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Headless=False so we can see what's happening
        page = browser.new_page()
        page.goto("https://www.google.com/maps/search/Restoran+di+Semarang")
        
        print("Waiting for results to load...")
        page.wait_for_selector('div[role="feed"]', timeout=20000)
        time.sleep(3) # Wait a bit for initial items to fully render
        
        print("Scrolling the feed to load all items. This might take a few minutes...")
        # Scroll continuously until we hit the end of the list.
        previous_count = 0
        stuck_count = 0
        scroll_attempts = 0
        while True:
            scroll_attempts += 1
            page.evaluate('''(document.querySelector('div[role="feed"]') || document.body).scrollBy(0, 5000)''')
            time.sleep(2)
            
            # Check if new items are actually loading
            current_count = len(page.query_selector_all('div[role="article"]'))
            if current_count == previous_count:
                stuck_count += 1
                if stuck_count >= 3:
                    print(f"Reached the end of the list after {scroll_attempts} scrolls.")
                    break
            else:
                stuck_count = 0
            
            previous_count = current_count
        
        print("Extracting data...")
        # A common selector for individual result cards in the feed is 'a' tags with specific aria labels or roles
        # In current Google Maps, result items usually have role="article" or similar.
        items = page.query_selector_all('div[role="article"]')
        
        if not items:
            print("Could not find items using 'div[role=\"article\"]'. Trying generic 'a' tags inside the feed.")
            items = page.query_selector_all('div[role="feed"] > div > div > a')
            
        print(f"Found {len(items)} items to process.")
        
        for item in items:
            try:
                name = item.get_attribute('aria-label')
                
                # We can also attempt to get text content to find rating, reviews, etc.
                text_content = item.inner_text()
                
                if not name and text_content:
                    # Fallback to the first line of the text content, which is usually the name
                    name = text_content.split('\n')[0].strip()
                
                # Basic parsing based on common text structure (might need adjustment based on exact DOM)
                rating = None
                reviews = None
                if text_content:
                    lines = text_content.split('\n')
                    for line in lines:
                        if '(' in line and ')' in line and ('.' in line or ',' in line):
                            # Usually looks like "4.5(1,234)" or "4.5 (1,234)"
                            rating_part = line.split('(')[0].strip()
                            reviews_part = line.split('(')[1].split(')')[0].strip()
                            rating = rating_part
                            reviews = reviews_part
                            break

                if name:
                    data.append({
                        "Name": name,
                        "Rating": rating,
                        "Reviews": reviews,
                        "Raw Content": text_content.replace('\n', ' ') if text_content else None
                    })
                else:
                    print("Skipping item because name could not be found.")
            except Exception as e:
                print(f"Error parsing an item: {e}")
                
        browser.close()
        
    return data

if __name__ == "__main__":
    print("Starting scraper...")
    scraped_data = scrape_google_maps()
    
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        import os
        os.makedirs("../../data/raw", exist_ok=True)
        output_file = "../../data/raw/restaurants_semarang.csv"
        df.to_csv(output_file, index=False)
        print(f"Successfully scraped {len(scraped_data)} restaurants and saved to {output_file}")
    else:
        print("No data scraped.")
