"""
train_models.py
ML pipeline for CS2 match outcome prediction.

Loads real HLTV data, preprocesses it, trains 3 models,
and prints a full evaluation table.

Authors : Seisenbek Dias · Mergen Temirzhan · Onashov Aidos
Course  : Research Methods | Narxoz University
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, roc_auc_score,
)

# -------------------------------------------------------------
# 1. LOAD DATA
# -------------------------------------------------------------
CSV_PATH = "data/cs2_newestcombinedmatches_team1_reference_reduced2.csv"

MAP_COLS = {
    "mirage":   "team1_mirage",
    "inferno":  "team1_inferno",
    "nuke":     "team1_nuke",
    "dust2":    "team1_dust2",
    "ancient":  "team1_ancient",
    "anubis":   "team1_anubis",
    "vertigo":  "team1_vertigo",
    "overpass": "team1_overpass",
    "train":    "team1_train",
}

print("=" * 60)
print("  CS2 MATCH OUTCOME PREDICTION — ML PIPELINE")
print("=" * 60)
print("\n[1/5] Loading data ...")

df = pd.read_csv(CSV_PATH, low_memory=False)

df["match_outcome"]         = df["team1_win_flag"].astype(int)
df["mean_hltv_rating"]      = pd.to_numeric(df["team1_avg_RATING"], errors="coerce")
df["mean_kpr"]              = pd.to_numeric(df["team1_avg_KPR"],    errors="coerce")
df["head_to_head_win_rate"] = pd.to_numeric(df["team1_head2head_percentage"], errors="coerce") / 100

def get_map_win_rate(row):
    col = MAP_COLS.get(str(row.get("decider_map", "")).strip().lower())
    if col and col in row.index:
        try:
            return float(row[col]) / 100
        except Exception:
            return np.nan
    return np.nan

df["map_win_rate"] = df.apply(get_map_win_rate, axis=1)

FEATURES = ["mean_hltv_rating", "mean_kpr", "head_to_head_win_rate", "map_win_rate"]
FEAT_LABELS = ["HLTV Rating", "KPR", "H2H Win Rate", "Map Win Rate"]
TARGET = "match_outcome"

print(f"    Total records : {len(df):,}")
print(f"    Win rate      : {df[TARGET].mean():.1%}  (Win) / "
      f"{1 - df[TARGET].mean():.1%}  (Loss)")

# -------------------------------------------------------------
# 2. PREPROCESSING
# -------------------------------------------------------------
print("\n[2/5] Preprocessing ...")

dc = df[[TARGET] + FEATURES].copy()

# Missing values
mwr_missing = int(dc["map_win_rate"].isnull().sum())
mwr_mean = dc["map_win_rate"].mean()
for col in FEATURES:
    dc[col] = dc[col].fillna(dc[col].median())
dc["map_win_rate"] = dc["map_win_rate"].fillna(mwr_mean)
dc["head_to_head_win_rate"] = dc["head_to_head_win_rate"].fillna(0.50)

print(f"    map_win_rate missing -> imputed with mean ({mwr_mean:.4f})")
print(f"    All other features  -> 0 missing values")

# Winsorize outliers (1st / 99th percentile)
for col in FEATURES:
    p1, p99 = dc[col].quantile(0.01), dc[col].quantile(0.99)
    before = dc[col].copy()
    dc[col] = dc[col].clip(p1, p99)
    clipped = int((before != dc[col]).sum())
    print(f"    {col:<30} clipped {clipped} outliers  [{p1:.4f}, {p99:.4f}]")

# -------------------------------------------------------------
# 3. SPLIT & SCALE
# -------------------------------------------------------------
print("\n[3/5] Splitting and scaling ...")

X = dc[FEATURES]
y = dc[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print(f"    Train : {len(X_train):,} records")
print(f"    Test  : {len(X_test):,}  records")
print(f"    Scaler fit on training set only (prevents data leakage)")

# -------------------------------------------------------------
# 4. NAIVE BASELINE
# -------------------------------------------------------------
y_naive = np.ones(len(y_test), dtype=int)   # always predict Win
naive = {
    "Accuracy"   : accuracy_score(y_test, y_naive),
    "Binary F1"  : f1_score(y_test, y_naive, zero_division=0),
    "Macro F1"   : f1_score(y_test, y_naive, average="macro", zero_division=0),
    "AUC-ROC"    : 0.500,
    "CV Acc"     : f"{y_train.mean():.4f} +/- 0.0000",
}

# -------------------------------------------------------------
# 5. TRAIN MODELS
# -------------------------------------------------------------
print("\n[4/5] Training models ...")

model_defs = {
    "Logistic Regression": (
        LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        True,   # use scaled data
    ),
    "Random Forest": (
        RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1),
        False,
    ),
    "Gradient Boosting": (
        GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42),
        False,
    ),
}

results = {}
cv_scores = {}

for name, (model, use_scaled) in model_defs.items():
    X_fit  = X_train_scaled if use_scaled else X_train.values
    X_pred = X_test_scaled  if use_scaled else X_test.values

    model.fit(X_fit, y_train)
    y_pred = model.predict(X_pred)
    y_prob = model.predict_proba(X_pred)[:, 1]

    cv = cross_val_score(model, X_fit, y_train, cv=5, scoring="accuracy")
    cv_scores[name] = cv

    results[name] = {
        "Accuracy" : accuracy_score(y_test, y_pred),
        "Binary F1": f1_score(y_test, y_pred, zero_division=0),
        "Macro F1" : f1_score(y_test, y_pred, average="macro", zero_division=0),
        "AUC-ROC"  : roc_auc_score(y_test, y_prob),
        "CV Acc"   : f"{cv.mean():.4f} +/- {cv.std():.4f}",
        "model"    : model,
        "y_pred"   : y_pred,
    }
    print(f"    {name:<22}  Acc={results[name]['Accuracy']:.4f}  "
          f"MacroF1={results[name]['Macro F1']:.4f}  "
          f"AUC={results[name]['AUC-ROC']:.4f}  "
          f"CV={results[name]['CV Acc']}")

best_name = max(results, key=lambda k: results[k]["Macro F1"])

# -------------------------------------------------------------
# 6. RESULTS TABLE
# -------------------------------------------------------------
print("\n[5/5] Results summary")
print()

COL_W = [22, 10, 10, 10, 10, 18]
HEADERS = ["Model", "Accuracy", "Binary F1", "Macro F1", "AUC-ROC", "5-Fold CV Acc"]

def row_str(cells):
    return "  ".join(str(c).ljust(w) for c, w in zip(cells, COL_W))

sep = "-" * (sum(COL_W) + 2 * len(COL_W))
print(sep)
print(row_str(HEADERS))
print(sep)

# Naive baseline row
n = naive
print(row_str([
    "Naive Baseline",
    f"{n['Accuracy']:.4f}",
    f"{n['Binary F1']:.4f}",
    f"{n['Macro F1']:.4f}",
    f"{n['AUC-ROC']:.4f}",
    n["CV Acc"],
]))

for name, r in results.items():
    tag = "  <- BEST" if name == best_name else ""
    print(row_str([
        name + tag,
        f"{r['Accuracy']:.4f}",
        f"{r['Binary F1']:.4f}",
        f"{r['Macro F1']:.4f}",
        f"{r['AUC-ROC']:.4f}",
        r["CV Acc"],
    ]))

print(sep)
print(f"\n  Best model (Macro F1): {best_name}")

# -------------------------------------------------------------
# 7. PAIRED T-TESTS  (best vs. others)
# -------------------------------------------------------------
print("\n  Paired t-test (5-fold CV, best vs. others):")
for name in results:
    if name == best_name:
        continue
    t, p = stats.ttest_rel(cv_scores[best_name], cv_scores[name])
    sig = "significant" if p < 0.05 else "NOT significant"
    print(f"    {best_name} vs {name:<22}  t={t:.3f}  p={p:.4f}  -> {sig}")

# -------------------------------------------------------------
# 8. FEATURE IMPORTANCES  (RF + GB)
# -------------------------------------------------------------
print("\n  Feature importances:")
for name in ["Random Forest", "Gradient Boosting"]:
    imp = results[name]["model"].feature_importances_
    ranked = sorted(zip(FEAT_LABELS, imp), key=lambda x: -x[1])
    print(f"    {name}:")
    for feat, val in ranked:
        bar = "#" * int(val * 40)
        print(f"      {feat:<18} {val:.4f}  {bar}")

# -------------------------------------------------------------
# 9. CONFUSION MATRICES
# -------------------------------------------------------------
print("\n  Confusion matrices (rows=Actual, cols=Predicted):")
print("              Loss   Win")
for name, r in results.items():
    cm = confusion_matrix(y_test, r["y_pred"])
    print(f"  {name}")
    for label, row_vals in zip(["  Actual Loss", "  Actual Win "], cm):
        print(f"    {label}   {row_vals[0]:4d}   {row_vals[1]:4d}")

print()
print("=" * 60)
print("  Done. Run generate_paper_journal.py to rebuild the PDF.")
print("=" * 60)
