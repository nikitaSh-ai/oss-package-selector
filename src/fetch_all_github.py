import time
from fetch_github import fetch_github_data, save_to_db, HEADERS
from package_list import TEST_PACKAGES
import requests


def check_rate_limit():
    """Check remaining GitHub API quota."""
    response = requests.get("https://api.github.com/rate_limit", headers=HEADERS)
    data = response.json()
    remaining = data["resources"]["core"]["remaining"]
    reset_time = data["resources"]["core"]["reset"]
    return remaining, reset_time


def fetch_batch(packages: list):
    for pkg in packages:
        remaining, reset_time = check_rate_limit()
        print(f"[{pkg['name']}] Rate limit remaining: {remaining}")

        if remaining < 10:
            wait_seconds = reset_time - int(time.time()) + 5
            print(f"⚠️ Rate limit low. Waiting {wait_seconds}s for reset...")
            time.sleep(max(wait_seconds, 0))

        try:
            result = fetch_github_data(pkg["repo"])
            if "error" in result:
                print(f"❌ Error fetching {pkg['name']}: {result['error']}")
                continue

            save_to_db(pkg["name"], pkg["category"], result)

        except Exception as e:
            print(f"❌ Unexpected error on {pkg['name']}: {e}")
            continue

        time.sleep(1)  # small courtesy delay between requests


if __name__ == "__main__":
    fetch_batch(TEST_PACKAGES)
    print("\n✅ Batch complete.")