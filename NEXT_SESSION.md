# NEXT_SESSION.md — Pickup guide for the next conversation

This file is the deliberate compaction-survival point. Read this first when starting a new session on Paper 2; everything else in the project state is either pointed to from here or is canonical truth in `decisions.log` / `overleaf_project/OSF_PREREGISTRATION.md`.

## Where the project is, in one paragraph

The Paper 2 manuscript ("Segmentation-perturbation propagation in pretrained foundation-model embeddings versus IBSI-aligned radiomics for lung-nodule malignancy classification on the LIDC-IDRI cohort") is **submission-ready except for the manuscript narrative reorientation pass**. The OSF Registration is archived (https://osf.io/9kt3c, DOI 10.17605/OSF.IO/9KT3C, immutable). The GitHub repository (https://github.com/Iranchamika/paper2-segperturb-fm-radiomics) is public, on commit `e2c345b` or later, 9+ commits, all green. The bibliography is fully verified against authoritative sources with the per-entry provenance in `overleaf_project/references_provenance.log`. The RadImageNet pipeline integration is complete after a state-dict load bug was caught by audit and corrected (decisions.log #025). All four pipeline-output artefacts (icc_table.csv, downstream_metrics.csv, downstream_metrics_by_stratum.csv, fm_embeddings_radimagenet.parquet) carry the corrected RadImageNet column.

## The single open work item

**Task #50 — Manuscript narrative reorientation to the four-paradigm finding.** Estimated 4-6 hours of focused writing work, best done in a single sitting. All required input numbers are already in `results/*.csv`, in `decisions.log` #025, and in the memory file `paper2_radimagenet_finding.md`. No further analysis is required.

## Authoritative truth — read these before writing

1. `decisions.log` entry **#025** (2026-05-26) — the canonical record of the Plan A execution, the silent state-dict no-load bug, the audit that caught it, the fix, and the corrected headline numbers.
2. `decisions.log` entry **#024** (2026-05-26) — the references.bib verification pass plus the OSF "Other context" Pai DOI corrigendum. Codifies the verification protocol that caught both integrity issues this day.
3. `overleaf_project/OSF_PREREGISTRATION.md` Section P amendments **7 and 8** — Plan A executed and RadImageNet correction.
4. `overleaf_project/references_provenance.log` — every BibTeX entry's authoritative source URL with date verified.
5. Memory file `paper2_radimagenet_finding.md` (in the persistent memory directory, indexed from `MEMORY.md`) — the corrected headline numbers with CI bounds and within-stratum disposition.

## Corrected headline numbers — copy directly into manuscript text

ICC stratum distribution (counts, n features per paradigm):

| Paradigm     | excellent (≥ 0.90) | good [0.75, 0.90) | moderate [0.50, 0.75) | poor (< 0.50) | NA | % stable (≥ 0.75) | n total |
|--------------|--------------------|--------------------|------------------------|---------------|----|--------------------|---------|
| biomedclip   | 1                  | 462                | 49                     | 0             | 0  | 90.4               | 512     |
| radiomics-2d | 69                 | 24                 | 8                      | 1             | 0  | 91.2               | 102     |
| radiomics-3d | 67                 | 34                 | 5                      | 1             | 0  | 94.4               | 107     |
| radimagenet  | 647                | 892                | 410                    | 98            | 1  | 75.1               | 2 048   |

Downstream AUC on pooled out-of-fold predictions (5-fold patient-grouped stratified CV):

| Paradigm     | AUC (all features) | AUC (best ICC threshold) | ΔAUC under filtering |
|--------------|--------------------|--------------------------|----------------------|
| radiomics-3d | ~0.95              | ~0.95                    | ~0                   |
| radiomics-2d | ~0.95              | ~0.95                    | ~0                   |
| biomedclip   | 0.898              | 0.912 (icc ≥ 0.85)       | +0.014               |
| radimagenet  | 0.794              | 0.817 (icc ≥ 0.90)       | +0.023               |

RadImageNet within-stratum AUC with 95 percent bootstrap CI:

| Stratum       | n total | n malignant | AUC   | 95% CI            | Disposition                                                        |
|---------------|---------|-------------|-------|-------------------|---------------------------------------------------------------------|
| 6-10 mm       | 134     | 8 (6 %)     | 0.438 | [0.254, 0.619]    | CI spans 0.5; class-imbalance-limited, not significantly different from chance |
| 10-20 mm      | 99      | 73 (74 %)   | 0.677 | [0.565, 0.793]    | Significantly above chance; the only stratum with measurable discrimination |
| > 20 mm       | 77      | 74 (96 %)   | NaN   | —                 | Insufficient class balance (3 benign); AUC undefined                |

H1 (one-sided z-test of FM more stable than radiomics) under Bonferroni alpha 0.05 / 4 = 0.0125 across four paradigm-pair contrasts:

- BiomedCLIP vs Radiomics-2D: Δ = -0.8 pp, rejected
- BiomedCLIP vs Radiomics-3D: Δ = -4.0 pp, rejected
- RadImageNet vs Radiomics-2D: Δ = -16.1 pp, rejected
- RadImageNet vs Radiomics-3D: Δ = -19.3 pp, rejected

H1 is uniformly rejected. Neither FM is more stable than radiomics.

## The new manuscript thesis (single sentence)

"Across two foundation models (BiomedCLIP, RadImageNet ResNet50) and two IBSI-aligned PyRadiomics variants on 310 LIDC-IDRI lung nodules, neither foundation model achieved the perturbation stability of handcrafted radiomic features, but both foundation models showed a consistent +1.4 to +2.3 percentage-point AUC lift under intraclass-correlation-coefficient (ICC) filtering, while radiomics showed no meaningful change under the same filter; the aggregate AUC ranking across paradigms is driven by the structural correlation between nodule diameter and malignancy that the size-stratified analysis exposes, and we additionally document a silent state-dict load-failure mode in a community-distributed FM port that, if undetected, would have produced an apparently publishable but artefactual result."

## Sections to edit, in writing order

The recommended order is bottom-up (smaller sections first, then the abstract last so it can summarise the locked text):

1. **`overleaf_project/methods.tex` §2.4** — un-qualify the RadImageNet paradigm from "contingent on weight access" to a confirmatory third FM arm. Add citation `\cite{mei2022radimagenet}`. ~15 min.
2. **`overleaf_project/results.tex` §3.1** — replace the three-row reliability table with the four-row version from this file. ~30 min.
3. **`overleaf_project/results.tex` §3.3** — extend the K-S distribution-shape comparison from two paradigm-pairs to six (including the highly significant BiomedCLIP versus RadImageNet contrast). ~30 min.
4. **`overleaf_project/results.tex` §3.4** — extend the AUC-degradation table to four paradigms with the +1.4 / +2.3 pp filtering lifts. ~30 min.
5. **`overleaf_project/results.tex` §3.5** — replace the stratified-AUC paragraph with the corrected per-paradigm-per-stratum text using the dispositions in the table above (6-10 mm class-imbalance-limited; 10-20 mm meaningfully discriminative; >20 mm undefined). ~30 min.
6. **`overleaf_project/discussion.tex` §4.2** — reframe the FM-versus-radiomics comparison to four paradigms; emphasise that neither FM beats radiomics on either axis, and the consistent ICC-filter lift for both FMs is the actionable observation. ~45 min.
7. **`overleaf_project/discussion.tex` §4.5** — drop the single-FM limitation paragraph; replace with a "two FMs is still a small slice of the contemporary FM landscape" framing. ~15 min.
8. **`overleaf_project/discussion.tex` §4.6 (NEW)** — write the validation-procedure subsection. Content: silent `load_state_dict(strict=False)` failure mode is a community-wide issue for FM weight ports with non-standard key conventions; the dual structural-and-functional validation procedure (strict=True load with explicit key normalisation; magnitude-floor assertion plus cosine-separability check) catches such bugs pre-emptively. Cite the Nature 2026 arXiv-ban article (`\cite{singh2026arxiv}` — needs adding to references.bib if used). ~60 min.
9. **`overleaf_project/conclusions.tex`** — narrow the conclusion to the four-paradigm hierarchy plus the methodological contribution. ~15 min.
10. **`overleaf_project/introduction.tex`** paragraphs 2-3 — add RadImageNet alongside BiomedCLIP in the FM enumeration; sharpen the Pai 2024 hook because the present study extends and complicates Pai's multi-FM stability finding. ~30 min.
11. **`overleaf_project/abstract.tex`** — full rewrite to the four-paradigm framing per the single-sentence thesis above. 350 word budget. ~60 min.

## Small clean-up items not on the critical path

- **Verify fig4 regenerated correctly.** The agent flagged that `figures/fig4_stratified_auc.png` may not have been regenerated. Open it in a viewer; if it shows three paradigms instead of four, re-run `python 08_make_figures.py` and commit.
- **`overleaf_project/figures/` sync.** Script 08 writes to `figures/` but the manuscript LaTeX expects `overleaf_project/figures/`. One-line fix: add `\graphicspath{{figures/}{overleaf_project/figures/}}` to `main.tex` preamble.
- **Rename misleading function `to_central_axial_slice` in `04_extract_radiomics.py`** to `to_max_area_axial_slice` (the function actually selects max-area, not centroid — name is a vestige from the pre-harmonization version per decisions.log #017). ~5 min, no feature-value change expected.
- **Revoke any temporary GitHub Personal Access Token used during the initial 2026-05-26 repository push.** GitHub Credential Manager has cached fresh credentials, so subsequent pushes work silently and the temporary token is no longer needed. Token-revocation page: https://github.com/settings/tokens.
- **Cover letter DOI insertion** per the updated OSF_FILL_GUIDE.md step 8 — add `10.17605/OSF.IO/9KT3C` to the "Pre-registration and data availability" paragraph in `overleaf_project/COVER_LETTER.md`.

## Standing protocol going forward (binding for any future BibTeX or FM-loader change)

From decisions.log #024:
- All future BibTeX edits must source every field from an authoritative endpoint and append to `overleaf_project/references_provenance.log`.
- No DOI digit string may be generated from assistant memory at any step, including in narrative paragraphs intended for permanent archival contexts.
- If a citation cannot be verified against an authoritative endpoint, it is marked UNVERIFIED and held out of the deliverable pending user input.

From decisions.log #025:
- Any future loader for a community-distributed FM checkpoint must use `strict=True` after explicit key normalisation. `strict=False` is reserved for cases where a small, named, documented subset of keys is expected to be absent (typically a classification head being replaced with `Identity`). The "tolerant load" pattern with no key inspection is now a banned default in this project.

## How to validate this file is current

This file is current if and only if all of the following are true (check at the start of every new session):

1. The latest commit on `main` is `e2c345b` or later. Run `git log -1 --oneline`.
2. `decisions.log` ends with entry #025 plus the line `*Next entry will be #026.*`.
3. `overleaf_project/OSF_PREREGISTRATION.md` Section P contains amendments 7 and 8.
4. The memory file `paper2_radimagenet_finding.md` (indexed in `MEMORY.md`) records the corrected RadImageNet numbers with CI bounds.
5. `git status` shows a clean working tree.

If any of these are not true, this file may have drifted. Reconstruct from `decisions.log` (canonical truth) and update this file before doing any new work.
