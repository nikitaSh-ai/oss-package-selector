import pandas as pd

def load_features() -> pd.DataFrame:
    return pd.read_csv("data/features.csv")


# Excluded from predictors:
# - package_name, category: identifiers, not features (category could be
#   used later as a categorical feature, but we'll keep the first model
#   simple and category-agnostic)
# - days_since_last_commit: DIRECTLY used to construct the label — including
#   it would cause data leakage (the model could trivially "cheat")
# - well_maintained: this is the target, not a predictor

PREDICTOR_COLS = [
    "repo_age_days",
    "releases_per_year",
    "stars_per_day",
    "contributors_per_year",
    "doc_completeness_score",
    "has_license",
    "weekly_downloads",
    "open_issues",
]
TARGET_COL = "well_maintained"


def get_X_y(df: pd.DataFrame):
    X = df[PREDICTOR_COLS]
    y = df[TARGET_COL]
    return X, y


if __name__ == "__main__":
    df = load_features()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    print("\nMissing values per column:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)

    print("\nValue ranges (min/max) for numeric columns:")
    numeric_cols = df.select_dtypes(include="number").columns
    print(df[numeric_cols].agg(["min", "max"]).T)

    X, y = get_X_y(df)
    print(f"\nPredictor matrix X: {X.shape}")
    print(f"Target vector y: {y.shape}")
    print(f"\nPredictor columns: {list(X.columns)}")