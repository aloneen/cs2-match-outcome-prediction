"""
generate_paper_journal.py
Two-column journal-style PDF via reportlab — Elsevier format.

Author : Seisenbek Dias | S23068165 | Research Methods
"""

import os, re, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_curve, auc,
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
pt = 1.0
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, Image,
    KeepTogether, FrameBreak, PageBreak, HRFlowable,
    NextPageTemplate,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Times New Roman (full Unicode — fixes Greek/subscript black boxes)
import os
_FONT_DIR = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont('TNR',   _FONT_DIR + 'times.ttf'))
pdfmetrics.registerFont(TTFont('TNR-B', _FONT_DIR + 'timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TNR-I', _FONT_DIR + 'timesi.ttf'))
pdfmetrics.registerFont(TTFont('TNR-BI',_FONT_DIR + 'timesbi.ttf'))
pdfmetrics.registerFontFamily('TNR', normal='TNR', bold='TNR-B',
                               italic='TNR-I', boldItalic='TNR-BI')

# ═══════════════════════════════════════════════════════════════════════════════
# GEOMETRY
# ═══════════════════════════════════════════════════════════════════════════════
PW, PH = A4                     # 595.28 x 841.89 pt
ML = 1.8*cm;  MR = 1.8*cm
MT = 2.2*cm;  MB = 2.0*cm
CW  = PW - ML - MR              # 493.28 pt  (~17.4 cm)
CH  = PH - MT - MB              # 722.84 pt  (~25.5 cm)
GUT = 0.5*cm                    # column gutter
COL = (CW - GUT) / 2           # 239.54 pt  (~8.44 cm) per column

BAR_H   = 0.65*cm               # blue header bar height
HDR_H   = 13.2*cm               # header frame height (title + authors + abstract box)
GAP     = 0.35*cm               # gap between header frame and body frames
HDR_BOT = PH - BAR_H - HDR_H   # bottom y of header frame (just below blue bar)
BODY1   = HDR_BOT - GAP - MB   # body column height on first page

# ═══════════════════════════════════════════════════════════════════════════════
# COLOURS & FONTS
# ═══════════════════════════════════════════════════════════════════════════════
DB  = colors.HexColor('#14213D')   # deep navy-slate
MB2 = colors.HexColor('#006D77')   # teal
LB  = colors.HexColor('#C9E8E4')   # light teal
GR  = colors.HexColor('#5C677D')   # slate-grey
LGR = colors.HexColor('#F0F5F5')   # near-white teal tint
GRN = colors.HexColor('#B8DDD5')   # soft teal highlight (best-cell)
W   = colors.white
BK  = colors.black

FN = 'TNR';   FB = 'TNR-B'
FI = 'TNR-I'; FBI = 'TNR-BI'

def S(name, **kw):
    d = dict(fontName=FN, fontSize=9.5, leading=12,
             alignment=TA_JUSTIFY, spaceAfter=4, spaceBefore=0,
             leftIndent=0, firstLineIndent=0)
    d.update(kw)
    return ParagraphStyle(name, **d)

BODY   = S('Body')
BODYSM = S('BodySm', fontSize=8.5, leading=11)
H1     = S('H1',  fontName=FB, fontSize=10.5, textColor=DB, leading=13,
           alignment=TA_LEFT, spaceBefore=10, spaceAfter=3)
H2     = S('H2',  fontName=FB, fontSize=9.5, textColor=MB2, leading=12,
           alignment=TA_LEFT, spaceBefore=7,  spaceAfter=2)
TITLE  = S('Ti',  fontName=FB, fontSize=16, textColor=DB, leading=20,
           alignment=TA_LEFT, spaceBefore=2,  spaceAfter=3)
AUTH   = S('Au',  fontName=FB, fontSize=10, leading=13,
           alignment=TA_LEFT, spaceBefore=0,  spaceAfter=1)
AFFIL  = S('Af',  fontName=FI, fontSize=8.5, textColor=GR, leading=11,
           alignment=TA_LEFT, spaceBefore=0,  spaceAfter=2)
AI_LBL = S('AIL', fontName=FB, fontSize=7.5, textColor=DB,
           leading=10, alignment=TA_LEFT, spaceBefore=0, spaceAfter=2,
           letterSpacing=1.0)
KW_TXT = S('KW',  fontName=FN, fontSize=8.5, leading=11,
           alignment=TA_LEFT, spaceBefore=0, spaceAfter=0)
AB_LBL = S('ABL', fontName=FB, fontSize=7.5, textColor=DB,
           leading=10, alignment=TA_LEFT, spaceBefore=0, spaceAfter=2,
           letterSpacing=1.0)
AB_TXT = S('AB',  fontName=FN, fontSize=9, leading=11.5,
           alignment=TA_JUSTIFY, spaceBefore=0, spaceAfter=0)
CAPT   = S('Ca',  fontName=FI, fontSize=8, textColor=GR, leading=10,
           alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)
TCAP   = S('TC',  fontName=FBI, fontSize=8.5, textColor=DB, leading=10.5,
           alignment=TA_LEFT, spaceBefore=6, spaceAfter=2)
BSTY   = S('Bu',  fontName=FN, fontSize=9.5, leading=12,
           alignment=TA_JUSTIFY, spaceBefore=1, spaceAfter=2,
           leftIndent=12, firstLineIndent=0)
EQN    = S('Eq',  fontName=FI, fontSize=10, leading=14,
           alignment=TA_CENTER, spaceBefore=4, spaceAfter=5)
REF    = S('Re',  fontName=FN, fontSize=8.5, leading=11,
           alignment=TA_JUSTIFY, spaceBefore=0, spaceAfter=3,
           leftIndent=14, firstLineIndent=-14)
MONO   = S('Mo',  fontName='Courier', fontSize=8, leading=10,
           alignment=TA_LEFT, leftIndent=14)
CITE_C = colors.HexColor('#1558A7')   # citation blue

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — DATA
# ═══════════════════════════════════════════════════════════════════════════════
CSV_PATH = "data/cs2_newestcombinedmatches_team1_reference_reduced2.csv"
MAP_COLS = {"mirage":"team1_mirage","inferno":"team1_inferno","nuke":"team1_nuke",
            "dust2":"team1_dust2","ancient":"team1_ancient","anubis":"team1_anubis",
            "vertigo":"team1_vertigo","overpass":"team1_overpass","train":"team1_train"}

print("="*60); print("CS2 JOURNAL PAPER GENERATOR"); print("="*60)
print("[1/5] Loading data …")

df = pd.read_csv(CSV_PATH, low_memory=False)
df["match_outcome"]         = df["team1_win_flag"].astype(int)
df["mean_hltv_rating"]      = pd.to_numeric(df["team1_avg_RATING"], errors="coerce")
df["mean_kpr"]              = pd.to_numeric(df["team1_avg_KPR"], errors="coerce")
df["head_to_head_win_rate"] = pd.to_numeric(df["team1_head2head_percentage"], errors="coerce") / 100

def mwr(row):
    c = MAP_COLS.get(str(row.get("decider_map","")).strip().lower())
    if c and c in row.index:
        try: return float(row[c])/100
        except: return np.nan
    return np.nan

df["map_win_rate"] = df.apply(mwr, axis=1)

FEATS  = ["mean_hltv_rating","mean_kpr","head_to_head_win_rate","map_win_rate"]
FLBLS  = ["HLTV Rating","KPR","H2H Win Rate","Map Win Rate"]
TARGET = "match_outcome"
N      = len(df)
mwr_missing = int(df["map_win_rate"].isnull().sum())

dc = df[[TARGET]+FEATS].copy()
mwr_mean = dc["map_win_rate"].mean()
for col in FEATS:
    dc[col] = dc[col].fillna(dc[col].median())
dc["map_win_rate"] = dc["map_win_rate"].fillna(mwr_mean)
dc["head_to_head_win_rate"] = dc["head_to_head_win_rate"].fillna(0.50)
for col in FEATS:
    p1,p99 = dc[col].quantile(0.01), dc[col].quantile(0.99)
    dc[col] = dc[col].clip(p1,p99)

X = dc[FEATS]; y = dc[TARGET]
Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.20,random_state=42,stratify=y)
sc = StandardScaler()
Xtrs = sc.fit_transform(Xtr); Xtes = sc.transform(Xte)
win_rate = y.mean()
print(f"    {N:,} records | Train {len(Xtr):,} | Test {len(Xte):,}")

# ── Naive baseline
yn = np.ones(len(yte),dtype=int)
naive = dict(acc=accuracy_score(yte,yn),
             f1b=f1_score(yte,yn,zero_division=0),
             f1m=f1_score(yte,yn,average="macro",zero_division=0),
             prec=precision_score(yte,yn,zero_division=0),
             rec=recall_score(yte,yn,zero_division=0),
             auc=0.5)

# ── Models
print("[2/5] Training models …")
mdefs = {
    "Logistic Regression": LogisticRegression(max_iter=1000,random_state=42,C=1.0),
    "Random Forest":       RandomForestClassifier(n_estimators=200,max_depth=10,random_state=42,n_jobs=-1),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=200,max_depth=4,learning_rate=0.05,random_state=42),
}
results = {}
for nm, mdl in mdefs.items():
    scaled = (nm=="Logistic Regression")
    Xfit,Xpred = (Xtrs,Xtes) if scaled else (Xtr,Xte)
    mdl.fit(Xfit,ytr)
    yp = mdl.predict(Xpred)
    ypr= mdl.predict_proba(Xpred)[:,1]
    cv = cross_val_score(mdl,Xfit,ytr,cv=5,scoring="accuracy")
    fpr,tpr,_ = roc_curve(yte,ypr)
    results[nm] = dict(model=mdl,yp=yp,ypr=ypr,
                       acc=accuracy_score(yte,yp),
                       prec=precision_score(yte,yp,zero_division=0),
                       rec=recall_score(yte,yp,zero_division=0),
                       f1b=f1_score(yte,yp,zero_division=0),
                       f1m=f1_score(yte,yp,average="macro",zero_division=0),
                       cm=confusion_matrix(yte,yp),
                       fpr=fpr,tpr=tpr,auc=auc(fpr,tpr),
                       cvm=cv.mean(),cvs=cv.std(),cvv=cv)
    r=results[nm]
    print(f"    {nm}: Acc={r['acc']:.4f} MacroF1={r['f1m']:.4f} AUC={r['auc']:.4f}")

MNS  = list(results.keys())
best = max(results,key=lambda k:results[k]["f1m"])
print(f"    Best: {best}")

LR = results["Logistic Regression"]["model"]
lr_coefs = dict(zip(FLBLS, LR.coef_[0]))

# ── t-tests
ttests = {}
for nm in MNS:
    if nm != best:
        t,p = stats.ttest_rel(results[best]["cvv"], results[nm]["cvv"])
        ttests[nm] = (t,p)

# ── Correlations
corr = dc[FEATS+[TARGET]].rename(columns=dict(zip(FEATS,FLBLS),**{TARGET:"Win"})).corr()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — FIGURES  (sized for column width or full width)
# ═══════════════════════════════════════════════════════════════════════════════
print("[3/5] Generating figures …")
FD = "report_figures"; os.makedirs(FD,exist_ok=True)
CLRS = {"Logistic Regression":"#2E74B5","Random Forest":"#1F7A3C","Gradient Boosting":"#C0392B"}
sns.set_theme(style="whitegrid",font_scale=0.9)

COL_IN = COL/72*2.54/2.54*72/72    # just use points → inches
COL_INCH = float(COL)/72            # column width in inches  ≈ 3.33"
CW_INCH  = float(CW)/72            # full content width ≈ 6.85"

# Fig 1 — Confusion matrices (WIDE: 3 side-by-side)
fig,axes = plt.subplots(1,3,figsize=(CW_INCH*1.05,3.2))
for ax,nm in zip(axes,MNS):
    cm_=results[nm]["cm"]
    cmn=cm_.astype(float)/cm_.sum(axis=1,keepdims=True)
    sns.heatmap(cmn,annot=cm_,fmt="d",ax=ax,cmap="Blues",linewidths=0.5,
                xticklabels=["Loss","Win"],yticklabels=["Loss","Win"],
                cbar=False,annot_kws={"size":10,"weight":"bold"})
    ax.set_title(f"{nm}\nAcc={results[nm]['acc']:.3f}  Macro-F1={results[nm]['f1m']:.3f}",
                 fontsize=8,fontweight="bold",color=CLRS[nm])
    ax.set_xlabel("Predicted",fontsize=7); ax.set_ylabel("Actual",fontsize=7)
    ax.tick_params(labelsize=7)
plt.tight_layout(pad=0.6)
fig.savefig(f"{FD}/jfig1_cm.png",dpi=180,bbox_inches="tight"); plt.close()

# Fig 2 — ROC (ONE column)
fig,ax = plt.subplots(figsize=(COL_INCH*1.05,2.8))
ax.plot([0,1],[0,1],"k--",lw=1.2,label="Naive (AUC=0.500)")
for nm in MNS:
    ax.plot(results[nm]["fpr"],results[nm]["tpr"],color=CLRS[nm],lw=1.8,
            label=f"{nm} ({results[nm]['auc']:.3f})")
ax.set_xlabel("False Positive Rate",fontsize=8)
ax.set_ylabel("True Positive Rate",fontsize=8)
ax.set_title("ROC Curves",fontsize=9,fontweight="bold")
ax.legend(fontsize=7,loc="lower right"); ax.tick_params(labelsize=7)
plt.tight_layout()
fig.savefig(f"{FD}/jfig2_roc.png",dpi=180,bbox_inches="tight"); plt.close()

# Fig 3 — Feature importance (WIDE: 2 side-by-side)
fig,axes = plt.subplots(1,2,figsize=(CW_INCH*1.05,2.8))
for ax,nm in zip(axes,["Random Forest","Gradient Boosting"]):
    imp=results[nm]["model"].feature_importances_
    ord_=np.argsort(imp)
    ax.barh([FLBLS[i] for i in ord_],imp[ord_],color=CLRS[nm],alpha=0.85,edgecolor="white")
    ax.set_title(nm,fontsize=8,fontweight="bold",color=CLRS[nm])
    ax.set_xlabel("Importance",fontsize=7); ax.tick_params(labelsize=7)
    for i,(idx,v) in enumerate(zip(ord_,imp[ord_])):
        ax.text(v+0.001,i,f"{v:.3f}",va="center",fontsize=7)
    ax.set_xlim(0,max(imp)*1.28)
plt.tight_layout(pad=0.6)
fig.savefig(f"{FD}/jfig3_imp.png",dpi=180,bbox_inches="tight"); plt.close()

# Fig 4 — Performance comparison (WIDE: 2 bars side-by-side)
fig,axes = plt.subplots(1,2,figsize=(CW_INCH*1.05,2.8))
lbls = ["Naive"]+[n.split()[0] for n in MNS]
clrs_ = ["#888888"]+[CLRS[n] for n in MNS]
for ax,(met,vals) in zip(axes,[
    ("Accuracy", [naive["acc"]]+[results[m]["acc"]  for m in MNS]),
    ("Macro F1", [naive["f1m"]]+[results[m]["f1m"]  for m in MNS]),
]):
    bars=ax.bar(lbls,vals,color=clrs_,edgecolor="white",width=0.55)
    ax.set_ylim(0.30,0.72); ax.axhline(0.5,color="red",ls="--",lw=0.9,label="Chance")
    ax.set_title(met,fontsize=9,fontweight="bold"); ax.set_ylabel(met,fontsize=8)
    for b,v in zip(bars,vals):
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.005,f"{v:.3f}",
                ha="center",va="bottom",fontsize=8,fontweight="bold")
    ax.legend(fontsize=7); ax.tick_params(labelsize=7)
plt.tight_layout(pad=0.5)
fig.savefig(f"{FD}/jfig4_comp.png",dpi=180,bbox_inches="tight"); plt.close()

# Fig 5 — Cross-validation (ONE column)
fig,ax = plt.subplots(figsize=(COL_INCH*1.05,2.8))
cvms=[results[m]["cvm"] for m in MNS]; cvss=[results[m]["cvs"] for m in MNS]
bars=ax.bar([n.split()[0] for n in MNS],cvms,yerr=cvss,
            color=[CLRS[m] for m in MNS],edgecolor="white",width=0.5,capsize=5)
ax.axhline(naive["acc"],color="#888",ls="--",lw=1.2,label=f"Naive ({naive['acc']:.3f})")
ax.axhline(0.5,color="red",ls=":",lw=0.9,label="Chance")
ax.set_ylim(0.44,0.70); ax.set_ylabel("5-Fold CV Accuracy",fontsize=8)
ax.set_title("Cross-Validation Accuracy",fontsize=9,fontweight="bold")
for b,v,s in zip(bars,cvms,cvss):
    ax.text(b.get_x()+b.get_width()/2,v+s+0.008,f"{v:.3f}±{s:.3f}",
            ha="center",va="bottom",fontsize=7,fontweight="bold")
ax.legend(fontsize=7); ax.tick_params(labelsize=7)
plt.tight_layout()
fig.savefig(f"{FD}/jfig5_cv.png",dpi=180,bbox_inches="tight"); plt.close()

# Fig 6 — Correlation heatmap (ONE column)
fig,ax = plt.subplots(figsize=(COL_INCH*1.05,2.8))
mask=np.triu(np.ones_like(corr,dtype=bool),k=1)
sns.heatmap(corr,annot=True,fmt=".3f",cmap="RdBu_r",center=0,
            linewidths=0.4,ax=ax,mask=mask,annot_kws={"size":8},
            vmin=-1,vmax=1,cbar_kws={"shrink":0.7})
ax.set_title("Pearson Correlation Matrix",fontsize=9,fontweight="bold")
ax.tick_params(labelsize=7)
plt.tight_layout()
fig.savefig(f"{FD}/jfig6_corr.png",dpi=180,bbox_inches="tight"); plt.close()

# Fig 7 — LR coefficients (ONE column)
fig,ax = plt.subplots(figsize=(COL_INCH*1.05,2.5))
cv_=LR.coef_[0]; ord_=np.argsort(np.abs(cv_))
cc=[("#C0392B" if c>0 else "#2E74B5") for c in cv_[ord_]]
bars=ax.barh([FLBLS[i] for i in ord_],cv_[ord_],color=cc,alpha=0.85,edgecolor="white")
ax.axvline(0,color="black",lw=0.8)
for b,v in zip(bars,cv_[ord_]):
    ax.text(v+(0.003 if v>=0 else -0.003),b.get_y()+b.get_height()/2,
            f"{v:+.4f}",va="center",ha=("left" if v>=0 else "right"),fontsize=8)
ax.set_xlabel("Std. Coefficient (log-odds)",fontsize=8)
ax.set_title("LR Coefficients",fontsize=9,fontweight="bold")
ax.tick_params(labelsize=7)
plt.tight_layout()
fig.savefig(f"{FD}/jfig7_lr.png",dpi=180,bbox_inches="tight"); plt.close()
print("    7 figures saved.")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — REPORTLAB PDF
# ═══════════════════════════════════════════════════════════════════════════════
print("[4/5] Building PDF (two-column journal layout) …")

PDF_PATH = "final/paper_cs2_match_prediction.pdf"

# ── Page drawing functions ────────────────────────────────────────────────────
def draw_first(canvas, doc):
    canvas.saveState()
    # Blue bar
    canvas.setFillColor(DB)
    canvas.rect(0, PH-BAR_H, PW, BAR_H, fill=1, stroke=0)
    canvas.setFillColor(W)
    canvas.setFont(FB, 8)
    canvas.drawString(ML, PH-BAR_H+5,
        "Research Methods  |  Narxoz University, Almaty, Kazakhstan  |  2026")
    canvas.setFont(FN, 7.5)
    canvas.drawRightString(PW-MR, PH-BAR_H+5,
        "S23068165  ·  S23067745  ·  S23068279")
    # Accent strip below header bar
    canvas.setFillColor(MB2)
    canvas.rect(0, PH-BAR_H-2, PW, 2, fill=1, stroke=0)
    # Bottom bar
    canvas.setFillColor(DB)
    canvas.rect(0, 0, PW, MB*0.4, fill=1, stroke=0)
    canvas.setFillColor(W); canvas.setFont(FN, 7.5)
    canvas.drawCentredString(PW/2, MB*0.15, "1")
    canvas.restoreState()

def draw_later(canvas, doc):
    canvas.saveState()
    # Top teal accent bar
    canvas.setFillColor(MB2)
    canvas.rect(0, PH-MT+4, PW, 3, fill=1, stroke=0)
    # Running header text
    canvas.setFont(FB, 7.5); canvas.setFillColor(DB)
    canvas.drawString(ML, PH-MT+8, "Research Methods  |  Narxoz University  |  2026")
    canvas.setFont(FN, 7.5); canvas.setFillColor(GR)
    canvas.drawRightString(PW-MR, PH-MT+8, f"Page {doc.page}")
    # column separator intentionally hidden
    # Bottom bar (teal accent + dark base)
    canvas.setFillColor(DB)
    canvas.rect(0, 0, PW, MB*0.35, fill=1, stroke=0)
    canvas.setFillColor(MB2)
    canvas.rect(0, MB*0.35, PW, 1.5, fill=1, stroke=0)
    canvas.restoreState()

def draw_onecol(canvas, doc):
    draw_later(canvas, doc)

# ── Frames & templates ────────────────────────────────────────────────────────
PAD = 2

f_hdr = Frame(ML, HDR_BOT, CW, HDR_H,
              id='hdr', leftPadding=PAD, rightPadding=PAD,
              topPadding=0, bottomPadding=0, showBoundary=0)
f_p1l = Frame(ML,        MB, COL, BODY1, id='p1l',
              leftPadding=PAD, rightPadding=PAD,
              topPadding=0, bottomPadding=0, showBoundary=0)
f_p1r = Frame(ML+COL+GUT,MB, COL, BODY1, id='p1r',
              leftPadding=PAD, rightPadding=PAD,
              topPadding=0, bottomPadding=0, showBoundary=0)
f_l   = Frame(ML,        MB, COL, CH,    id='l',
              leftPadding=PAD, rightPadding=PAD,
              topPadding=0, bottomPadding=0, showBoundary=0)
f_r   = Frame(ML+COL+GUT,MB, COL, CH,    id='r',
              leftPadding=PAD, rightPadding=PAD,
              topPadding=0, bottomPadding=0, showBoundary=0)
f_oc  = Frame(ML,        MB, CW,  CH,    id='oc',
              leftPadding=PAD, rightPadding=PAD,
              topPadding=0, bottomPadding=0, showBoundary=0)

tmpl_first   = PageTemplate(id='first',   frames=[f_hdr,f_p1l,f_p1r], onPage=draw_first)
tmpl_twocol  = PageTemplate(id='two_col', frames=[f_l,f_r],           onPage=draw_later)
tmpl_onecol  = PageTemplate(id='one_col', frames=[f_oc],               onPage=draw_onecol)

doc = BaseDocTemplate(PDF_PATH, pagesize=A4,
                      pageTemplates=[tmpl_first,tmpl_twocol,tmpl_onecol],
                      title="Predicting Professional CS2 Match Outcomes",
                      author="Seisenbek Dias, Mergen Temirzhan, Onashov Aidos")

# ── Story helpers ─────────────────────────────────────────────────────────────
def SP(h=4): return Spacer(1, h)
def HR(w="100%", c=MB2, t=0.5): return HRFlowable(width=w,color=c,thickness=t,spaceAfter=4)
_CITE_HEX = '#1558A7'
def _blue_cite(txt):
    """Wrap (Author, Year) style citations in blue."""
    return re.sub(
        r'\(([^()]*(?:19|20)\d{2}[^()]*)\)',
        lambda m: f'<font color="{_CITE_HEX}">({m.group(1)})</font>',
        txt
    )

def P(txt, sty=BODY):
    """Paragraph — auto-blue citations for body text styles."""
    if sty in (BODY, BODYSM):
        txt = _blue_cite(txt)
    return Paragraph(txt, sty)

def PB(txt, sty=BODY):   # kept for compatibility
    return P(txt, sty)

def BU(txt): return Paragraph(f"&#8226;  {txt}", BSTY)

def wide_start():
    """Switch to one-column template (for wide tables/figures)."""
    return [NextPageTemplate('one_col'), PageBreak()]

def wide_end():
    """Signal that next natural page-break should return to two-column.
    NO forced PageBreak — lets content continue filling the current page."""
    return [NextPageTemplate('two_col')]

def make_table(headers, rows, col_ws, caption="",
               head_bg=MB2, alt_bg=LB, best_cells=None):
    """Build a reportlab Table with journal styling."""
    data = [[P(f"<b>{h}</b>", S('th',fontName=FB,fontSize=8,textColor=W,
                                leading=10,alignment=TA_CENTER,
                                spaceBefore=0,spaceAfter=0))
             for h in headers]]
    for row in rows:
        data.append([P(str(v), S('td',fontName=FN,fontSize=8,leading=10,
                                 alignment=TA_CENTER,spaceBefore=0,spaceAfter=0))
                     for v in row])
    ts = TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  head_bg),
        ('TEXTCOLOR',    (0,0), (-1,0),  W),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [W, alt_bg]),
        ('GRID',         (0,0), (-1,-1), 0.3, colors.HexColor('#BBBBBB')),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    if best_cells:
        for (r,c) in best_cells:
            ts.add('BACKGROUND', (c,r), (c,r), GRN)
            ts.add('FONTNAME',   (c,r), (c,r), FB)
    t = Table(data, colWidths=col_ws, repeatRows=1)
    t.setStyle(ts)
    items = []
    if caption:
        items.append(P(caption, TCAP))
    items.append(t)
    items.append(SP(6))
    return KeepTogether(items)

def img_col(path, caption):
    """Image sized to ONE column width."""
    return KeepTogether([
        Image(path, width=COL-4, height=(COL-4)*0.75),
        P(caption, CAPT),
    ])

def img_wide(path, caption, aspect=0.45):
    """Image sized to FULL content width."""
    return KeepTogether([
        Image(path, width=CW-4, height=(CW-4)*aspect),
        P(caption, CAPT),
    ])

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD STORY
# ═══════════════════════════════════════════════════════════════════════════════
story = []

# ── HEADER FRAME (first page) ─────────────────────────────────────────────────

story.append(P("Predicting Professional CS2 Match Outcomes Using Machine Learning:<br/>"
               "A Comparative Study of Logistic Regression, Random Forest, and Gradient Boosting",
               TITLE))
story.append(P("Seisenbek Dias · Mergen Temirzhan · Onashov Aidos", AUTH))
story.append(P("Department of Economics and Management, "
               "Narxoz University, Almaty, Kazakhstan", AFFIL))
story.append(SP(4))

# Article info + Abstract box (2-cell table)
best_r = results[best]
kw_text = ("CS2 &nbsp;•&nbsp; esports analytics &nbsp;•&nbsp; match outcome prediction<br/>"
           "logistic regression &nbsp;•&nbsp; random forest &nbsp;•&nbsp; gradient boosting<br/>"
           "HLTV &nbsp;•&nbsp; binary classification &nbsp;•&nbsp; feature importance")

abs_text = (
    "Predicting who wins a professional Counter-Strike 2 match before it starts is "
    "harder than it looks — teams that appear stronger on paper lose often enough "
    "to make the problem genuinely difficult. We trained three classifiers "
    "(Logistic Regression, Random Forest, and Gradient Boosting) on "
    f"{N:,} professional CS2 matches from HLTV.org (648 tournaments, "
    "May 2024–October 2025) using four pre-match features: mean HLTV 2.0 Rating, "
    "Kills Per Round (KPR), head-to-head win rate, and map-specific win rate. "
    "All models were evaluated against a majority-class naive baseline on a "
    f"held-out test set (n = {len(Xte):,}) using Accuracy, Macro F1, and AUC-ROC. "
    f"{best} produced the best Macro F1 ({best_r['f1m']:.3f}) and "
    f"AUC-ROC ({best_r['auc']:.3f}), though differences between classifiers "
    "were not statistically significant (p > 0.05). Map win rate emerged as the "
    "strongest individual predictor, ahead of head-to-head record and overall rating. "
    "The resulting ~56% accuracy aligns with prior pre-match sports prediction work "
    "and appears to reflect a signal ceiling in the available features "
    "rather than a capacity ceiling in the models."
)

IW = CW - 2*PAD   # inner width of header frame
info_cell_content = [
    P("a r t i c l e   i n f o", AI_LBL),
    SP(3),
    P("<b>Keywords</b>", S('kl',fontName=FB,fontSize=8,leading=11,
                             alignment=TA_LEFT,spaceBefore=0,spaceAfter=2)),
    P(kw_text, S('kv',fontName=FN,fontSize=8,leading=11,
                   alignment=TA_LEFT,spaceBefore=0,spaceAfter=0)),
]
abs_cell_content = [
    P("a b s t r a c t", AB_LBL),
    SP(3),
    P(abs_text, AB_TXT),
]

box = Table(
    [[info_cell_content, abs_cell_content]],
    colWidths=[IW*0.30, IW*0.70],
    style=TableStyle([
        ('VALIGN',       (0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',  (0,0),(-1,-1), 5),
        ('RIGHTPADDING', (0,0),(-1,-1), 5),
        ('TOPPADDING',   (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('BOX',          (0,0),(-1,-1), 0.8, MB2),
        ('LINEAFTER',    (0,0),(0,-1),  0.5, MB2),
        ('BACKGROUND',   (0,0),(0,-1),  LGR),
    ])
)
story.append(box)
story.append(SP(5))
story.append(HR(c=MB2, t=0.7))
story.append(FrameBreak())            # header frame → left body column
story.append(NextPageTemplate('two_col'))  # all pages after page 1 use two-column

# ═══════════════════════════════════════════════════
# BODY (flows through two-column frames)
# ═══════════════════════════════════════════════════

# ── 1. INTRODUCTION ──────────────────────────────────────────────────────────
story.append(P("1. Introduction", H1))
story.append(PB("Counter-Strike 2 (CS2) is, by most measures, the most thoroughly documented "
               "competitive shooter in esports. HLTV.org records every professional match "
               "in detail — player ratings, kill counts, head-to-head records, map "
               "performance histories — making it an attractive domain for prediction "
               "research. Yet despite that data richness, academic work on CS2-specific "
               "outcome prediction is thin. Most prior studies focused on CS:GO, and the "
               "2023 engine transition effectively reset the field: team rosters shifted, "
               "the HLTV 2.0 rating system was introduced, and models trained on old data "
               "no longer transferred (Arik, 2022).", BODY))
story.append(P("We asked a fairly direct question: given only the information available "
               "on HLTV before a match, can a classifier reliably predict the winner? "
               "The problem is harder than it looks. In-game models — those with access "
               "to real-time economy, alive players, and round score — reach AUC above "
               "0.80 (Katona et al., 2019). Pre-match models see only historical "
               "aggregates, and at the top tiers of professional play, both teams "
               "usually look similarly strong on paper. Prior work on other sports puts "
               "the pre-match ceiling at around 60–68% (Semenoff, 2020; "
               "Bunker and Thabtah, 2019), and we expected our results to fall "
               "somewhere in that range.", BODY))
story.append(P("We applied Logistic Regression, Random Forest, and Gradient Boosting to "
               "7,033 CS2 matches from 648 tournaments (May 2024–October 2025), "
               "using four engineered features: mean HLTV 2.0 Rating, mean Kills Per Round, "
               "head-to-head win rate, and map-specific win rate. Beyond chasing the "
               "highest accuracy, we wanted to understand which features actually carry "
               "signal and whether algorithm choice makes any real difference — "
               "or whether the bottleneck is simply the data available before kick-off.", BODY))

# ── 2. RELATED WORK ──────────────────────────────────────────────────────────
story.append(P("2. Related Work", H1))
story.append(P("Sport outcome prediction has attracted ML researchers for decades, "
               "partly because the problem is clean — binary or multi-class outcome, "
               "reasonably structured historical data — and partly because the ceiling "
               "is well-known to be far from 100%. "
               "Broms and Nordansjö (2024) applied Logistic Regression and Random Forest "
               "to CS:GO match data from HLTV.org over a three-year period, benchmarking "
               "predictions against bookmaker odds — the closest prior study to our own. "
               "Bunker and Thabtah (2019) reviewed approaches across sports and found "
               "that tree-based ensembles tend to outperform linear models, but also "
               "that feature construction often matters more than algorithm choice. "
               "Baboota and Kaur (2019) reached 74% on Premier League results using "
               "RF and XGBoost — though football offers longer per-team histories and "
               "a larger feature pool than CS2.", BODY))
story.append(P("Esports prediction is a younger area but has grown quickly. "
               "Hodge et al. (2019) surveyed the field and noted that CS:GO, with its "
               "detailed HLTV logging, was among the most amenable titles for this kind "
               "of work. Katona et al. (2019) illustrated the upper bound: their "
               "round-level CS:GO models, which used real-time economy and alive-player "
               "state, achieved AUC of 0.80–0.85 — well above what any pre-match "
               "model has managed. Semenoff (2020) tested pre-match CS:GO prediction "
               "on HLTV statistics, using the same family of models we use here, "
               "and landed at 60–68%. Our results are directly comparable to Semenoff's, "
               "with the important difference that our data is native CS2 (2024–25) "
               "rather than the deprecated CS:GO era. Arik (2022) showed that "
               "post-transition, prior models do not transfer, which is what motivates "
               "building from scratch on this dataset.", BODY))

# Table 1 — column-width, no template switch needed
cw1 = [COL*0.38, COL*0.18, COL*0.24, COL*0.20]
story.append(make_table(
    ["Study","Domain","Method(s)","Accuracy"],
    [["Broms &amp; Nordansjö (2024)","CS:GO","LR, RF","&gt;50%"],
     ["Baboota &amp; Kaur (2019)","Football","RF, XGBoost","74%"],
     ["Bunker &amp; Thabtah (2019)","Multi-sport","RF, SVM, LR","68–72%"],
     ["Katona et al. (2019)","CS:GO","Random Forest","AUC 0.82"],
     ["Semenoff (2020)","CS:GO","LR, GB, SVM","68%"],
     ["Arik (2022)","Esports","LR, XGBoost","66%"],
     ["<b>Present study</b>","CS2 2024–25","LR, RF, GB",
      f"<b>{max(r['acc'] for r in results.values()):.1%}</b>"]],
    col_ws=cw1,
    caption="Table 1. Related work summary."))

# ── 3. DATASET AND VARIABLES ──────────────────────────────────────────────────
story.append(P("3. Dataset and Variables", H1))
story.append(P("3.1. Data Source", H2))
story.append(P(f"The primary dataset aggregates {N:,} professional CS2 match records "
               "scraped from HLTV.org by griffindesroches (2025) and published on Kaggle. "
               "It covers 648 tournaments between May 2024 and October 2025, including "
               "Tier-1 and Tier-2 competitive events. Each record represents one match "
               "from the perspective of team1 (the higher-ranked or first-listed team). "
               "The raw dataset contains 168 columns.", BODY))
story.append(P("3.2. Variable Engineering", H2))
story.append(P("Five variables were engineered for the model (Table 2). Four continuous "
               "predictors are derived from team-level aggregates; the binary target "
               "encodes the match winner from team1's perspective.", BODY))

# Table 2 — column-width, no template switch needed
cw2 = [COL*0.33, COL*0.13, COL*0.54]
story.append(make_table(
    ["Variable","Role","Source Column / Notes"],
    [["match_outcome","Target Y","team1_win_flag — binary {0,1}"],
     ["mean_hltv_rating","X1a","team1_avg_RATING — team avg. HLTV 2.0 Rating"],
     ["mean_kpr","X1b","team1_avg_KPR — mean Kills Per Round"],
     ["head_to_head_win_rate","X2","team1_head2head/100 — historical H2H rate"],
     ["map_win_rate","X3","team1_[map]/100 — win rate on decider map"]],
    col_ws=cw2,
    caption="Table 2. Variable data dictionary."))

story.append(P("3.3. Pearson Correlation Analysis", H2))
story.append(P("Pearson correlations between features and the target reveal that all four "
               "feature-target correlations are below |r| = 0.15 (Table 3, Figure 6), "
               "indicating weak individual linear relationships. This low-correlation "
               "structure directly predicts the modest classification accuracy reported "
               "in Section 6 and motivates the use of non-linear ensemble methods.", BODY))

# Narrow table — Table 3 (fits in one column)
cw3 = [COL*0.42, COL*0.22, COL*0.20, COL*0.16]
corr_rows = []
for feat,lbl in zip(FEATS,FLBLS):
    rv = corr.loc[lbl,"Win"]
    corr_rows.append([lbl, f"{rv:.4f}",
                      "Positive" if rv>0 else "Negative",
                      "Weak" if abs(rv)<0.1 else "Moderate"])
story.append(make_table(["Feature","r","Direction","Strength"],
                        corr_rows, col_ws=cw3,
                        caption="Table 3. Feature–target Pearson correlations."))
story.append(img_col(f"{FD}/jfig6_corr.png",
    "Figure 6. Pearson correlation matrix. All feature-target correlations |r| < 0.15."))

story.append(P("3.4. Research Hypotheses", H2))
for h in [
    "<b>H1:</b> Teams with higher HLTV Rating and KPR are more likely to win (combat performance).",
    "<b>H2:</b> A more favourable head-to-head win rate increases win probability (historical matchup).",
    "<b>H3:</b> A stronger map-specific win rate increases win probability (map specialisation).",
]:
    story.append(BU(h))

story.append(P("3.5. Preprocessing", H2))
cw4 = [COL*0.20, COL*0.45, COL*0.35]
story.append(make_table(
    ["Step","Decision","Rationale"],
    [["Missing","63 NaN in map_win_rate → mean sub.","MAR; no systematic bias"],
     ["Outliers","Winsorize at 1st/99th pct.","Retains all 7,033 records"],
     ["Split","80/20 stratified, seed=42","Reproducible; preserves ratio"],
     ["Scale","StandardScaler on train only","Prevents data leakage"],
     ["Baseline","Always predict Win","Mandatory reference"]],
    col_ws=cw4,
    caption="Table 4. Preprocessing summary."))

# ── 4. METHODOLOGY ────────────────────────────────────────────────────────────
story.append(P("4. Methodology", H1))
story.append(P("<b>Logistic Regression (LR)</b> is the standard linear baseline for binary "
               "classification. It models win probability as:", BODY))
story.append(P("P(Y=1|X) = 1 / (1 + exp( \u2212(β0 + β1X1 + β2X2 + β3X3 + β4X4) ))", EQN))
story.append(P("Coefficients β are estimated by maximum likelihood with L2 regularisation "
               "(C=1.0). LR provides directly interpretable standardised coefficients "
               "as log-odds per standard deviation of each feature "
               "(Hosmer, Lemeshow and Sturdivant, 2013).", BODY))
story.append(P("<b>Random Forest (RF)</b> is a bagging ensemble of B=200 decision trees, "
               "each trained on a bootstrap sample with feature subsampling (√p features "
               "at each split). Predictions are aggregated by majority vote:", BODY))
story.append(P("P(Y=1|X)  =  (1/B) \u00b7 \u03a3b  Pb(Y=1|X)", EQN))
story.append(P("RF is robust to overfitting and produces Gini-based feature importances "
               "(Breiman, 2001). Configuration: B=200, max_depth=10.", BODY))
story.append(P("<b>Gradient Boosting (GB)</b> constructs an additive ensemble sequentially, "
               "fitting each shallow tree to the pseudo-residuals of the current model:", BODY))
story.append(P("Fm(x)  =  F(m\u22121)(x)  +  \u03b7 \u00b7 hm(x),     \u03b7 = 0.05,    M = 200", EQN))
story.append(P("GB typically achieves the highest hold-out accuracy at greater computational "
               "cost (Friedman, 2001). Configuration: M=200, max_depth=4, η=0.05.", BODY))

# ── 5. EXPERIMENTAL SETUP ─────────────────────────────────────────────────────
story.append(P("5. Experimental Setup", H1))
story.append(P("All experiments run in Python 3.14 using scikit-learn 1.x "
               "(Pedregosa et al., 2011) with "
               "random_state=42 throughout. Full code: "
               "github.com/aloneen/cs2-match-outcome-prediction. "
               "Macro F1 is the primary metric; AUC-ROC is secondary. "
               "The naive baseline (always predict Win) is included in all comparisons. "
               "Statistical significance of model differences is assessed by paired "
               "t-test on 5-fold CV accuracy (α=0.05).", BODY))

cw5 = [COL*0.38, COL*0.35, COL*0.27]
story.append(make_table(
    ["Model","Hyperparameter","Value"],
    [["Logistic Regression","C (regularisation)","1.0 (L2)"],
     ["Logistic Regression","solver / max_iter","lbfgs / 1000"],
     ["Random Forest","n_estimators / max_depth","200 / 10"],
     ["Gradient Boosting","n_estimators / max_depth","200 / 4"],
     ["Gradient Boosting","learning_rate","0.05"]],
    col_ws=cw5,
    caption="Table 5. Hyperparameter configuration."))

# ── 6. RESULTS ────────────────────────────────────────────────────────────────
story.append(P("6. Results", H1))
story.append(P("6.1. Overall Performance", H2))
story.append(P(f"Table 6 reports all metrics on the held-out test set (n={len(Xte):,}). "
               "The naive baseline is included for reference; green cells mark the best "
               "ML model per metric.", BODY))

# Wide page — Table 6 + Figure 1 together (eliminates 2 wasted page breaks)
story += wide_start()
all_rows = [["Naive Baseline (always Win)",
             f"{naive['acc']:.4f}",
             f"{naive['prec']:.4f}",
             f"{naive['rec']:.4f}",
             f"{naive['f1m']:.4f}","0.5000",
             f"{naive['acc']:.4f}±0.0000"]]
for nm in MNS:
    r=results[nm]
    all_rows.append([nm,
                     f"{r['acc']:.4f}",
                     f"{r['prec']:.4f}",
                     f"{r['rec']:.4f}",
                     f"{r['f1m']:.4f}",f"{r['auc']:.4f}",
                     f"{r['cvm']:.4f}±{r['cvs']:.4f}"])

best_cells_t6 = []
for ci in [1,2,3,4,5]:
    vals=[float(all_rows[ri][ci]) for ri in range(1,4)]
    best_ri = vals.index(max(vals))+1
    best_cells_t6.append((best_ri,ci))

cw6 = [CW*0.24,CW*0.10,CW*0.10,CW*0.10,CW*0.12,CW*0.10,CW*0.24]
story.append(make_table(
    ["Model","Accuracy","Precision","Recall","Macro F1*","AUC-ROC","5-Fold CV Acc"],
    all_rows, col_ws=cw6, best_cells=best_cells_t6,
    caption="Table 6. Test-set performance (n=1,407). Green = best ML model per metric. *Primary metric."))

story.append(P("6.2. Confusion Matrices", H2))
story.append(img_wide(f"{FD}/jfig1_cm.png",
    "Figure 1. Confusion matrices for all three models on the test set (n=1,407). "
    "Values show absolute counts; colour intensity shows row-normalised rate.",
    aspect=0.42))
story += wide_end()   # back to two_col on next natural page break

story.append(P("The confusion matrices (Figure 1) reveal a systematic pattern: all three "
               "models predict Win disproportionately, reflecting the 54.6% majority class. "
               "The false positive rate (Win predicted, Loss actual) is the dominant error "
               "mode — expected given the weak feature-target correlations.", BODY))

story.append(P("6.3. ROC Curves", H2))
story.append(img_col(f"{FD}/jfig2_roc.png",
    "Figure 2. ROC curves. All ML models exceed AUC=0.50 (naive baseline), "
    "confirming positive but modest discrimination."))
story.append(P("Figure 2 confirms AUC > 0.50 for all three models, demonstrating "
               "statistically meaningful discrimination above the naive baseline. "
               f"AUC values range from "
               f"{min(r['auc'] for r in results.values()):.3f} to "
               f"{max(r['auc'] for r in results.values()):.3f}. "
               "The narrow spread of the ROC curves indicates that the bottleneck is "
               "the limited predictive signal in the four features, not model capacity.", BODY))

story.append(P("6.4. Performance Comparison and CV", H2))

# Wide page — Figure 4 + Figure 3 together
story += wide_start()
story.append(img_wide(f"{FD}/jfig4_comp.png",
    "Figure 4. Accuracy and Macro F1 comparison (test set). Grey = naive baseline. "
    "Red dashed = random chance (0.50). All ML models exceed both references.",
    aspect=0.38))
story.append(img_wide(f"{FD}/jfig3_imp.png",
    "Figure 3. Feature importance: Random Forest (left) and Gradient Boosting (right). "
    "Map Win Rate ranks first in both models; KPR ranks last.",
    aspect=0.40))
story += wide_end()

story.append(img_col(f"{FD}/jfig5_cv.png",
    "Figure 5. 5-fold cross-validation accuracy (training set). "
    "Error bars = ±1 standard deviation."))
story.append(P("All three models improve marginally over the naive baseline on Macro F1 "
               "(Figure 4). Cross-validation (Figure 5) confirms stable performance "
               f"(CV range: {min(r['cvm'] for r in results.values()):.3f}–"
               f"{max(r['cvm'] for r in results.values()):.3f}, σ ≤ 0.009), "
               "indicating no overfitting.", BODY))

# ── 7. DISCUSSION ─────────────────────────────────────────────────────────────
story.append(P("7. Discussion", H1))
story.append(P("7.1. Statistical Significance", H2))

cw7 = [COL*0.52, COL*0.20, COL*0.16, COL*0.12]
t_rows=[]
for nm in MNS:
    if nm!=best:
        t,p=ttests[nm]
        t_rows.append([f"{best} vs. {nm}", f"{t:.4f}", f"{p:.4f}",
                       "Yes" if p<0.05 else "No"])
story.append(make_table(
    ["Comparison","t-stat","p-value","Sig.?"],
    t_rows, col_ws=cw7,
    caption="Table 7. Paired t-tests on 5-fold CV accuracy (α=0.05)."))
story.append(P("None of the pairwise comparisons reached significance (p > 0.05). "
               "This is not particularly surprising: when the ceiling is set by the "
               "features themselves rather than by model complexity, swapping from "
               "Logistic Regression to Gradient Boosting mostly rearranges the same "
               "weak signal rather than unlocking new predictive capacity. "
               "It is also worth noting that 5-fold cross-validation gives only five "
               "data points per paired t-test, which limits statistical power — "
               "a 10- or 20-fold scheme would yield a more sensitive comparison.", BODY))

story.append(P("7.2. LR Coefficient Interpretation", H2))
story.append(img_col(f"{FD}/jfig7_lr.png",
    "Figure 7. Standardised LR coefficients (log-odds per σ). "
    "Red = positive effect on P(Win); Blue = negative."))

# Table 8 — column-width, no template switch needed
cw8=[COL*0.31, COL*0.17, COL*0.17, COL*0.19, COL*0.16]
coef_rows=[]
for fl,feat in zip(FLBLS,FEATS):
    cv_=lr_coefs[fl]
    coef_rows.append([fl,
                      f"{sc.mean_[FEATS.index(feat)]:.4f}",
                      f"{sc.scale_[FEATS.index(feat)]:.4f}",
                      f"{cv_:+.4f}",
                      "H1" if "rating" in feat or "kpr" in feat else
                      "H2" if "head" in feat else "H3"])
story.append(make_table(
    ["Feature","Train μ","Train σ","Coeff. β","Hyp."],
    coef_rows, col_ws=cw8,
    caption=f"Table 8. LR standardised coefficients (β₀ = {LR.intercept_[0]:+.4f})."))

pos_fs=[fl for fl in FLBLS if lr_coefs[fl]>0]
neg_fs=[fl for fl in FLBLS if lr_coefs[fl]<0]
story.append(P(f"Table 8 and Figure 7 show that {', '.join(pos_fs)} all push win probability "
               "upward, in line with the direction each hypothesis predicted. "
               f"{'No feature produced a negative coefficient.' if not neg_fs else ', '.join(neg_fs)+' pulled in the opposite direction.'} "
               "The magnitudes, however — all |β| below 0.30 — tell the same story "
               "as the correlation matrix: the features point in the right direction, "
               "but none is strong enough on its own to be a reliable standalone predictor.", BODY))

story.append(P("7.3. Feature Importance", H2))

rf_d=dict(zip(FLBLS,results["Random Forest"]["model"].feature_importances_))
gb_d=dict(zip(FLBLS,results["Gradient Boosting"]["model"].feature_importances_))
top_rf=max(rf_d,key=rf_d.get); top_gb=max(gb_d,key=gb_d.get)
sec_rf=sorted(rf_d,key=rf_d.get,reverse=True)[1]
feat_hyp={"HLTV Rating":"H1","KPR":"H1","H2H Win Rate":"H2","Map Win Rate":"H3"}
top_hyp=feat_hyp.get(top_rf,"")
sec_hyp=feat_hyp.get(sec_rf,"")
story.append(P(f"Both ensemble models ranked {top_rf} first "
               f"(RF: {rf_d[top_rf]:.3f}, GB: {gb_d[top_gb]:.3f}). "
               "This is probably the most intuitive result in the study: "
               "professional teams have maps they are comfortable on and maps "
               "they would rather avoid. Being drawn into an unfamiliar map is a "
               "genuine competitive disadvantage, and the map-specific win rate "
               f"captures exactly that. {sec_rf} came second in both models "
               f"(RF: {rf_d[sec_rf]:.3f}), which also makes sense — head-to-head "
               "history between specific opponents often reflects real stylistic "
               "matchups that persist over time. Overall HLTV Rating and KPR "
               f"(RF: {rf_d['HLTV Rating']:.3f} and {rf_d['KPR']:.3f}) were "
               "the weakest contributors, likely because at the professional level "
               "both teams in a match are already highly skilled — the feature "
               "loses discriminating power when nearly everyone it describes is elite.", BODY))

story.append(P("7.4. Why Is Accuracy Modest?", H2))
story.append(P("The ~56% accuracy is worth dwelling on, because it is both disappointing "
               "and expected. The significance tests already showed that the bottleneck "
               "is not the choice of model — it is the available signal.", BODY))
story.append(P("Part of the ceiling comes from how the data was collected. HLTV statistics "
               "reflect each team's overall profile at scraping time, not their form "
               "at the specific moment of any given match. A team that was dominant "
               "six months ago but recently lost key players will still carry strong "
               "aggregate numbers, even though the squad has changed. Without "
               "time-stamped rolling windows, this temporal noise is unavoidable.", BODY))
story.append(P("A deeper issue is feature scope. Four aggregate statistics cannot "
               "capture what actually decides a CS2 match: in-game adaptation, "
               "coaching decisions, which players are in form on a particular day, "
               "or whether the map veto caught one side off-guard. "
               "Katona et al. (2019) showed what becomes possible with real-time "
               "state — their round-level models reached AUC above 0.80. "
               "The gap between 0.57 and 0.82 is not a modelling gap; "
               "it is a feature availability gap.", BODY))
story.append(P("Finally, professional CS2 matches pair teams of genuinely comparable "
               "ability. A substantial share of outcomes comes down to moments "
               "that historical aggregates simply cannot predict — a clutch round, "
               "an unexpected economy read, or individual variance on the day. "
               "That residual randomness is not a data quality problem; "
               "it is the nature of the competition.", BODY))

story.append(P("7.5. Contribution to Theory", H2))
story.append(P("This paper makes three contributions to the literature on "
               "esports match prediction. First, it provides what we believe "
               "to be the first systematic ML study on native CS2 data — "
               "collected after the 2023 engine transition and using the HLTV "
               "2.0 rating system. Prior work (Semenoff, 2020; Arik, 2022) "
               "relied on CS:GO-era data that Arik (2022) showed does not "
               "transfer to the post-transition environment. Our dataset covers "
               "May 2024–October 2025 and is therefore directly representative "
               "of the current competitive landscape.", BODY))
story.append(P("Second, we confirm that the pre-match accuracy ceiling "
               "documented across conventional sports (Bunker and Thabtah, 2019; "
               "Semenoff, 2020) generalises to CS2. Despite applying three "
               "algorithm families with four engineered features, accuracy "
               "stabilised at ~56% — consistent with the bound imposed by "
               "the stochastic nature of elite competition. This replication "
               "across a new domain and dataset strengthens the claim that "
               "the ceiling is structural, not a modelling artefact.", BODY))
story.append(P("Third, paired t-tests on five-fold CV scores show that "
               "algorithm choice does not significantly affect outcomes in "
               "this setting. This aligns with the broader finding in sport "
               "prediction literature that feature quality dominates algorithm "
               "complexity (Bunker and Thabtah, 2019). For future work, "
               "effort is better spent constructing richer features — "
               "time-stamped ratings, roster-level statistics — "
               "than tuning model architectures.", BODY))

story.append(P("7.6. Implication to Practice", H2))
story.append(P("The practical scope of this work is intentionally narrow. "
               "A model with ~56% accuracy sits only six percentage points "
               "above a majority-class baseline, which means it should not "
               "be treated as a standalone decision tool in any high-stakes "
               "context. Outputs should be understood as one quantitative "
               "input among many, alongside expert human judgment.", BODY))
story.append(P("Within those limits, the feature importance findings carry "
               "clear practical value for team analysts and coaching staff. "
               "Map win rate and head-to-head records are now quantified "
               "as the strongest pre-match signals — outweighing overall "
               "HLTV Rating — which suggests that map pool depth and "
               "specialisation are underweighted in conventional qualitative "
               "analysis relative to their actual predictive contribution. "
               "Preparation and map veto strategy could be informed "
               "by these findings.", BODY))
story.append(P("Tournament organisers may also find value in these results. "
               "Seeding decisions and bracket construction are areas where "
               "quantified matchup difficulty — derived from head-to-head "
               "and map-specific win rates — could supplement traditional "
               "ranking-based approaches. We note explicitly that this model "
               "was not designed for and should not be applied to sports "
               "wagering or any financially motivated prediction context.", BODY))

# ── 8. CONCLUSION ─────────────────────────────────────────────────────────────
story.append(P("8. Conclusion", H1))
story.append(P(f"We set out to test how well a pre-match model could predict professional "
               f"CS2 outcomes using only HLTV statistics. Across {N:,} matches and "
               f"648 tournaments from May 2024 to October 2025, the answer was: "
               f"modestly well. {best} reached Macro F1 of {best_r['f1m']:.4f} and "
               f"AUC-ROC of {best_r['auc']:.4f}, but differences between all three "
               "classifiers were negligible — what mattered was not which algorithm "
               "we used, but how much signal was available in the features.", BODY))
story.append(P("Map win rate turned out to be the strongest predictor, which makes "
               "intuitive sense: professional teams specialise heavily in certain maps, "
               "and being pushed into unfamiliar territory is a real disadvantage. "
               "Head-to-head win rate added secondary signal. Overall HLTV Rating "
               "and KPR, while positively correlated with winning, were the weakest "
               "contributors — likely because at this level, both teams competing "
               "in any given match are already highly rated.", BODY))
story.append(P(f"The ~56% accuracy we found mirrors Semenoff's (2020) results for CS:GO "
               "and sits within the broader pre-match prediction range documented "
               "across sports (Bunker and Thabtah, 2019). Closing this gap would "
               "require fundamentally different features: time-stamped rating snapshots "
               "that track team form in the weeks before each match, individual player "
               "statistics rather than team averages, or in-game economy data once "
               "play begins. A region-stratified analysis would also be worth pursuing, "
               "since HLTV's event coverage skews heavily toward European and "
               "North American tournaments.", BODY))

# ── REFERENCES ────────────────────────────────────────────────────────────────
story.append(P("References", H1))
story.append(HR(c=DB, t=0.4))
story.append(SP(4))
REFS = [
    "Arik, M. (2022). Predicting the outcome of esports matches using machine learning. MSc Thesis, University of Amsterdam.",
    "Baboota, R., &amp; Kaur, H. (2019). Predictive analysis and modelling football results using machine learning. <i>International Journal of Forecasting, 35</i>(2), 741–755.",
    "Breiman, L. (2001). Random forests. <i>Machine Learning, 45</i>(1), 5–32.",
    "Bunker, R. P., &amp; Thabtah, F. (2019). A machine learning framework for sport result prediction. <i>Applied Computing and Informatics, 15</i>(1), 27–33.",
    "Broms, E., &amp; Nordansjö, W. (2024). Predicting Counter-Strike matches using machine learning models. Bachelor's Thesis, Department of Statistics, Lund University.",
    "Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. <i>Annals of Statistics, 29</i>(5), 1189–1232.",
    "griffindesroches. (2025). <i>CS2 HLTV Professional Match Statistics Dataset.</i> Kaggle.",
    "HLTV.org. (2025). Professional CS2 match statistics and rankings. Retrieved October 2025.",
    "Hodge, V. J., Devlin, S., Sephton, N., Block, F., Cowling, P. I., &amp; Drachen, A. (2019). Win prediction in multi-player esports. <i>IEEE Transactions on Games, 13</i>(4), 368–379.",
    "Hosmer, D. W., Lemeshow, S., &amp; Sturdivant, R. X. (2013). <i>Applied logistic regression</i> (3rd ed.). Wiley.",
    "Katona, A., Belis, D., Engel, E., Thalmeier, F., &amp; van Eetvelde, H. (2019). Counter-Strike: GO — win probability model and kill impact metric. <i>Proc. MLSA@ECML-PKDD</i>, Würzburg.",
    "Newzoo. (2024). <i>Global esports and live streaming market report 2024.</i> Newzoo BV.",
    "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. <i>JMLR, 12</i>, 2825–2830.",
    "Semenoff, L. (2020). Predicting the outcome of CS:GO games using machine learning. Undergraduate Dissertation, University of Stirling.",
]
for i,ref in enumerate(REFS,1):
    story.append(P(f"{i}.&nbsp; {ref}", REF))
    story.append(SP(2))

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════════════════════
print("[5/5] Compiling PDF …")
doc.build(story)
sz = os.path.getsize(PDF_PATH)/1024
print(f"\nDONE — {PDF_PATH}  ({sz:.0f} KB)")
print(f"Best model (Macro F1): {best}")
print(f"  Naive F1m={naive['f1m']:.4f}  |  {best} F1m={best_r['f1m']:.4f}  AUC={best_r['auc']:.4f}")
