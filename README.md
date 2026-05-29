# CS2 Match Outcome Prediction

**Course:** Research Methods — Narxoz University  
**Team:** Seisenbek Dias · Mergen Temirzhan · Onashov Aidos

---

## What is this?

Can you predict who wins a professional CS2 match before it starts — using only team stats?

This project trains and compares three machine learning models (Logistic Regression, Random Forest, Gradient Boosting) on 7,033 professional CS2 matches from HLTV.org. We use four features: team HLTV rating, kills per round, head-to-head win rate, and map win rate.

**Short answer:** yes, slightly. Best model hits ~57% accuracy vs 54.6% naive baseline. The ceiling is real — pre-match data only goes so far.

---

## Results

| Model | Accuracy | Macro F1 | AUC-ROC |
|---|---|---|---|
| Naive Baseline (always predict Win) | 54.6% | 0.353 | 0.500 |
| Logistic Regression | 56.2% | 0.484 | 0.574 |
| **Random Forest** | **57.2%** | **0.536** | 0.571 |
| Gradient Boosting | 56.4% | 0.528 | 0.573 |

Top feature: **Map Win Rate**, followed by H2H Win Rate.  
Differences between models are not statistically significant (paired t-test, p > 0.05).

---

## Repo Structure

```
cs2-match-outcome-prediction/
│
├── generate_paper_journal.py   # Runs full pipeline + generates PDF paper
├── train_models.py             # Standalone ML training, prints results table
│
├── final/                      # Final outputs
│   ├── paper_cs2_match_prediction.pdf
│   └── paper_cs2_match_prediction.docx
│
├── previous_tasks/             # Submitted reports (Tasks 4–7)
│   ├── Ethical_Risk_Assessment_Brief.pdf
│   ├── Conceptual_Framework_Humanized.pdf
│   ├── task6-solution.pdf
│   └── task7_report.docx
│
├── old/                        # Superseded scripts and drafts
│
└── data/                       # Raw CSV datasets from HLTV/Kaggle
```

---

## Quick Start

```bash
pip install pandas numpy scikit-learn matplotlib seaborn reportlab scipy
```

**Train models and see results:**
```bash
python train_models.py
```

**Regenerate the full PDF paper:**
```bash
python generate_paper_journal.py
```

---

## Data

**Source:** [CS2 HLTV Professional Match Statistics](https://www.kaggle.com/datasets/griffindesroches/cs2-hltv-professional-match-statistics-dataset) — griffindesroches (Kaggle)  
**Coverage:** 7,033 matches · 648 tournaments · May 2024 – October 2025

> Academic use only. Not for betting, commercial forecasting, or competitive intelligence.
