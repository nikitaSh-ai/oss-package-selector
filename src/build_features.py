import sqlite3
import pandas as pd
from datetime import datetime, timezone

def load_raw_data() -> pd.DataFrame:
    conn = sqlite3.connect("data/raw_packages.db")
    df = pd.read_sql_query("SELECT * FROM packages", conn)
    conn.close()
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows with complete GitHub data (required for feature engineering)."""
    before = len(df)
    df = df[df["stars"].notna()].copy()
    after = len(df)
    print(f"Dropped {before - after} rows with missing GitHub data ({after} remain)")
    return df




def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive repo age and recency features from raw date columns."""
    now = datetime.now(timezone.utc)

    created = pd.to_datetime(df["created_at"], utc=True)
    last_commit = pd.to_datetime(df["last_commit_date"], utc=True)

    df["repo_age_days"] = (now - created).dt.days
    df["days_since_last_commit"] = (now - last_commit).dt.days

    return df




if __name__ == "__main__":
    df = load_raw_data()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    df = clean_data(df)
    df = add_time_features(df)

    print("\nSample of new features:")
    print(df[["package_name", "repo_age_days", "days_since_last_commit"]].head(10))

    print("\nSummary stats:")
    print(df[["repo_age_days", "days_since_last_commit"]].describe())