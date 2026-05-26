"""
utils.py — shared helpers for the Paper 2 segmentation-perturbation pipeline.

Provides three groups of utilities consumed by every numbered pipeline script
(00_download_weights.py through 08_make_figures.py):

  1. Reproducibility: ``fix_seed`` seeds numpy and (if installed) torch with
     SEED = 42. Decision provenance: decisions.log #014 (cohort lock) requires
     bit-exact reproducibility for the seeded downsampling step that produces
     the balanced 155 + 155 cohort.

  2. Path constants: ``PROJECT_ROOT``, ``DATA_RAW``, ``DATA_PROCESSED``,
     ``DATA_PERTURB``, ``MODELS``, ``RESULTS``, ``FIGURES``. Hard-coded to
     ``D:\\Research work\\Paper2_SegPerturbation_FM_vs_Radiomics\\`` because
     every downstream script reads from / writes to these paths and centralising
     them prevents the 'where did the parquet go?' class of bug.

  3. Image I/O and 2D-slice helpers: ``load_sitk``, ``save_sitk``,
     ``get_bbox_3d``, ``central_axial_slice`` (DEPRECATED, see #017),
     ``max_area_axial_slice``, ``max_area_axial_mask_slice``,
     ``max_area_axial_slice_index``, ``hu_window_to_uint8``, ``crop_to_bbox_2d``.
     The max-area helpers were added per decisions.log #017 to harmonise the FM
     embedding slice with the 2D PyRadiomics arm; the original centroid-based
     ``central_axial_slice`` is retained for backward compatibility with
     pre-#017 sandbox code but must NOT be called from new scripts.

Author: Iran (Independent Researcher), 2026.
"""

from __future__ import annotations

import logging
import os
import random
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import SimpleITK as sitk

# --------------------------------------------------------------------------- #
# Reproducibility
# --------------------------------------------------------------------------- #
SEED = 42


def fix_seed(seed: int = SEED) -> None:
    """Seed every RNG the pipeline touches.

    Called as the first action in every numbered script. Seeds three sources:
    Python's ``random``, NumPy, and (if installed) PyTorch. Torch deterministic
    algorithms are explicitly left OFF because we never train a heavy network
    in this study (only forward-inference on pretrained BiomedCLIP), so the
    speed penalty of deterministic CUDNN is not worth paying.

    Parameters
    ----------
    seed : int, default=42
        The seed value. 42 is hard-coded by convention and matches the seed
        used in script 02b for the balanced-cohort downsampling step that is
        required to be bit-exact reproducible (decisions.log #014).
    """
    random.seed(seed)
    np.random.seed(seed)
    try:
        # torch is an optional dep for scripts 00-04 / 06-08 but mandatory for
        # 05 (FM embedding extraction). Seeding here even when torch is absent
        # is harmless and keeps the call-site simple.
        import torch

        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(False)  # see docstring — speed wins
    except ImportError:
        pass


# --------------------------------------------------------------------------- #
# Project paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(r"D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics")
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PERTURB = PROJECT_ROOT / "data" / "perturbations"
MODELS = PROJECT_ROOT / "models"
RESULTS = PROJECT_ROOT / "results"
FIGURES = PROJECT_ROOT / "figures"

for _p in (DATA_RAW, DATA_PROCESSED, DATA_PERTURB, MODELS, RESULTS, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        f = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        h.setFormatter(f)
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger


# --------------------------------------------------------------------------- #
# Image I/O helpers
# --------------------------------------------------------------------------- #
def load_sitk(path: str | os.PathLike) -> sitk.Image:
    return sitk.ReadImage(str(path))


def save_sitk(img: sitk.Image, path: str | os.PathLike) -> None:
    sitk.WriteImage(img, str(path), useCompression=True)


def get_bbox_3d(mask: sitk.Image, padding_mm: float = 5.0) -> Tuple[int, int, int, int, int, int]:
    """Return the 3D bounding box of a binary mask in voxel coordinates.

    Used in conjunction with ``crop_to_bbox_2d`` to extract a focused image
    region around a nodule for FM inference. The mm-based padding parameter
    means the absolute pad in voxels scales correctly across LIDC's variable
    in-plane spacing (typically 0.5--0.9 mm).

    Parameters
    ----------
    mask : SimpleITK.Image
        Binary 3D mask in (z, y, x) array order.
    padding_mm : float, default=5.0
        Padding to add on each side of the bbox, in millimetres. Converted
        to voxels using the image spacing, with a floor of 1 voxel per axis.

    Returns
    -------
    tuple of six ints
        (x0, x1, y0, y1, z0, z1) inclusive bbox in voxel coordinates.

    Raises
    ------
    ValueError
        If the mask is empty (sum of voxel values == 0).
    """
    arr = sitk.GetArrayFromImage(mask)  # z,y,x
    if arr.max() == 0:
        raise ValueError("Empty mask passed to get_bbox_3d.")
    zs, ys, xs = np.where(arr > 0)
    spacing = np.array(mask.GetSpacing())[::-1]  # z,y,x
    pad_z, pad_y, pad_x = (padding_mm / spacing).astype(int).clip(min=1)
    return (
        max(int(xs.min()) - pad_x, 0),
        min(int(xs.max()) + pad_x, arr.shape[2] - 1),
        max(int(ys.min()) - pad_y, 0),
        min(int(ys.max()) + pad_y, arr.shape[1] - 1),
        max(int(zs.min()) - pad_z, 0),
        min(int(zs.max()) + pad_z, arr.shape[0] - 1),
    )


def central_axial_slice(img: sitk.Image, mask: sitk.Image) -> np.ndarray:
    """DEPRECATED — selects by mask centroid. Use `max_area_axial_slice` for new code.

    Kept only for backward compatibility; do not call from script 05 anymore.
    """
    mask_arr = sitk.GetArrayFromImage(mask)
    if mask_arr.sum() == 0:
        raise ValueError("Empty mask in central_axial_slice.")
    z_center = int(np.round(np.argwhere(mask_arr).mean(axis=0)[0]))
    img_arr = sitk.GetArrayFromImage(img)
    return img_arr[z_center]


def max_area_axial_slice_index(mask: sitk.Image) -> int:
    """Return the z-index of the axial slice with the largest mask area.

    Added 2026-05-25 to harmonize FM-embedding slice selection with the 2D
    PyRadiomics arm (which uses the max-area slice per the central-slice patch
    applied to `04_extract_radiomics.py` after the shape2D crash). Using the
    same slice for both paradigms is required for an apples-to-apples
    FM-vs-radiomics comparison (see decisions.log #017).
    """
    arr = sitk.GetArrayFromImage(mask)
    if arr.sum() == 0:
        raise ValueError("Empty mask in max_area_axial_slice_index.")
    areas = arr.sum(axis=(1, 2))  # area per axial slice
    return int(areas.argmax())


def max_area_axial_slice(img: sitk.Image, mask: sitk.Image) -> np.ndarray:
    """Return the 2D axial slice with the largest mask area (image-space)."""
    z = max_area_axial_slice_index(mask)
    img_arr = sitk.GetArrayFromImage(img)
    return img_arr[z]


def max_area_axial_mask_slice(mask: sitk.Image) -> np.ndarray:
    """Return the 2D mask of the max-area axial slice (mask-space)."""
    z = max_area_axial_slice_index(mask)
    mask_arr = sitk.GetArrayFromImage(mask)
    return mask_arr[z]


def hu_window_to_uint8(slice_2d: np.ndarray, wl: int = -600, ww: int = 1500) -> np.ndarray:
    """Apply a CT lung window and convert to uint8 [0, 255].

    The default window level (-600) and window width (1500) are the standard
    pulmonary parenchyma window used in thoracic radiology — same window the
    LIDC readers used when producing the annotations we are extracting masks
    from, so the FM input matches what a radiologist would see on PACS.

    Parameters
    ----------
    slice_2d : numpy.ndarray
        2D float array of raw Hounsfield units (typical CT range -1024 to 3072).
    wl : int, default=-600
        Window level (centre of the displayed intensity window) in HU.
    ww : int, default=1500
        Window width (total extent of the displayed intensity window) in HU.

    Returns
    -------
    numpy.ndarray
        2D uint8 array, values in [0, 255], suitable for PIL.Image.fromarray.
    """
    lo, hi = wl - ww // 2, wl + ww // 2
    clipped = np.clip(slice_2d.astype(np.float32), lo, hi)
    norm = (clipped - lo) / (hi - lo)
    return (norm * 255).astype(np.uint8)


def crop_to_bbox_2d(slice_2d: np.ndarray, mask_2d: np.ndarray, pad_frac: float = 0.5) -> np.ndarray:
    """Crop a 2D slice around the mask bbox with fractional padding.

    ``pad_frac=0.5`` means the bbox is expanded by 50 % of its own width/height
    on each side before cropping; this is the standard 'context window' used in
    FM-radiomics studies to give the encoder some surrounding parenchyma rather
    than just the lesion in isolation. The 50 % pad is also what BiomedCLIP's
    own training pipeline expected, so we match it (decisions.log #017).

    Parameters
    ----------
    slice_2d : numpy.ndarray
        2D image array (already lung-windowed, typically uint8).
    mask_2d : numpy.ndarray
        2D binary mask, same shape as ``slice_2d``.
    pad_frac : float, default=0.5
        Padding as a fraction of the bbox dimensions, applied on each side.

    Returns
    -------
    numpy.ndarray
        Cropped 2D image. If the mask is empty, falls back to a 224x224 centre
        crop so the downstream FM call does not raise.
    """
    ys, xs = np.where(mask_2d > 0)
    if len(xs) == 0:
        h, w = slice_2d.shape
        return slice_2d[h // 2 - 112 : h // 2 + 112, w // 2 - 112 : w // 2 + 112]
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    bh, bw = y1 - y0 + 1, x1 - x0 + 1
    pad_h, pad_w = int(bh * pad_frac), int(bw * pad_frac)
    y0p = max(y0 - pad_h, 0)
    y1p = min(y1 + pad_h, slice_2d.shape[0])
    x0p = max(x0 - pad_w, 0)
    x1p = min(x1 + pad_w, slice_2d.shape[1])
    return slice_2d[y0p:y1p, x0p:x1p]
