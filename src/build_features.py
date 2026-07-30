import sqlite3
import pandas as pd

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


if __name__ == "__main__":
    df = load_raw_data()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    df = clean_data(df)
    print(f"\nFinal dataset shape: {df.shape}")
    print(f"\nCategory distribution:")
    print(df["category"].value_counts())