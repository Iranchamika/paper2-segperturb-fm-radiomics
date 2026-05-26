# Manuscript Skeleton — Paper 2

**Target journal:** *Medical Physics* (AAPM, Wiley)
**Article type:** Research Article (10-page limit)
**Working title:** Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort
**Short title (running head):** FM vs radiomics under segmentation perturbation
**Author:** Iran [surname], MSc (Medical Physics), Independent Researcher, Adelaide, Australia
**Corresponding email:** a1846500@adelaide.edu.au
**Word budget:** ≤6 500 words main body; 4 figures; 2 tables; unlimited supplementary

---

## Abstract (structured, 250 words)

**Purpose.** To compare the propagation of segmentation perturbation through handcrafted IBSI-aligned radiomic features versus pretrained foundation-model (FM) embeddings on the publicly available LIDC-IDRI lung-CT cohort, and to quantify the downstream impact of intraclass-correlation-coefficient (ICC)-based stability filtering on malignancy classification.

**Methods.** We selected 200 LIDC-IDRI lung nodules (100 benign, 100 malignant; ≥3 reader segmentations each; ≥10 mm median diameter). For every nodule we applied four natural inter-reader perturbations and nine controlled synthetic perturbations (erosion / dilation / translation, radius 1-3 voxels). PyRadiomics (v3.1.0, IBSI-aligned, 107 features), BiomedCLIP (512-dim embedding) and RadImageNet ResNet50 (2048-dim embedding) features were extracted from each perturbation condition. ICC(3,1) was computed per feature/dimension. Downstream malignancy classification used L2-logistic regression with 5-fold stratified CV, pre-vs-post ICC filtering at thresholds 0.50, 0.75, 0.85, 0.90.

**Results.** [PLACEHOLDER pending Week 4 analysis. Expected: FM embeddings will show a larger proportion of stable dimensions (ICC ≥ 0.75) than radiomics features (~XX % vs ~YY %); post-filter AUC will remain within ±0.02 of pre-filter AUC for both paradigms, generalising the Cosma 2025 finding to lung CT and FM embeddings.]

**Conclusions.** [PLACEHOLDER]

**Keywords:** radiomics; foundation models; segmentation variability; reproducibility; lung CT; LIDC-IDRI; intraclass correlation coefficient.

---

## 1. Introduction (≈800 wds)

- Motivation: quantitative image-feature extraction now bifurcates between IBSI-aligned handcrafted radiomics and dense pretrained FM embeddings.
- Known issue with radiomics: high inter-rater segmentation sensitivity; routine practice is to ICC-filter at ≥0.75 prior to modelling.
- Open question: how does segmentation-perturbation propagate through FM embeddings vs radiomics? Does the FM pretraining objective implicitly confer invariance to segmentation perturbation that handcrafted features lack?
- Existing precedent reviewed:
  - **Pai 2024 (peer-reviewed, *Nature Machine Intelligence*)** — introduced FMCIB; reported ICC = 0.984 for FMCIB on RIDER test-retest and significantly higher stability than Supervised CNN under seed-point jitter (σ²=16 vx). Did **not** perturb segmentation mask, did **not** compare against IBSI radiomics, used only 3D FMs.
  - Pai 2025 *TumorImagingBench* (Research Square **preprint**, not peer-reviewed) — extends to 10 3D FMs using cosine similarity; cited only as a preprint contemporaneous with this work.
  - Cosma 2025 (SPIE J Med Imag, arxiv 2504.01692) — studied segmentation-variability propagation in **breast MRI radiomics only**, found ICC-filtering may exclude predictive features.
  - No peer-reviewed work to date pairs LIDC-IDRI's 4-reader natural variability with FM embedding per-dimension ICC analysis under controlled synthetic perturbations with a head-to-head PyRadiomics comparator.
- Hypotheses (H1-H4) carried verbatim from `01_Protocol.md` §2.
- Contribution statement (4 bullets): (i) first head-to-head segmentation-stability comparison of FM embeddings vs radiomics on lung CT; (ii) joint reader-variability + synthetic-perturbation design at controlled magnitudes; (iii) per-dimension ICC analysis on dense embeddings (not previously reported); (iv) downstream malignancy classification with rigorous pre-vs-post-filter AUC, Brier, and ECE reporting.

## 2. Methods (≈1500 wds)

### 2.1 Study design and ethical declaration
Prospective, in-silico, controlled-perturbation reproducibility study. Secondary analysis of fully de-identified TCIA LIDC-IDRI data. IRB exempt under standard TCIA Data Use Agreement. Pre-specified analysis protocol deposited at OSF on 2026-05-26 (link in supplementary). Single solo investigator; intra-rater reliability documented on 10 % re-extraction.

### 2.2 Dataset and inclusion criteria
[Verbatim from protocol §4.]

### 2.3 Perturbation conditions
[Verbatim from protocol §5; include Figure 1 here showing example perturbed masks.]

### 2.4 Feature extraction
**Radiomics:** PyRadiomics v3.1.0, IBSI-aligned, parameters as Table S1.
**FM embeddings:** BiomedCLIP `microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224` (Zhang 2024); RadImageNet-ResNet50 (Mei 2022). Central axial slice through nodule centroid, bounding-box crop with 50 % padding, ImageNet-style normalisation.

### 2.5 Statistical analysis
[Protocol §7 condensed.]

### 2.6 Reproducibility
Code, parameter files, extracted-features tables, and per-fold predictions released on GitHub at submission. Random seeds fixed. Environment pinned in `environment.yml`. Intra-rater κ reported in §3.5.

## 3. Results (≈1200 wds)

### 3.1 Cohort characteristics
[Table 1: cohort age / sex / nodule size / reader counts / label distribution.]

### 3.2 Feature stability under perturbation (H1)
[Figure 2 (a) stacked-bar ICC stratum per paradigm; (b) ECDF of ICC per paradigm. Insert proportion stable + two-proportion z-test result.]

### 3.3 Downstream malignancy classification (H2, H3)
[Figure 3 — forest of pre-vs-post-filter AUC with Brier/ECE annotation. Paired permutation test ΔAUC between paradigms.]

### 3.4 Stable-informative-core hypothesis (H4)
[Figure 4 — cumulative |linear-probe weight| vs ICC-rank for each FM and radiomics.]

### 3.5 Sensitivity analyses & intra-rater reliability
[Subgroup by nodule size; supplementary analysis at ICC thresholds 0.50/0.85/0.90; intra-rater κ on 10 % re-extracted subset.]

## 4. Discussion (≈1500 wds)

### 4.1 Summary of findings
[3-4 sentence headline.]

### 4.2 Comparison to existing literature
- **Pai 2024 (peer-reviewed):** our per-dimension ICC sharpens their single-output ICC = 0.984 finding by revealing whether the stability is concentrated in a small "stable-informative core" or spread evenly across embedding dimensions. Our segmentation-mask perturbation arm extends their seed-point-jitter result to the dominant real-world noise source for handcrafted radiomics, demonstrating that FM stability advantage [does / does not — fill in after analysis] persist when the mask itself moves rather than the seed point.
- **Pai 2025 (preprint):** noted as contemporaneous preprint extending Pai 2024 to 10 FMs via cosine similarity; not yet peer-reviewed.
- **Cosma 2025:** did our lung-CT result confirm the "ICC-filtering may exclude predictive features" finding? If yes, suggests it's a property of modern regularised classifiers across modalities, not a breast-MRI quirk.
- **Pavic 2018 / van Timmeren 2020:** the radiomics ICC-filter literature is internally consistent with our radiomics ICC distribution but our finding that filtering does not improve downstream AUC challenges the necessity of filtering when modern regularised classifiers are used.

### 4.3 Mechanistic interpretation
- Why might FM embeddings have higher per-dimension stability? Pretraining at scale exposes the encoder to a wide range of crop and image transformations; the learned representations become approximately invariant to small spatial perturbations of input content.
- Why would post-filter AUC be similar to pre-filter AUC? Regularised regression already implicitly down-weights noisy dimensions; explicit ICC filtering is therefore redundant in the presence of L2 / Elastic Net penalisation.

### 4.4 Implications for practice
- For new FM-based radiomic pipelines: routine ICC-filtering at 0.75 may be unnecessary if (a) a regularised linear-or-tree classifier is used, and (b) a calibration analysis is reported on a held-out external cohort.
- For radiomics: the same finding holds; the field's reflexive ICC-filtering may discard information without improving downstream performance.
- IBSI compliance and segmentation-blinding declarations remain non-negotiable regardless of paradigm.

### 4.5 Limitations
- Single dataset (LIDC-IDRI), single anatomy (lung), single modality (CT). External validation deferred to Paper 3 in the same series.
- Central-axial-slice 2D protocol for FM embeddings discards volumetric context; 3D FMs (CT-FM, Merlin) deferred to future work due to CPU-only constraint.
- Synthetic erosion/dilation/translation does not capture all clinically relevant segmentation variability modes (e.g., regional under-/over-contouring of speculations, missed multifocal lesions).
- Reviewer / single-investigator design; intra-rater κ documented but no independent inter-rater pass.
- ICC(3,1) assumes condition fixed and target random; alternative ICC(2,1) (both random) would widen CIs slightly.

### 4.6 Future work
- 3D FM extension on GPU-enabled compute (CT-FM, Merlin, CT-CLIP).
- External validation on NSCLC-Radiomics (Aerts 2014) and the planned Paper 3 multi-institutional cohort.
- Extension to non-lung anatomies (pancreas, brain) where segmentation variability is reportedly higher.

### 4.7 Conclusions
- Pre-specified, two-sentence "conclusion-line" appropriate for citation extraction.

## 5. Acknowledgements
The author acknowledges the TCIA / LIDC-IDRI consortium for public release of the imaging cohort, the BiomedCLIP and RadImageNet teams for open release of pretrained weights, and the open-source SimpleITK, PyRadiomics, scikit-learn, and pingouin maintainer communities. AI-assisted manuscript preparation: Anthropic Claude (Sonnet/Opus 2026 line) was used for literature triage, protocol drafting and grammar polishing; all final analytical decisions, code, and manuscript wording are the author's responsibility.

## 6. Conflict of interest
None to declare.

## 7. Data availability
Code, parameter files, extracted feature tables, and per-fold out-of-fold predictions are available at https://github.com/Iranchamika/paper2-segperturb-fm-radiomics. The underlying imaging data are publicly available from TCIA under the LIDC-IDRI Collection (https://www.cancerimagingarchive.net/collection/lidc-idri/).

## 8. References (Vancouver, AAPM format)
Numbered list rendered from `references/refs.bib`. Anticipated ~30 references.

---

## Tables
- **Table 1.** Cohort characteristics (n=200 nodules) — age, sex, nodule diameter (median, IQR), reader count (3 vs 4), label distribution.
- **Table 2.** Feature-level summary: total features, % stable at ICC≥0.75, downstream AUC pre/post-filter (with 95 % CI), Brier, ECE.

## Figures (1 200 dpi PNG + EPS)
- **Fig 1.** Perturbation examples (3×3 grid: original / eroded / dilated for 3 nodules).
- **Fig 2.** ICC distributions per paradigm: (a) stacked-bar stratum, (b) ECDF.
- **Fig 3.** Forest plot of pre-vs-post-filter AUC with bootstrap 95 % CI, annotated Brier and ECE.
- **Fig 4.** Stable-informative-core: cumulative |linear-probe weight| vs ICC-rank.

## Supplementary
- **S1.** Full PyRadiomics parameter file (yaml).
- **S2.** Per-feature ICC table (csv).
- **S3.** Per-fold out-of-fold predictions (csv).
- **S4.** Self-scored RQS and CLAIM checklists.
- **S5.** Sensitivity analyses at ICC thresholds 0.50, 0.85, 0.90.
- **S6.** Intra-rater reliability κ on 10 % re-extracted subset.
- **S7.** OSF pre-registration deposit link.
