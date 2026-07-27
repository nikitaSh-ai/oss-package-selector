import requests

# Test call: fetch metadata for a well-known package (axios)
response = requests.get("https://registry.npmjs.org/axios")

if response.status_code == 200:
    data = response.json()
    print(f"✅ npm call successful! Package: {data['name']}")
    print(f"   Latest version: {data['dist-tags']['latest']}")
else:
    print(f"❌ npm call failed. Status code: {response.status_code}")