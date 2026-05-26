# Pai 2025 — TumorImagingBench: Structured digest for differentiation framing

**Citation.** Pai et al. (2025). *Foundation model embeddings for quantitative tumor imaging biomarkers.* **Research Square preprint v1 — NOT peer-reviewed as of May 2026.** PubMed Central indexes it via Research Square's deposit agreement, which does not grant peer-review status. PMC: [PMC12154149](https://pmc.ncbi.nlm.nih.gov/articles/PMC12154149/) · PMID: 40502795 · [DOI: 10.21203/rs.3.rs-6630446/v1](https://doi.org/10.21203/rs.3.rs-6630446/v1). *According to PubMed.*

> **Status correction (2026-05-21):** earlier draft mistakenly framed this as the primary peer-reviewed precedent. The proper peer-reviewed reference is **Pai et al. 2024, *Nature Machine Intelligence*** ([DOI: 10.1038/s42256-024-00807-9](https://doi.org/10.1038/s42256-024-00807-9)) — see `Pai_Literature_Digest.md`. This 2025 preprint is cited only as a contemporaneous preprint with explicit status disclosure, per our protocol convention of excluding preprints from peer-reviewed precedence claims.

**Why this paper still matters for us.** Reviewers may have read the preprint and will ask how our work differs from it. We must therefore retain the six-axis differentiation digest here even though Pai 2025 is not a peer-reviewed precedent.

---

## 1. What Pai 2025 actually does

### 1.1 Datasets
Six public oncology datasets (3 244 scans total):
- **LUNA16** — 888 thoracic CT, 1 186 nodules from LIDC-IDRI, malignancy classification (677-nodule subset used).
- **DLCS (Duke Lung Cancer Screening)** — 1 714 scans, pathology-confirmed malignancy, Lung-RADS-flagged.
- **NSCLC-Radiomics (Aerts)** — 421 patients, 2-year survival post-radiotherapy.
- **NSCLC-Radiogenomics (Stanford)** — 133 patients, 2-year survival post-surgery.
- **C4KC-KiTS** — 134 patients, renal carcinoma 2-year survival.
- **Colorectal-Liver-Metastases (MSKCC)** — 194 patients, 2-year survival post-resection.

### 1.2 Models benchmarked
Ten **3D** foundation models: ModelsGenesis (UNet, restorative SSL), FMCIB (contrastive, lesion-vs-non-lesion patch-level), CTClip (3D CLIP, vision-language), PASTA (nnUNet + synthetic tumours), VISTA3D (segmentation pre-training), Voco (geometric-context SSL), SUPREM (supervised), Merlin (vision-language abdominal), MedImageInsight (2D, averaged across slices), CT-FM.

### 1.3 Downstream classifier
**kNN with cosine distance**, 10-fold CV, Optuna hyperparameter tuning of k ∈ [1, 50] inside each fold. 95% CIs from the 10-fold variance.

### 1.4 Robustness analyses (the key passage for our differentiation)

Two robustness arms, neither involving segmentation-mask perturbation:

1. **Test-retest reliability on RIDER.** "A collection of chest CT scans from 26 patients where each patient underwent two scans within a 15-minute interval. For each model, we calculated the **cosine similarity** between embeddings generated from these paired scans." Higher cosine ⇒ more robust to scanner-repeat noise. Result: most models 0.97-1.00; Merlin 0.81; CTClip 0.93.

2. **Annotation-variability simulation via seed-point jitter.** "We simulated annotation variability by generating 50 random perturbations of each **seed point**. These perturbations followed a three-dimensional multivariate normal distribution (zero mean, diagonal covariance matrix) with a variance of 16 voxels in each dimension. We then trained models on one trial and compared predictions across all trials, measuring agreement using **Cohen's Kappa** after converting continuous predictions to categorical values."

### 1.5 Their own stated limitations (verbatim from Discussion)
- Public-data-only benchmark; restricted-access cohorts not included.
- Image-only evaluation; multimodal models penalised.
- Fixed embeddings (no fine-tuning).
- kNN classifier only.

---

## 2. The six-axis differentiation we claim against Pai 2025

For each axis the question is: *does Pai already do this?* If yes, our novelty collapses on that axis. If no, it stands.

| # | Axis | Pai 2025 | Paper 2 (this work) | Differentiation status |
|---|------|----------|---------------------|------------------------|
| 1 | **What is perturbed** | Scan acquisition (test-retest on RIDER, 26 patients, 15-min interval) AND **seed point** (3D Gaussian, σ²=16 vx) | **Segmentation mask** itself: 4-reader natural (LIDC-IDRI) + 7 controlled morphological + 1 Dice-calibrated synthetic | **CLEAR — Pai never perturbs the mask.** |
| 2 | **Metric used** | **Global cosine similarity** between embedding vectors + Cohen's Kappa on categorical predictions | **Per-feature/per-dimension ICC(2,1)** two-way random absolute agreement, with 95% CIs and stability stratification (poor / moderate / good / excellent) | **CLEAR — per-dim ICC is finer-grained than global cosine.** |
| 3 | **Comparator paradigm** | FM-vs-FM (10 FMs against each other) | **FM-vs-handcrafted radiomics** head-to-head on the same lesions under the same perturbations (PyRadiomics 2D and 3D arms) | **CLEAR — Pai has no radiomics arm.** |
| 4 | **Downstream task evaluation pre vs post stability filter** | None — no filter is applied; raw embeddings always used | **Nested-CV malignancy classification** with ICC-filtering at τ ∈ {0.50, 0.75, 0.85, 0.90} compared against unfiltered. Pre-vs-post ΔAUC is the primary effect-size for H2. | **CLEAR — Pai never reports the filter effect.** |
| 5 | **Classifier choice** | kNN (Optuna-tuned k) with cosine distance | L2-regularised logistic regression in nested CV; selection-stability Jaccard reported in supplementary | **MODERATE — different classifier, but defensible because L2 logistic is what radiomics literature uses (Pavic 2018, van Timmeren 2020), enabling like-for-like comparison.** |
| 6 | **Model family** | **3D** FMs only (FMCIB, ModelsGenesis, VISTA3D, CTClip, Voco, etc.) | **2D** FMs (BiomedCLIP, RadImageNet-ResNet50) on the central axial slice; matched against PyRadiomics 2D (fairness arm) and 3D (reference) | **MODERATE — different model family. Important caveat: our 2D-FM choice is forced by the laptop-only constraint. Manuscript Limitations §4.5 must acknowledge that 3D FMs would be the natural extension.** |
| 7 (bonus) | **Use of LIDC-IDRI's 4-reader natural variability** | Uses LIDC for malignancy labels (LUNA16 subset, 677 nodules with "at least one indication of malignancy suspicion") — but **does not use the 4-reader independent segmentations as a perturbation arm** | Uses the 4-reader segmentations as a primary natural-perturbation arm, with the consensus mask as the synthetic-perturbation anchor | **CLEAR — under-exploited resource in Pai.** |

---

## 3. Plain-English novelty paragraph for our manuscript Introduction

> Pai et al. (2025) recently introduced TumorImagingBench, a 10-FM benchmark across six public oncology cohorts that measures embedding stability via cosine similarity on RIDER same-day repeat scans and via Cohen's Kappa under 50-trial 3D-Gaussian seed-point jitter (σ²=16 voxels). Their work establishes that the leading 3D FMs (FMCIB, ModelsGenesis, VISTA3D) produce highly repeatable embeddings under scan-acquisition repetition. It does not, however, address how those embeddings respond when the segmentation mask itself is perturbed — the dominant source of feature noise in the IBSI-aligned radiomics literature — and it does not include a handcrafted-radiomics comparator, leaving the central practical question of *whether ICC-style stability filtering remains necessary in the foundation-model era* unanswered. Our work addresses this gap directly: we perturb the segmentation mask (four expert readers plus seven controlled morphological transformations plus one Dice-calibrated synthetic mask per nodule), compute per-feature/per-dimension ICC(2,1) on the resulting embeddings and on matched 2D and 3D PyRadiomics features extracted from the same lesions, and report the downstream malignancy-AUC consequence of stability-based feature filtering in a nested cross-validation that prevents selection-stage leakage.

---

## 4. References we now cite in §1 and §4.2 of the manuscript

- Pai 2025 — [DOI: 10.21203/rs.3.rs-6630446/v1](https://doi.org/10.21203/rs.3.rs-6630446/v1) (PMC12154149).
- Armato 2011 — original LIDC-IDRI paper.
- Pavic 2018 — radiomics ICC inter-rater segmentation literature.
- van Timmeren 2020 — radiomics QA review.
- Cosma 2025 — TNBC breast MRI segmentation variability finding ([arXiv:2504.01692](https://arxiv.org/abs/2504.01692)).
- Zwanenburg 2020 — IBSI 1.0 reference.
- Mongan 2020 — CLAIM checklist.

*According to PubMed.*
