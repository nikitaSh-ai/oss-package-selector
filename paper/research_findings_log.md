# Research Findings Log
**Purpose:** Running record of every methodological decision, data-quality finding, and result — written so it can be lifted almost directly into the paper's Methodology, Results, and Threats to Validity sections. Updated continuously through the project.

---

## Week 1 — Data Collection

### F1. Discovery method: hybrid seed + keyword search
Pure keyword-tag search on npm (`keywords:testing-framework`, etc.) returned semantically noisy results for some categories (e.g., "Testing frameworks" search missed jest/mocha/vitest entirely). Fixed by combining a hand-curated seed list of canonical packages with keyword-discovered packages for diversity. **Citable as:** hybrid discovery methodology — more reproducible than pure manual curation, more relevant than pure automated search.

### F2. `dependents_count` — no reliable data source (documented limitation)
Investigated 3 sources:
1. npm registry API — no official endpoint (feature requested since 2017, never shipped)
2. npmjs.com website scraping — blocked by Cloudflare bot protection (HTTP 403)
3. npms.io aggregator API — endpoint exists but data is stale (~2022), field absent from current responses

**Decision:** Field retained in schema for completeness, left NULL for all packages, documented as an honest limitation rather than substituted with unreliable data.

### F3. `is_deprecated` — constant across dataset (discovery-method bias)
Zero of 331 packages are npm-flagged as deprecated. Root cause: our discovery method (popularity/relevance-ranked search + curated seeds) inherently biases toward actively maintained packages — genuinely deprecated packages rarely surface in top search results. Column dropped from both label and predictors as a result (zero information / constant value).

### F4. Data completeness: 331/368 packages (89.9%) usable
37 packages (10.1%) had missing/broken GitHub repository links — either the `repository` field was absent from npm metadata, or the linked repo returned 404 (renamed/deleted). This is normal, expected real-world noise; per-package error isolation in the pipeline ensured these failures didn't interrupt collection of the other 331.

---

## Week 2 — Feature Engineering & Modeling

### F5. Outlier cluster: bot-like publishing patterns in AI-agent-tooling packages
A cluster of recently created (64–354 day old) packages (e.g., `pi-agent-core` variants) showed implausible activity rates — up to 972 releases/year and 227 stars/day — consistent with automated/CI-driven publishing rather than normal human-paced maintenance. Not a data error; a genuine anomalous subpopulation. **Handled via winsorization** (capped at 95th percentile) rather than manual exclusion, preserving the low-activity tail (which is genuine "less reliable" signal) while preventing a handful of anomalous rows from dominating model training.

### F6. Label circularity risk — identified and avoided
Initial plan was a composite "maintenance score" built from a weighted combination of the same signals (recency, release cadence, docs, license) intended as model predictors. This would have made the label trivially reconstructable from the predictors themselves — the model would show near-100% accuracy without learning any real pattern, and SHAP explanations would just reflect our own hand-chosen weights back.

**Fix:** Target label (`well_maintained`) built from a *direct* signal only — `days_since_last_commit ≤ 365` — kept strictly separate from the predictor feature set. Predictors (release cadence, doc completeness, license presence, popularity, contributor rate, open issues, repo age) are correlated with but not definitionally identical to the label, so the model has to discover genuine relationships.

### F7. Label threshold: 365 days, chosen from real distribution
Checked abandonment rates at 5 candidate cutoffs (180/270/365/545/730 days) before choosing. 365 days gives a 35%/65% (less-reliable/well-maintained) split — workable for classification, not degenerate, and matches a widely recognized "no activity in over a year" definition of software abandonment. Verified the split holds reasonably across all 6 categories (range: 44.7%–92.2% well-maintained) — no category is entirely one class.

### F8. Category-level variation in label balance (real signal, not noise)
HTTP clients skew heavily "well-maintained" (92.2%) — plausible: a stale HTTP client is a security liability, so the ecosystem prunes/updates them faster. Date/time and Utility libraries skew lower (44–48%) — plausible: many small, "feature-complete" utility packages go long periods without commits despite being perfectly functional, not neglected.

**Related limitation:** our label conflates "abandoned" with "stable/feature-complete." A utility library untouched for 2 years might be fine, not neglected. Documented as a Threats-to-Validity item; not fixed within project scope.

### F9. Second leakage catch: `days_since_last_commit` in predictor list
During Day 10 data-prep, caught that `days_since_last_commit` — the exact column used to construct the label — was still present in the predictor column list. Removed before training. Reinforces the value of an explicit label/predictor separation check as a standard step, not a one-time fix.

### F10. Random Forest is scale-invariant — no feature scaling needed
Raw feature scales vary hugely (`weekly_downloads` up to 367M vs `has_license` as 0/1), but Random Forest splits on per-feature thresholds rather than distances, so no scaling/normalization step was required. Noted as a modeling simplification specific to tree-based methods (would not hold if a distance-based model were used instead).

### F11. Baseline Random Forest results
- Single train/test split (80/20, stratified): train accuracy 100%, test accuracy 85.1%
- 5-fold stratified cross-validation (full dataset): **81.3% ± 2.8%** — the more statistically honest number to report, given the single-split test set is only 67 rows
- Confusion matrix: model is conservative in the *safe* direction — only 3/23 genuinely less-reliable packages were misclassified as well-maintained (93% precision on "well-maintained" predictions); more common error is the reverse (7/44 well-maintained packages flagged as risky)

### F12. Hyperparameter tuning: unconstrained depth outperformed constrained
Grid search over `max_depth` (4/6/8/None), `min_samples_leaf` (1/3/5), `n_estimators` (100/200) found the *unconstrained* tree depth (`max_depth=None`) performed best — same as baseline defaults. Depth-constraining reduced performance rather than helping.

**Interpretation:** Random Forest's ensemble averaging (each tree sees a random row/feature subset; predictions are averaged) already provides substantial regularization independent of individual tree depth. The train/test accuracy gap (100% vs ~81–85%) reflects this architecture, not necessarily harmful overfitting. Best model retained: 200 trees, unconstrained depth.

### F13. Feature importance (Gini-based, from tuned Random Forest)
| Feature | Importance |
|---|---|
| releases_per_year | 0.269 |
| contributors_per_year | 0.179 |
| repo_age_days | 0.157 |
| stars_per_day | 0.151 |
| open_issues | 0.115 |
| weekly_downloads | 0.106 |
| doc_completeness_score | 0.019 |
| has_license | 0.004 |

Activity-based signals (release cadence, contributor rate) dominate; documentation/license signals contribute comparatively little. Worth cross-checking against SHAP values in Week 3 — Gini importance is known to be biased toward high-cardinality/continuous features (like our rate-based features) versus low-cardinality binary ones (like `has_license`), so this ranking should not be taken as final without SHAP corroboration.

---

## Open items / planned follow-ups
- [ ] Threshold sensitivity check: re-evaluate model at 270/365/545-day label cutoffs to confirm results aren't fragile to our specific 365-day choice (planned for Week 4 validation)
- [x] XGBoost comparison model — completed (see F14)
- [ ] SHAP importance vs. Gini importance cross-check (Week 3)




### F14. XGBoost comparison model
Trained XGBoost with matched settings (same predictors, split, `scale_pos_weight` as the class-imbalance equivalent of Random Forest's `class_weight="balanced"`). Random Forest outperformed XGBoost on every metric, though narrowly:

| Metric | Random Forest (tuned) | XGBoost |
|---|---|---|
| CV Mean Accuracy | 81.3% | 80.0% |
| CV Std | 2.8% | 3.9% |
| Test Accuracy | 85.1% | 83.6% |
| Precision (Well-Maintained) | 93% | 90% |

**Interpretation:** With only 264 training rows, Random Forest's ensemble-averaging approach appears more stable than XGBoost's sequential boosting, which typically benefits from larger datasets to fully exploit its ability to correct prior trees' errors. **Decision:** Random Forest retained as the primary model for SHAP explainability (Week 3); XGBoost result kept as a documented comparison baseline.






### F15. SHAP global importance confirms and extends Gini ranking
SHAP mean |value| ranking closely matches Day 13's Gini-based feature importance (F13) — same top 2 features (releases_per_year, contributors_per_year), with only ranks 3/4 (stars_per_day, repo_age_days) swapped, and those are nearly tied in both methods. Convergence across two independent importance methods is evidence the model learned a stable pattern rather than an artifact of one metric's known biases.

**Beyond Gini, SHAP reveals relationship shape, not just magnitude:**
- releases_per_year, contributors_per_year, stars_per_day show clean monotonic relationships (high value → pushes toward "well-maintained"), matching intuition.
- repo_age_days shows a **non-monotonic** pattern (mixed high/low values on both sides of zero) — Gini importance could not have revealed this; SHAP shows the relationship is more complex than "older is better/worse."
- open_issues shows a similar mixed pattern, suggesting a possible non-linear ("Goldilocks") relationship rather than "more issues = worse." Noted as a hypothesis for further inspection, not a confirmed claim.






### F16. Per-instance SHAP explanations validated on contrasting examples
Tested explanation generation on two contrasting packages:
- **axios** (94.0% predicted well-maintained): top contributors were star velocity, contributor rate, and release cadence — consistent with its known high-activity profile. Notably, repo_age_days contributed slightly *negatively* despite axios being an excellent package, providing a concrete example of the non-monotonic age relationship identified in F15.
- **validate.io-function** (~0% predicted well-maintained): near-zero activity across release cadence, contributor rate, and star growth dominated the prediction. Notably, weekly_downloads (2.8M — a substantial number) still contributed negatively, illustrating that the model does not let raw popularity override clear inactivity signals — consistent with the deliberate exclusion of popularity from label construction (F6).

Both explanations are coherent and human-readable, confirming the SHAP pipeline produces genuinely useful justifications, not just technically-correct-but-meaningless numbers.



### F17. Comparison tool: close-call threshold for near-tied predictions
Initial testing (axios vs got, 94% vs 96%) revealed that declaring a flat "winner" for closely-matched packages overstates the tool's confidence and could mislead users into thinking a close second choice is meaningfully worse. Added a 5-percentage-point close-call threshold: comparisons within this margin are framed as "both are strong choices" with only a slight edge noted, rather than a confident recommendation. This is a deliberate interpretability/UX design choice for a decision-support tool, not a statistical constant — chosen as a reasonable, defensible round number.






### F18. Known failure case: moment vs dayjs ranks against real-world consensus
CLI testing revealed the tool ranks `moment` (100%) above `dayjs` (93%), despite moment.js being widely known in the developer community as being in "maintenance mode" — its maintainers have publicly stated it is feature-frozen and recommend migrating to alternatives like dayjs/date-fns.

**Root cause analysis:** moment's large legacy scale (historical stars, contributors, and open-issue count accumulated over its long lifetime) keeps activity-based features looking strong, and its `days_since_last_commit` likely still falls under the 365-day threshold due to occasional maintenance patches — even though genuine feature development has stopped. The model has no feature capturing community migration sentiment or "feature-freeze" status, which real developers weigh heavily.

**Significance:** this is a concrete, real-world example of the recency-vs-abandonment limitation already noted in F8, and directly motivates the Week 4 human-comparison validation exercise — this case demonstrates the tool's activity-based signals can diverge from expert/community consensus, and such cases should be surfaced honestly in the paper's Threats to Validity section rather than cherry-picking only favorable examples (like axios) for the write-up.





### F19. Day 21 end-to-end testing: resolving power and a second legacy-scale case
Tested 4 additional real package pairs (lodash/ramda, superagent/ky, jest/mocha, joi/ajv). All 4 fell within the close-call threshold (2-5%), revealing that the model's predicted probabilities compress toward the high end among packages that are all reasonably well-maintained — the classifier distinguishes "clearly healthy" from "clearly abandoned" confidently, but has limited resolving power for fine-grained ranking *within* the healthy cluster. This is a genuine limitation, not a bug, and should be stated plainly rather than implying the tool offers precise fine-grained rankings among already-solid packages.

**Positive validation case:** jest vs mocha (99% vs 94%, jest favored) matches broad real-world developer consensus that jest is the more dominant, actively-evolving testing framework today.

**Second legacy-scale case (milder echo of F18):** superagent vs ky (98% vs 94%, superagent favored) shows the same underlying pattern as the moment/dayjs case — an older, larger-scale package's accumulated stars/contributors/issues can outweigh a newer, leaner package's activity profile, even where community sentiment may favor the newer option. Smaller magnitude than F18, but same root cause (activity-scale features do not directly capture "community migration" or relative modernity).