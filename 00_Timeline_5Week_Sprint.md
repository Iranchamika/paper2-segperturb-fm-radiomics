# 5-Week Sprint Timeline — Paper 2 (Segmentation-Perturbation Propagation)

**Owner:** Iran (independent researcher)
**Target submission:** *Medical Physics* (AAPM, Q1, IF ~3.8)
**Today's date:** 2026-05-21
**Hard submission target:** 2026-06-25 (Thursday, week 5)
**Constraint:** Laptop CPU only, solo author

---

## Week-by-week deliverables

| Week | Dates | Track A (Compute) | Track B (Writing) | End-of-week deliverable |
|------|-------|--------------------|---------------------|--------------------------|
| 1 | 2026-05-21 → 2026-05-27 | Environment setup; TCIA access for LIDC-IDRI; download **N≥400** nodule subset; verify 4-reader masks; PyRadiomics dry run on 5 nodules; read Pai 2025 end-to-end | Lock protocol v1.1 (post-verification amendments applied); draft Introduction (650 wds, with explicit Pai 2025 differentiation) | `01_Protocol.md` v1.1 locked, `nodules_v1.csv` (N≥400), Methods §2.1-2.3 drafted |
| 2 | 2026-05-28 → 2026-06-03 | Generate perturbations (4 reader + 7 synthetic + 1 Dice-calibrated); full PyRadiomics extraction in **both 3D and 2D arms** × ≥400 nodules; intermediate ICC(2,1) pass | Draft Methods (1600 wds, including dual-radiomics-arm justification); start Results outline | `radiomics_features_3d.parquet`, `radiomics_features_2d.parquet`, Methods complete |
| 3 | 2026-06-04 → 2026-06-10 | FM embedding extraction: BiomedCLIP, RadImageNet-ResNet50; optional MedSAM on 50-nodule sub-sample | Draft Results §3.1-3.3 (1100 wds); generate Figures 1-3 | `fm_embeddings_*.parquet`, Figures 1-3 |
| 4 | 2026-06-11 → 2026-06-17 | **Nested-CV** downstream classifier (no full-set leakage); pre-vs-post-filter AUC/Brier/ECE; sensitivity analyses (subgroup by nodule size, by reader Dice; supplementary ICC(3,1) and τ∈{0.50,0.85,0.90}); selection-stability Jaccard | Draft Discussion + Limitations (1600 wds; new sub-section on stability-informativeness decoupling); polish Figures; Abstract | Manuscript v0.9 complete |
| 5 | 2026-06-18 → 2026-06-24 | Code freeze; reproducibility check on fresh clone; upload to private GitHub; OSF pre-registration deposit (must precede results in the manuscript) | Self-critique vs CLAIM + RQS + TRIPOD+AI; Medical Physics formatting; cover letter; supplementary | **Manuscript submitted 2026-06-25** |

---

## Daily compute budget (worst case)

| Step | Per-unit time (CPU) | Units | Total |
|------|----------------------|--------|--------|
| LIDC-IDRI download | n/a | 200 cases | ~2 hours (network) |
| PyRadiomics 3D extraction | ~5 sec/mask | 400 × 12 perturbations = 4 800 | ~6.7 hours |
| PyRadiomics 2D extraction | ~2 sec/mask | 4 800 | ~2.7 hours |
| BiomedCLIP encoding | ~2 sec/slice | 4 800 | ~2.7 hours |
| RadImageNet-ResNet50 | ~1 sec/slice | 4 800 | ~1.4 hours |
| MedSAM image-encoder (optional, 50-nodule subset) | ~25 sec/slice | 600 | ~4.2 hours |
| ICC computation | ~instant | n/a | ~5 min |
| Downstream classifier | ~30 sec | 100 bootstraps × 4 configs | ~30 min |
| Nested-CV classifier | ~10 min per config | 4 paradigms × 5 thresholds = 20 | ~3.3 hours |
| **Total compute** | — | — | **~21 hours over 4 weeks** ≈ 1 hour/day average (well within laptop budget). |

---

## Decision gates

- **End of Week 1:** if LIDC-IDRI download fails or DUA delay >5 days → pivot to NSCLC-Radiomics (Aerts 2014) + synthetic perturbations only (no multi-reader). Decision recorded in `decisions.log`.
- **End of Week 2:** if PyRadiomics ICC distribution looks degenerate (all features ICC>0.95 or all <0.50) → widen perturbation magnitudes. Re-run within 2 days.
- **End of Week 3:** if BiomedCLIP embedding ICC is near-identical to PyRadiomics ICC (no story) → escalate analysis to per-dimension cluster-level ICC and downstream task degradation. The headline becomes the downstream-impact divergence, not the raw ICC contrast.
- **End of Week 4:** internal reviewer pass (own self-critique against CLAIM 42-item + RQS 16-item). Anything failing >2 items gets a remediation sprint on day 30-31.

---

## Risk register (Paper-2 specific)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LIDC-IDRI download blocked (TCIA outage) | Low | High | Pre-cache subset on Week 1 day 1; backup dataset = NSCLC-Radiomics |
| BiomedCLIP HuggingFace weights moved/deleted | Low | High | Pin to exact commit hash; mirror to local in Week 1 |
| MedSAM CPU inference too slow | Medium | Low | Drop MedSAM from primary analysis; relegate to supplementary |
| Reviewer flags ICC threshold (0.75) as arbitrary | High | Medium | Pre-specify a sensitivity analysis at 0.50, 0.75, 0.90 and report all three |
| Reviewer flags Hanley-McNeil approximation for AUC SE | Medium | Low | Use stratified bootstrap (1000 reps) for AUC CIs, not Hanley-McNeil |
| Reviewer asks for external dataset | High | Medium | Pre-register a secondary external sanity check on NSCLC-Radiomics (smaller N, 1 reader) for revision response |
| Medical Physics page-limit overshoot | Medium | Low | Hard cap at 6 500 wds main body + 4 figures + 2 tables; supplementary unrestricted |

---

*End of timeline v1.0. Update after Week 1 wrap.*
