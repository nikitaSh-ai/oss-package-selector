# An Explainable Machine Learning Framework for Evidence-Based Open-Source Package Selection

**Author:** Nikita Sharma

---

## 1. Introduction

Modern software development depends heavily on open-source packages to avoid reimplementing common functionality. For nearly any given feature, developers face dozens of candidate packages that appear to serve the same purpose, and choosing the wrong one can introduce long-term maintenance risk, security vulnerabilities, or project instability. Currently, this selection process relies on manual, ad-hoc judgment — checking GitHub stars, last commit dates, and documentation quality — a process that is time-consuming, inconsistent, and lacks standardized automated support.

While prior research has studied *what* factors developers consider when evaluating open-source packages, this knowledge has not been translated into a working, automated decision-support tool. Separately, most abandonment-prediction research in this space focuses on dependencies *after* they have already been adopted — assessing risk in an existing dependency tree — rather than supporting the *initial selection* decision, before a package is even chosen.

This project addresses that gap by designing and implementing a lightweight, explainable machine learning system that takes two or more candidate open-source packages, automatically extracts evidence signals from public GitHub and npm registry data, and produces a scored, ranked recommendation accompanied by a human-readable justification — not a black-box score. The system is built on a Random Forest classifier trained on 331 npm packages across six categories, with explanations generated via SHAP (SHapley Additive exPlanations). Beyond building the tool, this project places equal emphasis on **honestly characterizing its limitations**: a structured validation exercise against independently researched developer consensus revealed that the tool's predictions systematically diverge from real-world judgment in a specific, identifiable way — favoring packages with large accumulated historical scale over packages with genuine current momentum — a finding that is reported and analyzed rather than omitted.

---

## 2. Related Work

Research on open-source package selection falls into three broad areas, each of which this project draws from and extends.

**Survey- and interview-based studies of selection criteria.** A body of prior work has identified, through developer surveys and interviews, the factors practitioners report considering when choosing between packages — activity level, documentation quality, community size, and licensing among them. This research establishes *what* matters but stops short of automating these factors into a working tool; the present project operationalizes this prior knowledge into a concrete, evidence-based feature set.

**Dependency abandonment prediction.** A separate body of work models the risk that an *already-adopted* open-source dependency will become abandoned or unmaintained over time. This research is valuable for managing existing dependency trees but does not address the earlier, arguably higher-leverage decision point: selecting among *candidate* packages before any commitment has been made. This project targets that earlier decision point specifically.

**Explainable AI in software engineering.** A recent survey of XAI applications in software engineering found the large majority of existing work (approximately 68%) targets code-level maintenance tasks (e.g., defect prediction, code review), while the management and decision-making phase of software engineering — where package selection sits — remains comparatively underexplored (approximately 8%). This project contributes to this underexplored area by applying SHAP-based explainability specifically to a package-selection decision-support context.

**Positioning.** Unlike tools that output a single opaque "health score," this project's core contribution is pairing a validated classification model with SHAP-derived, natural-language justifications — and, distinctively, with a structured validation exercise that surfaces and analyzes cases where the tool's evidence-based predictions diverge from real-world developer consensus, rather than presenting only favorable examples.

---

## 3. Methodology

### 3.1 Data Collection

Candidate packages were identified using a hybrid discovery method combining a hand-curated seed list of canonical, well-known packages with npm keyword-qualified search results, across six categories: HTTP clients, Date/time libraries, Testing frameworks, State management, Utility libraries, and Data validation. Pure free-text keyword search was found to return semantically noisy results for some categories (e.g., a "testing framework" query surfacing unrelated packages); the hybrid approach was adopted to balance reproducibility with relevance. This process identified 368 candidate packages.

For each candidate, metadata was collected from two public APIs: the GitHub REST API (stars, forks, open issues, contributor count, commit recency, repository age, README/wiki presence, license) and the npm Registry API (latest version, weekly downloads, publish history, deprecation status). GitHub repository URLs were automatically derived from each package's npm registry metadata, rather than manually mapped, to support reliable collection at scale. Collection used per-package error isolation and rate-limit-aware batching so that individual failures (e.g., a deleted or renamed repository) did not interrupt the overall run. Of 368 candidates, 331 (89.9%) yielded complete data from both sources and were retained for analysis; the remaining 37 had broken or missing repository links, a normal and expected rate of real-world data attrition.

One data field specified in the initial project schema — a package's "dependents count" (the number of other packages that depend on it) — was found to have no reliable public data source. Three approaches were investigated: the official npm registry API (no such endpoint exists), direct scraping of the npm website (blocked by anti-bot protection), and a third-party aggregator API (data found to be several years stale). This field was retained in the schema for completeness but left unpopulated, and is documented here as a data limitation rather than approximated with unreliable data.

### 3.2 Feature Engineering

Raw collected fields were transformed into eight model-ready predictor features, primarily by normalizing activity counts relative to repository age (e.g., releases per year, contributors per year, stars per day), since raw cumulative counts alone are not comparable across repositories of different ages. A minimum age floor (90 days) was applied to these normalization denominators to prevent very young repositories from producing extreme, statistically noisy rates. During this process, a cluster of very recently created packages exhibiting implausibly high release velocity (in excess of 500 releases per year) was identified, consistent with automated or CI-driven publishing rather than typical human-paced maintenance. Rather than manually excluding these packages, all normalized activity features were winsorized (capped at the 95th percentile), preserving the full range of genuinely low-activity packages — an important signal for the classification task — while preventing a small number of anomalous packages from disproportionately influencing model training.

### 3.3 Target Label Design

The binary target label (`well_maintained`) required particular care in its construction. An initial design considered combining multiple signals (commit recency, release cadence, documentation completeness, license presence) into a single weighted composite score. This approach was rejected after recognizing it would create label circularity: since these same signals were intended as model predictors, a model could achieve high apparent accuracy simply by reconstructing the label-construction formula, without learning any genuine relationship between package characteristics and maintenance outcomes.

The label was instead constructed from a single, direct signal — repository commit recency — strictly separated from all predictor features: `well_maintained = 1` if the repository's most recent commit occurred within 365 days, else `0`. This threshold was selected empirically by examining the resulting class balance across several candidate cutoffs (180 to 730 days) rather than chosen arbitrarily, and corresponds to a widely recognized definition of software abandonment. The resulting split (65% well-maintained, 35% less-reliable) was verified to hold reasonably across all six package categories, with no category degenerately composed of a single class.

A second, independent leakage check during data preparation identified that the recency field itself — despite being excluded from the composite-label design — had been inadvertently retained in the predictor feature list. This was corrected prior to model training. A package's npm-registry deprecation flag was also considered as a label signal but found to be constant (zero) across the entire dataset, likely reflecting a bias in the popularity-oriented discovery method toward actively maintained packages; this field was dropped from both label construction and predictors.

### 3.4 Modeling

A Random Forest classifier (scikit-learn, 200 trees, class-balanced weighting) was trained on an 80/20 stratified train-test split (264/67 packages) using eight leakage-free predictor features: repository age, normalized release cadence, normalized star growth, normalized contributor rate, documentation completeness, license presence, weekly downloads, and open issue count. Hyperparameter tuning via grid search (tree depth, minimum leaf size, tree count) found that unconstrained tree depth performed best, suggesting the ensemble's inherent averaging across randomly-sampled trees already provides sufficient regularization at this dataset size, without requiring additional depth constraints. An XGBoost classifier was trained under matched conditions as a comparison baseline; Random Forest achieved marginally higher and more stable cross-validated accuracy and was retained as the primary model.

### 3.5 Explainability

SHAP (SHapley Additive exPlanations) values were computed for the trained Random Forest using the TreeExplainer method, which provides exact (non-approximated) attributions for tree-based models. Correctness was verified by confirming that each package's baseline expected value plus the sum of its SHAP values exactly reproduced the model's predicted probability. Global feature importance derived from mean absolute SHAP values was cross-checked against the model's built-in Gini-based importance, showing strong agreement between the two independent methods. Per-package SHAP values were converted into natural-language justifications via a feature-to-phrase mapping, and a two-package comparison function was built on top of this explanation layer, including an explicit close-call threshold (5 percentage points) to avoid overstating confidence when two candidates' predicted probabilities are nearly tied.

### 3.6 Validation

To assess whether tool predictions align with real-world developer judgment, a structured validation exercise was conducted comparing tool output against independently researched evidence — official maintainer statements, third-party package health-scoring services, and npm download/version trend data — for eight package pairs spanning sanity checks, previously observed contested cases, and cases of a priori uncertain outcome. This approach was adopted specifically to mitigate the risk of unverified self-opinion bias, given that a multi-person peer panel (as originally envisioned) was not available for this project; each judgment in the validation exercise is traceable to an external, citable source rather than personal preference alone.






## 4. Results

### 4.1 Model Performance

The tuned Random Forest classifier achieved a test-set accuracy of 85.1% on a single 80/20 stratified split, and a 5-fold cross-validated accuracy of **81.3% (± 2.8%)** across the full dataset — the latter is reported as the primary performance metric, being less sensitive to the particular composition of any single train-test split. The model showed conservative behavior in the safer error direction: precision on "well-maintained" predictions was 93%, meaning that when the tool recommends a package as well-maintained, it is correct 93% of the time; the more common error was the reverse — a genuinely well-maintained package being flagged as potentially less reliable (16% false-negative rate on this class). For a decision-support tool, this asymmetry is preferable to the alternative, since a false "well-maintained" recommendation carries greater practical risk than an overly cautious one.

A comparison XGBoost model, trained under matched conditions, achieved a lower cross-validated accuracy of 80.0% (± 3.9%), with a larger standard deviation suggesting reduced stability at this dataset size (331 rows). Random Forest's ensemble-averaging approach appears better suited to a dataset of this scale than XGBoost's sequential boosting, which typically benefits from larger training sets.

### 4.2 Feature Importance and Explainability

Both Gini-based feature importance (derived directly from the trained model) and SHAP-based mean absolute importance identified the same top predictors, in near-identical order: normalized release cadence, contributor activity rate, and star growth rate dominate the model's decisions, while documentation completeness and license presence contribute comparatively little. This agreement between two independent importance methods provides evidence that the model learned a stable, non-arbitrary pattern rather than an artifact specific to one metric's known biases.

Beyond ranking feature importance, SHAP analysis revealed relationship *shape* that Gini importance alone cannot express: repository age showed a non-monotonic relationship with the predicted outcome — neither "older is better" nor "older is worse" uniformly — while release cadence, contributor rate, and star growth showed the expected clean monotonic pattern (higher activity, higher predicted probability of being well-maintained).

### 4.3 Natural-Language Explanation Quality

Per-package SHAP explanations were validated on contrasting examples. A well-known, actively maintained package (axios) received a 94% predicted probability of being well-maintained, with the explanation correctly attributing this to strong community growth, contributor activity, and release frequency. An obscure, low-activity package (vali-date) received a 10% predicted probability, with the explanation correctly attributing this to weak activity across the same three dimensions. In both cases, the generated natural-language justification was coherent, specific, and consistent with the underlying quantitative signal — meeting the project's core objective of producing evidence-based, human-readable justifications rather than an opaque score.

### 4.4 Validation Against Independent Evidence

A structured validation exercise compared tool predictions for eight package pairs against independently researched, documented developer consensus (official maintainer statements, third-party package health-scoring metrics, npm download and version trend data). The tool's recommendations agreed with independent evidence in 4 of 8 cases (50%), disagreed in 3 of 8 (37.5%), and were inconclusive in 1 of 8 (12.5%).

Critically, the three disagreement cases were not randomly distributed: all three (moment.js vs. dayjs; lodash vs. ramda; joi vs. ajv) followed the same pattern — the tool favored an older, larger-scale, legacy-established package over a newer or more actively-evolving alternative, even where independent evidence favored the newer option. This is discussed further in Section 5 (Threats to Validity).

## 5. Threats to Validity

**Label construction reflects recency, not true abandonment.** The target label was deliberately built from a single direct signal (commit recency) to avoid label circularity with predictor features (Section 3.3). However, this means the label conflates genuine abandonment with legitimate feature-completeness — a small, stable utility package that has not required a commit in over a year may be functioning correctly, not neglected. This limitation was observed directly in the validation exercise's three disagreement cases, where established, historically large packages (which may see infrequent but still-occurring maintenance activity) were rated more favorably than the label's recency-based construction alone would suggest is warranted, or conversely, cases where genuinely large-but-slowing packages retained a "well-maintained" label despite reduced real-world relative momentum.

**Discovery method introduces a survivorship-style bias.** Because the candidate package set was assembled via popularity- and relevance-ranked search combined with a seed list of well-known packages, the resulting dataset skews toward already-successful, actively maintained packages. This is evidenced concretely by the npm deprecation flag being constant (zero) across all 331 packages in the dataset — genuinely deprecated packages were essentially absent from the collection, despite deprecation being a real and relevant outcome the tool would ideally help developers avoid.

**No feature captures relative modernity or community migration sentiment.** The validation exercise's central finding is that all activity-based predictor features (release cadence, contributor rate, star growth, and similar) measure *absolute* or *rate-normalized* activity, but none captures whether a package's userbase is actively migrating toward a newer alternative — the exact situation with moment.js, which retains substantial legacy scale and occasional maintenance activity despite its maintainers publicly recommending migration away from it. This is a structural limitation of the feature set rather than a fixable bug, and represents the most significant, well-characterized limitation of the current system.

**Modest dataset size limits statistical precision.** With 331 packages, cross-validation fold accuracies ranged from 77.3% to 84.8% — a real, non-trivial spread that should be kept in mind when interpreting any single reported metric as precise. Larger-scale data collection in future work would likely narrow this uncertainty.

**Self-conducted, evidence-grounded validation is not equivalent to independent peer validation.** The original project plan anticipated a peer-panel validation exercise; due to practical constraints, validation was conducted by a single researcher, with self-opinion bias mitigated by grounding each judgment in independently documented, citable evidence rather than personal preference. This is methodologically stronger than pure self-opinion but weaker than genuine multi-person independent validation, and the 50% agreement rate should be interpreted with this constraint in mind.





## 5. Threats to Validity
*(To be drafted — Day 26)*

## 6. Conclusion
*(To be drafted — Day 27)*