import sqlite3
import os

DB_PATH = os.path.join("data", "raw_packages.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            package_name TEXT PRIMARY KEY,
            category TEXT,
            repo_url TEXT,
            stars INTEGER,
            forks INTEGER,
            open_issues INTEGER,
            last_commit_date TEXT,
            created_at TEXT,
            contributor_count INTEGER,
            has_readme INTEGER,
            has_wiki INTEGER,
            license TEXT,
            default_branch TEXT,
            latest_version TEXT,
            weekly_downloads INTEGER,
            dependents_count INTEGER,
            is_deprecated INTEGER,
            last_publish_date TEXT,
            num_versions INTEGER,
            fetch_date TEXT,
            fetch_errors TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()