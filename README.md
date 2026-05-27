# Paper 2: Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort

[![OSF Registration DOI](https://img.shields.io/badge/OSF%20Registration-10.17605%2FOSF.IO%2F9KT3C-blue)](https://osf.io/9kt3c)
[![OSF Project](https://img.shields.io/badge/OSF%20Project-3f76x-lightblue)](https://osf.io/3f76x)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Repository for the data-extraction, ICC, classifier and figure-generation code behind the manuscript of the same name (target journal: *Medical Physics*, AAPM / Wiley). Author: **W. A. I. C. Kumarananda**, Independent Researcher, Adelaide, South Australia.

## What this is

A controlled-perturbation reproducibility study comparing two pretrained foundation-model (FM) embeddings (BiomedCLIP, RadImageNet ResNet50) against IBSI-aligned PyRadiomics handcrafted features under segmentation-mask perturbation on 310 LIDC-IDRI lung nodules from 227 patients. The four pre-registered hypotheses and the diameter-stratified subgroup analysis are documented in `OSF_PREREGISTRATION.md`; the protocol-amendment trail is in `decisions.log` (entries #001 through #025).

## Headline findings

| Finding | Where in the manuscript |
|---------|--------------------------|
| H1 rejected across all four FM-versus-radiomics paradigm-pair contrasts: no FM exceeds either radiomics arm on the proportion of features stable at ICC ≥ 0.75 (radiomics-3D 94.4 %, radiomics-2D 91.2 %, BiomedCLIP 90.4 %, RadImageNet 75.1 %) | Results §3.2 |
| H1' supported (K-S test across six paradigm-pairs): per-feature ICC distributions differ substantially between paradigms, with RadImageNet bimodal-shape-spread, BiomedCLIP unimodal-good-band-concentrated, radiomics bimodal-shape-versus-texture | Results §3.3 |
| Both FMs benefit consistently from ICC-based filtering with a +1.4 to +2.3 pp AUC lift (BiomedCLIP 0.898 → 0.912 at ICC ≥ 0.85; RadImageNet 0.794 → 0.817 at ICC ≥ 0.90); radiomics shows no meaningful change under the same filter | Results §3.4 + Discussion §4.3 |
| H3 supported in all paradigms: post-filter AUC non-inferior to pre-filter at the pre-registered 0.020 margin | Results §3.4 |
| BiomedCLIP calibration improves substantially under ICC ≥ 0.85 filter (Brier 0.144 → 0.115; ECE 0.129 → 0.065) | Results §3.4 + Discussion §4.3 |
| Aggregate AUC ranking (radiomics ~0.95 > BiomedCLIP 0.898 > RadImageNet 0.794) is largely a size-class artefact: within-stratum AUC is only meaningfully measurable in the 10-20 mm band; the 6-10 mm band is class-imbalance-limited (6 % positive rate) and the >20 mm band has insufficient benign cases for AUC computation | Results §3.5 + Discussion §4.4 |
| **Methodological contribution:** dual structural-and-functional validation procedure for community-distributed FM weights — pre-emptively catches silent `load_state_dict(strict=False)` no-load failures that would otherwise produce publication-relevant artefacts. The validation procedure was developed in response to a real RadImageNet PyTorch-port key-mismatch bug caught during the present study | Discussion §4.6 (new subsection) |

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
├── decisions.log               # append-only protocol-amendment record #001-#025
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
python 05_extract_fm_embeddings.py --fm biomedclip   # ~13 min (CPU)
python 05_extract_fm_embeddings.py --fm radimagenet  # ~8  min (CPU; requires weights — see below)
python 06_compute_icc.py                 # ~34 min  (pingouin ICC across four paradigms; bootstrap variance dominant)
python 07_downstream_classifier.py --labels ../data/labels_balanced.csv
python 07b_subgroup_analysis.py --labels ../data/labels_balanced.csv
python 08_make_figures.py                # ~5 s     (matplotlib PNGs for Figs 1-4)
```

Bit-exact reproducibility was verified for the downstream classifier across two independent runs on the same machine. Random seeds are fixed at 42 in numpy, torch, and pandas's `DataFrame.sample`. The PyRadiomics 3.1.0 pin is required for Windows; on Linux any 3.0.x or 3.1.0 should also work.

## RadImageNet weights

The RadImageNet PyTorch pretrained ResNet50 weights are openly downloadable (no form gating; the BMEII-AI Google Form gates the underlying training dataset only). Download `RadImageNet_pytorch.zip` (186 MB) from https://drive.google.com/file/d/1RHt2GnuOYlc_gcoTETtBDSW73mFyRAtR/view?usp=sharing, extract `ResNet50.pt`, and rename to the path expected by script 05:

```bash
mkdir -p models/radimagenet
# Place ResNet50.pt from the extracted zip at models/radimagenet/RadImageNet-ResNet50_notop.pt
```

**Important loader note (per decisions.log #025).** The RadImageNet PyTorch port stores weights in `nn.Sequential` indexing (`backbone.0.*` through `backbone.7.*`) rather than torchvision's named attributes (`conv1.*`, `bn1.*`, `layer1.*` through `layer4.*`). The patched `load_radimagenet()` in `code/05_extract_fm_embeddings.py` applies a rename map and uses `strict=True` to fail loudly on any structural mismatch. Earlier versions of this loader used `strict=False` which silently accepted the mismatch and ran inference with random Kaiming-uniform weights — a publication-relevant artefact caught only by audit. Do not regress to `strict=False`.

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

OSF Registration: https://osf.io/9kt3c (permanent DOI `10.17605/OSF.IO/9KT3C`, archived 2026-05-26). Associated working OSF Project: https://osf.io/3f76x. Eight protocol amendments since initial deposit (2026-05-25) are documented in Section P of `overleaf_project/OSF_PREREGISTRATION.md` and cross-referenced from each entry in `decisions.log` (entries #001 through #025). Amendments 7 and 8 record the Plan A execution that added RadImageNet as the second confirmatory FM paradigm and the subsequent silent state-dict no-load bug that was caught by audit and corrected before manuscript narrative lock-in.

## License

Code is released under the MIT License (see `LICENSE`). The manuscript LaTeX source under `overleaf_project/` is released under CC-BY 4.0. The LIDC-IDRI imaging data is governed by the TCIA Data Use Agreement and is not redistributed in this repository.

## Contact

W. A. I. C. Kumarananda — Independent Researcher, Adelaide, South Australia, Australia.
Email: iran.wanniarachchige@student.adelaide.edu.au
