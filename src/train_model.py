from sklearn.model_selection import train_test_split
from prepare_model_data import load_features, get_X_y
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


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






def train_baseline_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=100,   # number of trees — 100 is a solid default
        random_state=42,    # reproducibility
        class_weight="balanced",  # accounts for our 65/35 imbalance
    )
    model.fit(X_train, y_train)
    return model







def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    print("\nConfusion Matrix:")
    print("(rows = actual, columns = predicted)")
    cm = confusion_matrix(y_test, y_pred)
    print(f"                 Predicted: Less Reliable   Predicted: Well-Maintained")
    print(f"Actual: Less Reliable      {cm[0][0]:>18}   {cm[0][1]:>25}")
    print(f"Actual: Well-Maintained    {cm[1][0]:>18}   {cm[1][1]:>25}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Less Reliable", "Well-Maintained"]))





if __name__ == "__main__":
    df = load_features()
    X, y = get_X_y(df)

    X_train, X_test, y_train, y_test = split_data(X, y)

    print(f"Train set: {X_train.shape[0]} rows")
    print(f"Test set: {X_test.shape[0]} rows")

    print(f"\nTrain label balance: {y_train.mean()*100:.1f}% well-maintained")
    print(f"Test label balance: {y_test.mean()*100:.1f}% well-maintained")

    model = train_baseline_model(X_train, y_train)
    print(f"\n✅ Model trained on {X_train.shape[0]} rows with {X_train.shape[1]} features")

    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    print(f"\nTrain accuracy: {train_accuracy:.3f}")
    print(f"Test accuracy: {test_accuracy:.3f}")


    evaluate_model(model, X_test, y_test)