# Cover Letter — Medical Physics submission

[date of submission]

The Editor-in-Chief
*Medical Physics*
American Association of Physicists in Medicine
Alexandria, VA, USA

Dear Editor,

I am pleased to submit the enclosed manuscript, **"Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort,"** for consideration as a Research Article in *Medical Physics*.

This work directly addresses a question that has emerged with the rapid adoption of pretrained foundation models in medical imaging but has not yet been answered in the peer-reviewed literature: how does segmentation perturbation — long known to destabilise handcrafted radiomic features — propagate through foundation-model embeddings, and does the routine ICC-based stability filter inherited from the radiomics era serve the same function for FM features? The peer-reviewed precedent is Pai et al. (*Nature Machine Intelligence*, 2024), which introduced the FMCIB foundation model and demonstrated that its feature-based predictions are highly stable to scanner-repeat and seed-point jitter, but did not perturb the segmentation mask, did not compare against IBSI-aligned PyRadiomics, and did not report pre-vs-post stability-filter downstream task performance. A more recent *Research Square* preprint by the same group (Pai et al. 2025, TumorImagingBench) extends this to a 10-FM panel using cosine similarity but has not yet undergone peer review. Cosma et al. (*SPIE J Med Imag*, 2025) studied radiomic feature stability under segmentation variability in breast MRI for TNBC subtype prediction but did not include a foundation-model arm. To our knowledge, no peer-reviewed study has yet performed a head-to-head, per-dimension comparison of FM and IBSI-aligned radiomic stability on lung CT with the LIDC-IDRI multi-reader cohort under controlled segmentation-mask perturbation, which is the contribution of the present manuscript.

Our key contributions are:
1. The first head-to-head comparison of segmentation-perturbation propagation through FM embeddings (BiomedCLIP, RadImageNet ResNet50) versus IBSI-aligned PyRadiomics on the same lung-CT cohort.
2. A combined natural-inter-reader and synthetic-perturbation design at controlled magnitudes, leveraging LIDC-IDRI's 4-reader segmentations.
3. Per-dimension ICC analysis on dense FM embeddings — a level of granularity not previously reported.
4. Rigorous downstream malignancy classification with pre-vs-post-filter AUC, Brier score, and expected calibration error, generalising the Cosma 2025 finding (that ICC-filtering may exclude predictive features) to lung CT and FM embeddings.

The work is pre-registered on the Open Science Framework prior to any analysis; all code, parameter files, extracted feature tables, and per-fold out-of-fold predictions are available at a public GitHub repository linked in the manuscript. The work uses only publicly available, de-identified TCIA LIDC-IDRI data and is therefore IRB-exempt. No funding was received for this work; the author has no conflicts of interest to declare.

I am submitting as an independent researcher and have followed *Medical Physics*'s submission guidelines for AI / machine-learning papers, including the AI methodological-elements checklist and disclosure of AI-assisted manuscript preparation per COPE guidelines. The manuscript is original, has not been published elsewhere, and is not under consideration by another journal.

I confirm that the work falls squarely within the scope of *Medical Physics*: it concerns the quantitative reproducibility of image-derived features for clinical decision support, with explicit attention to IBSI compliance, ICC methodology, and downstream calibration. I believe the paper will be of substantial interest to your readership of medical physicists working at the intersection of imaging quality assurance, radiomics, and modern deep-learning representation methods.

Thank you for your consideration. I look forward to your decision.

Sincerely,

**Iran [surname], MSc**
Independent Researcher
Adelaide, South Australia
a1846500@adelaide.edu.au
