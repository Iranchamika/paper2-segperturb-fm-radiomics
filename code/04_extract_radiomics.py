"""
04_extract_radiomics.py — IBSI-aligned PyRadiomics extraction in dual 3D / 2D modes.

Fifth script in the pipeline. For every perturbation mask produced by script 03,
extracts the full IBSI-aligned PyRadiomics feature set in one of two modes and
writes the result to a mode-tagged parquet (``radiomics_features_3d.parquet`` or
``radiomics_features_2d.parquet``).

Two parallel modes, both run sequentially per the manuscript Methods §2.4.1:

  - ``--mode 3d``: volumetric extraction over the full mask. 107 features per
    extraction across firstorder (18), shape (14), GLCM (24), GLRLM (16),
    GLSZM (16), NGTDM (5), GLDM (14). Resamples to 1x1x1 mm isotropic via
    sitkBSpline. This is the upper-bound radiomics reference per
    decisions.log #002.
  - ``--mode 2d``: single-slice extraction with ``force2D=True`` and
    ``shape2D`` substituted for ``shape``. 102 features per extraction (the
    14-feature ``shape`` class is replaced by the 9-feature ``shape2D``
    class, so the count drops by 5). This is the apples-to-apples comparator
    for the BiomedCLIP arm in script 05, which also operates on a single
    slice — decisions.log #002 added this arm specifically to prevent a
    reviewer 2 'you compared FM 2D against radiomics 3D, that is unfair'
    rejection.

The 2D mode requires a pre-processing step (``to_central_axial_slice``) because
PyRadiomics' shape2D feature class refuses to compute on a 3D mask that has
more than one populated z-slice — we reduce each mask to its single maximum-area
axial slice before extraction. The same slice-selection rule is used in
script 05 (max-area, not centroid) per the harmonisation patch in
decisions.log #017, so the 2D PyRadiomics and BiomedCLIP arms see the same
input slice.

Outputs:
    results/radiomics_features_3d.parquet  (mode=3d, ~107 columns + 3 keys)
    results/radiomics_features_2d.parquet  (mode=2d, ~102 columns + 3 keys)

Key columns: case_id, nodule_id, perturbation. Feature columns are prefixed
``original_`` (we extract only the un-filtered image type; wavelet/LoG filters
are deferred to a supplementary sensitivity analysis).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk
import yaml
from radiomics import featureextractor
from tqdm import tqdm

from utils import DATA_PERTURB, RESULTS, fix_seed, get_logger

log = get_logger("04_radiomics")

# --------------------------------------------------------------------------- #
# PyRadiomics configuration — IBSI-aligned defaults
# --------------------------------------------------------------------------- #
# Updated 2026-05-21 (decisions.log #002): support both 3D (full-volume) and
# 2D (central-axial-slice) extraction. 2D arm uses shape2D in lieu of shape.
def pyradiomics_params(mode: str = "3d") -> dict:
    """Return the PyRadiomics parameter dict for the requested extraction mode.

    Parameters
    ----------
    mode : {"3d", "2d"}
        ``"3d"``: full-volume extraction with the standard 14-feature ``shape``
        class, BSpline resampling to 1x1x1 mm isotropic.
        ``"2d"``: single-slice extraction with ``force2D=True``,
        ``force2Ddimension=0`` (axial), the 9-feature ``shape2D`` class
        substituted for ``shape``, and resampling pixel spacing
        ``[1.0, 1.0, 0.0]`` (zero on the z-axis disables resampling along
        that axis, preserving the native slice geometry).

    The returned dict is written verbatim to disk by ``build_extractor`` so
    that the exact parameter set used for the run is auditable (Supplementary
    File 2 in the manuscript).
    """
    if mode == "3d":
        return {
            "setting": {
                "binWidth": 25,
                "resampledPixelSpacing": [1.0, 1.0, 1.0],
                "interpolator": "sitkBSpline",
                "padDistance": 5,
                "geometryTolerance": 1e-4,
                "weightingNorm": None,
                "label": 1,
            },
            "imageType": {"Original": {}},
            "featureClass": {
                "firstorder": [],
                "shape": [],
                "glcm": [],
                "glrlm": [],
                "glszm": [],
                "ngtdm": [],
                "gldm": [],
            },
        }
    elif mode == "2d":
        return {
            "setting": {
                "binWidth": 25,
                "resampledPixelSpacing": [1.0, 1.0, 0.0],  # in-plane only
                "interpolator": "sitkBSpline",
                "padDistance": 5,
                "geometryTolerance": 1e-4,
                "weightingNorm": None,
                "label": 1,
                "force2D": True,
                "force2Ddimension": 0,  # axial
            },
            "imageType": {"Original": {}},
            "featureClass": {
                "firstorder": [],
                "shape2D": [],
                "glcm": [],
                "glrlm": [],
                "glszm": [],
                "ngtdm": [],
                "gldm": [],
            },
        }
    raise ValueError(f"Unknown mode {mode}")


def build_extractor(mode: str = "3d") -> featureextractor.RadiomicsFeatureExtractor:
    """Construct a PyRadiomics RadiomicsFeatureExtractor for the requested mode.

    Writes the parameter dict to ``results/pyradiomics_params_<mode>.yaml`` as
    a side effect so the exact extractor configuration is preserved on disk
    alongside the extracted features. The YAML is referenced as Supplementary
    File 2 in the manuscript and lets reviewers verify our IBSI compliance
    without needing to re-run our code.
    """
    params = pyradiomics_params(mode)
    params_path = RESULTS / f"pyradiomics_params_{mode}.yaml"
    params_path.write_text(yaml.safe_dump(params))
    return featureextractor.RadiomicsFeatureExtractor(str(params_path))


# --------------------------------------------------------------------------- #
def find_image_path(nodule_dir_processed: Path) -> Path:
    return nodule_dir_processed / "img.nrrd"


def list_perturbation_masks(nodule_dir_perturb: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in nodule_dir_perturb.glob("mask_*.nrrd"):
        tag = p.stem.replace("mask_", "")
        out[tag] = p
    return out


# --------------------------------------------------------------------------- #
def to_central_axial_slice(mask_path: Path) -> sitk.Image:
    """Reduce a 3D mask to its single central axial slice (the slice with the
    largest mask area). pyradiomics' `shape2D` requires the mask to be exactly
    1 voxel thick in one axis; without this preprocessing every 2D extraction
    crashes with 'Size of the mask in dimension %i is more than 1'.
    The chosen slice == the slice with maximum nodule area, which is the
    standard 2D-radiomics convention for 3D segmentations.
    """
    m = sitk.ReadImage(str(mask_path))
    arr = sitk.GetArrayFromImage(m)  # (z, y, x)
    areas = arr.sum(axis=(1, 2))
    if int(areas.sum()) == 0:
        return m
    z_max = int(areas.argmax())
    out = np.zeros_like(arr)
    out[z_max] = arr[z_max]
    out_img = sitk.GetImageFromArray(out)
    out_img.CopyInformation(m)
    return out_img


def extract_for_nodule(
    extractor, img_path: Path, masks: dict[str, Path], case_id: str, nodule_id: str, mode: str = "3d"
) -> list[dict]:
    """Run PyRadiomics across every perturbation mask for one nodule.

    Returns one dict per successful extraction (one row in the output
    parquet). Extractions that raise (typically due to a degenerate mask
    surviving past script 03's guard) are logged and skipped — the run
    continues. This is the same per-extraction error-isolation pattern used
    in script 01's per-series download loop and script 05's per-slice FM
    inference loop: a single bad nodule should not abort a multi-hour run.

    The output row keys are restricted to features prefixed ``original_``
    (i.e. extracted from the un-filtered image). PyRadiomics' diagnostic
    keys (``diagnostics_*``) are intentionally dropped because they are
    not biomarker features and they would clutter the downstream ICC
    computation in script 06.
    """
    rows = []
    for tag, mask_path in masks.items():
        try:
            if mode == "2d":
                mask_obj = to_central_axial_slice(mask_path)
                features = extractor.execute(str(img_path), mask_obj)
            else:
                features = extractor.execute(str(img_path), str(mask_path))
        except Exception as e:
            log.error(f"{case_id}/{nodule_id}/{tag} radiomics failed: {e}")
            continue
        row = {"case_id": case_id, "nodule_id": nodule_id, "perturbation": tag}
        for k, v in features.items():
            if k.startswith("original_"):
                row[k] = float(v) if hasattr(v, "__float__") else v
        rows.append(row)
    return rows


def main(processed_root: Path, perturb_root: Path, out_path: Path, mode: str = "3d"):
    """Walk the perturbation tree, extract features, write the mode-tagged parquet.

    The walk iterates ``data/perturbations/<case_id>/nodule_*/`` directories
    (the superset of 353 nodules) rather than reading ``labels.csv``. Per
    decisions.log #016 the labels-filter is applied downstream in script 07,
    which lets us extract once and run multiple sensitivity analyses
    (balanced 310, unbalanced 353, strict-10 mm 129) on different cohort
    definitions without re-extraction.
    """
    fix_seed()
    extractor = build_extractor(mode)

    all_rows: list[dict] = []
    case_dirs = sorted([p for p in perturb_root.glob("*/nodule_*") if p.is_dir()])
    log.info(f"Extracting radiomics for {len(case_dirs)} nodules.")

    for nodule_dir_perturb in tqdm(case_dirs):
        rel = nodule_dir_perturb.relative_to(perturb_root)
        case_id, nodule_id = rel.parts[0], rel.parts[1]
        nodule_dir_proc = processed_root / rel
        img_path = find_image_path(nodule_dir_proc)
        if not img_path.exists():
            log.error(f"Missing image at {img_path}; skipping.")
            continue
        masks = list_perturbation_masks(nodule_dir_perturb)
        if not masks:
            log.warning(f"No masks in {nodule_dir_perturb}; skipping.")
            continue
        rows = extract_for_nodule(extractor, img_path, masks, case_id, nodule_id, mode)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    # Tag the output filename with the mode for the dual-arm design.
    out_path = out_path.with_name(f"{out_path.stem}_{mode}.parquet")
    df.to_parquet(out_path, index=False)
    log.info(f"Wrote {len(df)} rows × {df.shape[1] - 3} features → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed", type=Path, default=Path(r"D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\data\processed"))
    parser.add_argument("--perturb", type=Path, default=DATA_PERTURB)
    parser.add_argument("--out", type=Path, default=RESULTS / "radiomics_features.parquet")
    parser.add_argument("--mode", choices=["3d", "2d"], default="3d", help="Volumetric vs central-slice extraction.")
    args = parser.parse_args()
    main(args.processed, args.perturb, args.out, args.mode)
