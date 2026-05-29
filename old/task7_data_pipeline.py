"""
================================================================================
CS2 Match Outcome Prediction — Data Audit and Cleaning Pipeline
Task 7: Data Audit and Cleaning Protocol
================================================================================
Authors : Seisenbek Dias | Mergen Temirzhan | Onashov Aidos
Course  : Research Methods
Date    : April 2026
--------------------------------------------------------------------------------
Disclaimer: This dataset is synthetically generated for academic research
purposes only. It must not be used for commercial forecasting, sports betting,
player recruitment, or any form of competitive intelligence.
================================================================================
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — MOCK DATASET GENERATION  (n = 1,450)
# ─────────────────────────────────────────────────────────────────────────────
np.random.seed(42)
N = 1_450

SEPARATOR = "=" * 68

print(SEPARATOR)
print("  CS2 Match Outcome Prediction — Data Audit & Cleaning Pipeline")
print(SEPARATOR)

# ── 1a. Core feature distributions ───────────────────────────────────────────
#  X1a: Mean HLTV 2.0 Rating  — normally distributed around professional mean
mean_hltv_rating = np.random.normal(loc=1.05, scale=0.12, size=N)

#  X1b: Mean Team KPR (Kills Per Round) — narrower spread around 0.72
mean_kpr = np.random.normal(loc=0.72, scale=0.065, size=N)

#  X2: Head-to-Head Win Rate — Beta(5, 5) centres around 0.50 (neutral prior)
head_to_head_win_rate = np.random.beta(a=5, b=5, size=N)

#  X3: Map Win Rate — Beta(6, 5) gives a slight positive skew (pro teams
#      tend to play maps where they already perform well)
map_win_rate = np.random.beta(a=6, b=5, size=N)

# ── 1b. Inject structural outliers ───────────────────────────────────────────
#  HLTV outliers: 29 elite-anomaly matches where rating exceeded 1.85
rng_outlier = np.random.default_rng(seed=7)
hltv_outlier_idx = rng_outlier.choice(N, size=29, replace=False)
mean_hltv_rating[hltv_outlier_idx] = rng_outlier.uniform(low=1.86, high=2.05, size=29)

#  KPR outliers: 22 statistically impossible values (data entry / scraping errors)
kpr_outlier_idx = rng_outlier.choice(
    np.setdiff1d(np.arange(N), hltv_outlier_idx), size=22, replace=False
)
mean_kpr[kpr_outlier_idx] = rng_outlier.uniform(low=1.05, high=1.14, size=22)

# ── 1c. Generate binary outcome (correlated with predictors via logit link) ──
log_odds = (
    2.80 * (mean_hltv_rating - 1.05) +
    3.50 * (mean_kpr - 0.72) +
    1.80 * (head_to_head_win_rate - 0.50) +
    1.20 * (map_win_rate - 0.545)
)
prob_win    = 1 / (1 + np.exp(-log_odds))
match_outcome = np.random.binomial(n=1, p=prob_win, size=N).astype(int)

# ── 1d. Assemble raw DataFrame ───────────────────────────────────────────────
df_raw = pd.DataFrame({
    "match_outcome":          match_outcome,
    "mean_hltv_rating":       mean_hltv_rating,
    "mean_kpr":               mean_kpr,
    "head_to_head_win_rate":  head_to_head_win_rate,
    "map_win_rate":           map_win_rate,
})

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — INJECT STRUCTURAL MISSING DATA
# ─────────────────────────────────────────────────────────────────────────────
# X2 (Head-to-Head Win Rate): 28 % MCAR — teams with no prior matchup history
h2h_miss_n   = int(N * 0.28)          # = 406 records
h2h_miss_idx = np.random.choice(N, h2h_miss_n, replace=False)
df_raw.loc[h2h_miss_idx, "head_to_head_win_rate"] = np.nan

# X3 (Map Win Rate): 6 % MAR — newer rosters with limited map-specific data
map_miss_n   = int(N * 0.06)          # = 87 records
map_miss_idx = np.random.choice(
    np.setdiff1d(np.arange(N), h2h_miss_idx), map_miss_n, replace=False
)
df_raw.loc[map_miss_idx, "map_win_rate"] = np.nan

# ── 2a. Audit before cleaning ────────────────────────────────────────────────
print("\n[STEP 1]  MISSING DATA AUDIT  —  Raw Dataset")
print("-" * 68)
missing_count = df_raw.isnull().sum()
missing_pct   = (missing_count / N * 100).round(2)
audit_df = pd.DataFrame(
    {"Missing Count": missing_count, "Missing (%)": missing_pct}
)
print(audit_df.to_string())
print(f"\n  Total records   : {N:,}")
print(f"  Complete records: {df_raw.dropna().shape[0]:,}  "
      f"({df_raw.dropna().shape[0] / N * 100:.1f}% of dataset)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — OUTLIER DETECTION  (IQR method, pre-cleaning)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 2]  OUTLIER DETECTION  —  Before Winsorization")
print("-" * 68)

CONTINUOUS = ["mean_hltv_rating", "mean_kpr", "head_to_head_win_rate", "map_win_rate"]

for col in CONTINUOUS:
    q1  = df_raw[col].quantile(0.25)
    q3  = df_raw[col].quantile(0.75)
    iqr = q3 - q1
    lo  = q1 - 1.5 * iqr
    hi  = q3 + 1.5 * iqr
    n_out = int(((df_raw[col] < lo) | (df_raw[col] > hi)).sum())
    print(f"  {col:<28}  outliers={n_out:>3}  "
          f"IQR-fence=[{lo:.3f}, {hi:.3f}]")

print(f"\n  Pre-Winsorization HLTV — "
      f"min={df_raw['mean_hltv_rating'].min():.4f}, "
      f"max={df_raw['mean_hltv_rating'].max():.4f}")
print(f"  Pre-Winsorization KPR  — "
      f"min={df_raw['mean_kpr'].min():.4f}, "
      f"max={df_raw['mean_kpr'].max():.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — CLEANING PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
df = df_raw.copy()

# ── 4a. Neutral imputation — Head-to-Head Win Rate ──────────────────────────
#  Rationale: 0.50 is the epistemically neutral prior for an unknown matchup;
#  using the sample mean would artificially inflate/deflate values for teams
#  with no recorded history.
df["head_to_head_win_rate"] = df["head_to_head_win_rate"].fillna(0.50)

# ── 4b. Mean substitution — Map Win Rate ────────────────────────────────────
#  Rationale: missingness is MAR (linked to roster novelty) so the column
#  mean of observed values is an appropriate central estimator.
map_wr_mean = df["map_win_rate"].mean()          # computed BEFORE imputation
df["map_win_rate"] = df["map_win_rate"].fillna(map_wr_mean)

print(f"\n[STEP 3]  IMPUTATION")
print("-" * 68)
print(f"  Head-to-Head Win Rate  -> filled {h2h_miss_n} NaNs with 0.50 (neutral prior)")
print(f"  Map Win Rate           -> filled {map_miss_n} NaNs with mean = {map_wr_mean:.4f}")

# ── 4c. Winsorization — clip at 1st and 99th percentiles ────────────────────
winsor_report = {}
for col in CONTINUOUS:
    p01 = df[col].quantile(0.01)
    p99 = df[col].quantile(0.99)
    n_clipped_low  = int((df[col] < p01).sum())
    n_clipped_high = int((df[col] > p99).sum())
    df[col] = df[col].clip(lower=p01, upper=p99)
    winsor_report[col] = {
        "1st-pct cap": round(p01, 4),
        "99th-pct cap": round(p99, 4),
        "clipped low": n_clipped_low,
        "clipped high": n_clipped_high,
    }

print(f"\n[STEP 4]  WINSORIZATION RESULTS  (1st / 99th percentile)")
print("-" * 68)
for col, stats in winsor_report.items():
    print(f"  {col:<28}  "
          f"floor={stats['1st-pct cap']:.4f}  "
          f"cap={stats['99th-pct cap']:.4f}  "
          f"clipped_lo={stats['clipped low']}  "
          f"clipped_hi={stats['clipped high']}")

print(f"\n  Post-Winsorization HLTV — "
      f"min={df['mean_hltv_rating'].min():.4f}, "
      f"max={df['mean_hltv_rating'].max():.4f}")
print(f"  Post-Winsorization KPR  — "
      f"min={df['mean_kpr'].min():.4f}, "
      f"max={df['mean_kpr'].max():.4f}")

# ── 4d. Confirm zero missing values ─────────────────────────────────────────
print(f"\n[STEP 5]  MISSING DATA POST-IMPUTATION CHECK")
print("-" * 68)
remaining_nulls = df.isnull().sum()
print(remaining_nulls.to_string())
assert remaining_nulls.sum() == 0, "ERROR: Unresolved missing values detected."
print("  Assertion passed — zero missing values in cleaned dataset.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — TARGET ENCODING AND CLASS DISTRIBUTION
# ─────────────────────────────────────────────────────────────────────────────
#  match_outcome already encoded: 1 = Win, 0 = Loss
print(f"\n[STEP 6]  TARGET VARIABLE  —  Class Distribution")
print("-" * 68)
vc = df["match_outcome"].value_counts().sort_index(ascending=False)
for label, count in vc.items():
    tag = "Win" if label == 1 else "Loss"
    print(f"  {tag} ({label}): {count:>5} records  ({count / N * 100:.2f}%)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — TRAIN / TEST SPLIT  (80/20, stratified, random_state=42)
# ─────────────────────────────────────────────────────────────────────────────
FEATURES = ["mean_hltv_rating", "mean_kpr", "head_to_head_win_rate", "map_win_rate"]
TARGET   = "match_outcome"

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y          # preserves class proportions in both splits
)

print(f"\n[STEP 7]  TRAIN / TEST SPLIT  (80 / 20, stratified)")
print("-" * 68)
print(f"  Training set : {X_train.shape[0]:>5} records  "
      f"({X_train.shape[0] / N * 100:.1f}%)")
print(f"  Test set     : {X_test.shape[0]:>5} records  "
      f"({X_test.shape[0] / N * 100:.1f}%)")
print(f"  Train class balance — "
      f"Win={y_train.sum()} ({y_train.mean()*100:.1f}%)  "
      f"Loss={len(y_train)-y_train.sum()} ({(1-y_train.mean())*100:.1f}%)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — Z-SCORE STANDARDIZATION
# ─────────────────────────────────────────────────────────────────────────────
#  Fit scaler on training data ONLY; apply (transform) to test set to prevent
#  data leakage from test statistics influencing the training distribution.
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(
    scaler.fit_transform(X_train),
    columns=FEATURES,
    index=X_train.index
)
X_test_scaled = pd.DataFrame(
    scaler.transform(X_test),
    columns=FEATURES,
    index=X_test.index
)

print(f"\n[STEP 8]  Z-SCORE STANDARDIZATION  (fit on training set only)")
print("-" * 68)
print(f"  {'Feature':<28}  {'Train Mean':>10}  {'Train Std':>10}")
print(f"  {'-' * 52}")
for i, col in enumerate(FEATURES):
    print(f"  {col:<28}  {scaler.mean_[i]:>10.4f}  {scaler.scale_[i]:>10.4f}")

print(f"\n  Verify standardization — "
      f"X_train_scaled mean ≈ {X_train_scaled.mean().mean():.6f}  "
      f"(should be ~0.0)")
print(f"  Verify standardization — "
      f"X_train_scaled std  ≈ {X_train_scaled.std().mean():.6f}  "
      f"(should be ~1.0)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — FINAL DATASET SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[STEP 9]  FINAL DATASET DIMENSIONS")
print("-" * 68)
print(f"  X_train_scaled : {X_train_scaled.shape}")
print(f"  X_test_scaled  : {X_test_scaled.shape}")
print(f"  y_train        : {y_train.shape}")
print(f"  y_test         : {y_test.shape}")

print(f"\n[STEP 10]  SAMPLE — First 5 rows of scaled training features")
print("-" * 68)
print(X_train_scaled.head().round(4).to_string())

print(f"\n{SEPARATOR}")
print("  Pipeline complete. Cleaned & standardized dataset ready for modelling.")
print(SEPARATOR)

# ─────────────────────────────────────────────────────────────────────────────
# Optional: export cleaned datasets for downstream modelling
# ─────────────────────────────────────────────────────────────────────────────
# X_train_scaled.to_csv("X_train_scaled.csv", index=False)
# X_test_scaled.to_csv("X_test_scaled.csv",  index=False)
# y_train.to_csv("y_train.csv", index=False)
# y_test.to_csv("y_test.csv",   index=False)
