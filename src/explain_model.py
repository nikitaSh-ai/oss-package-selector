import shap
import joblib
from prepare_model_data import load_features, get_X_y

def load_trained_model(path="models/random_forest_model.pkl"):
    return joblib.load(path)


if __name__ == "__main__":
    model = load_trained_model()
    df = load_features()
    X, y = get_X_y(df)

    print(f"Model loaded: {type(model).__name__} with {model.n_estimators} trees")
    print(f"Feature matrix: {X.shape}")

    # TreeExplainer is optimized specifically for tree-based models
    # (Random Forest, XGBoost, etc.) — much faster than the general-
    # purpose KernelExplainer, and gives exact (not approximated) values.
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    print(f"\nSHAP values computed.")
    print(f"Type: {type(shap_values)}")
    if isinstance(shap_values, list):
        print(f"List length: {len(shap_values)} (likely one per class)")
        print(f"Shape of each: {shap_values[0].shape}")
    else:
        print(f"Shape: {shap_values.shape}")









    # Extract SHAP values for class 1 ("well_maintained")
    # Shape becomes (331, 8) — one SHAP value per package per feature
    shap_values_class1 = shap_values[:, :, 1]

    print(f"\nSHAP values for 'well_maintained' class: {shap_values_class1.shape}")

    # Sanity check: SHAP values should sum (plus the baseline) to the
    # model's actual predicted probability for that class, for each row
    expected_value = explainer.expected_value[1]
    print(f"\nBaseline (expected) value for class 1: {expected_value:.4f}")

    row_idx = 0
    predicted_prob = model.predict_proba(X.iloc[[row_idx]])[0][1]
    shap_sum = shap_values_class1[row_idx].sum() + expected_value

    print(f"\nSanity check on row 0 ({X.index[row_idx]}):")
    print(f"  Model's predicted probability (class 1): {predicted_prob:.4f}")
    print(f"  Baseline + sum of SHAP values:            {shap_sum:.4f}")
    print(f"  Match: {abs(predicted_prob - shap_sum) < 0.001}")