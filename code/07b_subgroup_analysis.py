"""
07b_subgroup_analysis.py — diameter-stratified AUC subgroup analysis (size-confound mitigation).

Eighth-and-a-half script in the pipeline. Sibling of 07_downstream_classifier.py.
Implements the pre-registered diameter-stratified subgroup analysis from
decisions.log #014 (size-confound mitigation, formalised after the cohort
descriptive statistics in decisions.log #014 revealed the strong correlation
between malignancy and nodule diameter in LIDC: median benign 7.74 mm vs
median malignant 19.36 mm). This script is the engine behind Figure 4 and
the entire manuscript Discussion §4.4 size-confound narrative.

Why this is critical-path rather than supplementary:

  The aggregate downstream AUCs in script 07 show radiomics (~0.95) ahead
  of BiomedCLIP (~0.90). Without the size-stratified check, a reviewer
  cannot tell whether that 0.05 gap reflects a real paradigm-level
  feature-quality difference or whether it is a size-correlation
  artefact. Decisions.log #022 documents the empirical finding: within
  matched-size strata the AUC gap collapses, so the aggregate gap is
  largely a size-confound artefact. That finding is the manuscript's
  most methodologically consequential contribution per the Discussion
  §4.4 framing, and it lives or dies on this script.

Per-stratum design choices:

  - Strata are 6-10 mm / 10-20 mm / >20 mm, matching the pre-specification
    in decisions.log #011 and aligning with Lung-RADS clinical conventions
    (MacMahon et al. Radiology 2017 Fleischner Update). The >20 mm
    stratum is reported as "not evaluable" because LIDC contains only ~3
    benign nodules in that size range (Lung-RADS classifies >20 mm solid
    nodules as suspicious by definition, biasing the source cohort).
  - All features used (no ICC filter), so the within-stratum comparison
    isolates 'paradigm' from 'feature selection'.
  - 5-fold stratified CV with min-5-per-fold floor on minority class
    (matches scikit-learn defaults). Strata with <5 of the minority
    class get reported with NaN AUC and a non-evaluable note.

Inputs:
    --labels  CSV with case_id, nodule_id, label, median_diameter_mm
              (typically data/labels_balanced.csv from script 02b)
    results/radiomics_features_3d.parquet
    results/radiomics_features_2d.parquet
    results/fm_embeddings_biomedclip.parquet

Output:
    results/downstream_metrics_by_stratum.csv with columns:
        paradigm, stratum, n_total, n_malignant, auc, auc_ci_lo, auc_ci_hi
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

from utils import RESULTS, fix_seed, get_logger

log = get_logger("07b_subgroup")

# Same paradigm list as 07_downstream_classifier.py.
PARADIGMS = [
    ("radiomics-3d", "radiomics_features_3d.parquet"),
    ("radiomics-2d", "radiomics_features_2d.parquet"),
    ("biomedclip", "fm_embeddings_biomedclip.parquet"),
]

# Diameter strata per decisions.log #011.
STRATA = [
    ("6-10mm", 6.0, 10.0),
    ("10-20mm", 10.0, 20.0),
    (">20mm", 20.0, float("inf")),
]

MIN_PER_FOLD = 5  # need at least n_splits minority-class examples for 5-fold CV
MIN_N_TOTAL = 10
N_SPLITS = 5
N_BOOTSTRAP = 1000
SEED = 42


def stratum_of(diameter_mm: float) -> str:
    """Map a nodule's median diameter (mm) to its stratum label.

    Returns ``"6-10mm"``, ``"10-20mm"``, ``">20mm"``, or ``"na"`` if the
    diameter does not match any stratum (which should never happen given
    the script-02 inclusion criterion of median diameter >=6 mm but the
    fallback prevents silent corruption if upstream criteria change).
    """
    for name, lo, hi in STRATA:
        if lo <= diameter_mm < hi:
            return name
    return "na"


def evaluate(X: np.ndarray, y: np.ndarray) -> dict | None:
    """5-fold stratified CV with L2 LogReg and stratified-bootstrap AUC CI.

    Skips strata that are unevaluable due to small N or extreme class
    imbalance, returning None. The caller logs the skip and writes a NaN
    row for that stratum so the output CSV stays rectangular.

    Two skip conditions:
      - Only one class present (logistic regression undefined).
      - Minority class smaller than ``MIN_PER_FOLD = 5`` (cannot stratify
        a 5-fold CV with fewer than 5 minority examples — scikit-learn
        would raise ValueError).

    The >20 mm stratum routinely trips the second condition because LIDC
    has structurally ~3 benigns at >20 mm — see the module docstring.
    """
    if len(np.unique(y)) < 2:
        return None
    minority = int(min(np.bincount(y)))
    if minority < MIN_PER_FOLD:
        return None
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    oof_prob = np.zeros(len(y))
    for tr, va in skf.split(X, y):
        scaler = StandardScaler().fit(X[tr])
        clf = LogisticRegression(penalty="l2", C=1.0, max_iter=2000)
        clf.fit(scaler.transform(X[tr]), y[tr])
        oof_prob[va] = clf.predict_proba(scaler.transform(X[va]))[:, 1]
    auc = roc_auc_score(y, oof_prob)

    rng = np.random.RandomState(SEED)
    aucs = []
    for _ in range(N_BOOTSTRAP):
        idx = rng.choice(len(y), size=len(y), replace=True)
        if len(np.unique(y[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y[idx], oof_prob[idx]))
    if not aucs:
        return {"auc": auc, "auc_ci_lo": float("nan"), "auc_ci_hi": float("nan")}
    ci_lo, ci_hi = np.quantile(aucs, [0.025, 0.975])
    return {"auc": float(auc), "auc_ci_lo": float(ci_lo), "auc_ci_hi": float(ci_hi)}


def main(labels_csv: Path, out_csv: Path) -> None:
    """Iterate (paradigm, stratum) pairs and write the per-stratum metrics CSV.

    Stratifies the labelled cohort by median diameter, then for each of
    the three paradigms (radiomics-3D, radiomics-2D, BiomedCLIP) runs the
    within-stratum AUC evaluation. The output CSV has 3 paradigms x 3
    strata = 9 rows (with NaN AUC for skipped strata) and is the data
    source for Figure 4 in script 08.

    All features unfiltered within each stratum, deliberately — the
    purpose of this script is to ask 'does the unfiltered AUC ranking
    survive size matching?', not 'how does the ICC filter behave within
    strata?'. The within-stratum ICC-filter analysis is supplementary.
    """
    fix_seed()
    labels = pd.read_csv(labels_csv)
    labels["stratum"] = labels["median_diameter_mm"].map(stratum_of)
    log.info(
        f"Loaded {len(labels)} labelled nodules. "
        f"Stratum sizes: {labels['stratum'].value_counts().to_dict()}"
    )

    rows: list[dict] = []
    for paradigm, feat_file in PARADIGMS:
        p = RESULTS / feat_file
        if not p.exists():
            log.warning(f"Missing {p}; skipping {paradigm}.")
            continue

        df = pd.read_parquet(p)
        if "fm" in df.columns:
            df = df.drop(columns=["fm"])
        df = df[df["perturbation"] == "consensus"].copy()
        feature_cols = [
            c
            for c in df.columns
            if c not in ("case_id", "nodule_id", "perturbation")
            and not c.startswith("diagnostics_")
        ]
        merged = df.merge(
            labels[["case_id", "nodule_id", "label", "stratum"]],
            on=["case_id", "nodule_id"],
            how="inner",
        )

        for stratum_name, _, _ in STRATA:
            sub = merged[merged["stratum"] == stratum_name]
            n_total = len(sub)
            n_malignant = int((sub["label"] == 1).sum())
            row = {
                "paradigm": paradigm,
                "stratum": stratum_name,
                "n_total": n_total,
                "n_malignant": n_malignant,
            }
            if n_total < MIN_N_TOTAL:
                log.warning(f"[{paradigm}/{stratum_name}] n={n_total} (<{MIN_N_TOTAL}); skipping eval")
                row.update({"auc": float("nan"), "auc_ci_lo": float("nan"), "auc_ci_hi": float("nan")})
                rows.append(row)
                continue
            X = sub[feature_cols].to_numpy(dtype=np.float32)
            y = sub["label"].to_numpy(dtype=int)
            res = evaluate(X, y)
            if res is None:
                log.warning(
                    f"[{paradigm}/{stratum_name}] n={n_total} m={n_malignant}; "
                    f"insufficient class balance for {N_SPLITS}-fold CV"
                )
                row.update({"auc": float("nan"), "auc_ci_lo": float("nan"), "auc_ci_hi": float("nan")})
                rows.append(row)
                continue
            row.update(res)
            rows.append(row)
            log.info(
                f"[{paradigm}/{stratum_name}] N={n_total} (M={n_malignant}, "
                f"B={n_total - n_malignant})  AUC={res['auc']:.3f} "
                f"({res['auc_ci_lo']:.3f}-{res['auc_ci_hi']:.3f})"
            )

    out = pd.DataFrame(rows)
    out.to_csv(out_csv, index=False)
    log.info(f"Wrote {len(out)} rows -> {out_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=RESULTS / "downstream_metrics_by_stratum.csv")
    args = parser.parse_args()
    main(args.labels, args.out)
