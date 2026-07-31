import sys
import shap
from explain_model import (
    load_trained_model, FEATURE_PHRASES,
    generate_natural_language_explanation, compare_packages
)
from prepare_model_data import load_features, get_X_y


def setup():
    """Load model, data, and compute SHAP values once."""
    model = load_trained_model()
    df = load_features()
    X, y = get_X_y(df)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap_values_class1 = shap_values[:, :, 1]
    expected_value = explainer.expected_value[1]

    return df, X, shap_values_class1, expected_value


def main():
    print("Loading model and computing explanations (this takes a few seconds)...")
    df, X, shap_values_class1, expected_value = setup()

    print(f"\n✅ Ready. {len(df)} packages available.\n")

    while True:
        print("-" * 60)
        name1 = input("Enter first package name (or 'quit' to exit): ").strip()
        if name1.lower() == "quit":
            break
        name2 = input("Enter second package name to compare: ").strip()

        result = compare_packages(name1, name2, df, X, shap_values_class1, expected_value)
        print(result)


if __name__ == "__main__":
    main()