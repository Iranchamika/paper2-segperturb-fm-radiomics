"""
02b_balance_cohort.py — downsample the larger class to produce a balanced cohort.

Third-and-a-half script in the pipeline. Reads ``data/labels.csv`` (the 353-row
unbalanced yield from script 02: 198 malignant + 155 benign) and writes
``data/labels_balanced.csv`` (the 310-row balanced cohort: 155 + 155). The
original ``labels.csv`` is left untouched so the unbalanced yield remains
available for the pre-specified sensitivity analyses (decisions.log #014).

Why balance at this stage rather than weighting the classifier:

  - The downstream L2-logistic regression in script 07 reports AUC, Brier, and
    expected calibration error. AUC is class-balance insensitive in the
    asymptotic limit but exhibits noticeable finite-sample bias on imbalanced
    cohorts (Brier and ECE are even more sensitive).
  - Downsampling rather than upsampling avoids fabricating data and preserves
    the genuine variability of the surviving malignants.
  - The 43 discarded malignant nodules remain on disk in ``data/processed/``
    and ``data/perturbations/``; the discard is purely at the labels-join
    stage in script 07. They are therefore freely available for the planned
    'unbalanced sensitivity' supplementary analysis without re-extraction.
  - Class weighting in logistic regression would not address the calibration
    issue because the class prior fed into the sigmoid would still be
    mis-specified; downsampling fixes the prior.

Provenance: decisions.log #014 (cohort lock, 2026-05-25). Bit-exact
reproducibility verified across two independent runs because both the
``fix_seed`` call and the inner ``random_state=0`` on ``DataFrame.sample``
pin every RNG that pandas touches during the groupby-and-sample.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from utils import DATA_PROCESSED, fix_seed, get_logger

log = get_logger("02b_balance")


def main(labels_in: Path, labels_out: Path) -> None:
    """Downsample the majority class to the minority count and persist labels_balanced.csv.

    Parameters
    ----------
    labels_in : Path
        Path to the unbalanced labels CSV from script 02 (typically
        ``data/labels.csv``). Must have at least the columns ``case_id``,
        ``nodule_id``, ``label`` (0 = benign, 1 = malignant).
    labels_out : Path
        Path to write the balanced labels CSV (typically
        ``data/labels_balanced.csv``).

    Side effects: writes one CSV; logs the input / output class counts. The
    final row order is sorted (label, case_id, nodule_id) so the file is
    deterministic across runs.
    """
    # fix_seed seeds numpy/random/torch with 42 (utils.SEED). It does NOT
    # affect pandas' DataFrame.sample, which is why we pin random_state=0
    # on the .sample call below — together they pin every RNG that touches
    # the downsampling step.
    fix_seed()
    df = pd.read_csv(labels_in)
    counts = df["label"].value_counts().to_dict()
    # n_min is the minority-class count (155 benigns at the 6 mm threshold,
    # per decisions.log #014). The balanced cohort takes this many per class.
    n_min = min(counts.values())
    log.info(f"Input: {len(df)} nodules, per-class counts {counts}, balancing to {n_min}/class")

    # groupby + apply + sample preserves the within-group ordering but lets
    # us downsample each group independently. ``group_keys=False`` keeps the
    # original row index, which we then drop because the labels CSV is
    # row-position-indexed downstream.
    sampled = (
        df.groupby("label", group_keys=False)
        .apply(lambda g: g if len(g) <= n_min else g.sample(n=n_min, random_state=0))
        .reset_index(drop=True)
    )
    # Sort for deterministic on-disk ordering — important for the
    # bit-exact-reproducibility claim in Methods §2.6 and decisions.log #014.
    sampled = sampled.sort_values(["label", "case_id", "nodule_id"]).reset_index(drop=True)

    out_counts = sampled["label"].value_counts().to_dict()
    log.info(f"Output: {len(sampled)} nodules, per-class counts {out_counts}")

    sampled.to_csv(labels_out, index=False)
    log.info(f"Wrote {labels_out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-in", type=Path, default=DATA_PROCESSED.parent / "labels.csv")
    parser.add_argument("--labels-out", type=Path, default=DATA_PROCESSED.parent / "labels_balanced.csv")
    args = parser.parse_args()
    main(args.labels_in, args.labels_out)
