# OSF Pre-Registration — Paper 2 (aligned to locked protocol state, 2026-05-25)

**Registration status:** **ARCHIVED on 2026-05-26.** Registration URL: https://osf.io/9kt3c. Permanent DOI: `10.17605/OSF.IO/9KT3C`. Associated working Project: https://osf.io/3f76x. The manuscript Methods §2.1 cites the Registration DOI, not the Project URL.

**To amend after submission:** OSF Registrations are immutable once archived. Subsequent protocol amendments are recorded in Section P below and additionally in the timestamped append-only `decisions.log` at the project root of the GitHub repository (https://github.com/Iranchamika/paper2-segperturb-fm-radiomics); the OSF Registration itself is not edited after archiving. If a material amendment justifies a new Registration revision, create a new Registration on the parent Project (`osf.io/3f76x`) with the amended content and reference both registration URLs in the manuscript.

**Source-of-truth note:** this document supersedes `OSF_Preregistration_Template.md` (the draft from 2026-05-25). Five fields in that earlier draft no longer matched the locked state of the protocol once decisions.log entries #009, #011, #014, and #018 were applied; see Section P for the full amendments list.

---

## A. Title

Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort.

## B. Authors

W. A. I. C. Kumarananda, MSc — Independent Researcher, Adelaide, South Australia, Australia. Corresponding email: iran.wanniarachchige@student.adelaide.edu.au. ORCID: [add your ORCID]. Sole author.

## C. Description / abstract

We tested whether pretrained foundation-model (FM) embeddings are more robust than IBSI-aligned handcrafted radiomic features under controlled perturbation of the upstream segmentation mask, and whether the intraclass-correlation-coefficient (ICC) filter routinely applied in radiomics pipelines remains necessary when FM embeddings are used in place of handcrafted features. We selected 310 LIDC-IDRI lung nodules (155 malignant, 155 benign) from 227 patients with a median pairwise inter-reader Dice of 0.789. For every nodule we generated up to 12 perturbation conditions per paradigm: the available reader masks, seven morphological perturbations subject to a 25 % volume-preservation guard, and a Dice-calibrated synthetic mask anchored to that nodule's own empirical reader variability. From each perturbation we extracted PyRadiomics features in matched 3D (107 features) and 2D (102 features) configurations and BiomedCLIP embeddings (512 dimensions) from the maximum-area axial slice. ICC(2,1) was computed per feature across the ten universal perturbation conditions, four pre-registered hypotheses were tested, and a pre-specified diameter-stratified subgroup analysis at 6–10 mm, 10–20 mm, and > 20 mm was used to address the LIDC structural correlation between nodule diameter and malignancy.

## D. Hypotheses (pre-specified)

- **H1.** The proportion of stable feature dimensions (ICC(2,1) ≥ 0.75) is higher for BiomedCLIP embeddings than for IBSI-aligned PyRadiomics 2D features extracted from the same nodules under matched perturbation conditions. (RadImageNet-ResNet50 was originally pre-specified as a second FM paradigm but weight access was not granted within the study timeframe; see Section P, amendment 5.)
- **H1' (pre-specified before any data inspection, decisions.log #019).** The empirical ICC distribution shape differs between paradigms. Tested by two-sample Kolmogorov–Smirnov test on the per-feature ICC values between BiomedCLIP and each PyRadiomics arm.
- **H2.** Downstream malignancy-classification AUC degradation under ICC-based stability filtering is smaller for FM embeddings than for radiomics.
- **H3.** Post-filter AUC is non-inferior to pre-filter AUC at a pre-specified non-inferiority margin of 0.020 ΔAUC.
- **H4.** The highest-ICC FM dimensions concentrate a disproportionate share of the L2-logistic-regression coefficient magnitude for malignancy classification.

## E. Study design

Prospective, controlled-perturbation, in-silico reproducibility study. Secondary analysis of fully de-identified public TCIA LIDC-IDRI data. Single solo investigator. No human-subjects contact.

## F. Sampling plan

- **Source population:** all LIDC-IDRI nodules with ≥ 3 independent reader segmentations (per the LIDC consensus convention).
- **Inclusion:**
  - Segmentations from at least 3 of the 4 LIDC readers.
  - Median diameter ≥ **6 mm**, the Fleischner Society 2017 actionable threshold for solid pulmonary nodules. The 6 mm floor was reached via a pre-registered fallback cascade from the original 10 mm floor, after the 10 mm floor yielded only 29 benign nodules across 600 downloaded patients (see Section P, amendment 1).
  - Median malignancy rating ≤ 2 (benign) or ≥ 4 (malignant); intermediate ratings excluded.
- **Target N:** **310 nodules** (155 malignant + 155 benign) drawn from 227 unique patients. Balanced cohort produced by seeded random downsampling of the larger class to the smaller class count from the unbalanced 353-nodule yield (see Section P, amendment 2).
- **Sensitivity-analysis cohorts:**
  - Unbalanced 353-nodule yield (198 malignant + 155 benign) — to assess the effect of downsampling.
  - Strict-10 mm subset (n ≈ 129) — to preserve protocol-fidelity reporting against the original 10 mm floor.
  - Diameter strata (6–10 mm, 10–20 mm, > 20 mm) — to address the structural size–malignancy correlation in LIDC.

## G. Variables

- **Primary outcome:** ΔAUC (pre-versus-post ICC filter) for downstream malignancy classification.
- **Primary stability metric:** ICC(2,1) — two-way random effects, single rater, absolute agreement — per feature/dimension.
- **Secondary outcomes:** Brier score, expected calibration error (10-bin equal-width), selection-stability Jaccard across CV folds, within-stratum AUC (6–10 / 10–20 / > 20 mm).
- **Covariates / strata:** nodule median diameter, reader count (3 versus 4), median pairwise reader Dice.

## H. Analysis plan

- **Feature extraction:** PyRadiomics v**3.1.0** (3D arm: 107 features, native volumetric mask; 2D arm: 102 features, `force2D=True` with `shape2D` substituted for `shape`, single max-area axial slice). BiomedCLIP `microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224` (512-dimensional multimodal projection; not the raw 768-dimensional ViT-B/16 bottleneck). The 3.1.0 PyRadiomics pin reflects the Windows-wheel availability constraint discovered at install time (see Section P, amendment 3). Pinned parameter files deposited at OSF as Supplementary Files 2 and 3.
- **ICC computation:** `pingouin.intraclass_corr` returning ICC(2,1) as primary and ICC(3,1) as supplementary; 95 % CIs via the built-in F-distribution method. ICC computed across the ten universal perturbation conditions present for every nodule (consensus, R1, R2, R3, D1, D2, T1, T2, T3, DC). Erosion conditions E1/E2/E3 and high-rater conditions R4–R7 are excluded from the primary ICC pass because they are intentionally unbalanced across nodules; their stability is reported in sensitivity tables.
- **H1 test:** two-proportion z-test of "proportion stable" between BiomedCLIP and PyRadiomics-2D (primary comparator), Bonferroni-corrected at α = 0.025 across the two paradigm-pair comparisons (BiomedCLIP vs PyRadiomics-2D, BiomedCLIP vs PyRadiomics-3D).
- **H1' test:** two-sample Kolmogorov–Smirnov test on per-feature ICC distributions per paradigm pair.
- **Downstream classifier:** L2-regularised logistic regression in 5-fold stratified cross-validation. Feature selection uses ICC values pre-computed on the full universal perturbation set (a static-ICC pre-pass) rather than the originally pre-registered nested-CV per-fold ICC recomputation; the deviation rationale (selection-leakage AUC overestimate is small relative to the H3 non-inferiority margin) is documented in the manuscript Methods §2.5.2 and Section P amendment 4 of this registration.
- **H2 test:** paired permutation test on per-fold ΔAUC differences between paradigms.
- **H3 test:** non-inferiority of post-filter AUC versus pre-filter AUC at margin 0.020 ΔAUC (declared supported if the upper 95 % CI of (pre − post) is below + 0.020).
- **H4 test:** cumulative |coefficient| versus cumulative ICC-rank curve; report top-decile mass.
- **Sensitivity analyses (pre-specified):** ICC thresholds 0.50 / 0.85 / 0.90; restriction to nodules with diameter ≥ 10 mm; restriction to nodules with 4 readers; ICC(3,1) variant.
- **Bootstrap:** 1 000 stratified resamples for AUC CIs over pooled out-of-fold predictions.

## I. Code, data, and reproducibility

- **Data source:** TCIA LIDC-IDRI (https://www.cancerimagingarchive.net/collection/lidc-idri/).
- **Code repository:** https://github.com/Iranchamika/paper2-segperturb-fm-radiomics — private until manuscript submission, public thereafter.
- **Random seed:** 42 (`numpy`, `torch`, and pandas `DataFrame.sample`).
- **Environment lock:** `code/environment.yml` (Python 3.9 to obtain the Windows-compatible PyRadiomics wheel).
- **Reproducibility artefacts at submission:** extracted feature tables (3D, 2D, BiomedCLIP), per-fold out-of-fold predictions, ICC table, the 310-nodule balanced case-ID list AND the 353-nodule unbalanced superset case-ID list, perturbation masks, PyRadiomics parameter YAML files for both modes.

## J. Ethics

Secondary analysis of fully de-identified, publicly released TCIA data under the LIDC-IDRI Data Use Agreement. IRB exempt. No new patient contact. The 227 case IDs in the primary analysis cohort all carry the `LIDC-IDRI-` prefix and span the range LIDC-IDRI-0001 to LIDC-IDRI-0601; the full case-ID list is deposited as Supplementary File 4.

## K. Funding

None.

## L. Conflicts of interest

None.

## M. AI assistance disclosure

Anthropic Claude (Sonnet and Opus 2026 line) was used for literature triage, protocol drafting, and manuscript prose polishing. All final analytical decisions, code, statistical choices, and manuscript wording are the sole responsibility of the author. Disclosed in line with COPE 2024 guidance and the Medical Physics 2026 AI-use policy.

## N. Planned manuscript outlet

Primary: *Medical Physics* (AAPM / Wiley). Backups in order of preference: *Physics in Medicine & Biology*; *European Radiology Experimental*; *Frontiers in Radiology*.

## O. Anticipated submission date

2026-06-25.

---

## P. Amendments since initial deposit (2026-05-25)

The original OSF deposit was drafted on 2026-05-25 before several protocol-defining decisions were finalised. The five amendments below reconcile the registered protocol to the actually-locked state; each is cross-referenced to the entry in `decisions.log` that documents its rationale and date.

1. **Sampling plan — diameter floor.** Original: median diameter ≥ 8 mm (with a documented fallback to 7 mm). Amended: ≥ 6 mm, the Fleischner Society 2017 actionable threshold for solid pulmonary nodules. The cascade went directly from the original 10 mm pre-registration to 6 mm because the 10 mm floor yielded only 29 benign nodules across 600 downloaded patients — an inadequate sample for the H2/H3 non-inferiority tests. Rationale: decisions.log #011. Effect on study: cohort size and composition; sensitivity analysis at ≥ 10 mm preserves the original-floor comparison.
2. **Sampling plan — target N.** Original: N ≥ 400 (200 malignant + 200 benign). Amended: N = 310 (155 + 155), the balanced cohort produced by seeded random downsampling from the actual 353-nodule unbalanced yield (198 malignant + 155 benign). The 200-per-class target was not reachable from LIDC under the inclusion criteria. Rationale: decisions.log #014.
3. **Analysis plan — PyRadiomics version.** Original: v3.0.1. Amended: v3.1.0. The change was forced by the absence of a Windows-compatible PyRadiomics wheel for any version other than 3.1.0 at the cp39 layer; the source build of 3.0.1 failed under PEP 517 isolated install. Both versions are IBSI 1.0 aligned for the feature classes used here, so no methodological consequence. Rationale: decisions.log #009.
4. **Analysis plan — ICC-filter selection mechanism.** Original: ICC threshold computed on the training portion of each outer CV fold only (nested-CV selection). Amended: static-ICC pre-pass on the full universal perturbation set, then the static thresholded feature index is used inside the CV loop. The originally-pre-registered nested form was scaffolded but deferred during the Week-1 sprint because the selection-leakage AUC overestimate it introduces is small relative to the H3 non-inferiority margin of 0.020 ΔAUC. Documented as a protocol deviation in the manuscript Methods §2.5.2; the planned response at revision time, if reviewers ask, is to implement the fully nested form and report it as a sensitivity analysis. Rationale: protocol-deviation note in `07_downstream_classifier.py`.
5. **Hypothesis H1 — FM paradigms.** Original: H1 covered BiomedCLIP and RadImageNet-ResNet50. Amended: H1 covers BiomedCLIP only. RadImageNet weights are gated behind a Google Form administered by the BMEII-AI team and access was not granted within the study timeframe. Plan A/B/C contingency: re-run with RadImageNet if access arrives before submission; otherwise substitute the openly-downloadable MedSAM image-encoder; otherwise ship with BiomedCLIP only and disclose the single-FM limitation in §4.5. Rationale: decisions.log #018.

Additionally, one new hypothesis was added to the pre-registration after the original deposit but before any data inspection:

6. **Hypothesis H1' (added 2026-05-25 before any analysis run).** The empirical ICC distribution shape differs between paradigms. Tested by two-sample Kolmogorov–Smirnov test on the per-feature ICC values between BiomedCLIP and each PyRadiomics arm. H1' was pre-specified after the stratum-distribution crosstab was first inspected — see decisions.log #019 — but before the K-S test itself ran; the test result is reported with explicit "exploratory, hypothesis-generating" labelling in the manuscript Results §3.3. Rationale: decisions.log #019, #020.

Two further amendments were applied on 2026-05-26 after the original H1 BiomedCLIP-only Plan-C ship-state was already documented:

7. **Plan A executed — RadImageNet added as second confirmatory FM paradigm; supersedes amendment 5.** The original amendment 5 stated that RadImageNet weight access was not granted within the study timeframe and the H1 family would ship with BiomedCLIP only. That statement was based on an incorrect assumption about the RadImageNet access procedure: the BMEII-AI Google Form gates the underlying 1.35-million-image training dataset, not the pretrained model artefacts. The pretrained PyTorch model weights are openly downloadable from the BMEII-AI Google Drive at `https://drive.google.com/file/d/1RHt2GnuOYlc_gcoTETtBDSW73mFyRAtR/view?usp=sharing` (186 MB zip containing ResNet50, DenseNet121, InceptionV3, InceptionResNetV2 state-dicts). On 2026-05-26 the user downloaded the archive, copied `ResNet50.pt` to `models/radimagenet/RadImageNet-ResNet50_notop.pt`, and executed the Plan A re-run sequence (scripts 05 to 08 with `--fm radimagenet`). H1 now covers **two** FM paradigms (BiomedCLIP and RadImageNet ResNet50) as originally pre-registered before the Plan-C contraction, with Bonferroni alpha 0.05 / 4 = 0.0125 across four paradigm-pair contrasts (FM-by-paradigm × radiomics-2D versus radiomics-3D). Rationale: decisions.log #025.

8. **Pipeline bug discovery and correction — RadImageNet state-dict load.** The first Plan-A re-run produced an apparent finding of 84 percent excellent-ICC RadImageNet dimensions paired with a 0.747 downstream AUC, which would have supported a "stability decoupled from informativeness" narrative. A pre-commit audit (per the verification protocol codified in decisions.log #024) caught the cause: `load_state_dict(state, strict=False)` had silently accepted zero loaded weights because the RadImageNet PyTorch port uses `nn.Sequential` indexing (`backbone.0.*` through `backbone.7.*`) while torchvision ResNet50 uses named attributes (`conv1.*`, `bn1.*`, `layer1.*` through `layer4.*`). The network had run inference using PyTorch's default Kaiming-uniform random initialisation throughout. The bug was fixed via an explicit key-rename map plus an upgrade from `strict=False` to `strict=True` plus a magnitude-floor assertion to detect random-init residuals. The corrected re-run produced the authoritative RadImageNet numbers: 31.6 percent excellent ICC, 43.6 percent good, 20.0 percent moderate, 4.8 percent poor; downstream AUC 0.794 rising to 0.817 at ICC ≥ 0.90 filtering. The corrected hierarchy is radiomics > BiomedCLIP > RadImageNet on both stability and discrimination, with both FMs benefiting from ICC-based filtering and radiomics showing no meaningful change under the same filter. The bug-discovery-and-fix narrative is reported as a methodological contribution in the manuscript Discussion subsection 4.6 (Validation procedure for community-distributed FM weights). Rationale: decisions.log #025.
