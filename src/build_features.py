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




def add_activity_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw counts by repo age, so older repos aren't unfairly
    advantaged just for having more accumulated history.

    A minimum age floor (90 days) is applied to the denominator only,
    to prevent very young repos from producing extreme, noisy rates
    (e.g., a 10-day-old repo with 5 contributors would otherwise show
    ~180 contributors/year, which is not a meaningful signal).
    """
    MIN_AGE_DAYS = 90
    safe_age_days = df["repo_age_days"].clip(lower=MIN_AGE_DAYS)
    age_years = safe_age_days / 365.25

    df["releases_per_year"] = df["num_versions"] / age_years
    df["stars_per_day"] = df["stars"] / safe_age_days
    df["contributors_per_year"] = df["contributor_count"] / age_years

    return df




def winsorize_features(df: pd.DataFrame, columns: list, upper_percentile: float = 0.95) -> pd.DataFrame:
    """
    Cap extreme outliers at the given percentile to prevent a small
    number of anomalous packages (e.g., bot-driven publishing) from
    dominating downstream model training. Applied only to the upper
    tail, since unusually LOW activity is a genuine, meaningful signal
    we want to preserve (that's literally what 'less reliable' looks like).
    """
    for col in columns:
        cap = df[col].quantile(upper_percentile)
        df[col] = df[col].clip(upper=cap)
    return df





def add_documentation_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple documentation/trust signals:
    - doc_completeness_score: 0, 1, or 2 (has_readme + has_wiki)
    - has_license: whether a license is declared at all (separate from
      which license — that's a categorical detail we're not modeling)
    """
    df["doc_completeness_score"] = df["has_readme"].fillna(0) + df["has_wiki"].fillna(0)
    df["has_license"] = df["license"].notna().astype(int)

    return df






if __name__ == "__main__":
    df = load_raw_data()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    df = clean_data(df)
    df = add_time_features(df)
    df = add_activity_features(df)

    normalized_cols = ["releases_per_year", "stars_per_day", "contributors_per_year"]
    df = winsorize_features(df, normalized_cols)

    df = add_documentation_features(df)

    print("\nFinal engineered feature columns:")
    feature_cols = [
        "package_name", "category",
        "repo_age_days", "days_since_last_commit",
        "releases_per_year", "stars_per_day", "contributors_per_year",
        "doc_completeness_score", "has_license",
        "is_deprecated", "weekly_downloads", "open_issues"
    ]
    print(df[feature_cols].head())

    df[feature_cols].to_csv("data/features.csv", index=False)
    print(f"\n✅ Saved {len(df)} rows with {len(feature_cols)} columns to data/features.csv")