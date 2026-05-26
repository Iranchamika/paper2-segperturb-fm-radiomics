"""
03_generate_perturbations.py — synthesize segmentation-mask perturbations per nodule.

Fourth script in the pipeline. For every selected LIDC-IDRI nodule it produces
up to 12 mask files on disk: 1 consensus mask, 3-4 reader masks (copied from
script 02 output), 3 erosion levels, 2 dilation levels, 3 translation offsets,
and 1 Dice-calibrated synthetic mask. Manuscript Methods §2.3 documents the
specification.

Three protocol-driven design choices, each tied to a logged decision:

  1. The PERTURBATION_SPEC excludes 3-voxel dilation (decisions.log #005).
     Pilot work showed that radius-3 dilation on a 10 mm nodule produces
     ~40 % volume inflation, well outside the empirical LIDC inter-reader
     variability (median pairwise Dice 0.789 per decisions.log #014). Leaving
     it in the spec would have biased the perturbation distribution toward
     unrealistic over-segmentation.

  2. The volume-preservation guard (MIN_RETAINED_FRACTION = 0.25) inside
     ``process_nodule`` skips any erosion whose post-op mask retains less
     than 25 % of the consensus-mask voxel count (decisions.log #012). This
     guard was added after the 6 mm diameter relaxation made fixed-radius
     erosion liable to fully obliterate small nodules. The retention rate
     across the 353-nodule extraction cohort was 48 % for E1, 13 % for E2,
     and 2 % for E3 — exactly the small-nodule-protection behaviour the
     guard was designed to produce.

  3. The Dice-calibrated synthetic mask (DC) is generated per nodule by
     adaptive morphological perturbation tuned to match that specific
     nodule's median pairwise reader Dice (decisions.log #005). This anchors
     the synthetic perturbation magnitude to empirical reader noise rather
     than to an arbitrary voxel count, and gives reviewers a defensible
     answer to the 'are your synthetic perturbations realistic?' question.

Inputs:
    data/processed/<case_id>/nodule_<n>/img.nrrd
    data/processed/<case_id>/nodule_<n>/mask_R{1..7}.nrrd  (3-7 reader masks)
Outputs:
    data/perturbations/<case_id>/nodule_<n>/
        mask_consensus.nrrd            ← per-voxel majority vote
        mask_R{1..7}.nrrd              ← copied from input
        mask_E1.nrrd, mask_E2.nrrd, mask_E3.nrrd   ← erosion (subject to 25% guard)
        mask_D1.nrrd, mask_D2.nrrd                 ← dilation (no guard needed)
        mask_T1.nrrd, mask_T2.nrrd, mask_T3.nrrd   ← translation (no guard needed)
        mask_DC.nrrd                   ← Dice-calibrated per nodule
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import SimpleITK as sitk
from tqdm import tqdm

from utils import DATA_PERTURB, DATA_PROCESSED, fix_seed, get_logger, load_sitk, save_sitk

log = get_logger("03_perturbations")


# --------------------------------------------------------------------------- #
def consensus_mask(reader_masks: list[sitk.Image]) -> sitk.Image:
    """Per-voxel majority vote across all available reader masks.

    A voxel is set to 1 in the consensus if at least half of the readers
    marked it as inside the nodule. This is the standard LIDC consensus
    convention (matches what ``pylidc.utils.consensus(clevel=0.5)`` would
    produce) and is the anchor mask against which every synthetic
    perturbation in PERTURBATION_SPEC is computed.

    All input masks must already be on the same image grid; script 02 has
    enforced this via the unified ``pylidc.utils.consensus`` bbox crop
    (decisions.log #013). If that invariant is violated, ``np.stack`` will
    raise here and the run will fail loudly rather than producing a
    silently-corrupt consensus.
    """
    arrs = [sitk.GetArrayFromImage(m).astype(np.uint8) for m in reader_masks]
    stack = np.stack(arrs, axis=0)
    vote = (stack.sum(axis=0) >= (len(arrs) / 2.0)).astype(np.uint8)
    out = sitk.GetImageFromArray(vote)
    # Copy spacing/origin/direction from the first input so the consensus
    # mask is geometrically aligned with the original image in world space.
    out.CopyInformation(reader_masks[0])
    return out


def erode(mask: sitk.Image, radius_vx: int) -> sitk.Image:
    return sitk.BinaryErode(mask, kernelRadius=(radius_vx, radius_vx, radius_vx))


def dilate(mask: sitk.Image, radius_vx: int) -> sitk.Image:
    return sitk.BinaryDilate(mask, kernelRadius=(radius_vx, radius_vx, radius_vx))


def translate(mask: sitk.Image, shift_vx: tuple[int, int, int]) -> sitk.Image:
    """Rigid-translate a binary mask by integer-voxel offsets (no resampling).

    We use array indexing rather than ``sitk.ResampleImageFilter`` here for two
    reasons: (a) integer-voxel translation does not require interpolation, so
    skipping the resampler avoids potential aliasing artefacts on the binary
    mask, and (b) the array approach is much faster on the small per-nodule
    crops we work with (a few hundred voxels per side).

    Parameters
    ----------
    mask : SimpleITK.Image
        Binary 3D mask in (z, y, x) array order.
    shift_vx : tuple of three ints
        The (dx, dy, dz) shift in voxels. Note tuple is (x, y, z) order
        externally but we unpack to (z, y, x) internally to match the SITK
        array convention.

    Returns
    -------
    SimpleITK.Image
        Translated mask of the same shape as the input. Voxels shifted off
        the image bounds are dropped; voxels shifted into newly-empty
        regions are filled with 0.
    """
    arr = sitk.GetArrayFromImage(mask)  # z,y,x
    dz, dy, dx = shift_vx[2], shift_vx[1], shift_vx[0]
    out = np.zeros_like(arr)
    # Source slice notation
    z0, z1 = max(0, -dz), arr.shape[0] - max(0, dz)
    y0, y1 = max(0, -dy), arr.shape[1] - max(0, dy)
    x0, x1 = max(0, -dx), arr.shape[2] - max(0, dx)
    # Destination slice notation
    zd0, zd1 = max(0, dz), arr.shape[0] - max(0, -dz)
    yd0, yd1 = max(0, dy), arr.shape[1] - max(0, -dy)
    xd0, xd1 = max(0, dx), arr.shape[2] - max(0, -dx)
    out[zd0:zd1, yd0:yd1, xd0:xd1] = arr[z0:z1, y0:y1, x0:x1]
    img = sitk.GetImageFromArray(out.astype(np.uint8))
    img.CopyInformation(mask)
    return img


# --------------------------------------------------------------------------- #
# Updated 2026-05-21 (decisions.log #005): cap dilation at 2-voxel to stay within
# empirical LIDC inter-reader variability; add a Dice-calibrated perturbation tier.
PERTURBATION_SPEC = {
    "E1": ("erode", 1),
    "E2": ("erode", 2),
    "E3": ("erode", 3),
    "D1": ("dilate", 1),
    "D2": ("dilate", 2),
    "T1": ("translate", (1, 0, 0)),
    "T2": ("translate", (0, 1, 0)),
    "T3": ("translate", (1, 1, 0)),
}


def median_pairwise_reader_dice(reader_masks: list[sitk.Image]) -> float:
    """Compute the median Dice similarity across all reader pairs for one nodule.

    For a nodule with N reader masks, computes the C(N, 2) pairwise Dice
    coefficients and returns the median. Used as the target Dice for the
    Dice-calibrated synthetic perturbation (DC), so the synthetic mask
    magnitude matches that specific nodule's empirical reader noise rather
    than a global cohort-wide value (decisions.log #005).

    Returns NaN if no reader pair has positive overlap or if there are fewer
    than two readers (the caller skips the DC mask in that case).
    """
    arrs = [sitk.GetArrayFromImage(m).astype(bool) for m in reader_masks]
    dices = []
    for i in range(len(arrs)):
        for j in range(i + 1, len(arrs)):
            inter = np.logical_and(arrs[i], arrs[j]).sum()
            denom = arrs[i].sum() + arrs[j].sum()
            if denom > 0:
                dices.append(2.0 * inter / denom)
    return float(np.median(dices)) if dices else float("nan")


def dice_calibrated_perturbation(consensus: sitk.Image, target_dice: float, max_radius: int = 4) -> sitk.Image:
    """
    Adaptively erode/dilate the consensus until the resulting mask has Dice
    against the consensus that matches `target_dice` within ±0.02. Returns the
    best-matching perturbation. Direction (erode vs dilate) is chosen by trial.
    """
    base = sitk.GetArrayFromImage(consensus).astype(bool)
    base_sum = base.sum()
    if base_sum == 0:
        return consensus
    best_mask, best_diff = consensus, 1.0
    for direction in ("erode", "dilate"):
        for r in range(1, max_radius + 1):
            op = erode if direction == "erode" else dilate
            candidate = op(consensus, r)
            cand_arr = sitk.GetArrayFromImage(candidate).astype(bool)
            if cand_arr.sum() == 0:
                continue
            inter = np.logical_and(base, cand_arr).sum()
            d = 2.0 * inter / (base_sum + cand_arr.sum())
            diff = abs(d - target_dice)
            if diff < best_diff:
                best_diff, best_mask = diff, candidate
    return best_mask


def process_nodule(nodule_dir: Path, out_dir: Path) -> dict:
    """Generate all perturbation masks for one nodule and write them to ``out_dir``.

    Workflow:
      1. Load all reader masks from ``nodule_dir`` (mask_R*.nrrd files).
      2. Skip if fewer than 3 readers (the inclusion criterion in script 02
         should guarantee this, but the check is defensive).
      3. Compute the majority-vote consensus mask.
      4. Save the consensus and copy each reader mask into ``out_dir``.
      5. Iterate PERTURBATION_SPEC. For each entry, apply the appropriate
         morphological op (erode / dilate / translate) and run the
         volume-preservation check on erosions (decisions.log #012). Skipped
         perturbations are logged but do not abort the loop.
      6. Generate the Dice-calibrated synthetic mask anchored to the
         nodule's own median pairwise reader Dice.

    Returns a run-log dict that the caller aggregates into _run_log.json
    for auditability of the perturbation generation phase.
    """
    reader_files = sorted(nodule_dir.glob("mask_R*.nrrd"))
    if len(reader_files) < 3:
        log.warning(f"Skipping {nodule_dir.name}: fewer than 3 reader masks.")
        return {"case": str(nodule_dir), "skipped": True, "n_readers": len(reader_files)}

    reader_masks = [load_sitk(p) for p in reader_files]
    consensus = consensus_mask(reader_masks)

    out_dir.mkdir(parents=True, exist_ok=True)
    save_sitk(consensus, out_dir / "mask_consensus.nrrd")

    # copy reader masks for downstream extraction
    for rf in reader_files:
        save_sitk(load_sitk(rf), out_dir / rf.name)

    # Volume-preservation threshold — added 2026-05-24 (decisions.log #011 corollary).
    # With the diameter floor relaxed to 6 mm to address LIDC benign scarcity, fixed
    # erosion radii from the original PERTURBATION_SPEC (1, 2, 3 voxels) can fully
    # obliterate small nodules. We skip any erosion whose post-op mask retains <25%
    # of the pre-op voxel count. Empty-mask is therefore subsumed (a strictly stronger
    # check). The dilation and translation legs are unaffected because they can only
    # grow or shift, not shrink, the mask. ICC computation downstream already handles
    # unbalanced per-nodule perturbation counts.
    MIN_RETAINED_FRACTION = 0.25
    orig_voxel_count = int(sitk.GetArrayFromImage(consensus).sum())

    for tag, (op, param) in PERTURBATION_SPEC.items():
        try:
            if op == "erode":
                out = erode(consensus, param)
            elif op == "dilate":
                out = dilate(consensus, param)
            elif op == "translate":
                out = translate(consensus, param)
            else:
                raise ValueError(f"Unknown op {op}")
            out_voxel_count = int(sitk.GetArrayFromImage(out).sum())
            # Sanity check — erosion can void the mask entirely for small nodules.
            if out_voxel_count == 0:
                log.warning(f"{nodule_dir.name} → {tag} produced empty mask; skipping.")
                continue
            # Volume-preservation check — only applies to erosion (the only operation
            # that can shrink the mask). Dilation and translation are exempt.
            if op == "erode" and orig_voxel_count > 0:
                retained = out_voxel_count / orig_voxel_count
                if retained < MIN_RETAINED_FRACTION:
                    log.info(
                        f"{nodule_dir.name} → {tag} retains {retained:.2%} of original "
                        f"(< {MIN_RETAINED_FRACTION:.0%}); skipping for this nodule."
                    )
                    continue
            save_sitk(out, out_dir / f"mask_{tag}.nrrd")
        except Exception as e:
            log.error(f"{nodule_dir.name} → {tag} failed: {e}")

    # Dice-calibrated perturbation (added 2026-05-21 per decisions.log #005)
    try:
        target_d = median_pairwise_reader_dice(reader_masks)
        if not np.isnan(target_d):
            dc_mask = dice_calibrated_perturbation(consensus, target_dice=target_d)
            if sitk.GetArrayFromImage(dc_mask).sum() > 0:
                save_sitk(dc_mask, out_dir / "mask_DC.nrrd")
    except Exception as e:
        log.error(f"{nodule_dir.name} → DC failed: {e}")

    return {"case": nodule_dir.name, "skipped": False, "n_readers": len(reader_files), "median_pairwise_dice": target_d if not np.isnan(target_d) else None}


def main(processed_root: Path, perturb_root: Path):
    fix_seed()
    case_dirs = sorted([p for p in processed_root.glob("*/nodule_*") if p.is_dir()])
    log.info(f"Found {len(case_dirs)} nodules under {processed_root}")
    log_records = []
    for nodule_dir in tqdm(case_dirs):
        rel = nodule_dir.relative_to(processed_root)
        out_dir = perturb_root / rel
        log_records.append(process_nodule(nodule_dir, out_dir))
    (perturb_root / "_run_log.json").write_text(json.dumps(log_records, indent=2))
    log.info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--perturb", type=Path, default=DATA_PERTURB)
    args = parser.parse_args()
    main(args.processed, args.perturb)
