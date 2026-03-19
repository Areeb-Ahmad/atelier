import requests
import time

def get_mondrian_ready_links(count=10):
    api_url = "https://commons.wikimedia.org/w/api.php"
    valid_links = []
    
    # User-Agent is required by Wikimedia policy
    headers = {'User-Agent': 'MondrianStudioBot/1.0 (contact: your@email.com)'}
    
    print(f"🚀 Starting high-speed fetch for {count} images...")

    while len(valid_links) < count:
        # Step 1: Get 10 random files at once to save on "trips" to the server
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnnamespace": 6,
            "rnlimit": 10 
        }
        
        try:
            r = requests.get(api_url, params=params, headers=headers).json()
            random_files = r['query']['random']
            
            for file in random_files:
                title = file['title']
                
                # OPTIMIZATION: Skip non-images before even asking for the URL
                if not title.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    continue

                # Step 2: Get the direct URL
                info_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "imageinfo",
                    "titles": title,
                    "iiprop": "url"
                }
                img_r = requests.get(api_url, params=info_params, headers=headers).json()
                
                pages = img_r['query']['pages']
                for p in pages:
                    if 'imageinfo' in pages[p]:
                        direct_url = pages[p]['imageinfo'][0]['url']
                        valid_links.append(direct_url)
                        print(f"✅ [{len(valid_links)}/{count}] {title}")
                
                # Stop immediately if we hit our target
                if len(valid_links) >= count: break

        except Exception as e:
            print(f"⚠️ Minor skip: {e}")
            continue

    return valid_links

# RUN IT
target_count = 1000000
links = get_mondrian_ready_links(target_count)

with open("mondrian_links.txt", "w") as f:
    for link in links:
        f.write(link + "\n")
