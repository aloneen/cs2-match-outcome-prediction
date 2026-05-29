---
theme: default
title: "Predicting Professional CS2 Match Outcomes"
fonts:
  sans: Inter
  weights: '300,400,600,700,900'
class: 'bg-black'
highlighter: shiki
---

<!-- SLIDE 1 — TITLE -->
<div class="h-full flex flex-col justify-between" style="background:#09090B;padding:3rem 3.5rem;">
  <p style="color:#555;font-size:0.65rem;letter-spacing:0.2em;font-weight:600;">NARXOZ UNIVERSITY &nbsp;·&nbsp; RESEARCH METHODS &nbsp;·&nbsp; 2026</p>
  <div>
    <h1 style="font-size:4.2rem;font-weight:900;line-height:1.05;color:#fff;margin:0;">Predicting Professional<br>CS2 Match Outcomes</h1>
    <div style="height:1px;background:#2a2a2a;margin:1.5rem 0;"></div>
    <p style="color:#666;font-style:italic;font-size:1rem;margin:0 0 0.6rem;">A Comparative Study of Logistic Regression, Random Forest, and Gradient Boosting</p>
    <p style="color:#e8e8e6;font-size:1.1rem;font-weight:600;margin:0;">Seisenbek Dias &nbsp;·&nbsp; Mergen Temirzhan &nbsp;·&nbsp; Onashov Aidos</p>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
    <div style="background:#1e1e1e;padding:1rem 1.2rem;border-left:3px solid #fff;">
      <p style="color:#fff;font-weight:700;margin:0 0 0.25rem;font-size:0.95rem;">Seisenbek Dias</p>
      <p style="color:#666;font-size:0.8rem;margin:0;">Problem · Data · Variables</p>
    </div>
    <div style="background:#1e1e1e;padding:1rem 1.2rem;border-left:3px solid #fff;">
      <p style="color:#fff;font-weight:700;margin:0 0 0.25rem;font-size:0.95rem;">Mergen Temirzhan</p>
      <p style="color:#666;font-size:0.8rem;margin:0;">Models · Setup · Results</p>
    </div>
    <div style="background:#1e1e1e;padding:1rem 1.2rem;border-left:3px solid #fff;">
      <p style="color:#fff;font-weight:700;margin:0 0 0.25rem;font-size:0.95rem;">Onashov Aidos</p>
      <p style="color:#666;font-size:0.8rem;margin:0;">Insights · Discussion · Conclusion</p>
    </div>
  </div>
</div>

---

<!-- SLIDE 2 — THE PROBLEM -->
<div class="h-full flex flex-col justify-between" style="background:#09090B;padding:2.5rem 3.5rem;">
  <p style="color:#555;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;">01. THE PROBLEM</p>
  <div style="height:1px;background:#1f1f1f;"></div>
  <div>
    <h1 style="font-size:4.8rem;font-weight:900;line-height:1.05;color:#fff;margin:0 0 0.5rem;">Top-tier teams look<br>identical on paper.</h1>
  </div>
  <div>
    <div style="height:1px;background:#2a2a2a;margin-bottom:1.2rem;"></div>
    <p style="color:#777;font-size:1rem;line-height:1.7;margin:0;">At the highest levels of Counter-Strike 2, aggregate statistics lose their discriminatory power.<br>Predicting a winner before the match starts is a problem of <em>stochastic variation</em>, not just historical data.</p>
  </div>
  <p style="color:#444;font-size:0.75rem;margin:0;">Seisenbek Dias</p>
</div>

---

<!-- SLIDE 3 — THE DATA -->
<div class="h-full flex flex-col justify-between" style="background:#F6F6F4;padding:2.5rem 3.5rem;">
  <p style="color:#999;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;">02. THE EVIDENCE</p>
  <div style="height:1px;background:#ddd;"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;align-items:end;">
    <div>
      <p style="font-size:6.5rem;font-weight:900;color:#111;margin:0;line-height:1;">7,033</p>
      <div style="height:3px;background:#111;margin:0.4rem 0;"></div>
      <p style="color:#999;font-size:1rem;margin:0;">Professional<br>Matches</p>
    </div>
    <div>
      <p style="font-size:6.5rem;font-weight:900;color:#111;margin:0;line-height:1;">648</p>
      <div style="height:3px;background:#111;margin:0.4rem 0;"></div>
      <p style="color:#999;font-size:1rem;margin:0;">Global<br>Tournaments</p>
    </div>
    <div>
      <p style="font-size:6.5rem;font-weight:900;color:#111;margin:0;line-height:1;">18</p>
      <div style="height:3px;background:#111;margin:0.4rem 0;"></div>
      <p style="color:#999;font-size:1rem;margin:0;">Months of Data<br>(May 2024 – Oct 2025)</p>
    </div>
  </div>
  <div style="height:1px;background:#ddd;"></div>
  <p style="color:#aaa;font-size:0.85rem;line-height:1.6;margin:0;">Post-Transition Architecture: Most prior studies rely on CS:GO data. The 2023 engine transition and the HLTV 2.0 rating system effectively reset the field. This study processes only native CS2 data from the current competitive landscape to isolate genuine predictive signals.</p>
  <p style="color:#bbb;font-size:0.75rem;margin:0;">Seisenbek Dias</p>
</div>

---

<!-- SLIDE 4 — THE VARIABLES -->
<div class="h-full flex" style="background:#F6F6F4;padding:2.5rem 3.5rem;gap:3rem;">
  <div style="flex:1;display:flex;flex-direction:column;gap:0;">
    <p style="color:#999;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">03. THE VARIABLES</p>
    <div style="height:1px;background:#ddd;margin-bottom:1.2rem;"></div>
    <div style="display:flex;gap:1rem;margin-bottom:0.9rem;align-items:flex-start;">
      <div style="background:#111;color:#fff;font-weight:700;font-size:0.85rem;padding:0.6rem 0.5rem;min-width:2.8rem;text-align:center;flex-shrink:0;">X1</div>
      <div>
        <p style="font-weight:700;font-size:1.05rem;color:#111;margin:0 0 0.15rem;">Mean HLTV 2.0 Rating</p>
        <p style="color:#999;font-size:0.85rem;margin:0;">The team's average aggregate performance score</p>
      </div>
    </div>
    <div style="display:flex;gap:1rem;margin-bottom:0.9rem;align-items:flex-start;">
      <div style="background:#111;color:#fff;font-weight:700;font-size:0.85rem;padding:0.6rem 0.5rem;min-width:2.8rem;text-align:center;flex-shrink:0;">X2</div>
      <div>
        <p style="font-weight:700;font-size:1.05rem;color:#111;margin:0 0 0.15rem;">Mean Kills Per Round</p>
        <p style="color:#999;font-size:0.85rem;margin:0;">The aggregate historical combat lethality</p>
      </div>
    </div>
    <div style="display:flex;gap:1rem;margin-bottom:0.9rem;align-items:flex-start;">
      <div style="background:#111;color:#fff;font-weight:700;font-size:0.85rem;padding:0.6rem 0.5rem;min-width:2.8rem;text-align:center;flex-shrink:0;">X3</div>
      <div>
        <p style="font-weight:700;font-size:1.05rem;color:#111;margin:0 0 0.15rem;">Head-to-Head Win Rate</p>
        <p style="color:#999;font-size:0.85rem;margin:0;">Specific historical matchup dominance between the two teams</p>
      </div>
    </div>
    <div style="display:flex;gap:1rem;margin-bottom:0.9rem;align-items:flex-start;">
      <div style="background:#111;color:#fff;font-weight:700;font-size:0.85rem;padding:0.6rem 0.5rem;min-width:2.8rem;text-align:center;flex-shrink:0;">X4</div>
      <div>
        <p style="font-weight:700;font-size:1.05rem;color:#111;margin:0 0 0.15rem;">Map-Specific Win Rate</p>
        <p style="color:#999;font-size:0.85rem;margin:0;">The team's historical success rate on the decided map</p>
      </div>
    </div>
    <div style="height:1px;background:#ddd;margin-top:0.5rem;"></div>
    <p style="color:#bbb;font-size:0.75rem;font-style:italic;margin-top:0.5rem;">* Pearson correlations: all feature-target |r| &lt; 0.15 — weak individual signal</p>
    <p style="color:#bbb;font-size:0.75rem;margin-top:auto;">Seisenbek Dias</p>
  </div>
  <div style="flex:1;display:flex;align-items:center;">
    <img src="/jfig6_corr.png" style="width:100%;border-radius:4px;" />
  </div>
</div>

---

<!-- SLIDE 5 — THE MODELS -->
<div class="h-full flex flex-col" style="background:#F6F6F4;padding:2.5rem 3.5rem;">
  <p style="color:#999;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">04. THE MODELS</p>
  <div style="height:1px;background:#ddd;margin-bottom:1.2rem;"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;flex:1;">
    <div style="background:#ECECEA;padding:1.4rem;display:flex;flex-direction:column;border-top:3px solid #111;">
      <p style="font-size:1.3rem;font-weight:900;color:#111;margin:0 0 0.2rem;">Logistic<br>Regression</p>
      <p style="color:#999;font-size:0.75rem;font-style:italic;margin:0 0 0.8rem;">Linear Baseline</p>
      <div style="height:1px;background:#ddd;margin-bottom:0.8rem;"></div>
      <div style="background:#111;padding:0.8rem;margin-bottom:0.8rem;border-radius:2px;">
        <p style="color:#fff;font-size:0.7rem;font-family:monospace;margin:0;text-align:center;line-height:1.6;">P(Y=1|X) = 1 / (1 + e^-(b0+b1X1+b2X2+b3X3+b4X4))</p>
      </div>
      <p style="color:#888;font-size:0.78rem;line-height:1.5;margin:0;">Maximum likelihood with L2 regularisation. Standardised log-odds per feature SD.</p>
    </div>
    <div style="background:#ECECEA;padding:1.4rem;display:flex;flex-direction:column;border-top:3px solid #111;">
      <p style="font-size:1.3rem;font-weight:900;color:#111;margin:0 0 0.2rem;">Random<br>Forest</p>
      <p style="color:#999;font-size:0.75rem;font-style:italic;margin:0 0 0.8rem;">Bagging Ensemble</p>
      <div style="height:1px;background:#ddd;margin-bottom:0.8rem;"></div>
      <div style="background:#111;padding:0.8rem;margin-bottom:0.8rem;border-radius:2px;">
        <p style="color:#fff;font-size:0.7rem;font-family:monospace;margin:0;text-align:center;line-height:1.6;">P(Y=1|X) = (1/B) * SUM_b P_b(Y=1|X)</p>
      </div>
      <p style="color:#888;font-size:0.78rem;line-height:1.5;margin:0;">200 decision trees, majority vote. Gini-based feature importances. Robust to overfitting.</p>
    </div>
    <div style="background:#ECECEA;padding:1.4rem;display:flex;flex-direction:column;border-top:3px solid #111;">
      <p style="font-size:1.3rem;font-weight:900;color:#111;margin:0 0 0.2rem;">Gradient<br>Boosting</p>
      <p style="color:#999;font-size:0.75rem;font-style:italic;margin:0 0 0.8rem;">Additive Ensemble</p>
      <div style="height:1px;background:#ddd;margin-bottom:0.8rem;"></div>
      <div style="background:#111;padding:0.8rem;margin-bottom:0.8rem;border-radius:2px;">
        <p style="color:#fff;font-size:0.7rem;font-family:monospace;margin:0;text-align:center;line-height:1.6;">F_m(x) = F_(m-1)(x) + n*h_m(x) | n=0.05, M=200</p>
      </div>
      <p style="color:#888;font-size:0.78rem;line-height:1.5;margin:0;">Sequential shallow trees fitting pseudo-residuals. Highest hold-out accuracy.</p>
    </div>
  </div>
  <p style="color:#bbb;font-size:0.75rem;margin-top:0.8rem;">Mergen Temirzhan</p>
</div>

---

<!-- SLIDE 6 — THE VERDICT -->
<div class="h-full flex flex-col" style="background:#F6F6F4;padding:2.5rem 3.5rem;">
  <p style="color:#999;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">05. THE VERDICT</p>
  <div style="height:1px;background:#ddd;margin-bottom:1.2rem;"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;flex:1;">
    <div style="background:#ECECEA;padding:1.6rem;display:flex;flex-direction:column;">
      <p style="font-size:1.25rem;font-weight:800;color:#111;margin:0 0 0.8rem;">Logistic<br>Regression</p>
      <div style="height:1px;background:#ccc;margin-bottom:0.6rem;"></div>
      <p style="font-size:4.5rem;font-weight:900;color:#111;margin:0;text-align:center;line-height:1.1;">56.1%</p>
      <p style="color:#999;text-align:center;font-size:0.8rem;margin:0.2rem 0 0.8rem;">Accuracy</p>
      <div style="height:1px;background:#ccc;margin-bottom:0.5rem;"></div>
      <p style="text-align:center;font-size:1rem;font-weight:700;color:#444;margin:0.2rem 0;">F1: 0.484</p>
      <p style="text-align:center;font-size:1rem;color:#999;margin:0;">AUC: 0.574</p>
    </div>
    <div style="background:#111;padding:1.6rem;display:flex;flex-direction:column;">
      <p style="font-size:1.25rem;font-weight:800;color:#fff;margin:0 0 0.8rem;">Random<br>Forest</p>
      <div style="height:1px;background:#333;margin-bottom:0.6rem;"></div>
      <p style="font-size:4.5rem;font-weight:900;color:#fff;margin:0;text-align:center;line-height:1.1;">57.2%</p>
      <p style="color:#666;text-align:center;font-size:0.8rem;margin:0.2rem 0 0.8rem;">Accuracy</p>
      <div style="height:1px;background:#333;margin-bottom:0.5rem;"></div>
      <p style="text-align:center;font-size:1rem;font-weight:700;color:#fff;margin:0.2rem 0;">F1: 0.536</p>
      <p style="text-align:center;font-size:1rem;color:#666;margin:0;">AUC: 0.571</p>
    </div>
    <div style="background:#ECECEA;padding:1.6rem;display:flex;flex-direction:column;">
      <p style="font-size:1.25rem;font-weight:800;color:#111;margin:0 0 0.8rem;">Gradient<br>Boosting</p>
      <div style="height:1px;background:#ccc;margin-bottom:0.6rem;"></div>
      <p style="font-size:4.5rem;font-weight:900;color:#111;margin:0;text-align:center;line-height:1.1;">56.4%</p>
      <p style="color:#999;text-align:center;font-size:0.8rem;margin:0.2rem 0 0.8rem;">Accuracy</p>
      <div style="height:1px;background:#ccc;margin-bottom:0.5rem;"></div>
      <p style="text-align:center;font-size:1rem;font-weight:700;color:#444;margin:0.2rem 0;">F1: 0.528</p>
      <p style="text-align:center;font-size:1rem;color:#999;margin:0;">AUC: 0.573</p>
    </div>
  </div>
  <p style="color:#bbb;font-size:0.75rem;font-style:italic;margin-top:0.7rem;text-align:center;">Paired t-tests (5-fold CV): differences between classifiers are not statistically significant (p &gt; 0.05)</p>
  <p style="color:#bbb;font-size:0.75rem;margin-top:0.3rem;">Mergen Temirzhan</p>
</div>

---

<!-- SLIDE 7 — 57.2% vs 54.6% -->
<div class="h-full flex" style="background:#09090B;padding:2.5rem 3.5rem;gap:3rem;">
  <div style="flex:1;display:flex;flex-direction:column;justify-content:space-between;">
    <div>
      <p style="color:#555;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">06. THE BASELINE</p>
      <div style="height:1px;background:#1f1f1f;margin-bottom:1.5rem;"></div>
      <p style="font-size:1.5rem;font-weight:800;color:#fff;line-height:1.2;margin:0 0 1rem;">The Bound of Stochastic Variation</p>
    </div>
    <p style="color:#666;font-size:0.9rem;line-height:1.7;">A naïve baseline — simply predicting the majority class (always predict 'Win') — yields an automatic 54.6% accuracy.<br><br>Applying a 200-tree Random Forest model lifts that accuracy by just <strong style="color:#aaa;">2.6%</strong>.<br><br>The models are <em>not failing</em>; they have reached the limits of pre-match data.</p>
    <p style="color:#444;font-size:0.75rem;">Mergen Temirzhan</p>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
    <p style="font-size:6.8rem;font-weight:900;color:#fff;margin:0;line-height:1;">57.2%</p>
    <div style="height:2px;background:#2a2a2a;margin:0.5rem 0;"></div>
    <p style="color:#666;font-size:0.95rem;margin:0 0 2rem;">Random Forest Maximum Accuracy</p>
    <p style="font-size:6.8rem;font-weight:900;color:#333;margin:0;line-height:1;">54.6%</p>
    <div style="height:2px;background:#2a2a2a;margin:0.5rem 0;"></div>
    <p style="color:#444;font-size:0.95rem;margin:0;">Naïve Baseline</p>
  </div>
</div>

---

<!-- SLIDE 8 — CONFUSION MATRICES -->
<div class="h-full flex flex-col" style="background:#F6F6F4;padding:2rem 3rem;">
  <p style="color:#999;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">07. CONFUSION MATRICES</p>
  <div style="height:1px;background:#ddd;margin-bottom:1rem;"></div>
  <div style="flex:1;display:flex;align-items:center;justify-content:center;">
    <img src="/jfig1_cm.png" style="max-height:100%;max-width:100%;object-fit:contain;" />
  </div>
  <p style="color:#bbb;font-size:0.78rem;font-style:italic;text-align:center;margin-top:0.5rem;">All models over-predict Win — false positive rate is the dominant error, as expected from weak feature-target correlations</p>
  <p style="color:#bbb;font-size:0.75rem;margin-top:0.3rem;">Mergen Temirzhan</p>
</div>

---

<!-- SLIDE 9 — THE SIGNAL -->
<div class="h-full flex flex-col" style="background:#09090B;padding:2.5rem 3.5rem;">
  <p style="color:#555;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">08. THE SIGNAL</p>
  <div style="height:1px;background:#1f1f1f;margin-bottom:1.2rem;"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem;flex:1;">
    <div style="display:flex;flex-direction:column;">
      <p style="font-size:5.5rem;font-weight:900;color:#1c1c1c;line-height:1;margin:0;">01</p>
      <p style="font-size:1.4rem;font-weight:800;color:#fff;margin:0 0 0.2rem;">Map Win Rate</p>
      <p style="color:#555;font-size:0.8rem;font-weight:600;margin:0 0 0.6rem;">Importance: 0.403 (RF)</p>
      <div style="height:1px;background:#1f1f1f;margin-bottom:0.6rem;"></div>
      <p style="color:#666;font-size:0.82rem;line-height:1.55;">The dominant predictor. At the elite tier, being pulled into an unfamiliar structural environment creates a measurable, objective disadvantage that raw skill cannot overcome.</p>
    </div>
    <div style="display:flex;flex-direction:column;">
      <p style="font-size:5.5rem;font-weight:900;color:#1c1c1c;line-height:1;margin:0;">02</p>
      <p style="font-size:1.4rem;font-weight:800;color:#fff;margin:0 0 0.2rem;">Head-to-Head</p>
      <p style="color:#555;font-size:0.8rem;font-weight:600;margin:0 0 0.6rem;">Importance: 0.269 (RF)</p>
      <div style="height:1px;background:#1f1f1f;margin-bottom:0.6rem;"></div>
      <p style="color:#666;font-size:0.82rem;line-height:1.55;">The secondary signal. Stylistic matchups and historical dominance persist over time, creating psychological and tactical friction between opponents.</p>
    </div>
    <div style="display:flex;flex-direction:column;">
      <p style="font-size:5.5rem;font-weight:900;color:#1c1c1c;line-height:1;margin:0;">03</p>
      <p style="font-size:1.4rem;font-weight:800;color:#fff;margin:0 0 0.2rem;">Aggregate Skill</p>
      <p style="color:#555;font-size:0.8rem;font-weight:600;margin:0 0 0.6rem;">Importance: 0.191 (HLTV) · 0.138 (KPR)</p>
      <div style="height:1px;background:#1f1f1f;margin-bottom:0.6rem;"></div>
      <p style="color:#666;font-size:0.82rem;line-height:1.55;">The weakest signal. When both teams are elite, historical combat lethality and overall ratings cancel each other out.</p>
    </div>
  </div>
  <p style="color:#444;font-size:0.75rem;margin-top:0.8rem;">Onashov Aidos</p>
</div>

---

<!-- SLIDE 10 — FEATURE IMPORTANCE CHART -->
<div class="h-full flex flex-col" style="background:#F6F6F4;padding:2rem 3rem;">
  <p style="color:#999;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">09. FEATURE IMPORTANCE — BOTH ENSEMBLE MODELS</p>
  <div style="height:1px;background:#ddd;margin-bottom:1rem;"></div>
  <div style="flex:1;display:flex;align-items:center;justify-content:center;">
    <img src="/jfig3_imp.png" style="max-height:100%;max-width:100%;object-fit:contain;" />
  </div>
  <p style="color:#bbb;font-size:0.78rem;font-style:italic;text-align:center;margin-top:0.5rem;">Map Win Rate ranks first in both RF and GB with ~40% importance. KPR is consistently the weakest contributor.</p>
  <p style="color:#bbb;font-size:0.75rem;margin-top:0.3rem;">Onashov Aidos</p>
</div>

---

<!-- SLIDE 11 — THE FEATURE CEILING -->
<div class="h-full flex flex-col" style="background:#09090B;padding:2.5rem 3.5rem;">
  <p style="color:#555;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">10. THE FEATURE CEILING</p>
  <div style="height:1px;background:#1f1f1f;margin-bottom:1.2rem;"></div>
  <div style="display:grid;grid-template-columns:1fr 1px 1fr;gap:2rem;flex:1;">
    <div style="display:flex;flex-direction:column;gap:0.7rem;">
      <p style="font-size:1.5rem;font-weight:800;color:#fff;margin:0;">Pre-Match Horizon</p>
      <div style="display:flex;flex-direction:column;gap:0.5rem;flex:1;">
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Historical Aggregates</p></div>
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Temporal Noise</p></div>
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Map Veto</p></div>
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Roster Shifts</p></div>
      </div>
      <div style="background:#111;padding:0.8rem 1rem;margin-top:0.5rem;">
        <p style="color:#fff;font-size:1.2rem;font-weight:800;margin:0;">Max Accuracy: ~56%</p>
      </div>
    </div>
    <div style="background:#1f1f1f;"></div>
    <div style="display:flex;flex-direction:column;gap:0.7rem;">
      <p style="font-size:1.5rem;font-weight:800;color:#fff;margin:0;">In-Game Reality</p>
      <div style="display:flex;flex-direction:column;gap:0.5rem;flex:1;">
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Real-Time Economy</p></div>
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Alive-Player State</p></div>
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Round Score</p></div>
        <div style="background:#1e1e1e;padding:0.7rem 1rem;"><p style="color:#ccc;font-size:0.95rem;margin:0;">Clutch Variance</p></div>
      </div>
      <div style="background:#111;padding:0.8rem 1rem;margin-top:0.5rem;">
        <p style="color:#fff;font-size:1.2rem;font-weight:800;margin:0;">Max Accuracy: 80%+</p>
      </div>
    </div>
  </div>
  <p style="color:#444;font-size:0.75rem;margin-top:0.8rem;">Onashov Aidos</p>
</div>

---

<!-- SLIDE 12 — CONCLUSION -->
<div class="h-full flex flex-col justify-between" style="background:#09090B;padding:2.5rem 3.5rem;">
  <div>
    <p style="color:#555;font-size:0.62rem;letter-spacing:0.18em;font-weight:600;margin:0 0 0.5rem;">11. CONCLUSION</p>
    <div style="height:1px;background:#1f1f1f;margin-bottom:1.5rem;"></div>
    <p style="font-size:2.9rem;font-weight:900;color:#fff;line-height:1.15;margin:0 0 0.2rem;">The algorithms do not lack capacity.</p>
    <p style="font-size:2.9rem;font-weight:900;color:#333;line-height:1.15;margin:0;">The data lacks certainty.</p>
  </div>
  <div>
    <div style="height:1px;background:#1f1f1f;margin-bottom:1rem;"></div>
    <p style="color:#666;font-size:0.92rem;line-height:1.7;margin:0 0 1.2rem;">At the highest tier of competition, pre-match outcomes are bound by a structural ceiling of stochastic variance.<br>To break the 56% barrier, we must look past aggregate history and measure the game in motion.</p>
    <div style="display:flex;flex-direction:column;gap:0.3rem;margin-bottom:1.2rem;">
      <div style="display:flex;gap:1.5rem;">
        <span style="color:#555;font-size:0.85rem;font-weight:600;min-width:4rem;">H3 ✓</span>
        <span style="color:#555;font-size:0.85rem;">Map Win Rate is the dominant predictor</span>
      </div>
      <div style="display:flex;gap:1.5rem;">
        <span style="color:#444;font-size:0.85rem;font-weight:600;min-width:4rem;">H2 ~</span>
        <span style="color:#444;font-size:0.85rem;">H2H Win Rate is the secondary signal</span>
      </div>
      <div style="display:flex;gap:1.5rem;">
        <span style="color:#333;font-size:0.85rem;font-weight:600;min-width:4rem;">H1 v</span>
        <span style="color:#333;font-size:0.85rem;">HLTV Rating / KPR — weakest contributors</span>
      </div>
    </div>
  </div>
  <div>
    <div style="height:1px;background:#1f1f1f;margin-bottom:0.8rem;"></div>
    <p style="color:#444;font-size:0.8rem;text-align:center;margin:0 0 0.4rem;">github.com/aloneen/cs2-match-outcome-prediction</p>
    <p style="font-size:1.8rem;font-weight:800;color:#fff;text-align:center;margin:0;">Thank you &nbsp;·&nbsp; Questions?</p>
  </div>
</div>
