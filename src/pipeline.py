import time
from fetch_github import fetch_github_data, save_to_db, HEADERS
from fetch_npm import fetch_npm_data, save_npm_to_db
from package_list import TEST_PACKAGES
import requests


def check_rate_limit():
    response = requests.get("https://api.github.com/rate_limit", headers=HEADERS)
    data = response.json()
    remaining = data["resources"]["core"]["remaining"]
    reset_time = data["resources"]["core"]["reset"]
    return remaining, reset_time


def process_package(name: str, category: str):
    """
    Fetch npm data first (to derive the GitHub repo), then GitHub data.
    Handles partial failures gracefully.
    """
    errors = []
    github_repo = None

    # --- npm (first, to get repo info) ---
    try:
        npm_result = fetch_npm_data(name)
        if "error" in npm_result:
            errors.append(f"npm: {npm_result['error']}")
        else:
            github_repo = npm_result.get("github_repo")
            save_npm_to_db(name, category, npm_result)
    except Exception as e:
        errors.append(f"npm exception: {e}")

    # --- GitHub (using derived repo) ---
    if github_repo:
        remaining, reset_time = check_rate_limit()
        if remaining < 10:
            wait_seconds = reset_time - int(time.time()) + 5
            print(f"⚠️ Rate limit low. Waiting {wait_seconds}s...")
            time.sleep(max(wait_seconds, 0))

        try:
            github_result = fetch_github_data(github_repo)
            if "error" in github_result:
                errors.append(f"GitHub: {github_result['error']}")
            else:
                save_to_db(name, category, github_result)
        except Exception as e:
            errors.append(f"GitHub exception: {e}")
    else:
        errors.append("No GitHub repo found in npm metadata")

    if errors:
        print(f"⚠️ {name} completed with issues: {'; '.join(errors)}")
    else:
        print(f"✅ {name} fully processed")

    time.sleep(1)



def run_pipeline(packages: list):
    for pkg in packages:
        process_package(pkg["name"], pkg["category"])
    print("\n✅ Pipeline run complete.")

    
if __name__ == "__main__":
    run_pipeline(TEST_PACKAGES)