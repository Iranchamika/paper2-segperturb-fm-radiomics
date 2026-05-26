# OSF Pre-Registration Template — Paper 2

**To submit:** create an OSF account (https://osf.io), start a new project, then add a registration using the **OSF Standard Pre-Data Collection Registration** template. Paste each section below into the matching OSF form field. **Deposit before any feature extraction begins (2026-05-26).** Once registered, OSF assigns a permanent DOI that you cite in the manuscript Methods §3.1.

---

## A. Title

Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort.

## B. Authors

Iran [surname], MSc — Independent Researcher, Adelaide, South Australia. Corresponding email: a1846500@adelaide.edu.au. ORCID: [add your ORCID]. Sole author.

## C. Description / abstract (≤500 words)

[Paste the abstract from `manuscript/03_Manuscript_Skeleton.md` §Abstract.]

## D. Hypotheses (pre-specified)

- **H1.** The proportion of stable feature dimensions (ICC(2,1) ≥ 0.75) is higher for BiomedCLIP and RadImageNet-ResNet50 embeddings than for IBSI-aligned PyRadiomics 2D features extracted from the same nodules under matched perturbation conditions.
- **H2.** Downstream malignancy-classification AUC degradation under ICC-based stability filtering is smaller for FM embeddings than for radiomics.
- **H3.** Post-filter AUC is non-inferior to pre-filter AUC at a pre-specified non-inferiority margin of 0.020.
- **H4.** The highest-ICC FM dimensions concentrate a disproportionate share of the L2-logistic-regression coefficient magnitude for malignancy classification.

## E. Study design

Prospective, controlled-perturbation, in-silico reproducibility study. Secondary analysis of fully de-identified public TCIA LIDC-IDRI data. Single solo investigator. No human-subjects contact.

## F. Sampling plan

- **Source population:** all LIDC-IDRI nodules with ≥3 independent reader segmentations.
- **Inclusion:** median diameter ≥8 mm; median malignancy rating ≤2 (benign) or ≥4 (malignant).
- **Target N:** ≥400 nodules (target 200 malignant + 200 benign). Sensitivity analysis at ≥10 mm.
- **Stopping rule:** N=400 with class balance ±10%. If LIDC cannot supply 200 nodules per class under inclusion, loosen median-diameter floor to 7 mm (recorded in `decisions.log`).

## G. Variables

- **Primary outcome:** ΔAUC (pre-vs-post ICC filter) for downstream malignancy classification.
- **Primary stability metric:** ICC(2,1) two-way random, absolute agreement, per feature/dimension.
- **Secondary outcomes:** Brier score, expected calibration error (10-bin), selection-stability Jaccard across CV folds.
- **Covariates / strata:** nodule diameter, reader count (3 vs 4), median pairwise reader Dice.

## H. Analysis plan

- **Feature extraction:** PyRadiomics v3.0.1 (3D and 2D arms), BiomedCLIP, RadImageNet-ResNet50, MedSAM image-encoder on a 50-nodule subset (supplementary). Pinned parameter files deposited at OSF as Supplementary Files.
- **ICC computation:** `pingouin.intraclass_corr` returning ICC(2,1) as primary and ICC(3,1) as supplementary; 95% CIs via the built-in F-distribution method.
- **H1 test:** two-proportion z-test of "proportion stable" between paradigms, Bonferroni-corrected α = 0.025 across two FM comparisons against RAD-2D primary.
- **Downstream classifier:** L2-regularised logistic regression in nested 5-fold stratified cross-validation. Feature selection by ICC threshold computed on the training portion of each outer fold only.
- **H2 test:** paired permutation test on per-fold ΔAUC differences between paradigms.
- **H3 test:** non-inferiority of post-filter AUC versus pre-filter AUC at margin 0.020 (declared supported if the upper 95% CI of (pre−post) is below +0.020).
- **H4 test:** cumulative |coefficient| vs cumulative ICC-rank curve; report top-decile mass.
- **Sensitivity analyses (pre-specified):** ICC thresholds 0.50/0.85/0.90; restriction to nodules with diameter ≥10 mm; restriction to nodules with 4 readers; ICC(3,1) variant.
- **Bootstrap:** 1 000 stratified resamples for AUC CIs over pooled out-of-fold predictions.

## I. Code, data, and reproducibility

- **Data source:** TCIA LIDC-IDRI (https://www.cancerimagingarchive.net/collection/lidc-idri/).
- **Code repository:** https://github.com/Iranchamika/paper2-segperturb-fm-radiomics — private until manuscript submission, public thereafter.
- **Random seed:** 42 (`numpy`, `torch`).
- **Environment lock:** `code/environment.yml`.
- **Reproducibility artefacts at submission:** extracted feature tables, per-fold predictions, ICC table, the 400-nodule case-ID list, perturbation masks, PyRadiomics parameter files.

## J. Ethics

Secondary analysis of fully de-identified, publicly released TCIA data under the LIDC-IDRI Data Use Agreement. IRB exempt. No new patient contact.

## K. Funding

None.

## L. Conflicts of interest

None.

## M. AI assistance disclosure

Anthropic Claude (Sonnet/Opus 2026 line) was used for literature triage, protocol drafting, and manuscript prose polishing. All final analytical decisions, code, statistical choices, and manuscript wording are the sole responsibility of the author. Disclosed per COPE 2024 guidance and Medical Physics 2026 AI-use policy.

## N. Planned manuscript outlet

Primary: *Medical Physics* (AAPM, Wiley). Backups (in order): *Physics in Medicine & Biology*; *European Radiology Experimental*; *Frontiers in Radiology*.

## O. Anticipated submission date

2026-06-25 (5-week sprint from this pre-registration deposit).
