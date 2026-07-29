import requests

import sqlite3


def save_npm_to_db(package_name: str, npm_data: dict):
    conn = sqlite3.connect("data/raw_packages.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE packages
        SET latest_version = ?,
            weekly_downloads = ?,
            dependents_count = ?,
            is_deprecated = ?,
            last_publish_date = ?,
            num_versions = ?
        WHERE package_name = ?
    """, (
        npm_data.get("latest_version"),
        npm_data.get("weekly_downloads"),
        npm_data.get("dependents_count"),
        int(npm_data.get("is_deprecated")) if npm_data.get("is_deprecated") is not None else None,
        npm_data.get("last_publish_date"),
        npm_data.get("num_versions"),
        package_name
    ))

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected == 0:
        print(f"⚠️ No existing row for {package_name} — GitHub fetch must run first.")
    else:
        print(f"✅ Updated {package_name} with npm data")


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
    }





if __name__ == "__main__":
    result = fetch_npm_data("axios")
    for key, value in result.items():
        print(f"{key}: {value}")

    save_npm_to_db("axios", result)