# Week-1 User Checklist — Day-by-day actions for you

**Week:** 2026-05-21 (Thu) → 2026-05-27 (Wed)
**Total your-side time:** ~6-8 hours active + overnight TCIA download (passive).

Tick each box as you go. Anything blocked, add a line in `decisions.log` and tell me — I'll re-plan.

---

## Thu 2026-05-21 (today)

- [ ] Skim the Week-1 protocol and decisions log (5 min):
  - `01_Protocol.md` §4 (Dataset) and §5 (Perturbations)
  - `decisions.log` entries #001-#006 (these are the verification-pass amendments)
- [ ] Open https://osf.io/, create a free account using your Adelaide alumni email.
- [ ] Open https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/, register for a TCIA account if you don't already have one (LIDC-IDRI does not require a separate DUA — it's public under CC-BY 3.0 — but the account is required for the NBIA bulk-download API).

## Fri 2026-05-22

- [ ] **Environment setup** (~30 min). Open Anaconda Prompt:
  ```powershell
  conda create -n paper2 python=3.11 -y
  conda activate paper2
  cd "D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\code"
  pip install -r ..\code\environment.yml   # or follow 02_Environment_Setup.md step-by-step
  ```
  Note: I've already pinned `pyradiomics==3.0.1` (3.1.0 has no PyPI wheel for Py3.10/3.11; verified in sandbox 2026-05-21 — see decisions.log #007 that I'll add below).
- [ ] Verify the environment:
  ```powershell
  python -c "import numpy, pandas, SimpleITK, pingouin, sklearn, pyarrow, scipy; from radiomics import featureextractor; print('OK')"
  ```
  Expected: `OK`. If anything fails, paste the traceback and I'll triage.
- [ ] **Read Pai 2024 first** ([DOI: 10.1038/s42256-024-00807-9](https://doi.org/10.1038/s42256-024-00807-9), *Nature Machine Intelligence*, peer-reviewed) — this is the proper peer-reviewed precedent we must engage with. The combined digest is at `references/Pai_Literature_Digest.md`. (~60 min.)
- [ ] **Read Pai 2025 preprint second** ([DOI: 10.21203/rs.3.rs-6630446/v1](https://doi.org/10.21203/rs.3.rs-6630446/v1)) only as context — it is *not* peer-reviewed and we cite it as a preprint. The standalone digest is at `references/Pai_2025_TumorImagingBench_Digest.md`. (~30 min.)
- [ ] Goal: be able to defend (i) the peer-reviewed differentiation against Pai 2024 and (ii) the preprint-status disclaimer against any reviewer who pushes back that the 2025 preprint "already does this."

## Sat 2026-05-23

- [ ] **Download model weights** (~15 min active + ~10 min download):
  ```powershell
  cd "D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\code"
  python 00_download_weights.py
  ```
  This caches BiomedCLIP (~1.4 GB via HuggingFace cache) and prints instructions for the RadImageNet manual download. Follow the RadImageNet form-request link printed; access usually granted within 24 hours.
- [ ] **Kick off LIDC-IDRI download** (will run overnight, ~2-6 hours wall-time depending on TCIA bandwidth):
  ```powershell
  python 01_download_lidc.py --n_cases 200
  ```
  We download 200 *cases* (patients) to be safe; from this you'll select ≥400 *nodules* per the inclusion criteria. Disk: budget ~15-25 GB.

## Sun 2026-05-24

- [ ] **Verify LIDC download** (5 min). Count case folders:
  ```powershell
  Get-ChildItem "D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\data\raw\LIDC-IDRI-*" -Directory | Measure-Object
  ```
  Expected: 150-200 (some series fail and that's fine). If fewer than 100, re-run `01_download_lidc.py` with `--n_cases 250`.
- [ ] **Apply inclusion criteria** (~5 min):
  ```powershell
  python 02_select_nodule_subset.py
  ```
  Outputs `data/labels.csv`. Check that the file has ≥400 rows with `label` 0/1 distribution roughly 200/200. If short of 400, log the count and tell me — I'll loosen the diameter floor in `decisions.log`.
- [ ] **PyRadiomics dry run on 5 nodules** (~5 min). Quick sanity check before the full Week-2 extraction:
  ```powershell
  python -c "
  import pandas as pd
  from pathlib import Path
  d = pd.read_csv('data/labels.csv').head(5)
  print(d)
  print('First 5 nodule dirs:')
  for _, r in d.iterrows():
      print(f\"  data/processed/{r.case_id}/{r.nodule_id}\")
  "
  ```
  Then run `03_generate_perturbations.py` and `04_extract_radiomics.py --mode 2d` on just those 5 — confirm no exceptions, mask files appear, feature parquet is non-empty.

## Mon 2026-05-25

- [ ] **OSF pre-registration deposit**. Paste the contents of `OSF_Preregistration_Template.md` into a new OSF Standard Pre-Data Collection Registration form. Once submitted, OSF mints a DOI. Add the DOI to:
  - `01_Protocol.md` line 4 (Protocol header block)
  - `manuscript/03_Manuscript_Skeleton.md` §2.1
  - `manuscript/04_Cover_Letter.md` second paragraph
- [ ] **Lock protocol v1.1.** Once the OSF DOI is in, change the line `Version: 1.0 (DRAFT — locks 2026-05-27)` to `Version: 1.1 (LOCKED 2026-05-25, OSF DOI: ...)`.

## Tue 2026-05-26

- [ ] **Begin Methods §2.1-2.3 prose draft.** I'll do the heavy lifting in Week 2, but spending an hour writing your own version first will surface any methodological holes you want renegotiated. Use `manuscript/03_Manuscript_Skeleton.md` as scaffolding.
- [ ] **Reproducibility commit.** Initialise a private git repository (don't push yet):
  ```powershell
  cd "D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics"
  git init
  git add .
  git commit -m "Week 1: protocol locked, env validated, LIDC downloaded, dry run passed"
  ```

## Wed 2026-05-27

- [ ] **Week-1 wrap. Tell me:**
  - Final LIDC nodule count selected (with diameter/reader stratification)
  - OSF DOI
  - Any deviations to log (these are normal; just record them)
  - Any blockers you want me to fix before Week 2
- [ ] I will then:
  - Patch any code issues you surfaced
  - Begin Week-2 prose (Methods §2.4-2.6, the FM-embedding methodology)
  - Run Week-2 compute coordination instructions

---

## Reference card — files you'll touch most this week

- [Protocol v1.1](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\01_Protocol.md)
- [Environment setup guide](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\02_Environment_Setup.md)
- [OSF pre-registration template](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\OSF_Preregistration_Template.md)
- [Pai literature digest — both papers, peer-reviewed status flagged (read this first)](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\references\Pai_Literature_Digest.md)
- [Pai 2025 preprint standalone digest](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\references\Pai_2025_TumorImagingBench_Digest.md)
- [Introduction draft v1](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\manuscript\05_Introduction_v1.md)
- [Decisions log (append-only)](computer://D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\decisions.log)
