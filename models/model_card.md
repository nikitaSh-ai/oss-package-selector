# Model Card: OSS Package Maintenance Classifier

## Model Details
- **Type:** Random Forest Classifier (scikit-learn)
- **Hyperparameters:** n_estimators=200, max_depth=None, min_samples_leaf=1, class_weight="balanced"
- **Trained:** Week 2, Day 11-14
- **File:** models/random_forest_model.pkl

## Task
Binary classification: predict whether an open-source npm package is
"well-maintained" (1) or "less reliable" (0), based on repository and
registry metadata, to support the explainable package-selection tool.

## Training Data
- 331 npm packages across 6 categories (HTTP clients, Date/time,
  Testing frameworks, State management, Utility libraries, Data validation)
- Collected via GitHub REST API + npm Registry API (Week 1)
- 264 training rows / 67 test rows (80/20 stratified split)

## Target Label
`well_maintained = 1` if `days_since_last_commit <= 365`, else `0`.
Chosen as a direct proxy (not a composite score) to avoid circularity
with predictor features. See research_findings_log.md (F6, F7) for
full reasoning.

## Predictor Features (8)
repo_age_days, releases_per_year, stars_per_day, contributors_per_year,
doc_completeness_score, has_license, weekly_downloads, open_issues

**Explicitly excluded:** days_since_last_commit (source of the label —
would cause data leakage), is_deprecated (constant in this dataset).

## Performance
- Test accuracy: 85.1%
- 5-fold CV accuracy: **81.3% ± 2.8%** (primary reported metric)
- Precision (Well-Maintained): 93%
- Precision (Less Reliable): 74%
- Recall (Well-Maintained): 84%
- Recall (Less Reliable): 87%

## Comparison Model
XGBoost was trained under matched conditions for comparison
(CV accuracy: 80.0% ± 3.9%). Random Forest retained as the primary
model — more stable given the dataset's modest size (331 rows).
See research_findings_log.md (F14).

## Known Limitations
- Label conflates "recently inactive" with "abandoned" — a stable,
  feature-complete utility package may be incorrectly scored low.
- Training data skews toward actively maintained packages due to the
  discovery method (popularity-ranked search), so truly deprecated/
  abandoned packages are underrepresented.
- Dataset size (331 rows) is modest for ML standards; CV std (2.8%)
  suggests reasonable but not perfect stability.

## Intended Use
Research prototype for an explainable package-comparison tool.
Not intended as a sole basis for production dependency decisions —
designed to surface evidence and explanations to support human
judgment, not replace it.