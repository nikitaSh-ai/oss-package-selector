from sklearn.model_selection import train_test_split
from prepare_model_data import load_features, get_X_y


def split_data(X, y, test_size=0.2, random_state=42):
    """
    stratify=y ensures both train and test sets keep the same
    well_maintained/not ratio (~65/35) — important with our moderate
    imbalance, so the test set isn't accidentally skewed.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    df = load_features()
    X, y = get_X_y(df)

    X_train, X_test, y_train, y_test = split_data(X, y)

    print(f"Train set: {X_train.shape[0]} rows")
    print(f"Test set: {X_test.shape[0]} rows")

    print(f"\nTrain label balance: {y_train.mean()*100:.1f}% well-maintained")
    print(f"Test label balance: {y_test.mean()*100:.1f}% well-maintained")