"""
05_extract_fm_embeddings.py — foundation-model embedding extraction (one FM per run).

Sixth script in the pipeline. Forward-passes each perturbation mask's
max-area axial slice through one foundation-model (FM) image encoder and
writes the resulting dense embedding vectors to a per-FM parquet file.

Supports two FM paradigms (one per run, selected via ``--fm``):

  - ``biomedclip``: ``microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224``
    via the open_clip library, 512-dim embedding (the multimodal projection
    layer, not the raw 768-dim ViT-B/16 bottleneck — confirmed against the
    HuggingFace config.json in our fact-check round per the conversation
    transcript). Pretrained on 15 million biomedical image-text pairs (PMC-15M).
  - ``radimagenet``: ResNet50 with the RadImageNet-pretrained state_dict
    loaded into a torchvision ResNet50 chassis (fc layer replaced with
    Identity, so the output is the 2048-dim global-average-pooled feature
    map). RadImageNet weights are gated behind a Google Form and may not
    be available; per decisions.log #018 the script raises a clear error
    pointing to the manual-download instructions in script 00.

The slice-selection rule (``slice_from_mask``) uses the SAME max-area axial
slice as the 2D PyRadiomics arm in script 04 per decisions.log #017. This
harmonisation was added after we realised that the original ``central_axial_slice``
helper picked the slice through the mask centroid, which can differ from the
max-area slice for irregular nodules and would have introduced a
slice-selection confound into every FM-vs-radiomics comparison.

CPU-only inference by default (``DEVICE = "cpu"``). The protocol commits to
CPU-only per decisions.log #002 because (a) the manuscript is targeting a
methodology audience that should be able to reproduce on a laptop, and
(b) BiomedCLIP CPU inference is fast enough at ~2 sec/slice that the full
4 000-extraction run completes in ~13 min anyway.

Outputs:
    results/fm_embeddings_biomedclip.parquet   (--fm biomedclip, 512-dim)
    results/fm_embeddings_radimagenet.parquet  (--fm radimagenet, 2048-dim)

Each row carries the key columns (case_id, nodule_id, perturbation, fm)
plus one column per embedding dimension named ``d0000``..``d0511``
(BiomedCLIP) or ``d0000``..``d2047`` (RadImageNet).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk
import torch
from PIL import Image
from tqdm import tqdm

from utils import (
    DATA_PERTURB,
    DATA_PROCESSED,
    MODELS,
    RESULTS,
    crop_to_bbox_2d,
    fix_seed,
    get_logger,
    hu_window_to_uint8,
    load_sitk,
    max_area_axial_slice,
    max_area_axial_mask_slice,
    max_area_axial_slice_index,
)

log = get_logger("05_fm_embeddings")
DEVICE = "cpu"


# --------------------------------------------------------------------------- #
def load_biomedclip():
    """Load BiomedCLIP from the HuggingFace cache populated by script 00.

    Returns the image encoder (.encode_image-callable) and the open_clip
    preprocessing transform that takes a PIL.Image and returns a
    1x3x224x224 normalised tensor. The model is moved to ``DEVICE`` (CPU
    per the protocol) and put in eval mode before return.

    The ``hf-hub:`` prefix tells open_clip to use the HuggingFace hub
    cache rather than its own model registry. Script 00 must have run at
    least once on this machine, or the call will attempt a network fetch
    and fail in an offline environment.
    """
    import open_clip

    model, _, preprocess = open_clip.create_model_and_transforms(
        "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224"
    )
    model.eval().to(DEVICE)
    return model, preprocess


def biomedclip_embed(model, preprocess, pil_image: Image.Image) -> np.ndarray:
    """Forward-pass one PIL image through BiomedCLIP and return the L2-normalised embedding.

    The L2 normalisation is applied here rather than downstream because
    (a) BiomedCLIP was trained with contrastive loss on L2-normalised
    embeddings, so cosine similarity in the trained metric requires
    L2 normalisation, and (b) normalising once at extraction means
    downstream code (script 06 ICC, script 07 classifier) never has to
    worry about whether the embeddings are pre-normalised or not.
    """
    img = preprocess(pil_image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feats = model.encode_image(img)
        # L2-normalise — see docstring rationale
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.squeeze(0).cpu().numpy().astype(np.float32)


# --------------------------------------------------------------------------- #
def load_radimagenet():
    """Load RadImageNet-pretrained ResNet50 from the manual weight download.

    Per decisions.log #018, RadImageNet weights are gated behind a Google
    Form and may not be available within the study timeframe; this function
    raises a clear FileNotFoundError pointing at the local target path so
    a user re-running the pipeline knows immediately what is missing rather
    than triggering an opaque downstream crash.

    The torchvision ResNet50 chassis is constructed with ``weights=None``
    (no ImageNet initialisation) and the fc head replaced with
    ``torch.nn.Identity`` so the forward pass outputs the 2048-dim
    global-average-pooled feature map rather than 1000 ImageNet logits.
    The RadImageNet state_dict is loaded with ``strict=False`` because
    the published checkpoint legitimately omits the fc-layer weights
    (RadImageNet was trained with a custom multi-modal head we do not need).

    The transform chain matches RadImageNet's published preprocessing:
    grayscale->3ch replication so a CT slice can pass through a ResNet
    that expects RGB; ImageNet mean/std normalisation as RadImageNet
    used during transfer learning.
    """
    from torchvision import models, transforms

    weights_path = MODELS / "radimagenet" / "RadImageNet-ResNet50_notop.pt"
    if not weights_path.exists():
        raise FileNotFoundError(
            f"Place RadImageNet ResNet50 weights at {weights_path} (see 02_Environment_Setup.md)"
        )
    state = torch.load(weights_path, map_location=DEVICE)
    # The RadImageNet PyTorch port stores weights in nn.Sequential indexing
    # (backbone.0.* through backbone.7.*). Rename to torchvision named-attribute
    # form before load to avoid the silent-no-load bug that strict=False would mask.
    rename_map = {
        "backbone.0.": "conv1.",
        "backbone.1.": "bn1.",
        # backbone.2 = ReLU (stateless), backbone.3 = MaxPool (stateless), skipped
        "backbone.4.": "layer1.",
        "backbone.5.": "layer2.",
        "backbone.6.": "layer3.",
        "backbone.7.": "layer4.",
    }
    renamed = {}
    for k, v in state.items():
        for prefix, replacement in rename_map.items():
            if k.startswith(prefix):
                renamed[replacement + k[len(prefix):]] = v
                break
        else:
            # Drop any keys that do not match an expected prefix (avgpool, fc, etc.)
            # rather than silently passing them to load_state_dict
            log.warning(f"Dropping unmapped state-dict key: {k}")

    model = models.resnet50(weights=None)
    model.fc = torch.nn.Identity()
    # Drop fc.weight/fc.bias from renamed if present, since we replaced fc with Identity
    renamed = {k: v for k, v in renamed.items() if not k.startswith("fc.")}

    # strict=True forces structural verification; the load fails loudly if any
    # parameter is still misaligned. The Identity replacement of fc means we
    # never expect fc.* in the loaded dict.
    model.load_state_dict(renamed, strict=True)
    log.info(f"State-dict load OK (strict=True). Total params loaded: {len(renamed)}")

    # Sanity check that we actually loaded trained weights, not random init.
    # Random Kaiming init produces conv1.abs().mean() ≈ 0.02 (fan_in=147 for 7x7x3->64);
    # any sanely-trained ResNet conv1 magnitude is at least ~0.05. We use a single
    # lower-bound assertion. The "layer4 << conv1" pattern holds for ImageNet-trained
    # ResNets (weight decay shrinks deep layers) but NOT for RadImageNet's PyTorch port,
    # which has flat per-layer magnitudes around 0.25 across all depths — likely an
    # artefact of Keras→PyTorch conversion absorbing BN scale into conv weights.
    # We log the depth profile so anomalous loads are visible but don't gate on it.
    conv1_mag = model.conv1.weight.abs().mean().item()
    layer4_mag = model.layer4[0].conv1.weight.abs().mean().item()
    log.info(
        f"Sanity: conv1.weight.abs().mean()={conv1_mag:.4g}, "
        f"layer4.0.conv1.weight.abs().mean()={layer4_mag:.4g} "
        f"(ratio={layer4_mag/conv1_mag:.2f})"
    )
    assert conv1_mag > 0.05, f"conv1 magnitude {conv1_mag} looks like random init (<0.05)"

    model.eval().to(DEVICE)
    tfm = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return model, tfm


def radimagenet_embed(model, tfm, pil_image: Image.Image) -> np.ndarray:
    x = tfm(pil_image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feats = model(x)
    return feats.squeeze(0).cpu().numpy().astype(np.float32)


# --------------------------------------------------------------------------- #
def slice_from_mask(img: sitk.Image, mask: sitk.Image) -> np.ndarray:
    """Select the max-area axial slice (decisions.log #017 — harmonized with
    the 2D PyRadiomics arm in `04_extract_radiomics.py`).

    Both the image slice and the mask slice are extracted at the SAME z-index
    — the index of the axial slice with the largest mask area. This guarantees
    that the FM embedding and the 2D radiomics features are computed from the
    same 2D input, eliminating the "different slice for different paradigm"
    confound that would otherwise contaminate the FM-vs-radiomics comparison.
    """
    z = max_area_axial_slice_index(mask)
    img_slice = sitk.GetArrayFromImage(img)[z]
    mask_slice = sitk.GetArrayFromImage(mask)[z]
    img_u8 = hu_window_to_uint8(img_slice)
    cropped = crop_to_bbox_2d(img_u8, mask_slice, pad_frac=0.5)
    return cropped


def to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr).convert("RGB")


# --------------------------------------------------------------------------- #
def main(fm_name: str, processed_root: Path, perturb_root: Path, out_path: Path):
    """Walk the perturbation tree, forward-pass each slice through the chosen FM, write parquet.

    Like script 04, this main loop iterates the on-disk perturbation
    directory tree rather than filtering by ``labels.csv``. Per decisions.log
    #016 the labels filter is applied downstream in script 07 so the
    feature extraction can be reused across multiple cohort definitions
    (balanced 310, unbalanced 353, strict-10mm 129).

    Per-extraction errors are logged and skipped, matching the error-handling
    pattern in scripts 01 and 04 — a single bad slice should never abort a
    multi-hour run.
    """
    fix_seed()
    if fm_name == "biomedclip":
        model, preprocess = load_biomedclip()
        embed_fn = lambda pil: biomedclip_embed(model, preprocess, pil)
        emb_dim = 512
    elif fm_name == "radimagenet":
        model, tfm = load_radimagenet()
        embed_fn = lambda pil: radimagenet_embed(model, tfm, pil)
        emb_dim = 2048
    else:
        raise ValueError(f"Unknown FM: {fm_name}")

    log.info(f"Loaded {fm_name} ({emb_dim}-dim embeddings).")

    case_dirs = sorted([p for p in perturb_root.glob("*/nodule_*") if p.is_dir()])
    rows = []
    for nodule_dir_perturb in tqdm(case_dirs):
        rel = nodule_dir_perturb.relative_to(perturb_root)
        case_id, nodule_id = rel.parts[0], rel.parts[1]
        img_path = processed_root / rel / "img.nrrd"
        if not img_path.exists():
            continue
        img = load_sitk(img_path)
        for mask_path in sorted(nodule_dir_perturb.glob("mask_*.nrrd")):
            tag = mask_path.stem.replace("mask_", "")
            try:
                mask = load_sitk(mask_path)
                arr = slice_from_mask(img, mask)
                pil = to_pil(arr)
                vec = embed_fn(pil)
                row = {"case_id": case_id, "nodule_id": nodule_id, "perturbation": tag, "fm": fm_name}
                for i, v in enumerate(vec):
                    row[f"d{i:04d}"] = float(v)
                rows.append(row)
            except Exception as e:
                log.error(f"{case_id}/{nodule_id}/{tag} {fm_name} failed: {e}")

    df = pd.DataFrame(rows)
    out_path = out_path.with_name(f"{out_path.stem}_{fm_name}.parquet")
    df.to_parquet(out_path, index=False)
    log.info(f"Wrote {len(df)} rows × {emb_dim} dims → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fm", choices=["biomedclip", "radimagenet"], required=True)
    parser.add_argument("--processed", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--perturb", type=Path, default=DATA_PERTURB)
    parser.add_argument("--out", type=Path, default=RESULTS / "fm_embeddings.parquet")
    args = parser.parse_args()
    main(args.fm, args.processed, args.perturb, args.out)
