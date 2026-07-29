import requests
import json

url = "https://api.npms.io/v2/package/axios"
response = requests.get(url, timeout=10)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    npm_section = data.get("collected", {}).get("npm", {})
    print("Keys under collected.npm:", list(npm_section.keys()))
    print("\nFull npm section:")
    print(json.dumps(npm_section, indent=2))
else:
    print("Response text:", response.text[:500])