import os
import requests
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

if not token:
    print("❌ No token found! Check your .env file.")
else:
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Auth successful! Logged in as: {data['login']}")
    else:
        print(f"❌ Auth failed. Status code: {response.status_code}")
        print(response.text)