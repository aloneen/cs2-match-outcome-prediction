"""
================================================================================
CS2 Match Outcome Prediction — Data Audit and Cleaning Pipeline
================================================================================
Author   : Seisenbek Dias
Course   : Research Methods
Dataset  : CS2 HLTV Professional Match Statistics (griffindesroches, Kaggle)
Source   : HLTV.org (aggregated via Kaggle)
Coverage : May 2024 - October 2025 | 7,033 matches | 648 tournaments
--------------------------------------------------------------------------------
Disclaimer: For academic research only. Not for betting, recruitment,
or any form of commercial use.
================================================================================
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

SEPARATOR = "=" * 72
CSV_PATH  = "data/cs2_newestcombinedmatches_team1_reference_reduced2.csv"

# Map name -> team1 win-rate column in the dataset
MAP_COL_LOOKUP = {
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

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — LOAD RAW DATA
# ─────────────────────────────────────────────────────────────────────────────
print(SEPARATOR)
print("  CS2 Match Outcome Prediction — Real Data Pipeline (HLTV via Kaggle)")
print(SEPARATOR)

df_raw = pd.read_csv(CSV_PATH, low_memory=False)

print(f"\n[STEP 1]  DATASET LOADED")
print("-" * 72)
print(f"  File          : {CSV_PATH}")
print(f"  Total rows    : {len(df_raw):,}")
print(f"  Total columns : {len(df_raw.columns)}")
print(f"  Date range    : {df_raw['date'].min()[:10]}  to  {df_raw['date'].max()[:10]}")
print(f"  Tournaments   : {df_raw['tournament'].nunique()}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — FEATURE ENGINEERING
# Map raw HLTV columns -> 5 model variables defined in Task 5
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[STEP 2]  FEATURE ENGINEERING")
print("-" * 72)

df = df_raw.copy()

# ── Y: Match Outcome (binary 1=Win / 0=Loss from team1 perspective) ──────────
# Column team1_win_flag is already 0/1 — no transformation needed
df['match_outcome'] = df['team1_win_flag'].astype(int)
print(f"  match_outcome       <- team1_win_flag          (no transform needed)")

# ── X1a: Mean HLTV 2.0 Rating ─────────────────────────────────────────────────
# team1_avg_RATING is the pre-computed mean across the 5-player roster
df['mean_hltv_rating'] = pd.to_numeric(df['team1_avg_RATING'], errors='coerce')
print(f"  mean_hltv_rating    <- team1_avg_RATING         (direct map)")

# ── X1b: Mean KPR (Kills Per Round) ───────────────────────────────────────────
df['mean_kpr'] = pd.to_numeric(df['team1_avg_KPR'], errors='coerce')
print(f"  mean_kpr            <- team1_avg_KPR            (direct map)")

# ── X2: Head-to-Head Win Rate ─────────────────────────────────────────────────
# team1_head2head_percentage is stored as 0-100; divide by 100 to get [0, 1]
df['head_to_head_win_rate'] = pd.to_numeric(
    df['team1_head2head_percentage'], errors='coerce') / 100.0
print(f"  head_to_head_win_rate <- team1_head2head_percentage / 100")

# ── X3: Map Win Rate ───────────────────────────────────────────────────────────
# decider_map tells us which map was played; look up team1's win rate on that map
# Map-specific win rates are stored as 0-100 percentages -> divide by 100
def get_map_winrate(row):
    map_name = str(row.get('decider_map', '')).strip().lower()
    col = MAP_COL_LOOKUP.get(map_name)
    if col and col in row.index:
        val = row[col]
        try:
            return float(val) / 100.0
        except (ValueError, TypeError):
            return np.nan
    return np.nan

df['map_win_rate'] = df.apply(get_map_winrate, axis=1)
print(f"  map_win_rate        <- team1_[decider_map] / 100  (lookup by map played)")

# ── Assemble model DataFrame ──────────────────────────────────────────────────
TARGET_COLS = ['match_outcome', 'mean_hltv_rating', 'mean_kpr',
               'head_to_head_win_rate', 'map_win_rate']
df_model = df[TARGET_COLS].copy()
N = len(df_model)

print(f"\n  Model DataFrame shape : {df_model.shape}")
print(f"\n  Sample (first 5 rows):")
print(df_model.head().round(4).to_string())

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — MISSING DATA AUDIT
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[STEP 3]  MISSING DATA AUDIT  (n = {N:,})")
print("-" * 72)
missing_count = df_model.isnull().sum()
missing_pct   = (missing_count / N * 100).round(2)
audit_df = pd.DataFrame({'Missing Count': missing_count, 'Missing (%)': missing_pct})
print(audit_df.to_string())
complete = df_model.dropna().shape[0]
print(f"\n  Complete records (no missing) : {complete:,}  ({complete/N*100:.1f}%)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — OUTLIER DETECTION (IQR method, pre-cleaning)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[STEP 4]  OUTLIER DETECTION  (IQR method, pre-cleaning)")
print("-" * 72)

CONTINUOUS = ['mean_hltv_rating', 'mean_kpr', 'head_to_head_win_rate', 'map_win_rate']

outlier_report = {}
for col in CONTINUOUS:
    q1  = df_model[col].quantile(0.25)
    q3  = df_model[col].quantile(0.75)
    iqr = q3 - q1
    lo  = q1 - 1.5 * iqr
    hi  = q3 + 1.5 * iqr
    n_out = int(((df_model[col] < lo) | (df_model[col] > hi)).sum())
    outlier_report[col] = {'lo': lo, 'hi': hi, 'n': n_out}
    print(f"  {col:<28}  outliers={n_out:>4}  fence=[{lo:.4f}, {hi:.4f}]")

print(f"\n  Pre-Winsorization HLTV : "
      f"min={df_model['mean_hltv_rating'].min():.4f}  "
      f"max={df_model['mean_hltv_rating'].max():.4f}")
print(f"  Pre-Winsorization KPR  : "
      f"min={df_model['mean_kpr'].min():.4f}  "
      f"max={df_model['mean_kpr'].max():.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — CLEANING PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
df_clean = df_model.copy()

# ── 5a. Neutral imputation — Head-to-Head Win Rate (MCAR) ────────────────────
# Teams with no prior history against this opponent -> neutral 50/50 prior
h2h_missing = int(df_clean['head_to_head_win_rate'].isnull().sum())
df_clean['head_to_head_win_rate'] = df_clean['head_to_head_win_rate'].fillna(0.50)

# ── 5b. Mean substitution — Map Win Rate (MAR) ───────────────────────────────
# Missing when decider_map was not recorded; observed values are an unbiased sample
map_wr_mean   = df_clean['map_win_rate'].mean()
map_wr_missing = int(df_clean['map_win_rate'].isnull().sum())
df_clean['map_win_rate'] = df_clean['map_win_rate'].fillna(map_wr_mean)

# ── 5c. Mean substitution — any residual NaNs in rating/KPR ─────────────────
for col in ['mean_hltv_rating', 'mean_kpr']:
    n_miss = int(df_clean[col].isnull().sum())
    if n_miss > 0:
        df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        print(f"  {col}: {n_miss} residual NaN -> column mean")

print(f"\n[STEP 5]  IMPUTATION")
print("-" * 72)
print(f"  head_to_head_win_rate : {h2h_missing} NaNs -> 0.50 (neutral prior)")
print(f"  map_win_rate          : {map_wr_missing} NaNs -> mean = {map_wr_mean:.4f}")

# ── 5d. Winsorization — clip at 1st and 99th percentiles ─────────────────────
print(f"\n[STEP 6]  WINSORIZATION  (1st / 99th percentile)")
print("-" * 72)

winsor_report = {}
for col in CONTINUOUS:
    p01 = df_clean[col].quantile(0.01)
    p99 = df_clean[col].quantile(0.99)
    n_lo = int((df_clean[col] < p01).sum())
    n_hi = int((df_clean[col] > p99).sum())
    df_clean[col] = df_clean[col].clip(lower=p01, upper=p99)
    winsor_report[col] = {
        'floor': round(p01, 4), 'cap': round(p99, 4),
        'clipped_low': n_lo, 'clipped_high': n_hi
    }
    print(f"  {col:<28}  floor={p01:.4f}  cap={p99:.4f}  "
          f"clipped_lo={n_lo}  clipped_hi={n_hi}")

print(f"\n  Post-Winsorization HLTV : "
      f"min={df_clean['mean_hltv_rating'].min():.4f}  "
      f"max={df_clean['mean_hltv_rating'].max():.4f}")
print(f"  Post-Winsorization KPR  : "
      f"min={df_clean['mean_kpr'].min():.4f}  "
      f"max={df_clean['mean_kpr'].max():.4f}")

# ── 5e. Verify zero missing values ───────────────────────────────────────────
print(f"\n[STEP 7]  POST-CLEANING VERIFICATION")
print("-" * 72)
remaining = df_clean.isnull().sum()
print(remaining.to_string())
assert remaining.sum() == 0, "ERROR: Unresolved missing values remain."
print("  Assertion passed -- zero missing values in cleaned dataset.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — TARGET VARIABLE DISTRIBUTION
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[STEP 8]  TARGET VARIABLE DISTRIBUTION")
print("-" * 72)
vc = df_clean['match_outcome'].value_counts().sort_index(ascending=False)
for label, count in vc.items():
    tag = "Win" if label == 1 else "Loss"
    print(f"  {tag} ({label}): {count:>5}  ({count/N*100:.2f}%)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — TRAIN / TEST SPLIT (80/20, stratified, random_state=42)
# ─────────────────────────────────────────────────────────────────────────────
FEATURES = ['mean_hltv_rating', 'mean_kpr', 'head_to_head_win_rate', 'map_win_rate']
TARGET   = 'match_outcome'

X = df_clean[FEATURES]
y = df_clean[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"\n[STEP 9]  TRAIN / TEST SPLIT  (80/20, stratified)")
print("-" * 72)
print(f"  Training set  : {X_train.shape[0]:>5} records  ({X_train.shape[0]/N*100:.1f}%)")
print(f"  Test set      : {X_test.shape[0]:>5} records  ({X_test.shape[0]/N*100:.1f}%)")
print(f"  Train Win rate: {y_train.mean()*100:.1f}%  |  "
      f"Test Win rate : {y_test.mean()*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — Z-SCORE STANDARDIZATION
# ─────────────────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(
    scaler.fit_transform(X_train), columns=FEATURES, index=X_train.index
)
X_test_scaled = pd.DataFrame(
    scaler.transform(X_test), columns=FEATURES, index=X_test.index
)

print(f"\n[STEP 10]  Z-SCORE STANDARDIZATION  (fit on training set only)")
print("-" * 72)
print(f"  {'Feature':<28}  {'Train Mean':>10}  {'Train Std':>10}")
print(f"  {'-'*52}")
for i, col in enumerate(FEATURES):
    print(f"  {col:<28}  {scaler.mean_[i]:>10.4f}  {scaler.scale_[i]:>10.4f}")

print(f"\n  Column-wise mean : {X_train_scaled.mean().mean():.8f}  (expect ~0.0)")
print(f"  Column-wise std  : {X_train_scaled.std().mean():.8f}  (expect ~1.0)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — DESCRIPTIVE STATISTICS & SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[STEP 11]  DESCRIPTIVE STATISTICS  (cleaned features)")
print("-" * 72)
print(df_clean[FEATURES].describe().round(4).to_string())

print(f"\n[STEP 12]  FINAL SUMMARY")
print("-" * 72)
print(f"  Raw rows              : {N:,}")
print(f"  Rows retained         : {len(df_clean):,}  (0 dropped)")
print(f"  X_train_scaled shape  : {X_train_scaled.shape}")
print(f"  X_test_scaled shape   : {X_test_scaled.shape}")
print(f"  y_train shape         : {y_train.shape}")
print(f"  y_test shape          : {y_test.shape}")

print(f"\n{SEPARATOR}")
print("  Pipeline complete. Real HLTV data cleaned and ready for modelling.")
print(SEPARATOR)
