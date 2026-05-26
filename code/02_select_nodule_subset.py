"""
02_select_nodule_subset.py — apply inclusion criteria and persist per-nodule artefacts.

Third script in the pipeline. Reads the LIDC-IDRI DICOMs downloaded by
``01_download_lidc.py``, parses the LIDC XML annotations, applies the
pre-registered inclusion cascade, and writes one directory per included
nodule with the CT subvolume and the per-reader binary masks. Also writes
``data/labels.csv`` with the case-id / nodule-id / class-label table.

Inclusion criteria (decisions.log #001, amended through #011 to the final
6 mm Fleischner threshold per MacMahon et al. Radiology 2017):
  - >=3 reader segmentations per nodule (manuscript H1 design requires this).
  - Median diameter >=6 mm (was 10 mm originally; relaxed because LIDC's
    benign-class pool at >=10 mm exhausts at ~29 nodules — see decisions.log
    #011 for the power analysis).
  - Median malignancy rating <=2 (benign) or >=4 (malignant). Ambiguous
    median=3 ratings are excluded to keep a clean binary label.
  - ``target_per_class`` controls when the inclusion loop breaks; we run it
    at 300 so the loop reaches a natural ceiling rather than terminating
    artificially early on whichever class is over-represented in the first
    few hundred patients.

Two non-obvious patches applied during Week 1:

  1. NumPy alias restoration (lines below the imports). pylidc 0.2.3 still
     calls ``np.int``, ``np.float``, ``np.bool`` which were removed in
     numpy 1.24+. We restore them as builtin aliases at import time so
     ``scan.cluster_annotations()`` does not crash on numpy 1.26.

  2. Unified consensus bbox via ``pylidc.utils.consensus`` (in the per-nodule
     loop). Originally each reader's mask was cropped in its own bounding
     box via ``ann.boolean_mask(pad=20)``, producing shape-mismatched arrays
     whenever readers disagreed on extent (which is almost always — that
     disagreement is precisely the inter-reader variability we are trying
     to study). Downstream ``np.stack(reader_masks)`` in script 03 crashed
     on the first nodule. The fix uses ``consensus(anns, clevel=0.5,
     pad=20, ret_masks=True)`` which returns a single bbox covering all
     readers and per-reader masks aligned to that bbox. Decision provenance:
     decisions.log #013.

Heavy lifting: pylidc (https://pylidc.github.io). Install via
``pip install pylidc==0.2.3``. pylidc requires LIDC-IDRI DICOMs in a
specific on-disk layout; configure ``~/.pylidcrc`` with a ``[dicom]``
section pointing to ``DATA_RAW`` before running this script.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

# pylidc 0.2.3 (latest on PyPI 2026-05-24) still uses np.int/np.float/np.bool
# which were removed in numpy 1.24+. Restore as builtin aliases so pylidc's
# cluster_annotations() works under numpy 1.26.
for _alias, _real in (("int", int), ("float", float), ("bool", bool)):
    if not hasattr(np, _alias):
        setattr(np, _alias, _real)

import pandas as pd
import SimpleITK as sitk
from tqdm import tqdm

from utils import DATA_PROCESSED, DATA_RAW, fix_seed, get_logger, save_sitk

log = get_logger("02_select")

INCLUSION = {
    "min_readers": 3,
    "min_diameter_mm": 6.0,        # was 10.0 — Fleischner actionable threshold (see decisions.log #011)
    "benign_max_score": 2,
    "malignant_min_score": 4,
    "target_per_class": 300,       # was 100 — will be re-tuned after first pass shows actual benign yield
}


def main(out_root: Path, labels_path: Path):
    """Iterate LIDC scans, apply inclusion criteria, persist per-nodule artefacts.

    For every LIDC-IDRI scan registered in pylidc's metadata DB (all 1018
    patients regardless of whether their DICOMs are on disk), this loop:

      1. Tries to read the DICOM volume via ``scan.to_volume`` — if the
         DICOMs are not on disk (pylidc lists all 1018 patients, but we
         only downloaded 600), the read raises and we ``continue`` past
         that scan. The bare-except on lines around the to_volume call is
         intentional: pylidc raises a heterogeneous set of exceptions
         (FileNotFoundError, KeyError, RuntimeError from pydicom) and we
         genuinely want to skip every one of them.

      2. Clusters the per-reader XML annotations into per-nodule groups
         via ``scan.cluster_annotations()``.

      3. For each clustered nodule, applies the inclusion criteria
         (``min_readers``, ``min_diameter_mm``, median malignancy rating).

      4. For included nodules, computes the unified consensus bbox via
         ``pylidc.utils.consensus`` (see module docstring patch #2) and
         persists img.nrrd + mask_R{1..N}.nrrd to disk.

    The ``records`` list accumulates one dict per included nodule; at the
    end it becomes ``labels.csv``. The loop terminates early once both
    benign and malignant counters hit ``target_per_class``, but at 6 mm
    diameter we never reach that ceiling (final yield 198 malignant + 155
    benign = 353 nodules from 251 unique patients per decisions.log #014).
    """
    try:
        import pylidc as pl
        from pylidc.utils import consensus
    except ImportError:
        log.error("pip install pylidc==0.2.3 and configure ~/.pylidcrc per README.")
        raise

    fix_seed()
    scans = pl.query(pl.Scan).all()
    log.info(f"Found {len(scans)} scans via pylidc.")

    records: list[dict] = []
    benign, malignant = 0, 0
    for scan in tqdm(scans):
        if benign >= INCLUSION["target_per_class"] and malignant >= INCLUSION["target_per_class"]:
            break
        try:
            nodules = scan.cluster_annotations()
            # to_volume reads DICOMs from disk; skip patients we didn't download
            # (pylidc's metadata DB lists all 1018 LIDC patients regardless)
            vol_sitk = sitk.GetImageFromArray(scan.to_volume(verbose=False).transpose(2, 0, 1))
            spacing = scan.pixel_spacing
            thickness = scan.slice_thickness or spacing
            vol_sitk.SetSpacing((float(spacing), float(spacing), float(thickness)))
        except Exception:
            continue

        for n_idx, anns in enumerate(nodules):
            if len(anns) < INCLUSION["min_readers"]:
                continue
            diameters = [a.diameter for a in anns]
            if np.median(diameters) < INCLUSION["min_diameter_mm"]:
                continue
            mal_scores = [a.malignancy for a in anns]
            med_mal = float(np.median(mal_scores))
            if med_mal <= INCLUSION["benign_max_score"]:
                label = 0  # benign
                if benign >= INCLUSION["target_per_class"]:
                    continue
                benign += 1
            elif med_mal >= INCLUSION["malignant_min_score"]:
                label = 1  # malignant
                if malignant >= INCLUSION["target_per_class"]:
                    continue
                malignant += 1
            else:
                continue

            out_dir = out_root / scan.patient_id / f"nodule_{n_idx:02d}"
            out_dir.mkdir(parents=True, exist_ok=True)

            # Use pylidc.utils.consensus to get a UNIFIED bounding box covering
            # all reader annotations, plus per-reader masks aligned to that bbox.
            # Previously each reader's mask was computed in its own bbox via
            # `ann.boolean_mask(pad=20)`, which produced shape-mismatched arrays
            # whenever readers disagreed on extent (i.e. nearly always). That
            # made downstream `np.stack(reader_masks)` in script 03 crash.
            _cmask, cbbox, reader_arrays = consensus(anns, clevel=0.5, pad=20, ret_masks=True)
            x_sl, y_sl, z_sl = cbbox  # pylidc bbox is (x, y, z)

            vol_arr = sitk.GetArrayFromImage(vol_sitk)
            sub_vol = vol_arr[z_sl.start:z_sl.stop, y_sl.start:y_sl.stop, x_sl.start:x_sl.stop]
            sub_img = sitk.GetImageFromArray(sub_vol)
            sub_img.SetSpacing(vol_sitk.GetSpacing())
            save_sitk(sub_img, out_dir / "img.nrrd")

            for r_idx, mask_arr_xyz in enumerate(reader_arrays, start=1):
                mask_arr = mask_arr_xyz.transpose(2, 0, 1).astype(np.uint8)
                mask_sitk = sitk.GetImageFromArray(mask_arr)
                mask_sitk.SetSpacing(vol_sitk.GetSpacing())
                save_sitk(mask_sitk, out_dir / f"mask_R{r_idx}.nrrd")

            records.append(
                {
                    "case_id": scan.patient_id,
                    "nodule_id": f"nodule_{n_idx:02d}",
                    "label": label,
                    "n_readers": len(anns),
                    "median_diameter_mm": float(np.median(diameters)),
                    "median_malignancy": med_mal,
                }
            )

    labels = pd.DataFrame(records)
    labels.to_csv(labels_path, index=False)
    log.info(f"Selected {len(labels)} nodules (benign={benign}, malignant={malignant}).")
    log.info(f"Wrote labels → {labels_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--labels", type=Path, default=DATA_PROCESSED.parent / "labels.csv")
    args = parser.parse_args()
    main(args.out, args.labels)
