import requests
from concurrent.futures import ThreadPoolExecutor

def get_mondrian_ready_links(count=100):
    api_url = "https://commons.wikimedia.org/w/api.php"
    valid_links = []
    headers = {'User-Agent': 'MondrianStudioBot/1.0 (contact: your@email.com)'}
    
    # Use a Session for connection pooling (much faster for multiple requests)
    session = requests.Session()
    session.headers.update(headers)

    print(f"🚀 Launching multi-threaded fetch for {count} images...")

    while len(valid_links) < count:
        # Step 1: Bulk fetch random image titles (up to 500 at once)
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnnamespace": 6,
            "rnlimit": 50  # Max for non-bots is usually 50
        }
        
        try:
            r = session.get(api_url, params=params).json()
            # Filter for images locally to save API calls
            titles = [
                f['title'] for f in r['query']['random'] 
                if f['title'].lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            ]

            if not titles: continue

            # Step 2: Batch query the URLs (The API supports up to 50 titles at once!)
            # This replaces the inner loop and saves dozens of round-trips
            info_params = {
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "titles": "|".join(titles), # Pipe-separated titles for batching
                "iiprop": "url"
            }
            
            img_r = session.get(api_url, params=info_params).json()
            pages = img_r.get('query', {}).get('pages', {})

            for page_id in pages:
                if 'imageinfo' in pages[page_id]:
                    url = pages[page_id]['imageinfo'][0]['url']
                    valid_links.append(url)
                    if len(valid_links) >= count: break

            print(f"✅ Collected {len(valid_links)}/{count}...")

        except Exception as e:
            print(f"⚠️ Connection blip: {e}")

    return valid_links[:count]

# Execution
target_count = 1000
links = get_mondrian_ready_links(target_count)

with open("testURLS.txt", "w") as f:
    f.write("\n".join(links))

print("🏁 Done!")