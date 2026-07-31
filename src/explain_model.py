import shap
import joblib
from prepare_model_data import load_features, get_X_y

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, so we can save without a display window
import matplotlib.pyplot as plt

FEATURE_PHRASES = {
    "releases_per_year": "release frequency",
    "contributors_per_year": "contributor activity",
    "stars_per_day": "community growth (star velocity)",
    "repo_age_days": "repository age",
    "open_issues": "open issue count",
    "weekly_downloads": "download popularity",
    "doc_completeness_score": "documentation completeness",
    "has_license": "license presence",
}




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










def generate_natural_language_explanation(package_name, df, X, shap_values_class1, expected_value, top_n=3):
    """Convert SHAP values into a readable justification sentence."""
    row_idx = df.index[df["package_name"] == package_name]
    if len(row_idx) == 0:
        return f"Package '{package_name}' not found."
    row_idx = row_idx[0]

    contributions = list(zip(X.columns, shap_values_class1[row_idx]))
    contributions.sort(key=lambda x: -abs(x[1]))

    predicted_prob = max(0.0, min(1.0, expected_value + shap_values_class1[row_idx].sum()))
    verdict = "well-maintained" if predicted_prob >= 0.5 else "less reliable"

    positive_reasons = [FEATURE_PHRASES[f] for f, v in contributions[:top_n] if v > 0]
    negative_reasons = [FEATURE_PHRASES[f] for f, v in contributions[:top_n] if v < 0]

    sentence = f"{package_name} is predicted to be {verdict} ({predicted_prob:.0%} confidence)."

    if positive_reasons:
        sentence += f" This is primarily supported by strong {', '.join(positive_reasons)}."
    if negative_reasons:
        sentence += f" This is weighed down by weak {', '.join(negative_reasons)}."

    return sentence









def compare_packages(name1, name2, df, X, shap_values_class1, expected_value):
    """Compare two packages and produce a recommendation with reasoning."""

    def get_prob(name):
        row_idx = df.index[df["package_name"] == name]
        if len(row_idx) == 0:
            return None
        row_idx = row_idx[0]
        return max(0.0, min(1.0, expected_value + shap_values_class1[row_idx].sum()))

    prob1, prob2 = get_prob(name1), get_prob(name2)

    if prob1 is None or prob2 is None:
        missing = name1 if prob1 is None else name2
        return f"❌ Package '{missing}' not found in dataset."

    winner, loser = (name1, name2) if prob1 >= prob2 else (name2, name1)
    winner_prob, loser_prob = max(prob1, prob2), min(prob1, prob2)

    margin = abs(prob1 - prob2)
    CLOSE_CALL_THRESHOLD = 0.05  # 5 percentage points

    result = f"\n{'='*60}\n"
    result += f"COMPARISON: {name1} vs {name2}\n"
    result += f"{'='*60}\n\n"
    result += f"  {name1:<20} {prob1:.0%} predicted well-maintained\n"
    result += f"  {name2:<20} {prob2:.0%} predicted well-maintained\n\n"
    if margin < CLOSE_CALL_THRESHOLD:
        result += f"RECOMMENDATION: Both are strong choices — the difference ({margin:.0%}) is within a close-call range. Slight edge: {winner}.\n\n"
    else:
        result += f"RECOMMENDATION: {winner} (margin: {margin:.0%})\n\n"
    result += generate_natural_language_explanation(winner, df, X, shap_values_class1, expected_value) + "\n\n"
    result += f"For comparison, {loser}:\n"
    result += generate_natural_language_explanation(loser, df, X, shap_values_class1, expected_value)

    return result







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



    print("\n--- Natural language explanations ---")
    print(generate_natural_language_explanation("axios", df, X, shap_values_class1, expected_value))
    print(generate_natural_language_explanation(lowest_package, df, X, shap_values_class1, expected_value))


    print(compare_packages("axios", "got", df, X, shap_values_class1, expected_value))