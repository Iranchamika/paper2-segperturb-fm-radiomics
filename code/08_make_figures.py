"""
08_make_figures.py — produce the four main-text figures for the Medical Physics submission.

Last script in the pipeline. Reads the three analysis CSVs (icc_table.csv,
downstream_metrics.csv, downstream_metrics_by_stratum.csv) plus a small
hand-picked set of nodule NRRDs, and writes four PNGs at 300 dpi into
``figures/``. Each figure supports a specific Results sub-section in the
manuscript and is rendered with serif fonts to match Medical Physics
journal style.

  - Figure 1 (``fig1_perturbation_examples``) — 3 nodules x 4 perturbation
    conditions overlay grid. Supports manuscript Methods §2.3 (perturbation
    conditions) and visually demonstrates the 25 % volume-preservation
    guard from decisions.log #012 — the small-benign row deliberately
    shows the ``(skipped by retention guard)`` annotation in the erosion
    column for small nodules that did not survive the guard, which is
    the pedagogical payoff of including a small example.

  - Figure 2 (``fig2_icc_distributions``) — two-panel ICC distribution
    summary. Supports manuscript Results §3.3 (distribution-shape
    divergence, H1'). Panel (a) is the stacked-bar stratum proportions
    that shows the bimodal radiomics vs unimodal-moderate BiomedCLIP
    pattern at a glance; panel (b) is the ECDF that makes the K-S D=0.72
    finding visually obvious.

  - Figure 3 (``fig3_auc_forest``) — 14-row forest of pre-vs-post-ICC-filter
    AUC by paradigm and threshold. Supports manuscript Results §3.4
    (downstream classification, H2 and H3). The BiomedCLIP icc>=0.85 row
    is the visual carrier of the calibration-improvement bonus finding.

  - Figure 4 (``fig4_stratified_auc_forest``) — three-panel within-stratum
    AUC forest. Supports manuscript Results §3.5 and Discussion §4.4
    (size-confound finding). The >20 mm panel deliberately shows the
    ``Stratum not evaluable`` annotation per decisions.log #022 — that
    annotation is part of the headline message, not a render bug.

The `main()` function gates each figure on the existence of its input CSV,
so the script can be re-run after a partial pipeline pass (e.g., after
script 06 completes but before script 07 finishes) and will produce
whichever figures have inputs available.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import SimpleITK as sitk

from utils import DATA_PERTURB, DATA_PROCESSED, FIGURES, RESULTS, get_logger

log = get_logger("08_figures")

sns.set_style("whitegrid")
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "legend.fontsize": 9,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)


def fig2_icc_distributions(icc_csv: Path, out: Path):
    """Render the two-panel ICC distribution summary (Figure 2 in the manuscript).

    Panel (a): stacked bar chart of stratum proportions per paradigm.
    Panel (b): empirical CDF of ICC per paradigm with the 0.75 stability
    threshold annotated.

    Reads the long-format ``icc_table.csv`` produced by script 06 (one
    row per (paradigm, feature) pair). The stratum bars use the RdYlGn
    diverging colormap so the eye reads poor->excellent left-to-right as
    red->green, matching the radiomics QA literature convention.

    Supports manuscript Results §3.3 (H1' distribution-shape divergence).
    The visual pattern this figure surfaces is the bimodal radiomics vs
    unimodal-moderate BiomedCLIP distribution — Kolmogorov-Smirnov
    D = 0.72, p < 10^-43 between BiomedCLIP and PyRadiomics-2D.
    """
    df = pd.read_csv(icc_csv)
    counts = df.groupby(["paradigm", "stratum"]).size().unstack(fill_value=0)
    # Force the four-stratum column order so the stacked bars read poor ->
    # moderate -> good -> excellent (left to right within each bar) and the
    # RdYlGn colormap maps poor -> red and excellent -> green.
    counts = counts[["poor", "moderate", "good", "excellent"]]
    pct = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    pct.plot(kind="bar", stacked=True, ax=axes[0], colormap="RdYlGn", edgecolor="black", linewidth=0.5)
    axes[0].set_ylabel("Proportion of features (%)")
    axes[0].set_xlabel("")
    axes[0].set_title("(a) ICC stratum distribution per paradigm")
    axes[0].legend(title="ICC stratum", loc="upper right", bbox_to_anchor=(1.4, 1))
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)

    for paradigm in df["paradigm"].unique():
        sub = df[df["paradigm"] == paradigm]["icc"].dropna().sort_values().values
        ecdf = np.arange(1, len(sub) + 1) / len(sub)
        axes[1].plot(sub, ecdf, label=paradigm, linewidth=2)
    axes[1].axvline(0.75, color="grey", linestyle="--", alpha=0.7, label="Stability threshold 0.75")
    axes[1].set_xlabel("ICC(3,1)")
    axes[1].set_ylabel("ECDF")
    axes[1].set_title("(b) ICC empirical CDF per paradigm")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    log.info(f"Saved {out}")


def fig3_auc_forest(metrics_csv: Path, out: Path):
    """Render the 14-row pre-vs-post-ICC-filter AUC forest (Figure 3 in the manuscript).

    One row per (paradigm, ICC-filter-threshold) configuration with the
    stratified-bootstrap 95 % CI as horizontal error bars. The k=
    annotation in each y-axis label shows how many features survived
    that paradigm's filter, which is the visual carrier of the H1'
    follow-on observation that BiomedCLIP retains 90 % of dimensions
    even at icc >= 0.75 but radiomics drops sharply.

    Reads ``downstream_metrics.csv`` produced by script 07. The filter
    category order is hard-coded so the y-axis reads top-to-bottom in
    threshold order ("all" first, then increasing ICC cut-offs).

    Supports manuscript Results §3.4 (H2 and H3). The BiomedCLIP icc>=0.85
    row sits visibly higher than the BiomedCLIP "all" row — that visual
    is the carrier of the calibration-improvement bonus finding the
    manuscript Discussion §4.3 calls out.
    """
    df = pd.read_csv(metrics_csv)
    paradigms = df["paradigm"].unique()
    # Categorical with explicit category order so .sort_values picks up the
    # natural threshold ordering rather than alphabetical.
    filters = ["all", "icc>=0.50", "icc>=0.75", "icc>=0.85", "icc>=0.90"]
    df["filter"] = pd.Categorical(df["filter"], categories=filters, ordered=True)
    df = df.sort_values(["paradigm", "filter"])

    fig, ax = plt.subplots(figsize=(8, 4 + 0.4 * len(df)))
    y_pos = np.arange(len(df))
    ax.errorbar(
        df["auc"],
        y_pos,
        xerr=[df["auc"] - df["auc_ci_lo"], df["auc_ci_hi"] - df["auc"]],
        fmt="o",
        capsize=3,
        linewidth=1.5,
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{r.paradigm} | {r.filter} (k={int(r.n_features)})" for r in df.itertuples()])
    ax.invert_yaxis()
    ax.axvline(0.5, color="grey", linestyle=":", alpha=0.6)
    ax.set_xlabel("Out-of-fold AUC (bootstrap 95% CI)")
    ax.set_title("Pre-vs-post ICC-filter downstream malignancy AUC")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    log.info(f"Saved {out}")


def fig1_perturbation_examples(out: Path):
    """Render the 3 x 4 perturbation-example grid (Figure 1 in the manuscript).

    Three rows (one nodule each, spanning small benign / medium malignant /
    large malignant) crossed with four columns (consensus / erosion /
    dilation r=2 / Dice-calibrated). Each cell shows the lung-windowed
    max-area axial slice with the perturbation mask boundary drawn in
    red. The small-benign row's erosion cell is allowed to render the
    ``(skipped by retention guard)`` annotation — that annotation is
    the pedagogical payoff of including a small nodule because it shows
    the decisions.log #012 25 % volume-preservation guard doing the
    thing it was designed to do.

    Example nodule selection is hard-coded in the ``examples`` list and
    was chosen once based on diameter + mask availability (see the chat
    session log from 2026-05-25). If reviewers ask for different examples,
    edit the list — no other change to the figure code is required.

    Supports manuscript Methods §2.3 (segmentation perturbation conditions).
    Lung-window WL/WW of -600/1500 matches standard pulmonary parenchyma
    display and the windowing used in script 05 for FM input.
    """
    # Picked once based on diameter + mask availability (see chat session 2026-05-25).
    # Each tuple: (case_id, nodule_id, row_label, erode_tag, erode_title)
    examples = [
        ("LIDC-IDRI-0386", "nodule_03", "Small benign\n(d=8 mm)",        "E1", "Erode r=1 vx"),
        ("LIDC-IDRI-0543", "nodule_01", "Medium malignant\n(d=16 mm)",   "E2", "Erode r=2 vx"),
        ("LIDC-IDRI-0015", "nodule_00", "Large malignant\n(d=23 mm)",    "E2", "Erode r=2 vx"),
    ]
    wl, ww = -600, 1500
    lo, hi = wl - ww / 2, wl + ww / 2

    fig, axes = plt.subplots(3, 4, figsize=(12, 9))

    for i, (case_id, nodule_id, row_label, erode_tag, erode_title) in enumerate(examples):
        img_path = DATA_PROCESSED / case_id / nodule_id / "img.nrrd"
        cons_path = DATA_PERTURB / case_id / nodule_id / "mask_consensus.nrrd"
        img = sitk.ReadImage(str(img_path))
        cons = sitk.ReadImage(str(cons_path))
        spacing = img.GetSpacing()  # (sx, sy, sz)
        img_arr = sitk.GetArrayFromImage(img)
        cons_arr = sitk.GetArrayFromImage(cons)

        # max-area axial slice from the consensus mask
        areas = cons_arr.sum(axis=(1, 2))
        z = int(areas.argmax())

        # lung windowing
        img_slice = np.clip(img_arr[z], lo, hi)
        img_slice = ((img_slice - lo) / (hi - lo) * 255).astype(np.uint8)

        # bbox crop from consensus + 50% pad
        mask_slice = cons_arr[z]
        ys, xs = np.where(mask_slice > 0)
        if len(ys) == 0:
            continue
        y0, y1 = int(ys.min()), int(ys.max())
        x0, x1 = int(xs.min()), int(xs.max())
        pad_y = int(0.5 * (y1 - y0) + 5)
        pad_x = int(0.5 * (x1 - x0) + 5)
        y0p = max(0, y0 - pad_y)
        y1p = min(img_slice.shape[0], y1 + pad_y + 1)
        x0p = max(0, x0 - pad_x)
        x1p = min(img_slice.shape[1], x1 + pad_x + 1)
        crop_img = img_slice[y0p:y1p, x0p:x1p]
        h, w = crop_img.shape

        col_tags = ["consensus", erode_tag, "D2", "DC"]
        col_titles = ["Consensus", erode_title, "Dilate r=2 vx", "Dice-matched"]

        for j, (tag, title) in enumerate(zip(col_tags, col_titles)):
            ax = axes[i, j]
            ax.imshow(crop_img, cmap="gray", interpolation="nearest", aspect="equal")

            mask_path = DATA_PERTURB / case_id / nodule_id / f"mask_{tag}.nrrd"
            if mask_path.exists():
                m_arr = sitk.GetArrayFromImage(sitk.ReadImage(str(mask_path)))
                m_crop = m_arr[z][y0p:y1p, x0p:x1p]
                if m_crop.any():
                    ax.contour(m_crop, levels=[0.5], colors=["red"], linewidths=1.5)
                else:
                    ax.text(0.5, 0.5, "(empty\nmask)", color="red", ha="center",
                            va="center", transform=ax.transAxes, fontsize=10, fontweight="bold")
            else:
                ax.text(0.5, 0.5, "(skipped by\nretention guard)", color="red",
                        ha="center", va="center", transform=ax.transAxes, fontsize=9,
                        fontweight="bold")

            if i == 0:
                ax.set_title(title)
            if j == 0:
                ax.set_ylabel(row_label, rotation=90, labelpad=14, fontsize=10)
                # nodule ID annotation top-left
                ax.text(0.02, 0.97, f"{case_id[-4:]} {nodule_id}",
                        color="white", transform=ax.transAxes,
                        fontsize=7, va="top",
                        bbox={"facecolor": "black", "alpha": 0.55, "pad": 1.5,
                              "edgecolor": "none"})
                # 10mm scale bar bottom-right
                bar_px = max(2, int(round(10.0 / spacing[0])))
                ax.plot([w - bar_px - 4, w - 4], [h - 4, h - 4],
                        color="white", linewidth=3, solid_capstyle="butt")
                ax.text(w - bar_px / 2 - 4, h - 7, "10 mm",
                        color="white", ha="center", va="bottom", fontsize=7,
                        bbox={"facecolor": "black", "alpha": 0.55, "pad": 1,
                              "edgecolor": "none"})

            ax.set_xticks([])
            ax.set_yticks([])

    fig.suptitle("Example nodules with consensus, erosion, dilation, and Dice-calibrated perturbation masks",
                 fontsize=11, y=1.00)
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    log.info(f"Saved {out}")


def fig4_stratified_auc_forest(stratum_csv: Path, out: Path):
    """Render the three-panel within-stratum AUC forest (Figure 4 in the manuscript).

    One panel per diameter stratum (6-10 mm / 10-20 mm / >20 mm) with
    three paradigms per panel (radiomics-3D / radiomics-2D / BiomedCLIP),
    each marker showing the within-stratum AUC and bootstrap 95 % CI.
    The >20 mm panel deliberately renders the ``Stratum not evaluable``
    annotation rather than a forest because LIDC contains only ~3 benigns
    in that size range (Lung-RADS clinical convention treats >20 mm solid
    nodules as suspicious by definition, biasing the source cohort).
    The annotation IS the finding — do not interpret it as a render bug.

    Reads ``downstream_metrics_by_stratum.csv`` from script 07b.

    Supports manuscript Results §3.5 and Discussion §4.4. This is the
    paper's headline methodological figure per decisions.log #022: the
    visual demonstration that the aggregate AUC gap (radiomics 0.95 vs
    BiomedCLIP 0.90) was largely a size-malignancy confound, because the
    paradigm AUCs converge within matched-size strata (6-10 mm: all
    three at ~0.77; 10-20 mm: radiomics-3D 0.889 vs BiomedCLIP 0.794
    with overlapping CIs).
    """
    df = pd.read_csv(stratum_csv)

    paradigm_order = ["radiomics-3d", "radiomics-2d", "biomedclip"]
    paradigm_colors = {
        "radiomics-3d": "#1f77b4",  # blue
        "radiomics-2d": "#17becf",  # teal
        "biomedclip": "#ff7f0e",    # orange
    }
    paradigm_labels = {
        "radiomics-3d": "radiomics-3D",
        "radiomics-2d": "radiomics-2D",
        "biomedclip": "BiomedCLIP",
    }
    strata = [
        ("6-10mm", "6-10 mm"),
        ("10-20mm", "10-20 mm"),
        (">20mm", ">20 mm"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)

    for ax, (stratum_key, stratum_label) in zip(axes, strata):
        sub = df[df["stratum"] == stratum_key]
        n_max = int(sub["n_total"].max()) if len(sub) else 0
        rep = sub[sub["n_total"] == n_max].iloc[0] if len(sub) else None
        if rep is not None:
            n_total = int(rep["n_total"])
            n_malig = int(rep["n_malignant"])
            pct_malig = 100 * n_malig / n_total if n_total else 0
            title = f"{stratum_label} (n={n_total}; {round(pct_malig)}% malignant)"
        else:
            title = stratum_label

        ax.set_title(title)
        ax.set_xlim(0.4, 1.0)
        ax.set_xlabel("AUC")
        ax.set_yticks(range(len(paradigm_order)))
        ax.set_yticklabels([paradigm_labels[p] for p in paradigm_order])
        ax.invert_yaxis()
        ax.axvline(0.5, color="grey", linestyle="--", alpha=0.5, linewidth=1)

        if sub["auc"].isna().all():
            ax.text(
                0.5, 0.5,
                "Stratum not evaluable\n(<5 benigns in LIDC corpus)",
                ha="center", va="center",
                transform=ax.transAxes,
                fontsize=12, color="grey", style="italic",
            )
            continue

        for y_pos, paradigm in enumerate(paradigm_order):
            row = sub[sub["paradigm"] == paradigm]
            if len(row) == 0 or pd.isna(row["auc"].iloc[0]):
                continue
            r = row.iloc[0]
            ax.errorbar(
                r["auc"], y_pos,
                xerr=[[r["auc"] - r["auc_ci_lo"]], [r["auc_ci_hi"] - r["auc"]]],
                fmt="o", markersize=8, capsize=4, linewidth=2,
                color=paradigm_colors[paradigm],
            )
            label = f'AUC = {r["auc"]:.3f} ({r["auc_ci_lo"]:.3f}-{r["auc_ci_hi"]:.3f})'
            ax.annotate(
                label,
                xy=(r["auc_ci_hi"], y_pos),
                xytext=(8, 0),
                textcoords="offset points",
                va="center",
                fontsize=8,
            )

    fig.suptitle(
        "Within-stratum malignancy classification AUC by feature paradigm",
        fontsize=12, y=1.02,
    )
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    log.info(f"Saved {out}")


def main():
    """Generate every available figure into the FIGURES directory.

    Each figure is gated on the existence of its required input CSV so the
    script can be re-run after a partial pipeline pass and will produce
    whichever figures have inputs available. Figure 1 has no CSV dependency
    (it reads NRRD files directly from the on-disk perturbation tree), so
    it is rendered unconditionally — if the hard-coded example nodules are
    missing on disk the function will log an error and continue.

    The four output PNGs land in ``figures/`` at 300 dpi (matplotlib
    rcParams above). LaTeX ``\\includegraphics`` calls in
    ``overleaf_project/results.tex`` pick them up by exact filename.
    """
    icc_csv = RESULTS / "icc_table.csv"
    metrics_csv = RESULTS / "downstream_metrics.csv"
    stratum_csv = RESULTS / "downstream_metrics_by_stratum.csv"
    fig1_perturbation_examples(FIGURES / "fig1_perturbation_examples.png")
    if icc_csv.exists():
        fig2_icc_distributions(icc_csv, FIGURES / "fig2_icc_distributions.png")
    if metrics_csv.exists():
        fig3_auc_forest(metrics_csv, FIGURES / "fig3_auc_forest.png")
    if stratum_csv.exists():
        fig4_stratified_auc_forest(stratum_csv, FIGURES / "fig4_stratified_auc.png")
    log.info("Figure generation complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
