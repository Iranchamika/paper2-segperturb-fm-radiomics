# Protocol — Segmentation-Perturbation Propagation in Foundation-Model Embeddings versus IBSI-aligned Radiomics

**Version:** 1.0 (DRAFT — locks 2026-05-27)
**Author:** Iran (Independent Researcher, a1846500@adelaide.edu.au)
**Target journal:** *Medical Physics* (AAPM, Wiley)
**OSF pre-registration:** to be deposited 2026-05-26 (before any feature extraction)
**Code/data repository:** private GitHub `paper2-segperturb-fm-radiomics` → public on submission

---

## 1. Background and rationale

*(Updated 2026-05-21 to position explicitly against Pai 2025 TumorImagingBench per verification pass.)*

Two paradigms now dominate quantitative medical-image feature extraction. Handcrafted radiomics produces mathematically defined, IBSI-aligned features whose sensitivity to upstream segmentation variability is well characterised: reproducibility studies routinely find that 20-60 % of radiomic features fall below ICC 0.75 across inter-rater contour variation, prompting the now-standard practice of ICC-filtering before downstream modelling [Refs: Pavic 2018; Yang 2020; van Timmeren 2020].

**Distinct contribution relative to Pai et al. 2024 (peer-reviewed, *Nature Machine Intelligence*, [DOI: 10.1038/s42256-024-00807-9](https://doi.org/10.1038/s42256-024-00807-9), PMC10957482).** Pai 2024 introduces FMCIB (a 3D contrastive-SSL ResNet50) and reports ICC = 0.984 for its feature-based predictions on RIDER same-day repeat scans, plus significantly higher stability than a Supervised CNN baseline under 50-trial 3D Gaussian seed-point jitter (σ² = 16 voxels per dimension) on the LUNG1 cohort. They (i) do not perturb the segmentation mask itself — only the seed point, (ii) do not include an IBSI-aligned handcrafted-radiomics arm (compared baselines are deep-learning: Supervised CNN, Med3D, Models Genesis), (iii) report a single ICC for the final model output rather than per-dimension ICC of the embedding, (iv) use only 3D FMs, and (v) do not report pre-vs-post stability-filter downstream AUC. Our study addresses all five gaps directly on the LIDC-IDRI lung-CT cohort, which uniquely provides up to 4-reader natural segmentation variability per nodule.

**Note on the 2025 TumorImagingBench preprint.** Pai et al. 2025 ([DOI: 10.21203/rs.3.rs-6630446/v1](https://doi.org/10.21203/rs.3.rs-6630446/v1), Research Square) extends Pai 2024 to ten 3D FMs using cosine similarity instead of ICC. It has not undergone peer review as of the submission date of this manuscript and is therefore cited as a *preprint* in §4.2 with that status noted explicitly. Per our pre-registered convention (consistent with the protocol of our companion systematic review, PROSPERO CRD420261393443), preprints are not treated as peer-reviewed precedents.

Pretrained foundation-model (FM) embeddings — BiomedCLIP, RadImageNet, MedSAM image-encoder, CT-FM and similar — produce dense vector representations from the same regions of interest, and have been shown to outperform handcrafted radiomics on a range of clinical prediction tasks [Refs: Pai 2025 TumorImagingBench; Iran 2026 systematic review]. The clinical promise of FM embeddings is partly that they may be more robust to upstream variability than handcrafted features because the pretraining objective implicitly enforces invariance to many imaging-domain perturbations.

This claim has not been tested under controlled segmentation perturbation in lung CT. *TumorImagingBench* (Pai 2025) measured embedding similarity via cosine distance on the RIDER test-retest dataset but did not perturb segmentations and did not compare against radiomics. A 2025 SPIE *Journal of Medical Imaging* paper (Cosma 2025, arxiv 2504.01692) studied segmentation-variability propagation in breast-MRI radiomics for TNBC subtype prediction and reported the counterintuitive finding that *segmentation accuracy does not significantly impact predictive performance* and that *ICC-based feature filtering may exclude valuable predictive features*. Whether this finding generalises (i) to lung CT, (ii) to foundation-model embeddings, and (iii) under controlled perturbation magnitudes beyond inter-rater variability, is unknown.

This protocol defines a prospectively designed, controlled-perturbation reproducibility study of FM embeddings versus IBSI-aligned PyRadiomics on the public LIDC-IDRI lung-CT cohort, where every nodule carries up to four independent expert segmentations. We add synthetic perturbations (erosion, dilation, translation) at controlled magnitudes to span a wider variability range than inter-rater alone, and we evaluate downstream malignancy classification performance with and without stability filtering.

## 2. Hypotheses (pre-specified)

**H1 (primary).** The proportion of feature dimensions classified as stable (ICC(3,1) ≥ 0.75) across segmentation perturbations is higher for BiomedCLIP and RadImageNet-ResNet50 embeddings than for IBSI-aligned PyRadiomics features extracted from the same nodules.

**H2 (secondary).** The downstream AUC degradation when training on stable-only features (post-ICC-filter at threshold 0.75) versus all features is smaller for FM embeddings than for radiomics, indicating greater task-relevant feature concentration in stable FM dimensions.

**H3 (exploratory).** The Cosma 2025 finding — that ICC-filtering may exclude predictive features — generalises to lung-CT FM embeddings: post-filter AUC will be non-inferior to or modestly lower than pre-filter AUC for both paradigms when classifier hyperparameters are tuned within-fold.

**H4 (mechanistic, exploratory).** Among FM embeddings, dimensions with the highest ICC under perturbation correspond to a small, identifiable subset (<10 % of total dimensions) whose linear-probe weights for malignancy classification are disproportionately large, supporting a "stable-informative core" interpretation of FM representational structure.

## 3. Study design

Prospective, controlled-perturbation, in-silico reproducibility study using publicly available, fully de-identified imaging data. No human subjects contact, no IRB required (TCIA Data Use Agreement covers all use). Single solo investigator; intra-rater reliability on a 10 % re-extraction subset will be documented.

## 4. Dataset

**Primary:** LIDC-IDRI (Lung Image Database Consortium and Image Database Resource Initiative; 1 018 thoracic CT scans, 2 669 annotated nodules ≥3 mm, up to 4 reader-independent segmentations per nodule, with malignancy ratings on a 1-5 scale by each reader) [Refs: Armato 2011].

**Subset for this study (final, locked 2026-05-25):** *(see decisions.log entries #001, #011, #014)* **310 nodules from 227 unique patients**, balanced 155 malignant + 155 benign, selected with the following inclusion criteria:
- Nodule has segmentations from ≥3 of 4 readers (ensures meaningful inter-rater ICC).
- **Median diameter ≥6 mm** (Fleischner Society actionable threshold for solid pulmonary nodules; relaxed from the original 10 mm pre-registered floor through the cascade documented in decisions.log #001 → #011 because the LIDC benign-≥10 mm pool exhausted at ~29 nodules across 600 downloaded patients).
- Median malignancy rating ≤2 (benign) or ≥4 (malignant) — yields a clean binary label.
- Balanced cohort produced by seeded random downsampling of the larger class (`02b_balance_cohort.py`, seed 42).

**Cohort descriptive statistics (Methods §3.2):**
- Benign (n=155): median diameter 7.74 mm (IQR 6.70-9.20, range 6.00-35.36 mm).
- Malignant (n=155): median diameter 19.36 mm (IQR 14.30-25.58, range 6.47-44.60 mm).
- 100% of nodules have ≥3 readers; 65% have all 4 readers.
- Median pairwise inter-reader Dice = 0.789 (mean 0.769, range 0.156-0.934) — within the published LIDC inter-reader range (0.75-0.80).

**Power justification:** At N=310 (155/155), minimum-detectable ΔAUC (DeLong, paired, ρ≈0.85, α=0.05, β=0.20) is ≈0.028 — comfortably below our pre-specified non-inferiority margin of 0.020 and adequate for the H2 primary test.

**Pre-specified sensitivity-analysis cohorts (decisions.log #011 / #014):**
- Imbalanced full yield (n=353, 198M/155B) — sensitivity to downsampling.
- Strict-10 mm subset (n≈129) — original protocol-fidelity check.
- Diameter strata (6-10 / 10-20 / >20 mm) — size-confound subgroup analysis.

**Backup dataset (decision gate at Week 1 end):** NSCLC-Radiomics (Aerts 2014, 422 patients, 1 segmentation per patient — used for synthetic-perturbation arm only, no inter-rater).

**Data Use Agreement:** TCIA standard DUA, executed in Week 1.

## 5. Perturbation conditions

*(Updated 2026-05-21 — see decisions.log entry #005.)*

For each of the ≥400 nodules:

**Natural inter-rater perturbations (R = up to 4 conditions per nodule):**
- M_R1, M_R2, M_R3, M_R4 — original reader masks.

**Synthetic perturbations applied to the median-reader consensus mask M_C (per-voxel majority vote across available reader masks):**

- **Erosion (3 levels):** structuring element radius 1, 2 voxels (3-voxel level capped — see below).
- **Dilation (2 levels):** structuring element radius 1, 2 voxels. 3-voxel dilation removed because on a 10-mm nodule it produces ~40 % volume inflation, far beyond reported inter-reader variability (Dice 0.7-0.85; mean surface distance 1-2 voxels on LIDC).
- **Translation (3 levels):** (Δx, Δy, Δz) ∈ {(1,0,0), (0,1,0), (1,1,0)} voxels.
- **Dice-calibrated tier:** for each nodule, a synthetic mask that matches the median pairwise reader Dice for that nodule, generated by adaptive isotropic morphological perturbation. This anchors synthetic noise to empirical reader noise and addresses the verification-pass concern that synthetic ≠ natural.

**Total perturbations per nodule:** up to 12 (4 reader + 7 synthetic + 1 Dice-calibrated).

All perturbations are applied in image-voxel space using SimpleITK BinaryErode, BinaryDilate, and ResampleImageFilter.

**Per-nodule volume-preservation guard (added 2026-05-24, decisions.log #012):** any erosion whose resulting mask retains less than 25 % of the consensus-mask voxel count is skipped for that specific nodule. Necessary corollary of the 6 mm diameter relaxation (decisions.log #011), because fixed 3-voxel erosion can fully obliterate small nodules.

**Actual yield across the 353-nodule pre-balanced cohort (decisions.log #015):** consensus / R1 / R2 / R3 retained for all nodules (100%); R4 for 230 (65%); E1 for 171 (48%); E2 for 45 (13%); E3 for 6 (2%); D1, D2, T1, T2, T3, DC for all 353 (100%, dilation/translation/DC cannot shrink the mask). Per-nodule perturbation-condition count K therefore varies between 7 and 12. ICC computation downstream (§7.1) handles unbalanced K natively via `pingouin.intraclass_corr`.

## 6. Feature extraction

### 6.1 Handcrafted radiomics (IBSI-aligned, primary comparator)

**Tool:** PyRadiomics v3.1.0 (pinned). *Updated 2026-05-21 after the actual Windows install:* PyPI tops out at the cp39 wheel; conda-forge has no Windows builds at all; the source build of 3.0.1 fails under PEP 517 isolated install. The env is therefore Python 3.9 + pyradiomics 3.1.0 (the last cp39 Windows wheel). See `decisions.log` entry #009.
**Image preprocessing:** resampled to 1×1×1 mm³ isotropic via BSpline interpolation (PyRadiomics default); intensity bin width = 25 HU; no normalisation (CT HU is calibrated).
**Feature classes:** first-order (18), shape (16), GLCM (24), GLRLM (16), GLSZM (16), NGTDM (5), GLDM (14).
**Filters:** original image only (supplementary adds wavelet 0.5×/2× σ).
**IBSI compliance:** all extracted feature names cross-referenced against IBSI 1.0 reference manual (Zwanenburg 2020).

**Two parallel radiomics arms** *(added 2026-05-21 after verification — see decisions.log entry #002):*

- **RAD-3D (primary):** PyRadiomics on full-volume mask. Yields ~107 features per ROI. Acts as the upper-bound radiomics reference.
- **RAD-2D (fairness arm):** PyRadiomics on the single central-axial slice through the nodule centroid using `shape2D` instead of `shape`. Yields ~88 features. Matched to FM input dimensionality so that any FM-vs-radiomics contrast cannot be confounded with the 2D/3D distinction.

The primary FM-vs-radiomics statistical comparisons (H1, H2) are run against **RAD-2D**. RAD-3D is reported alongside for context and is the secondary comparator. This addresses the verification-pass concern that central-axial-slice FM inference vs full-volume radiomics conflates paradigm with dimensionality.

### 6.2 Foundation-model embeddings (test paradigm)

**FM-1 — BiomedCLIP (Zhang 2024).** ViT-B/16 image encoder, pretrained on PMC-15M (15 M biomedical image-text pairs). Embedding dimension 512. CPU inference confirmed at ~2 sec/224×224 image. We extract from the central axial slice through the nodule centroid, applying a ROI-centred 224×224 crop (bounding box ±50 % padding).
**FM-2 — RadImageNet-ResNet50 (Mei 2022).** 2D ResNet50 pretrained on RadImageNet's 1.35 M radiology images across modalities. Embedding dimension 2 048. CPU inference ~1 sec/224×224 image. Same crop/centre slice protocol as FM-1.
**FM-3 (optional, supplementary) — MedSAM image-encoder (Ma 2024).** ViT-B image-encoder branch only. Embedding dimension 768 (averaged-pooled spatial tokens). CPU inference ~25 sec/1024×1024 image — used only on a 50-nodule sub-sample for supplementary cross-architecture sanity.

All three FMs use ImageNet-style normalisation per their original model cards; we will document any deviation in the manuscript Methods.

## 7. Statistical analysis plan

### 7.1 Per-feature ICC

*(Updated 2026-05-21 after verification — see decisions.log entry #003.)* We compute two ICC variants to satisfy reviewers who differ on whether perturbation conditions are fixed (ICC3) or random samples of plausible noise (ICC2):

- **ICC(2,1) — two-way random, single rater, absolute agreement** is the *primary* statistic. It treats both nodule (target) and perturbation condition (rater) as random samples, supporting generalisation beyond the specific 4 readers + 9 synthetic perturbations used here. Required when reviewers ask "would your stability ranking hold for a fifth reader?"
- **ICC(A,1) — variant of ICC2 with absolute agreement** for the synthetic-only sub-analysis.
- **ICC(3,1) — two-way mixed, single rater, consistency** is reported in supplementary for backward compatibility with the bulk of the radiomics literature (Pavic 2018, van Timmeren 2020).

Computed via `pingouin.intraclass_corr`. Per-feature 95% CIs use the F-distribution method built into pingouin.

Pre-specified ICC strata:
- ICC < 0.50: poor
- 0.50 ≤ ICC < 0.75: moderate
- 0.75 ≤ ICC < 0.90: good
- ICC ≥ 0.90: excellent

**Primary stability threshold:** ICC ≥ 0.75 (consistent with radiomics literature, e.g. Pavic 2018, van Timmeren 2020).

**Pre-specified sensitivity analyses:** ICC thresholds 0.50, 0.85, 0.90.

### 7.2 H1 test (proportion of stable features)

Two-sided two-proportion z-test, comparing the proportion of features with ICC ≥ 0.75 between PyRadiomics and each FM. Bonferroni-corrected α = 0.05 / 2 = 0.025 across the two FM comparisons.

### 7.3 H2 test (downstream AUC degradation, with nested CV to avoid double-dip)

*(Updated 2026-05-21 — see decisions.log entry #004.)* We use **nested 5-fold stratified cross-validation** to prevent ICC-selection from leaking outcome information into the validation fold:

- **Outer loop:** 5 stratified folds over the 400 nodules.
- **Inside each outer training fold:** ICC computed using the *training portion only*. Features with ICC ≥ τ (τ ∈ {0.50, 0.75, 0.85, 0.90}) are retained. An L2-regularised logistic regression is fit on the training portion. The model is evaluated on the held-out outer fold.

This eliminates the verification-pass concern that the full-set ICC + full-set linear-probe weights overlap and inflate the "stable-informative core" finding. Selection stability across folds (Jaccard of the selected feature sets) is reported as a supplementary table.

Report mean OOF AUC, Brier score, and ECE with stratified bootstrap CIs (1 000 reps) over pooled out-of-fold predictions. Pre-vs-post-filter ΔAUC is the primary effect size for H2; cross-paradigm ΔAUC tested via paired permutation on per-fold differences.

**Size-confound mitigation (added 2026-05-25, decisions.log #014 follow-up):** because the LIDC cohort has a structural size–malignancy correlation (median benign diameter 7.74 mm vs malignant 19.36 mm), the downstream classifier could in principle learn size as a proxy for malignancy and inflate AUC. We mitigate this in three ways: (i) report a diameter-stratified ΔAUC (6-10 / 10-20 / >20 mm strata) alongside the pooled estimate; (ii) report a size-residualised analysis in which a univariate-on-diameter logistic regression is fit and the residual AUC contributed by each feature paradigm reported; (iii) explicitly discuss the size-confound in Discussion §4.4. The paired within-lesion ICC analysis for H1 is unaffected because both feature paradigms see the same nodules in the same order.

### 7.4 H3 (Cosma 2025 generalisation)

Non-inferiority of post-filter AUC versus pre-filter AUC: pre-specified non-inferiority margin = 0.020 ΔAUC (i.e., we declare H3 supported if the upper 95 % CI of (pre-filter AUC − post-filter AUC) is below +0.020).

### 7.5 H4 (stable-informative core)

For each FM, sort dimensions by ICC. Plot the cumulative |linear-probe weight| as a function of cumulative ICC rank; report the proportion of total |weight| concentrated in the top-decile ICC dimensions.

### 7.6 Calibration

Report Brier score and Spiegelhalter z for each model. Plot calibration curves (10 bins, smoothed loess) for all four pre/post-filter classifier configurations.

### 7.7 Reporting

PRISMA 2020 does not apply (not a systematic review). We will follow the TRIPOD+AI 2024 reporting checklist for the prediction-modelling components, the IBSI 1.0 checklist for radiomics, and a CLAIM-compliant Methods section for the FM components. RQS will be self-scored and reported in the supplementary materials.

## 8. Reproducibility safeguards

- Random seeds fixed (`numpy.random.seed(42)`, `torch.manual_seed(42)`).
- Library versions pinned in `environment.yml`.
- All code and the 200-nodule case-ID list (with derived perturbation masks) released on GitHub at submission.
- Intra-rater check: a randomly sampled 10 % of nodules (n=20) re-extracted from raw DICOM through the full pipeline 7 days after the primary extraction; Cohen's κ for ICC stratum agreement will be reported.

## 9. Ethical and authorship statements

- **Ethics:** Secondary analysis of fully de-identified, publicly released TCIA data; IRB exempt under standard TCIA DUA.
- **Funding:** None.
- **Conflict of interest:** None to declare.
- **Author contributions:** Single-author manuscript; conceptualisation, methodology, software, analysis, writing all by I. [surname].
- **Use of AI in manuscript preparation:** Anthropic Claude (Sonnet/Opus, 2026) used for literature triage and protocol drafting assistance; all final analytical decisions, code, and manuscript wording reviewed and accepted by the author. Disclosed per Medical Physics 2026 AI-use policy.

## 10. Deviations from protocol

Any protocol deviation will be recorded in `decisions.log` (timestamped, justified) and reported transparently in the manuscript Methods.

---

*End of protocol v1.0. Locks Week 1 Friday (2026-05-29) after first PyRadiomics dry run.*
