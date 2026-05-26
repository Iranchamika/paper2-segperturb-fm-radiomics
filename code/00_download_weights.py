"""
00_download_weights.py — cache foundation-model weights for offline reuse.

First script in the pipeline. Run once on a machine that has internet access
to populate the HuggingFace cache for BiomedCLIP (~1.4 GB plus tokenizer
artefacts), so every subsequent extraction run in script 05 is fully offline.
Network reliability matters here because we lost ~6 sec on a TLS handshake
glitch during the live install (decisions.log narrative around HuggingFace
TLS reset, 2026-05-23) and the HuggingFace library does not retry the
metadata HEAD by default.

RadImageNet weights are NOT downloaded by this script because the
RadImageNet team gates access behind a Google Form. This script prints
the access instructions; the user fills the form, waits 1--3 business days
for an email link, downloads ``RadImageNet-ResNet50_notop.pt`` manually,
and places it at ``MODELS / 'radimagenet' /``. See decisions.log #018 for
the Plan A/B/C contingency if RadImageNet access does not arrive in time.

Provenance: BiomedCLIP from Zhang et al. (arXiv:2303.00915, 2024) — the
peer-reviewed-equivalent checkpoint hosted on HuggingFace at
``microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224``. The 768-dim
ViT-B/16 bottleneck is followed by a learnable projection to a 512-dim
multimodal space; we extract the 512-dim projection per the manuscript
Methods §2.4.2.
"""

from __future__ import annotations

from pathlib import Path

from utils import MODELS, get_logger

log = get_logger("00_weights")


def biomedclip():
    """Trigger BiomedCLIP weight download via the open_clip + HuggingFace hub path.

    Calling ``open_clip.create_model_and_transforms`` with the ``hf-hub:`` prefix
    forces the HuggingFace library to download the checkpoint into the user's
    HuggingFace cache (``~/.cache/huggingface/hub/``) rather than into our local
    ``models/biomedclip/`` directory. We still ``mkdir`` the local directory so
    the project tree is consistent. The cached weights are then reused by
    script 05 without network access.

    Side effects: ~1.4 GB write to the HuggingFace cache; brief network use.
    The downloaded model object is immediately discarded with ``del model`` —
    we only need the cache, not the in-memory model.
    """
    import open_clip

    target = MODELS / "biomedclip"
    target.mkdir(parents=True, exist_ok=True)
    log.info("Downloading BiomedCLIP (≈ 1.4 GB) ...")
    model, _, _ = open_clip.create_model_and_transforms(
        "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224"
    )
    log.info("BiomedCLIP cached in HuggingFace hub cache.")
    del model  # release the in-memory weights; we only wanted the cache


def radimagenet_instructions():
    """Print the manual-access instructions for RadImageNet weights.

    RadImageNet (Mei et al., Radiol AI 2022) is the planned second FM
    paradigm per the protocol but its weights are gated behind a Google
    Form request administered by the BMEII-AI team at Mount Sinai. We
    cannot automate the download — the access flow requires a human
    email confirmation step. This function only ensures the target
    directory exists and tells the user what to do.

    Plan-B fallback (decisions.log #018) if access is denied: substitute
    the MedSAM image-encoder (Ma et al., Nat Commun 2024) which is
    openly downloadable from the bowang-lab/MedSAM GitHub.
    """
    target = MODELS / "radimagenet"
    target.mkdir(parents=True, exist_ok=True)
    log.info(
        "RadImageNet weights require manual download:\n"
        "  1. Visit https://github.com/BMEII-AI/RadImageNet\n"
        "  2. Request access via the Google Form linked in the README\n"
        "  3. Download RadImageNet-ResNet50_notop.pt\n"
        f"  4. Place it at {target / 'RadImageNet-ResNet50_notop.pt'}\n"
    )


if __name__ == "__main__":
    biomedclip()
    radimagenet_instructions()
