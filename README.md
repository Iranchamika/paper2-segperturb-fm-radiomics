# Paper 2: Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort

[![OSF Registration DOI](https://img.shields.io/badge/OSF%20Registration-10.17605%2FOSF.IO%2F9KT3C-blue)](https://osf.io/9kt3c)
[![OSF Project](https://img.shields.io/badge/OSF%20Project-3f76x-lightblue)](https://osf.io/3f76x)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Repository for the data-extraction, ICC, classifier and figure-generation code behind the manuscript of the same name (target journal: *Medical Physics*, AAPM / Wiley). Author: **W. A. I. C. Kumarananda**, Independent Researcher, Adelaide, South Australia.

## What this is

A controlled-perturbation reproducibility study comparing pretrained foundation-model (FM) embeddings (BiomedCLIP) against IBSI-aligned PyRadiomics handcrafted features under segmentation-mask perturbation on 310 LIDC-IDRI lung nodules from 227 patients. The four pre-registered hypotheses and the diameter-stratified subgroup analysis are documented in `OSF_PREREGISTRATION.md`; the protocol-amendment trail is in `decisions.log`.

## Headline findings

| Finding | Where in the manuscript |
|---------|--------------------------|
| H1 rejected: FM and radiomics achieve comparable ~90 % stable feature rates at ICC ≥ 0.75 | Results §3.2 |
| H1' supported (post-hoc K-S test, D = 0.68-0.72, p < 1e-39): ICC distribution shapes differ substantially | Results §3.3 |
| H3 supported: post-filter AUC non-inferior to pre-filter at 0.020 margin in both paradigms | Results §3.4 |
| BiomedCLIP calibration improves substantially under ICC ≥ 0.85 filter (Brier 0.144 → 0.115; ECE 0.129 → 0.065) | Results §3.4 + Discussion §4.3 |
| Aggregate AUC gap (radiomics 0.95 vs BiomedCLIP 0.90) is a size-class artefact; gap dissolves within size-matched strata | Results §3.5 + Discussion §4.4 |

## Repository layout

```
.
├── code/                       # Pipeline scripts 00..08, run in order
│   ├── utils.py                # shared helpers (paths, seeding, image I/O)
│   ├── 00_download_weights.py  # cache BiomedCLIP weights for offline reuse
│   ├── 01_download_lidc.py     # TCIA NBIA v1 bulk DICOM download
│   ├── 02_select_nodule_subset.py  # pylidc inclusion cascade -> labels.csv
│   ├── 02b_balance_cohort.py   # seeded downsampling -> labels_balanced.csv
│   ├── 03_generate_perturbations.py  # consensus + 7 morphological + DC masks
│   ├── 04_extract_radiomics.py # PyRadiomics 3D and 2D arms
│   ├── 05_extract_fm_embeddings.py  # BiomedCLIP (and RadImageNet if available)
│   ├── 06_compute_icc.py       # ICC(2,1) + ICC(3,1) per feature per paradigm
│   ├── 07_downstream_classifier.py  # 5-fold CV L2-LogReg, bootstrap AUC CI
│   ├── 07b_subgroup_analysis.py     # diameter-stratified within-stratum AUC
│   ├── 08_make_figures.py      # Figures 1-4
│   └── environment.yml         # pinned conda environment (Python 3.9)
├── overleaf_project/           # LaTeX manuscript source
│   ├── main.tex                # IMRaD assembly
│   ├── abstract.tex, introduction.tex, methods.tex, results.tex,
│   │   discussion.tex, conclusions.tex
│   ├── references.bib          # Vancouver-format bibliography
│   ├── figures/                # PNG figures from script 08
│   ├── supplementary/          # S1-S5 PDFs and CSVs
│   ├── COVER_LETTER.md         # cover letter for Medical Physics submission
│   ├── OSF_PREREGISTRATION.md  # pre-registration body, archived as osf.io/9kt3c (DOI 10.17605/OSF.IO/9KT3C)
│   └── OSF_FILL_GUIDE.md       # tab-by-tab OSF Project fill instructions
├── decisions.log               # append-only protocol-amendment record #001-#023
├── results/                    # (gitignored) feature parquets, ICC table, metrics CSVs
├── data/                       # (gitignored) LIDC-IDRI DICOMs, processed NRRDs, masks
└── models/                     # (gitignored) cached FM weights (BiomedCLIP, RadImageNet)
```

The `data/`, `results/`, and `models/` directories are gitignored because they contain (a) the LIDC-IDRI DICOM corpus which is redistributable only through TCIA under the standard Data Use Agreement, and (b) ~13 GB of derived parquets and model weights that would inflate the repository pointlessly. To reproduce, follow the **Reproduce** section below.

## Reproduce

Requires Windows or Linux, a few hours of CPU time, and ~60 GB of free disk for the LIDC-IDRI download. No GPU required.

```bash
# 1. Set up the pinned environment
conda env create -f code/environment.yml
conda activate paper2

# 2. Register for free TCIA access (https://www.cancerimagingarchive.net/) and configure pylidc
# Create ~/.pylidcrc with a [dicom] section pointing to data/raw
# See https://pylidc.github.io for the exact format

# 3. Run the pipeline in order
cd code
python 00_download_weights.py            # ~15 min  (downloads BiomedCLIP ~1.4 GB to HuggingFace cache)
python 01_download_lidc.py --n_cases 600 # ~4-14 h  (network-bound; resumable per series)
python 02_select_nodule_subset.py        # ~1 h     (pylidc XML parsing + consensus bbox)
python 02b_balance_cohort.py             # ~5 s     (seeded random downsampling)
python 03_generate_perturbations.py      # ~2 min   (morphological ops, decisions.log #012 guard)
python 04_extract_radiomics.py --mode 3d # ~30 min  (PyRadiomics volumetric)
python 04_extract_radiomics.py --mode 2d # ~10 min  (PyRadiomics forced-2D)
python 05_extract_fm_embeddings.py --fm biomedclip  # ~13 min (CPU)
python 06_compute_icc.py                 # ~10 min  (pingouin ICC across paradigms)
python 07_downstream_classifier.py --labels ../data/labels_balanced.csv
python 07b_subgroup_analysis.py --labels ../data/labels_balanced.csv
python 08_make_figures.py                # ~5 s     (matplotlib PNGs for Figs 1-4)
```

Bit-exact reproducibility was verified for the downstream classifier across two independent runs on the same machine. Random seeds are fixed at 42 in numpy, torch, and pandas's `DataFrame.sample`. The PyRadiomics 3.1.0 pin is required for Windows; on Linux any 3.0.x or 3.1.0 should also work.

## Optional: RadImageNet second-FM extension

RadImageNet weights are gated behind a Google Form at https://github.com/BMEII-AI/RadImageNet. If access is granted after the initial submission, drop `RadImageNet-ResNet50_notop.pt` into `models/radimagenet/` and re-run:

```bash
python 05_extract_fm_embeddings.py --fm radimagenet
# Uncomment the radimagenet entry in 07_downstream_classifier.py's PARADIGMS list
python 06_compute_icc.py
python 07_downstream_classifier.py --labels ../data/labels_balanced.csv
python 07b_subgroup_analysis.py --labels ../data/labels_balanced.csv
python 08_make_figures.py
```

## Citation

If you use this code or data preprocessing pipeline, please cite the manuscript (preprint or final journal version, whichever is current) and the LIDC-IDRI dataset:

```bibtex
@article{kumarananda2026segperturb,
  author  = {Kumarananda, W. A. I. C.},
  title   = {Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort},
  journal = {Medical Physics},
  year    = {2026},
  note    = {Under review.}
}

@article{armato2011lidc,
  author  = {Armato, Samuel G III and others},
  title   = {The Lung Image Database Consortium (LIDC) and Image Database Resource Initiative (IDRI): a completed reference database of lung nodules on CT scans},
  journal = {Medical Physics},
  volume  = {38},
  number  = {2},
  pages   = {915--931},
  year    = {2011}
}
```

## Pre-registration and amendments

OSF Registration: https://osf.io/9kt3c (permanent DOI `10.17605/OSF.IO/9KT3C`, archived 2026-05-26). Associated working OSF Project: https://osf.io/3f76x. Five protocol amendments since initial deposit (2026-05-25) are documented in Section P of `overleaf_project/OSF_PREREGISTRATION.md` and cross-referenced from each entry in `decisions.log`.

## License

Code is released under the MIT License (see `LICENSE`). The manuscript LaTeX source under `overleaf_project/` is released under CC-BY 4.0. The LIDC-IDRI imaging data is governed by the TCIA Data Use Agreement and is not redistributed in this repository.

## Contact

W. A. I. C. Kumarananda — Independent Researcher, Adelaide, South Australia, Australia.
Email: iran.wanniarachchige@student.adelaide.edu.au
