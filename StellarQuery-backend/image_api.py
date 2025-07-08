import requests
import re

def extract_keyword(text: str):
    """
    Naive rule-based cleaner to extract object name from natural language.
    Example: 'Show me an image of the sun' -> 'sun'
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    stopwords = {"show", "me", "an", "a", "of", "the", "image", "please", "give", "picture", "photo", "send"}
    keywords = [word for word in text.split() if word not in stopwords]
    return " ".join(keywords) if keywords else text.strip()

def fetch_image(q: str):
    """Search NASA Image API for a Solar System object (cleaned query)."""
    keyword = extract_keyword(q)
    print(f"🔍 Cleaned search term: {keyword}")

    url = "https://images-api.nasa.gov/search"
    params = {
        "q": keyword,
        "media_type": "image",
        "year_start": "1900",
        "page": 1
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"❌ NASA image API failed: {e}")
        return None

    items = data.get("collection", {}).get("items", [])
    print(f"🔍 Found {len(items)} items for '{keyword}'")

    for item in items:
        try:
            image_data = item.get("data", [{}])[0]
            links = item.get("links", [])
            image_url = links[0].get("href") if links else None

            if image_url and image_url.startswith("https://"):
                check = requests.get(image_url, timeout=5)
                if check.status_code == 200:
                    return {
                        "title": image_data.get("title", "Untitled"),
                        "description": image_data.get("description", ""),
                        "date_created": image_data.get("date_created", ""),
                        "url": image_url
                    }
        except Exception as e:
            print(f"⚠️ Skipping item: {e}")
            continue

    print("⚠️ No valid image found.")
    return None
