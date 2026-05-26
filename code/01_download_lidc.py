"""
01_download_lidc.py — LIDC-IDRI bulk DICOM download via the TCIA NBIA REST API.

Second script in the pipeline. Downloads a configurable subset of LIDC-IDRI
patient series (default n=100; we ran n=200 then a second n=400 to reach the
final 600-patient pool per decisions.log #014). DICOMs are persisted under
``data/raw/LIDC-IDRI-XXXX/<series-uid>/series.zip``; pylidc in script 02
expects this exact layout.

Two non-obvious behaviours, both forced by live-debugging during Week 1:

  1. ``NBIA_BASE`` points at the v1 endpoint (``/nbia-api/services/v1/``),
     NOT the v4 endpoint our original code used. TCIA deprecated v4 in
     May 2026 and the old endpoint now hangs indefinitely; v1 returns the
     LIDC-IDRI manifest (15 116 series, 1 010 patients) in ~18 s.
     Decision provenance: decisions.log #010.

  2. ``download_series`` has both a per-chunk timeout (60 s, the requests
     default for ``stream=True``) AND an absolute wall-clock deadline
     (``max_wallclock_s=300``). Without the wall-clock check, a single
     wedged TCIA series can drip bytes at <1 kB/s and hold the connection
     open for hours. We lost ~12 h on one such wedge during the first run
     before the patch landed. On abort, the partial zip is removed so
     re-running actually retries instead of treating the half-write as
     complete. Decision provenance: decisions.log #010 (Known limitation
     paragraph).

References:
    Armato SG et al. (2011). The Lung Image Database Consortium (LIDC) and
        Image Database Resource Initiative (IDRI): a completed reference
        database of lung nodules on CT scans. Medical Physics 38(2):915-931.
    Clark K et al. (2013). The Cancer Imaging Archive (TCIA): maintaining
        and operating a public information repository. J Digit Imaging
        26(6):1045-1057.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

import requests
from tqdm import tqdm

from utils import DATA_RAW, get_logger

log = get_logger("01_download")

NBIA_BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1"  # v4 endpoint deprecated 2026-05; v1 returns the LIDC-IDRI manifest in ~18s
COLLECTION = "LIDC-IDRI"


def list_series(collection: str = COLLECTION) -> list[dict]:
    """Fetch the full series manifest for a TCIA collection.

    Returns a list of dicts with keys including ``PatientID``,
    ``SeriesInstanceUID``, ``Modality`` (we filter to ``CT`` in ``main``),
    and ``ImageCount``. For LIDC-IDRI this returns ~15 000 series across
    ~1 010 patients in ~18 seconds on the v1 endpoint.

    The ``timeout=300`` is per-chunk read; the manifest is small enough
    (~13 MB JSON for LIDC-IDRI) that a per-chunk timeout is sufficient
    here. The wall-clock deadline pattern is only needed for the bulk
    image download in ``download_series``.
    """
    url = f"{NBIA_BASE}/getSeries"
    r = requests.get(url, params={"Collection": collection}, timeout=300)
    r.raise_for_status()
    return r.json()


def download_series(series_uid: str, out_dir: Path, max_wallclock_s: int = 300) -> None:
    """Download one series with a hard wall-clock deadline.

    `timeout=60` is per-chunk; on a wedged connection that drips bytes slowly,
    that alone can leave the request running for hours (we lost ~12h on a single
    wedged series on 2026-05-23). The outer `max_wallclock_s` deadline ensures
    we abort a stalled series. On abort, the partial zip is removed so the next
    run actually retries instead of treating the half-written file as complete.
    """
    url = f"{NBIA_BASE}/getImage"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "series.zip"
    if zip_path.exists() and zip_path.stat().st_size > 1024:
        log.info(f"Already have {zip_path}; skipping.")
        return
    deadline = time.time() + max_wallclock_s
    try:
        with requests.get(url, params={"SeriesInstanceUID": series_uid}, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if time.time() > deadline:
                        raise TimeoutError(f"series wall-clock exceeded {max_wallclock_s}s")
                    f.write(chunk)
    except Exception:
        if zip_path.exists():
            zip_path.unlink()
        raise


def main(n_cases: int, out_root: Path):
    """Download up to ``n_cases`` LIDC-IDRI patient series.

    Workflow:
      1. Fetch the full series manifest via ``list_series`` (~18 s).
      2. Bucket the manifest by ``PatientID`` (the LIDC-IDRI patient ID,
         e.g. ``LIDC-IDRI-0042``).
      3. Take the first ``n_cases`` patients in sorted order (deterministic
         across runs, which is important for the auditable cohort provenance
         in decisions.log #014).
      4. For each patient, iterate their series and download every CT series
         (skip XR, SR, SEG, RTSTRUCT, etc. — pylidc reads CT only).
      5. Per-series ``download_series`` is resumable: any ``series.zip``
         already on disk with size >1 KB is skipped on re-run.

    Side effects: ~9 GB on disk for n_cases=200, ~52 GB for n_cases=600.
    Persists the full manifest to ``_series_manifest.json`` for auditability.
    """
    log.info(f"Listing LIDC-IDRI series (this may take ~30s)...")
    series = list_series()
    log.info(f"Found {len(series)} series total.")
    by_patient: dict[str, list[dict]] = {}
    for s in series:
        by_patient.setdefault(s["PatientID"], []).append(s)
    patients = sorted(by_patient)[:n_cases]
    log.info(f"Will download CT series for {len(patients)} patients.")
    (out_root / "_series_manifest.json").write_text(json.dumps(series, indent=2))

    for pid in tqdm(patients):
        for s in by_patient[pid]:
            if s.get("Modality") != "CT":
                continue
            out_dir = out_root / pid / s["SeriesInstanceUID"]
            try:
                download_series(s["SeriesInstanceUID"], out_dir)
                time.sleep(0.2)  # be polite to TCIA
            except Exception as e:
                log.error(f"{pid}/{s['SeriesInstanceUID']} failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_cases", type=int, default=100)
    parser.add_argument("--out", type=Path, default=DATA_RAW)
    args = parser.parse_args()
    main(args.n_cases, args.out)
