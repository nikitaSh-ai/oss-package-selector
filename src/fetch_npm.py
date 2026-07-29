import requests

import sqlite3
from datetime import datetime, timezone



def extract_github_repo(npm_json: dict) -> str:
    """
    Extract 'owner/repo' from npm's registry repository field.
    Returns None if not a GitHub repo or field is missing/malformed.
    """
    repo_info = npm_json.get("repository")
    if not repo_info:
        return None

    url = repo_info.get("url") if isinstance(repo_info, dict) else repo_info
    if not url or "github.com" not in url:
        return None

    # Normalize: strip git+, .git, trailing slashes, protocol prefixes
    url = url.replace("git+", "").replace(".git", "").rstrip("/")
    url = url.split("github.com/")[-1]
    # url = url.split("github.com:")[-1]  # handles git@github.com: format too
    if "github.com:" in repo_info.get("url", "") if isinstance(repo_info, dict) else str(repo_info):
        pass  # already handled by split above in most cases

    return url if url.count("/") == 1 else None




def save_npm_to_db(package_name: str, category: str, npm_data: dict):
    conn = sqlite3.connect("data/raw_packages.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO packages (
            package_name, category, latest_version, weekly_downloads,
            dependents_count, is_deprecated, last_publish_date, num_versions,
            fetch_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(package_name) DO UPDATE SET
            latest_version=excluded.latest_version,
            weekly_downloads=excluded.weekly_downloads,
            dependents_count=excluded.dependents_count,
            is_deprecated=excluded.is_deprecated,
            last_publish_date=excluded.last_publish_date,
            num_versions=excluded.num_versions,
            fetch_date=excluded.fetch_date
    """, (
        package_name, category,
        npm_data.get("latest_version"),
        npm_data.get("weekly_downloads"),
        npm_data.get("dependents_count"),
        int(npm_data.get("is_deprecated")) if npm_data.get("is_deprecated") is not None else None,
        npm_data.get("last_publish_date"),
        npm_data.get("num_versions"),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()
    print(f"✅ Saved/updated {package_name} npm data")






def fetch_dependents_count(package_name: str) -> None:
    """
    NOTE: No reliable source found for this metric.
    - npm registry: no official API for this (confirmed via npm's own
      GitHub issue tracker — feature requested since 2017, never shipped).
    - npmjs.com website: blocked by Cloudflare bot protection (403).
    - npms.io aggregator: data is stale (last analyzed ~2022), field
      not present in current API response.
    Documented as a known limitation. Always returns None.
    """
    return None





def fetch_weekly_downloads(package_name: str) -> int:
    url = f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json().get("downloads")



def fetch_npm_data(package_name: str) -> dict:
    """
    Fetch key metadata for an npm package.
    """
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Status {response.status_code}: {response.text}"}

    data = response.json()

    latest_version = data.get("dist-tags", {}).get("latest")
    latest_version_data = data.get("versions", {}).get(latest_version, {})

    return {
        "latest_version": latest_version,
        "is_deprecated": bool(latest_version_data.get("deprecated")),
        "last_publish_date": data.get("time", {}).get(latest_version) if latest_version else None,
        "num_versions": len(data.get("versions", {})),
        "weekly_downloads": fetch_weekly_downloads(package_name),
        "dependents_count": fetch_dependents_count(package_name),
        "github_repo": extract_github_repo(data),
    }






if __name__ == "__main__":
    result = fetch_npm_data("axios")
    for key, value in result.items():
        print(f"{key}: {value}")

    save_npm_to_db("axios", result)