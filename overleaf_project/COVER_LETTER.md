# Cover letter — source markdown (humanized)
**Manuscript:** Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort
**Target journal:** Medical Physics (AAPM / Wiley)
**Author:** W. A. I. C. Kumarananda
**Date:** [insertion at submission]
**Note:** Corresponding email is `iran.wanniarachchige@student.adelaide.edu.au` (Adelaide student/alumni address). Confirm the address is active before submission, or swap for a personal address.

---

[insertion at submission]

Editor-in-Chief
Medical Physics
American Association of Physicists in Medicine
Alexandria, VA, USA

Dear Editor,

Please consider for Medical Physics the attached manuscript, "Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort."

The headline finding: across 310 LIDC-IDRI lung nodules with four-reader natural segmentation variability, seven controlled morphological perturbations, and one Dice-calibrated synthetic mask per nodule, pretrained BiomedCLIP embeddings and IBSI-aligned PyRadiomics features reached comparable aggregate proportions of stable (ICC ≥ 0.75) features — about 90 % in both paradigms. Our pre-registered hypothesis that FM embeddings would be the more stable paradigm was rejected. The shape of the ICC distributions, however, differed substantially: PyRadiomics is bimodal with 63–68 % of features in the excellent stratum (ICC ≥ 0.90); BiomedCLIP is unimodal with 90 % of dimensions in the good band and no poor (ICC < 0.50) dimensions at all (Kolmogorov–Smirnov D = 0.68–0.72, p < 10⁻³⁹).

The downstream classification analysis added two unanticipated observations. ICC-based stability filtering had essentially no effect on classification AUC for either paradigm, extending to lung CT and FM embeddings a finding that Cosma et al. (2025) reported for breast MRI radiomics alone. BiomedCLIP's probability calibration also improved substantially under filtering (Brier 0.144 → 0.115, ECE 0.129 → 0.065 at ICC ≥ 0.85) while its discrimination improved at the same time. The calibration-improvement effect was not in the pre-registration; we treat it as a useful pointer for foundation-model deployment pipelines that report probability outputs.

The pre-specified diameter-stratified subgroup analysis produced what we read as the paper's most consequential finding for the wider methodology. The apparent aggregate AUC superiority of handcrafted radiomics over BiomedCLIP (0.95 versus 0.90) did not persist within size-matched strata: at 6–10 mm the three paradigms cluster at AUC ≈ 0.77 with overlapping confidence intervals, and at 10–20 mm PyRadiomics-3D retains a ≈ 0.095 lead but the confidence intervals still overlap. We read this as a methodological caution for FM-versus-radiomics benchmarking studies: any cohort with structural size–malignancy imbalance will inflate handcrafted radiomics' apparent advantage relative to foundation models whose preprocessing normalises size away, and aggregate AUC should be treated as a confounded secondary statistic in such cohorts.

The paper fits Medical Physics because the work concerns the quantitative reproducibility of image-derived features under controlled perturbation — the IBSI standardisation and ICC methodology your readership designs and audits. The peer-reviewed precedent we engage with is Pai et al. (Nature Machine Intelligence, 2024), which introduced FMCIB and demonstrated strong stability under scanner-repeat and seed-point jitter but did not perturb the segmentation mask, did not include an IBSI-aligned PyRadiomics comparator, and did not report pre-versus-post stability-filter downstream task performance. A contemporaneous Research Square preprint by the same group extends the FMCIB benchmark to ten 3D foundation models using global cosine similarity; we reference it for context but do not treat it as established precedent because it has not undergone peer review.

The protocol was pre-registered on the Open Science Framework before any feature extraction. All code, the pinned environment specification, extracted feature tables, per-fold out-of-fold predictions and figure-generation scripts are released publicly at submission. The work uses only publicly available, de-identified TCIA LIDC-IDRI data and is therefore IRB-exempt under the standard TCIA Data Use Agreement.

A standard set of declarations follows. The manuscript has not been published or submitted elsewhere. The listed author has read and approved the final version. There are no competing interests. AI-assisted manuscript preparation is disclosed in the Acknowledgements following COPE 2024 guidance and the Medical Physics 2026 AI-use policy: Anthropic Claude was used for literature triage, protocol drafting and grammar polishing, with all final analytical decisions, code, and manuscript wording the responsibility of the listed author.

Thank you for considering the paper.

Yours sincerely,

W. A. I. C. Kumarananda, MSc
Independent Researcher
Adelaide, South Australia, Australia
iran.wanniarachchige@student.adelaide.edu.au
