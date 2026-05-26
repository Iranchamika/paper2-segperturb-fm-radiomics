# Pai et al. — Literature digest for differentiation framing

**Important:** there are two related Pai papers in this space. Only one is peer-reviewed; the other is a preprint. They must be cited differently.

---

## Paper A — Pai et al. 2024, *Nature Machine Intelligence* (PEER-REVIEWED, primary citation)

### Citation
Pai S, Bontempi D, Hadzic I, Prudente V, et al. **Foundation model for cancer imaging biomarkers.** *Nature Machine Intelligence.* 2024 Mar 15. PMID: 38523679 · PMC: [PMC10957482](https://pmc.ncbi.nlm.nih.gov/articles/PMC10957482/) · [DOI: 10.1038/s42256-024-00807-9](https://doi.org/10.1038/s42256-024-00807-9). *According to PubMed.*

### What it does
- Introduces **FMCIB** — a 3D ResNet50 contrastively self-supervised pretrained (modified SimCLR) on 11 467 annotated lesions from 2 312 unique patients (DeepLesion source).
- Demonstrates FMCIB performance on three use cases: lesion anatomical site classification, LUNA16 nodule malignancy classification, NSCLC prognostication (LUNG1 + RADIO test cohorts).
- Documents two implementation modes: linear probe on frozen embeddings; full fine-tuning.

### Stability section — directly relevant to our work
- **Test-retest on RIDER (26 patients, 15-min interval):** FMCIB feature-based predictions achieved **ICC = 0.984**; the Supervised baseline reached ICC = 0.966. Spearman correlations on the flattened feature vectors were also strongly significant for both.
- **Inter-reader simulation on LUNG1:** generated 50 perturbations of each seed point sampled from a 3D multivariate normal with **σ²=16 voxels per dimension**. FMCIB features had significantly higher stability against simulated inter-reader variation in both feature distance and prediction performance than the Supervised baseline.

### What Pai 2024 does NOT do (these are open gaps in the peer-reviewed literature)
- Does **not perturb the segmentation mask itself** — only the centroid seed point.
- Does **not compare FM to handcrafted IBSI-aligned radiomics**. The compared baselines are Supervised CNN, Med3D, and Models Genesis — all deep-learning. PyRadiomics never appears.
- Uses only **3D FMs** (the proposed FMCIB and a 3D Med3D baseline). No 2D vision encoders are tested.
- Does **not report pre-vs-post stability-filter downstream AUC**.
- Reports a single ICC for the final model output (or for the 4 096-feature vector summed via Spearman), **not per-dimension ICC** across the embedding.

### Implication for our paper
Pai 2024 is the **peer-reviewed precedent** we must engage with in the Introduction and Discussion §4.2. The seed-point-jitter inter-reader simulation is established prior art and we will **not** claim it as novel. Our novel contributions remain (a) segmentation-mask perturbation, (b) head-to-head FM-vs-PyRadiomics on the same lesions, (c) downstream pre-vs-post-filter AUC, (d) per-dimension ICC granularity, (e) 2D-FM family extension.

---

## Paper B — Pai et al. 2025 "TumorImagingBench" (PREPRINT, NOT peer-reviewed)

### Citation
Pai S, et al. **Foundation model embeddings for quantitative tumor imaging biomarkers.** *Research Square* preprint, v1, May 2025. PMID: 40502795 · PMC: [PMC12154149](https://pmc.ncbi.nlm.nih.gov/articles/PMC12154149/) · [DOI: 10.21203/rs.3.rs-6630446/v1](https://doi.org/10.21203/rs.3.rs-6630446/v1). **Preprint** (Research Square, not peer-reviewed as of May 2026).

### What it does
- Benchmarks 10 3D FMs (FMCIB, ModelsGenesis, VISTA3D, CTClip, Voco, SUPREM, Merlin, MedImageInsight, CT-FM, PASTA) on 6 public oncology cohorts.
- Robustness: same RIDER test-retest framework (cosine similarity rather than ICC); same σ²=16-voxel seed-point jitter (Cohen's Kappa on categorical predictions).
- kNN classifier with cosine distance for all downstream tasks.

### How we treat it
- **Per our own Paper 1 protocol, preprints are excluded from the primary corpus.** Same logic applies here.
- We acknowledge Pai 2025 in §1 (Introduction) and §4.2 (Discussion) as a contemporaneous preprint that extends Pai 2024 to a 10-FM panel, with the explicit note that it has not yet undergone peer review.
- We do **not** cite it as a peer-reviewed reference in any claim that requires peer-review provenance.
- Reviewer 2 may still raise it; we are prepared with the differentiation digest in `Pai_2025_TumorImagingBench_Digest.md`.

---

## Updated novelty paragraph for our manuscript Introduction (replaces v1)

> The peer-reviewed precedent for FM-based imaging-biomarker reproducibility is Pai et al. 2024 (*Nature Machine Intelligence*), which introduced FMCIB — a contrastively pretrained 3D ResNet50 — and reported ICC = 0.984 for FMCIB feature-based predictions on RIDER same-day repeat scans and significantly higher stability than a Supervised CNN baseline under 50-trial three-dimensional Gaussian seed-point jitter (σ² = 16 voxels per dimension) on the LUNG1 cohort. Pai et al. 2024 establish that a well-pretrained FM can be more stable than a supervised CNN under acquisition-repeat and seed-point variability. Three open questions, however, remain unaddressed in the peer-reviewed literature: (i) how do FM embeddings respond when the *segmentation mask itself* is perturbed, the dominant noise source in IBSI-aligned handcrafted radiomics; (ii) does FM stability translate to a measurable advantage over PyRadiomics handcrafted radiomic features extracted from the same lesions under matched perturbation conditions; and (iii) does ICC-based stability filtering, the now-standard practice in radiomics pipelines, produce a measurable downstream-task benefit when applied to FM embeddings? A 2025 *Research Square* preprint by the same group (Pai et al. 2025, TumorImagingBench) extends the 2024 benchmark to ten 3D FMs and uses cosine similarity rather than ICC, but does not yet address these three questions and has not undergone peer review. Cosma et al. 2025, working independently on breast MRI for triple-negative breast cancer subtype prediction, report the counter-intuitive finding that ICC-based filtering of radiomic features can exclude features with predictive value — raising the possibility that the inherited ICC-filter convention may be unnecessary when modern regularised classifiers are used. The present study addresses all three open questions on the public LIDC-IDRI lung-CT cohort using a controlled-perturbation design that combines four-reader natural variability, seven controlled morphological perturbations, and one Dice-calibrated synthetic mask per nodule.
