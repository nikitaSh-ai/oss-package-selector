from sklearn.model_selection import train_test_split
from prepare_model_data import load_features, get_X_y
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier




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











def run_cross_validation(model, X, y, n_folds=5):
    """
    StratifiedKFold (not plain KFold) keeps the ~65/35 class balance
    consistent across all 5 folds — same reasoning as our stratified
    train/test split.
    """
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")

    print(f"\n5-Fold Cross-Validation Accuracy:")
    print(f"  Individual folds: {[f'{s:.3f}' for s in scores]}")
    print(f"  Mean: {scores.mean():.3f}")
    print(f"  Std:  {scores.std():.3f}")









def tune_model(X_train, y_train):
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [4, 6, 8, None],
        "min_samples_leaf": [1, 3, 5],
    }

    base_model = RandomForestClassifier(random_state=42, class_weight="balanced")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        base_model, param_grid, cv=cv, scoring="accuracy", n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    print(f"\nBest parameters: {grid_search.best_params_}")
    print(f"Best CV accuracy: {grid_search.best_score_:.3f}")

    return grid_search.best_estimator_






def show_feature_importance(model, feature_names):
    importances = model.feature_importances_
    ranked = sorted(zip(feature_names, importances), key=lambda x: -x[1])

    print("\nFeature Importance (built-in, Gini-based):")
    for name, score in ranked:
        print(f"  {name:<25} {score:.3f}")









def train_xgboost(X_train, y_train):
    # scale_pos_weight approximates class_weight="balanced" for XGBoost
    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos_weight = neg / pos

    model = XGBClassifier(
        n_estimators=200,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)
    return model




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
    run_cross_validation(model, X, y)

    tuned_model = tune_model(X_train, y_train)

    print("\n--- Tuned model performance ---")
    tuned_train_acc = tuned_model.score(X_train, y_train)
    tuned_test_acc = tuned_model.score(X_test, y_test)
    print(f"Train accuracy: {tuned_train_acc:.3f}")
    print(f"Test accuracy: {tuned_test_acc:.3f}")

    show_feature_importance(tuned_model, X.columns.tolist())


    print("\n=== XGBoost Comparison ===")
    xgb_model = train_xgboost(X_train, y_train)

    xgb_train_acc = xgb_model.score(X_train, y_train)
    xgb_test_acc = xgb_model.score(X_test, y_test)
    print(f"Train accuracy: {xgb_train_acc:.3f}")
    print(f"Test accuracy: {xgb_test_acc:.3f}")

    evaluate_model(xgb_model, X_test, y_test)
    run_cross_validation(xgb_model, X, y)