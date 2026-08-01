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
*(To be drafted — Day 25)*

## 4. Results
*(To be drafted — Day 26)*

## 5. Threats to Validity
*(To be drafted — Day 26)*

## 6. Conclusion
*(To be drafted — Day 27)*