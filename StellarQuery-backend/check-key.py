import os
import httpx
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Check if the key was loaded
if not api_key:
    print("❌ ERROR: OPENROUTER_API_KEY not found in .env file.")
    exit()

# Prepare request
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "anthropic/claude-3-sonnet",
    "max_tokens":400,
    "messages": [
        {"role": "user", "content": "Hello! Can you confirm if you're working?"}
    ]
}

# Send test request
try:
    response = httpx.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    print("✅ OpenRouter API key is working!")
    print("\n🤖 Claude says:\n", result['choices'][0]['message']['content'])
except httpx.HTTPStatusError as e:
    print(f"❌ API Error: HTTP {e.response.status_code}")
    print(e.response.text)
except Exception as e:
    print(f"❌ General Error: {str(e)}")
