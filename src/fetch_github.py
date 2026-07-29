import os
import requests

import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}





def check_has_readme(repo_full_name: str) -> bool:
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    response = requests.get(url, headers=HEADERS)
    return response.status_code == 200




def fetch_github_data(repo_full_name: str) -> dict:
    """
    Fetch key metadata for a GitHub repo.
    repo_full_name example: 'axios/axios'
    """
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": f"Status {response.status_code}: {response.text}"}

    data = response.json()

    # Contributor count needs a separate API call
    contributors_url = f"https://api.github.com/repos/{repo_full_name}/contributors?per_page=1&anon=true"
    contrib_response = requests.get(contributors_url, headers=HEADERS)
    # GitHub returns pagination info in headers; last page number = total count (rough estimate)
    contributor_count = None
    if contrib_response.status_code == 200:
        if "Link" in contrib_response.headers:
            # crude parse: last page number in Link header
            links = contrib_response.headers["Link"]
            try:
                last_page = links.split('page=')[-1].split('>')[0]
                contributor_count = int(last_page)
            except Exception:
                contributor_count = len(contrib_response.json())
        else:
            contributor_count = len(contrib_response.json())

    return {
        "repo_url": data.get("html_url"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "last_commit_date": data.get("pushed_at"),
        "created_at": data.get("created_at"),
        "contributor_count": contributor_count,
        "has_readme": check_has_readme(repo_full_name),
        "has_wiki": data.get("has_wiki"),
        "license": data.get("license", {}).get("name") if data.get("license") else None,
        "default_branch": data.get("default_branch"),
    }








def save_to_db(package_name: str, category: str, github_data: dict):
    conn = sqlite3.connect(os.path.join("data", "raw_packages.db"))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO packages (
            package_name, category, repo_url, stars, forks, open_issues,
            last_commit_date, created_at, contributor_count, has_readme,
            has_wiki, license, default_branch, fetch_date, fetch_errors
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(package_name) DO UPDATE SET
            category=excluded.category,
            repo_url=excluded.repo_url,
            stars=excluded.stars,
            forks=excluded.forks,
            open_issues=excluded.open_issues,
            last_commit_date=excluded.last_commit_date,
            created_at=excluded.created_at,
            contributor_count=excluded.contributor_count,
            has_readme=excluded.has_readme,
            has_wiki=excluded.has_wiki,
            license=excluded.license,
            default_branch=excluded.default_branch,
            fetch_date=excluded.fetch_date,
            fetch_errors=excluded.fetch_errors
    """, (
        package_name, category, github_data.get("repo_url"),
        github_data.get("stars"), github_data.get("forks"),
        github_data.get("open_issues"), github_data.get("last_commit_date"),
        github_data.get("created_at"), github_data.get("contributor_count"),
        int(github_data.get("has_readme")) if github_data.get("has_readme") is not None else None,
        int(github_data.get("has_wiki")) if github_data.get("has_wiki") is not None else None,
        github_data.get("license"), github_data.get("default_branch"),
        datetime.now(timezone.utc).isoformat(),
        github_data.get("error")
    ))

    conn.commit()
    conn.close()
    print(f"✅ Saved {package_name} to database")






if __name__ == "__main__":
    result = fetch_github_data("axios/axios")
    for key, value in result.items():
        print(f"{key}: {value}")

    save_to_db("axios", "HTTP clients", result)