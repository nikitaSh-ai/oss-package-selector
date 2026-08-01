# OSS Package Selector — Explainable ML Framework

An explainable machine learning tool that compares open-source packages 
(npm) using evidence-based signals from GitHub and npm, and explains 
**why** one package is recommended over another — not just a black-box score.

## Problem
Developers manually compare packages using ad-hoc signals (stars, last 
commit, etc.) — a slow, inconsistent process with no automated, 
explainable support.

## Approach
1. **Data Collection** — Pull activity/maintenance signals from GitHub 
   API + npm Registry API for 300–500 packages.
2. **Modeling** — Train a Random Forest to classify "well-maintained" 
   vs "less reliable" packages.
3. **Explainability** — Use SHAP to convert model predictions into 
   human-readable justifications.
4. **Comparison Tool** — Given two packages, output a ranked 
   recommendation with a plain-language explanation.




## Status
✅ Complete — All 4 weeks finished. Data pipeline (368 packages collected, 331 usable), trained and validated Random Forest model (81.3% ± 2.8% CV accuracy), SHAP explainability with natural-language justifications, interactive CLI comparison tool, structured validation exercise against independent evidence (50% agreement, systematic limitation identified and analyzed), and full paper (paper/Explainable_ML_Package_Selection_Paper.docx).

See `paper/research_findings_log.md` for the complete methodology decision log (20 documented findings).




## Tech Stack
Python, pandas, scikit-learn, SHAP, GitHub REST API, npm Registry API

## Setup
\`\`\`bash
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
\`\`\`

Create a `.env` file with:
\`\`\`
GITHUB_TOKEN=your_token_here
\`\`\`