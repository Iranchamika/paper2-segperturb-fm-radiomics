# Environment Setup — Paper 2 (Segmentation Perturbation, CPU-only)

**Tested on:** Windows 10/11, Python 3.11, 16 GB RAM (your laptop spec).
**Total install time:** ~30 minutes including weight downloads.

---

## Step 1 — Create a clean conda env

**Updated 2026-05-21 after the actual Windows install:** Python 3.9, not 3.11. PyRadiomics ships no Windows wheel for any version newer than cp39 on PyPI, and conda-forge has no Windows builds at all. The source build of pyradiomics 3.0.1 fails under PEP 517 isolated install. The single command that works end-to-end is:

```powershell
conda env create -f environment.yml
```

(The `environment.yml` in this folder already has the correct Python 3.9 + scipy 1.12.0 + pyradiomics 3.1.0 pins; pip install -r will not work because the file is conda-format, not a requirements.txt.)

For reference, the env was previously documented as Python 3.11, which is incorrect for Windows. The Linux sandbox where the original sandbox-validation happened does have a pyradiomics 3.0.1 source build that succeeds because the build env is not strictly PEP-517-isolated; the Windows install path is different.

## Steps 2-4 — All handled by `conda env create -f environment.yml`

The `environment.yml` already contains the full pinned pip block (numpy 1.26.4, scipy 1.12.0, pyradiomics 3.1.0, torch 2.3.0+cpu, etc.). Running `conda env create` in Step 1 does everything Steps 2-4 used to do manually. No further pip install commands needed.

**Note on torch+cpu vs cuda:** the protocol calls for CPU-only inference, so the default Windows `torch==2.3.0` PyPI wheel (which is `2.3.0+cpu`) is correct. **Do not install the CUDA build** — it adds ~2 GB and we don't use the GPU.

Two warnings during the first import are expected and benign:
- `timm.models.layers` deprecation (from transformers) — harmless.
- `pylidc` `pkg_resources` deprecation — harmless.

## Step 5 — Download model weights (one-time, ~2 GB total)

Create `D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\models\` and run `code/00_download_weights.py` (provided).

This will fetch:
- BiomedCLIP `microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224` (~1.4 GB) via huggingface_hub
- RadImageNet ResNet50 weights from https://github.com/BMEII-AI/RadImageNet (~98 MB) — direct download, then re-saved as state_dict for torchvision ResNet50

## Step 6 — TCIA download tool

```powershell
pip install nbia-data-retriever-cli==0.4.2  # or use the official Java GUI
# Alternative: TCIA API via `requests` — used in code/01_download_lidc.py
```

## Step 7 — Verify install

```powershell
python -c "import pyradiomics, SimpleITK, open_clip, torch, pingouin; print('OK')"
```

Expected: `OK` printed to console with no warnings.

---

## Folder layout (after setup complete)

```
D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\
├── 00_Timeline_5Week_Sprint.md
├── 01_Protocol.md
├── 02_Environment_Setup.md
├── 03_Manuscript_Skeleton.md
├── decisions.log
├── code\
│   ├── 00_download_weights.py
│   ├── 01_download_lidc.py
│   ├── 02_select_nodule_subset.py
│   ├── 03_generate_perturbations.py
│   ├── 04_extract_radiomics.py
│   ├── 05_extract_fm_embeddings.py
│   ├── 06_compute_icc.py
│   ├── 07_downstream_classifier.py
│   ├── 08_make_figures.py
│   ├── utils.py
│   └── environment.yml
├── data\
│   ├── raw\              # original DICOM + XML masks from LIDC-IDRI
│   ├── processed\        # SimpleITK .nrrd images and masks per nodule
│   └── perturbations\    # synthetic perturbation masks (eroded/dilated/translated)
├── models\
│   ├── biomedclip\       # downloaded HF weights
│   └── radimagenet\      # downloaded ResNet50 .pt
├── results\
│   ├── radiomics_features.parquet
│   ├── fm_embeddings.parquet
│   ├── icc_table.csv
│   ├── downstream_metrics.csv
│   └── intra_rater_kappa.csv
├── figures\
│   ├── fig1_perturbation_examples.png
│   ├── fig2_icc_distributions.png
│   ├── fig3_calibration_curves.png
│   ├── fig4_stability_vs_weight.png
│   └── supp\
├── references\
│   ├── refs.bib
│   └── seed_papers\     # PDFs for the 25 most-cited methodology refs
└── manuscript\
    ├── 03_Manuscript_Skeleton.md
    ├── 04_Cover_Letter.md
    └── 05_Supplementary.md
```

---

## Hardware sanity check

Expected RAM peak ~8 GB during PyRadiomics extraction on 200 nodules (well under 16 GB).
Expected disk: ~30 GB after LIDC-IDRI download (DICOM is bulky). The 200-nodule subset is ~12 GB.

If disk is tight: keep DICOM in a separate D:\Research work\_cache\ folder and process to compressed NRRD immediately, then optionally delete the DICOM source.
