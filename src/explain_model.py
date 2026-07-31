import shap
import joblib
from prepare_model_data import load_features, get_X_y

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, so we can save without a display window
import matplotlib.pyplot as plt


def load_trained_model(path="models/random_forest_model.pkl"):
    return joblib.load(path)







def save_summary_plot(shap_values_class1, X, path="models/shap_summary_plot.png"):
    plt.figure()
    shap.summary_plot(shap_values_class1, X, show=False)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n✅ Summary plot saved to {path}")


def get_mean_abs_shap(shap_values_class1, feature_names):
    """Global importance: mean absolute SHAP value per feature."""
    import numpy as np
    mean_abs = np.abs(shap_values_class1).mean(axis=0)
    ranked = sorted(zip(feature_names, mean_abs), key=lambda x: -x[1])
    return ranked






def explain_package(package_name, df, X, shap_values_class1, expected_value):
    """Print a human-readable breakdown of one package's prediction."""
    row_idx = df.index[df["package_name"] == package_name]
    if len(row_idx) == 0:
        print(f"Package '{package_name}' not found.")
        return
    row_idx = row_idx[0]

    contributions = list(zip(X.columns, X.iloc[row_idx], shap_values_class1[row_idx]))
    contributions.sort(key=lambda x: -abs(x[2]))  # sort by impact magnitude

    predicted_prob = expected_value + shap_values_class1[row_idx].sum()

    print(f"\n--- Explanation for '{package_name}' ---")
    print(f"Predicted probability of being well-maintained: {predicted_prob:.1%}")
    print(f"(Baseline: {expected_value:.1%})\n")

    print("Top feature contributions:")
    for feature, value, shap_val in contributions:
        direction = "pushes UP (more reliable)" if shap_val > 0 else "pushes DOWN (less reliable)"
        print(f"  {feature:<25} value={value:<12.2f} impact={shap_val:+.4f}  {direction}")







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


    save_summary_plot(shap_values_class1, X)

    print("\nGlobal feature importance (mean |SHAP value|):")
    ranked = get_mean_abs_shap(shap_values_class1, X.columns.tolist())
    for name, score in ranked:
        print(f"  {name:<25} {score:.4f}")





    explain_package("axios", df, X, shap_values_class1, expected_value)

    # Find a genuinely low-scoring package to test the other direction
    predicted_probs = expected_value + shap_values_class1.sum(axis=1)
    lowest_idx = predicted_probs.argmin()
    lowest_package = df.iloc[lowest_idx]["package_name"]
    explain_package(lowest_package, df, X, shap_values_class1, expected_value)