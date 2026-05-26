"""
06_compute_icc.py — per-feature ICC across perturbation conditions, per paradigm.

Seventh script in the pipeline. For every feature/dimension in every paradigm
(radiomics-3D, radiomics-2D, BiomedCLIP, and RadImageNet if available),
compute the intraclass correlation coefficient across the ten universal
perturbation conditions (consensus + R1, R2, R3 + D1, D2 + T1, T2, T3 + DC)
using nodule as the target and perturbation as the rater. The output
``icc_table.csv`` is the input to (i) the H1 z-test and H1' Kolmogorov-Smirnov
test in the manuscript Results §3.2 and §3.3, and (ii) the ICC-filter
selection in the downstream classifier (script 07).

Two non-obvious design choices, both tied to decisions.log entries:

  1. We report TWO ICC variants per feature, with ICC(2,1) as the primary
     and ICC(3,1) as the secondary (decisions.log #003):
       - ICC(2,1) — two-way random effects, single rater, absolute agreement.
         The 'two-way random' form treats BOTH nodule and perturbation as
         random samples from larger populations, which licences generalisation
         to readers / perturbations not in this study. The 'absolute
         agreement' form penalises systematic bias between perturbations,
         which is what we want when asking whether the value of a feature
         is *invariant* under perturbation (rather than just correlated
         under perturbation).
       - ICC(3,1) — two-way mixed effects, single rater, consistency. The
         'mixed effects' form treats perturbation as fixed; we report it
         alongside the primary because the radiomics QA literature
         historically uses ICC(3,1) and reviewers may want to compare.

  2. We restrict the ICC computation to the ten STANDARD perturbations
     present (or extractable) for every nodule (decisions.log derived from
     #015). pingouin's ICC requires a complete (target x rater) matrix and
     does listwise deletion otherwise. If we included E1/E2/E3 (which the
     #012 volume-preservation guard intentionally skips for small nodules)
     or R5/R6/R7 (which only exist for the small subset of LIDC nodules
     with >4 reader annotations), the strict set-intersection of available
     perturbations across all nodules collapses to almost nothing because
     each perturbation has 1-2 sporadic extraction failures on different
     nodules. Erosion and high-rater-count sensitivity analyses live in
     supplementary tables.

The output ``icc_table.csv`` has one row per (paradigm, feature) pair with
columns: paradigm, feature_name, icc (ICC2 primary), ci_lo, ci_hi,
icc3_consistency (ICC3 secondary), icc3_ci_lo, icc3_ci_hi, stratum
(poor / moderate / good / excellent per Koo & Li 2016 thresholds).

Inputs (any subset may exist; missing files are skipped with a warning):
    results/radiomics_features_3d.parquet
    results/radiomics_features_2d.parquet
    results/fm_embeddings_biomedclip.parquet
    results/fm_embeddings_radimagenet.parquet
Output: results/icc_table.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg
from tqdm import tqdm

from utils import RESULTS, fix_seed, get_logger

log = get_logger("06_icc")

# ICC stratum cut-offs per Koo & Li 2016 (J Chiropr Med 15(2):155-163), the
# standard guideline-paper citation for ICC reliability categories. These
# strata are used unchanged across the radiomics QA literature, so a reader
# can map our 'good' or 'excellent' counts directly onto comparable papers.
ICC_STRATA = [(0.00, 0.50, "poor"), (0.50, 0.75, "moderate"), (0.75, 0.90, "good"), (0.90, 1.01, "excellent")]


def stratum_of(icc: float) -> str:
    """Classify a single ICC value into one of the four standard strata.

    Returns ``"na"`` for NaN or out-of-range inputs, which lets the
    downstream stratum crosstab in ``main`` aggregate cleanly even when
    a small number of features failed to compute (typically due to
    constant-value features that produce a zero-variance ICC denominator).
    """
    for lo, hi, name in ICC_STRATA:
        if lo <= icc < hi:
            return name
    return "na"


# --------------------------------------------------------------------------- #
def icc_per_feature(df_long: pd.DataFrame) -> pd.DataFrame:
    """Compute ICC(2,1) and ICC(3,1) for one feature across perturbation conditions.

    The input must be long-format with one row per (case_id, nodule_id,
    perturbation) combination plus a ``value`` column carrying the
    feature's value for that combination. The function constructs a
    composite ``target`` column from case_id + nodule_id (pingouin needs
    a single string identifier for the 'target' of an ICC) and passes the
    frame to ``pingouin.intraclass_corr``.

    Returns a 1-row DataFrame so the caller can vstack across features
    cleanly. On failure (typically zero-variance features) returns a row
    of NaNs rather than raising — the caller filters NaN rows out of the
    stratum crosstab.

    Per decisions.log #003, ICC(2,1) is the primary statistic and ICC(3,1)
    is reported alongside for backward compatibility with the radiomics QA
    literature. See the module docstring for the full justification.
    """
    # pingouin expects targets=nodule (random), raters=perturbation (fixed)
    df_long = df_long.copy()
    df_long["target"] = df_long["case_id"].astype(str) + "_" + df_long["nodule_id"].astype(str)
    try:
        res = pg.intraclass_corr(
            data=df_long, targets="target", raters="perturbation", ratings="value", nan_policy="omit"
        )
        # Updated 2026-05-21 (decisions.log #003): ICC(2,1) two-way random,
        # absolute agreement is now the primary statistic. ICC(3,1) reported
        # alongside for backward compatibility.
        row2 = res[res["Type"] == "ICC2"]  # two-way random, absolute agreement, single rater
        row3 = res[res["Type"] == "ICC3"]  # two-way mixed, consistency, single rater
        return pd.DataFrame(
            {
                "icc": [float(row2["ICC"].iloc[0])],
                "ci_lo": [float(row2["CI95%"].iloc[0][0])],
                "ci_hi": [float(row2["CI95%"].iloc[0][1])],
                "icc3_consistency": [float(row3["ICC"].iloc[0])],
                "icc3_ci_lo": [float(row3["CI95%"].iloc[0][0])],
                "icc3_ci_hi": [float(row3["CI95%"].iloc[0][1])],
            }
        )
    except Exception as e:
        return pd.DataFrame({"icc": [np.nan], "ci_lo": [np.nan], "ci_hi": [np.nan], "icc3_consistency": [np.nan], "icc3_ci_lo": [np.nan], "icc3_ci_hi": [np.nan]})


def compute_for_paradigm(df: pd.DataFrame, paradigm: str, key_cols: tuple) -> pd.DataFrame:
    """Compute ICC for every feature/dimension in one paradigm.

    Workflow:
      1. Filter the long-format feature frame to the ten STANDARD
         perturbations (see module docstring rationale).
      2. Identify nodules with complete coverage of all ten standard
         perturbations and restrict to those — pingouin requires a
         complete (target x rater) matrix.
      3. Iterate over feature columns (everything except ``case_id``,
         ``nodule_id``, ``perturbation``). For each feature, slice the long
         frame to (keys + value) and call ``icc_per_feature``.
      4. Tag each result row with the paradigm name and the feature name
         and map the ICC into a stratum.

    Returns a long-format DataFrame with one row per feature for this
    paradigm; the caller (``main``) vstacks across paradigms into the
    final ``icc_table.csv``.

    The strict 'complete nodules only' filter is necessary because the
    25 % volume-preservation guard in script 03 (decisions.log #012)
    skips E1/E2/E3 for many small nodules, and LIDC reader counts vary
    (3-7 readers per nodule), so the available perturbations per nodule
    are heterogeneous. Without the filter, pingouin's listwise deletion
    would collapse nearly every feature to a degenerate ICC.
    """
    # ICC requires a complete (target × rater) matrix. Restrict to the
    # 10 STANDARD perturbations that script 03 produces for every nodule
    # (consensus + 3 inter-reader + 2 dilation + 3 translation + 1 Dice-calibrated),
    # then keep only nodules where every standard perturbation has been
    # successfully extracted in this paradigm (1-2 sporadic extraction
    # failures per perturbation otherwise collapse a strict set-intersection).
    # E1/E2/E3 are intentionally excluded because the #011 25%-retention guard
    # makes them unbalanced by design; R4-R7 are excluded because LIDC readers/
    # nodule varies. Both are addressed via supplementary sensitivity analyses.
    STANDARD_PERTS = ["consensus", "R1", "R2", "R3", "D1", "D2", "T1", "T2", "T3", "DC"]
    df = df[df["perturbation"].isin(STANDARD_PERTS)].copy()
    counts = df.groupby(["case_id", "nodule_id"])["perturbation"].nunique()
    complete_nodules = counts[counts == len(STANDARD_PERTS)].index
    log.info(
        f"[{paradigm}] using {len(complete_nodules)} of {len(counts)} nodules "
        f"(complete coverage of all {len(STANDARD_PERTS)} standard perturbations)"
    )
    df = df.set_index(["case_id", "nodule_id"]).loc[complete_nodules].reset_index()

    feature_cols = [c for c in df.columns if c not in key_cols]
    out = []
    for col in tqdm(feature_cols, desc=f"ICC[{paradigm}]"):
        long = df[list(key_cols) + [col]].rename(columns={col: "value"})
        res = icc_per_feature(long)
        res["paradigm"] = paradigm
        res["feature_name"] = col
        res["stratum"] = res["icc"].map(stratum_of)
        out.append(res)
    return pd.concat(out, ignore_index=True)


def main(out_csv: Path):
    """Load every available feature parquet, compute ICC per paradigm, vstack, write CSV.

    Iterates the four expected paradigms in a fixed order so the output CSV
    is deterministic across runs (radiomics-3d, radiomics-2d, biomedclip,
    radimagenet). Missing parquets (e.g., radimagenet when its weights
    were not granted in time — decisions.log #018 Plan B/C) are warned-and-
    skipped rather than raising, so the script can produce a partial
    icc_table.csv with whatever paradigms are extracted to date.

    Prints the headline stratum x paradigm crosstab at the end — this is
    the table I read off when verifying the H1 result during analysis,
    and it is what becomes Figure 2a's stacked bar chart.
    """
    fix_seed()
    rad_key = ("case_id", "nodule_id", "perturbation")
    tables = []

    # Radiomics arms are mode-suffixed (3d, 2d) per script 04 output convention.
    # The 2d arm exists to harmonize with the FM 2D-slice extraction (decisions.log #017),
    # so both paradigms get their own ICC pass and downstream comparison.
    for mode in ("3d", "2d"):
        p = RESULTS / f"radiomics_features_{mode}.parquet"
        if not p.exists():
            log.warning(f"Missing {p}; skipping.")
            continue
        rad = pd.read_parquet(p)
        rad = rad.drop(columns=[c for c in rad.columns if c.startswith("diagnostics_")])
        tables.append(compute_for_paradigm(rad, f"radiomics-{mode}", rad_key))

    for fm in ("biomedclip", "radimagenet"):
        p = RESULTS / f"fm_embeddings_{fm}.parquet"
        if not p.exists():
            log.warning(f"Missing {p}; skipping.")
            continue
        df = pd.read_parquet(p).drop(columns=["fm"], errors="ignore")
        tables.append(compute_for_paradigm(df, fm, rad_key))

    full = pd.concat(tables, ignore_index=True)
    full.to_csv(out_csv, index=False)
    log.info(f"Wrote ICC table for {len(full)} features → {out_csv}")

    # Print headline summary
    summary = full.groupby(["paradigm", "stratum"]).size().unstack(fill_value=0)
    print("\n=== ICC stratum distribution by paradigm ===")
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=RESULTS / "icc_table.csv")
    args = parser.parse_args()
    main(args.out)
