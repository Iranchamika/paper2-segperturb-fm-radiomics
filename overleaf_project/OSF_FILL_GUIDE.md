# OSF — step-by-step fill guide for osf.io/3f76x

**Project URL:** https://osf.io/3f76x/overview
**Project title (already set, correct):** Segmentation-Perturbation Propagation In Pretrained Foundation-Model Embeddings Versus IBSI-Aligned Radiomics For Lung-Nodule Malignancy Classification On The LIDC-IDRI Cohort.
**Author (already listed, correct):** Wanni Arachchige Iran Chamika Kumarananda

OSF has two distinct object types and we need both:

1. **Project** (what you have now at `/3f76x`) — a working container for files, wiki, metadata, and discussion. NOT a pre-registration on its own.
2. **Registration** — a frozen, timestamped snapshot of the project with a pre-registration form attached. Created FROM the project under the **Registrations** sidebar item. Once created, the registration receives the permanent DOI you cite in the manuscript Methods §2.1.

This guide walks the OSF tabs in the order I would fill them. Parts A-G are Project tabs, Part H is Registrations.

---

## A. Overview tab — Description field

In the right-hand **Metadata** card on the Overview page, click **Edit** next to **Description**. Replace the existing text entirely with the block below (paste into the Description field; OSF accepts ~5 000 characters here, this is ~1 200).

```
Purpose. We tested whether pretrained foundation-model (FM) embeddings are more robust than IBSI-aligned handcrafted radiomic features under controlled perturbation of the upstream segmentation mask, and whether the intraclass-correlation-coefficient (ICC) filter routinely applied in radiomics pipelines remains necessary when FM embeddings are used in place of handcrafted features.

Methods. We selected 310 LIDC-IDRI lung nodules (155 malignant, 155 benign) from 227 patients with a median pairwise inter-reader Dice of 0.789. For every nodule we generated up to 12 perturbation conditions per paradigm: the available reader masks, seven morphological perturbations subject to a 25% volume-preservation guard, and a Dice-calibrated synthetic mask anchored to that nodule's own empirical reader variability. From each perturbation we extracted PyRadiomics features in matched 3D (107 features) and 2D (102 features) configurations and BiomedCLIP embeddings (512 dimensions) from the maximum-area axial slice. ICC(2,1) was computed per feature across the ten universal perturbation conditions. Four pre-registered hypotheses were tested, alongside a pre-specified diameter-stratified subgroup analysis at 6-10 mm, 10-20 mm, and >20 mm.

Results. Both paradigms attained comparable proportions of stable features at ICC >= 0.75 (radiomics-2D 91.2%, radiomics-3D 94.4%, BiomedCLIP 90.4%; pairwise z-tests p > 0.19), so the pre-registered H1 was rejected. The shape of the ICC distributions differed substantially: PyRadiomics is bimodal with 63-68% of features in the excellent stratum (ICC >= 0.90); BiomedCLIP is unimodal with 90% of dimensions in the good band (0.75 <= ICC < 0.90) and no poor (ICC < 0.50) dimensions (Kolmogorov-Smirnov D = 0.68-0.72, p < 1e-39). Downstream malignancy AUC remained stable under ICC filtering for both paradigms (H3 non-inferiority supported at the 0.020 margin), and BiomedCLIP's calibration improved substantially under filtering (Brier 0.144 -> 0.115; ECE 0.129 -> 0.065 at ICC >= 0.85). The aggregate AUC difference (radiomics 0.95 vs BiomedCLIP 0.90) did not persist within size-matched strata.

Conclusions. FM embeddings and IBSI radiomics produce comparably stable feature pools, but the distribution of that stability differs substantially between paradigms. ICC filtering confers no discrimination benefit for either paradigm, yet it improves BiomedCLIP's probability calibration. The aggregate AUC ranking in our cohort was largely a size-class artefact, which we interpret as a methodological caution for the wider FM-versus-radiomics benchmarking literature.

Target journal: Medical Physics (AAPM / Wiley). Independent-researcher submission. All code, pinned environment, extracted feature tables, ICC tables, per-fold out-of-fold predictions, and figure-generation scripts are released at the GitHub repository linked under Add-ons / Linked Services.
```

Hit **Save**. The Overview card on the right should then show the full Purpose / Methods / Results / Conclusions blocks under **Description**.

---

## B. Metadata tab (left sidebar > Metadata)

Click **Metadata** in the left sidebar. Fill these fields:

| Field | Value |
|-------|-------|
| **Resource Type** | `Other` (OSF has no "Methodological article" type; use Other and let the description carry the type detail) |
| **Resource Language** | `English` |
| **License** | `CC-By Attribution 4.0 International` |
| **Tags** (comma-separated) | `radiomics`, `foundation models`, `BiomedCLIP`, `PyRadiomics`, `LIDC-IDRI`, `lung CT`, `intraclass correlation coefficient`, `segmentation variability`, `reproducibility`, `calibration`, `medical physics` |
| **Subjects** (OSF taxonomy) | Open the hierarchical picker and tick whichever of these leaves your OSF build actually exposes (OSF curates the bepress tree and trims some leaves). Recommended set, in priority order:<br>1. `Medicine and Health Sciences` → `Analytical, Diagnostic and Therapeutic Techniques and Equipment` → `Investigative Techniques` (radiomics / quantitative imaging).<br>2. `Medicine and Health Sciences` → `Radiology` (direct match, present in most OSF builds).<br>3. `Physical Sciences and Mathematics` → `Computer Sciences` → `Artificial Intelligence and Robotics` (the FM / BiomedCLIP arm). Fallback if absent: `Computer Sciences` → `Numerical Analysis and Computation`.<br>4. (Optional) `Engineering` → `Biomedical Engineering and Bioengineering` for the medical-physics framing.<br><br>If the deeper leaves are not shown, tick the closest parent that is — OSF's search treats parent ticks as covering descendants. Do NOT tick `Other Computer Sciences`; it may or may not be in your OSF build and is too generic anyway. |
| **Funders** | Leave blank. (Manuscript declares no funding; OSF will display "No funders associated with this project.") |
| **Affiliated Institutions** | Leave blank. (You are submitting as Independent Researcher, no institutional affiliation. If you have an Adelaide-alumni OSF affiliation listed in your account profile, OSF may auto-show it; either is fine.) |

Hit **Save**.

---

## C. Contributors tab (left sidebar > Contributors)

You are already listed as the sole contributor. No action needed. Confirm:

- **Contributor:** Wanni Arachchige Iran Chamika Kumarananda
- **Permission:** Admin
- **Bibliographic:** Yes (will appear in citation)

If OSF has not yet associated your ORCID, click your name and add it under your profile.

---

## D. Wiki tab (left sidebar > Wiki, or in-page Wiki Edit)

Click **Edit** on the Wiki card (or the Wiki tab in the left sidebar). Paste the entire block below. OSF Wiki accepts Markdown and will render headings, code blocks, links, and tables.

````markdown
# Project wiki — Paper 2

## What this project is

A controlled-perturbation reproducibility study comparing pretrained foundation-model (FM) embeddings (BiomedCLIP) against IBSI-aligned PyRadiomics handcrafted features under segmentation-mask perturbation, on 310 LIDC-IDRI lung nodules. The manuscript is targeted at *Medical Physics* (AAPM / Wiley). The full Description on the Overview page summarises the four hypotheses and the headline findings.

## Where things live

- **Code** — GitHub: `https://github.com/Iranchamika/paper2-segperturb-fm-radiomics` (private until manuscript submission, public thereafter). Will be linked under **Add-ons** once submitted.
- **Manuscript (LaTeX source)** — uploaded under **Files / OSF Storage** as `Paper2_v1.zip` (the `overleaf_project/` folder).
- **Supplementary files** — uploaded under **Files / OSF Storage**:
  - `S1_cohort_flow.pdf` — PRISMA-style cohort flow diagram.
  - `S2_strict10mm_sensitivity.pdf` — strict-10 mm sensitivity analysis.
  - `S3_icc3_table.csv` — ICC(3,1) per-feature table (radiomics QA-literature backwards-compatibility).
  - `S4_case_id_list.csv` — full case-ID list of the 227 LIDC-IDRI patients in the balanced cohort.
  - `S5_perturbation_retention.csv` — per-perturbation retention rates across the cohort.
- **Pre-registration** — a frozen registration of this project with the standard pre-data-collection template. The full OSF pre-registration text is the file `OSF_PREREGISTRATION.md` in the GitHub repository and is mirrored verbatim into the registration form fields when the registration is created.
- **Decisions log** — `decisions.log` in the repository documents every protocol amendment from initial deposit through manuscript freeze, with cross-references from each amendment to the manuscript section it affects.

## Pre-registered hypotheses (final, post-amendments)

- **H1** — proportion of stable features (ICC(2,1) >= 0.75) is higher for BiomedCLIP than for IBSI-aligned PyRadiomics 2D features on the same nodules under matched perturbation.
- **H1'** — empirical ICC distribution shape differs between paradigms (two-sample Kolmogorov-Smirnov on per-feature ICC values). Added before any analysis ran; see decisions.log #019.
- **H2** — downstream malignancy-classification AUC degradation under ICC-based stability filtering is smaller for FM embeddings than for radiomics.
- **H3** — post-filter AUC is non-inferior to pre-filter AUC at margin 0.020 ΔAUC.
- **H4** — the highest-ICC FM dimensions concentrate a disproportionate share of the L2-logistic-regression coefficient magnitude for malignancy classification.

## Amendments since initial registration

Five protocol amendments and one added hypothesis between initial OSF deposit (2026-05-25) and manuscript freeze. Each is cross-referenced to the decisions.log entry that documents its rationale and date. See `OSF_PREREGISTRATION.md` Section P (in the GitHub repository and uploaded as the body of the next registration revision).

1. Sampling-plan diameter floor: 8 mm -> 6 mm (Fleischner 2017 actionable threshold). decisions.log #011.
2. Target N: 400 -> 310 (balanced 155 + 155). decisions.log #014.
3. PyRadiomics version: v3.0.1 -> v3.1.0 (Windows wheel availability). decisions.log #009.
4. ICC-filter selection: nested-CV -> static-ICC pre-pass (protocol-deviation note in `07_downstream_classifier.py`).
5. FM paradigms: BiomedCLIP + RadImageNet -> BiomedCLIP only (RadImageNet weight access not granted within timeframe). decisions.log #018.
6. (New hypothesis) H1' added before any analysis run; pre-specified after stratum-distribution crosstab inspection but before K-S test. decisions.log #019.

## Reproducibility

- All random seeds fixed at 42 (numpy, torch, pandas).
- Environment pinned in `code/environment.yml` (Python 3.9 for Windows-compatible PyRadiomics wheel).
- Pipeline scripts numbered 00 through 08 in execution order. Documented in `code/` directory README.
- Bit-exact reproducibility across two independent runs of the downstream classifier verified for all 14 active metric rows.

## Ethics

Secondary analysis of fully de-identified, publicly released TCIA LIDC-IDRI data. IRB-exempt under the standard TCIA Data Use Agreement. No new patient contact.

## AI-assistance disclosure

Anthropic Claude (Sonnet and Opus 2026 line) was used for literature triage, protocol drafting, and manuscript prose polishing. All final analytical decisions, code, statistical choices, and manuscript wording are the sole responsibility of the author. Disclosed in the manuscript Acknowledgements following COPE 2024 guidance and the Medical Physics 2026 AI-use policy.
````

Hit **Save**.

---

## E. Files tab (left sidebar > Files, or OSF Storage card)

Upload the following files to **OSF Storage** (drag-and-drop into the Files Preview card, or use the Files tab and click **Upload**). Pre-build them locally first; the supplementary files listed are the ones I will produce in Round 6.

| File | Source on your laptop | Notes |
|------|------------------------|-------|
| `Paper2_v1.zip` | Zip up `D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\overleaf_project\` | The full LaTeX project — main.tex + section files + abstract + references.bib + figures/. OSF accepts up to 5 GB per file on free accounts. |
| `decisions.log` | `D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\decisions.log` | Append-only protocol-amendment log; gives OSF readers the full audit trail. |
| `OSF_PREREGISTRATION.md` | `D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\overleaf_project\OSF_PREREGISTRATION.md` | The pre-registration source text (also used in Section H below). |
| `COVER_LETTER.md` | `D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics\overleaf_project\COVER_LETTER.md` | Cover letter for the Medical Physics submission. |
| `S1_cohort_flow.pdf` | Round 6 deliverable | PRISMA-style cohort flow diagram. Will produce in the next round. |
| `S2_strict10mm_sensitivity.pdf` | Round 6 deliverable | Sensitivity analysis at the original 10 mm diameter floor. |
| `S3_icc3_table.csv` | Round 6 deliverable | ICC(3,1) per-feature table (backwards-compatibility with the radiomics QA literature). |
| `S4_case_id_list.csv` | Round 6 deliverable | Full case-ID list of the 227 LIDC-IDRI patients in the balanced cohort. |
| `S5_perturbation_retention.csv` | Round 6 deliverable | Per-perturbation retention rates across the cohort. |

For files I have not yet produced (S1-S5), upload `Paper2_v1.zip` and the three Markdown files now; we will upload S1-S5 after Round 6.

---

## F. Add-ons tab (left sidebar > Add-ons)

Optional but recommended. Connect:

- **GitHub** — link the `paper2-segperturb-fm-radiomics` repo. OSF will mirror the file tree under the **Linked Services** card so reviewers can browse code without leaving OSF.
- **OSF Storage** — already on by default. Used for the file uploads in Part E.

No other add-ons needed for a methodology paper of this scope.

---

## G. Privacy

Keep the project **Private** for now (the toggle at the top of the Overview shows it is private). Switch to **Public** at the moment of manuscript submission, so the OSF DOI is dereferenceable from the submission day onwards.

---

## H. Registrations tab — create the pre-registration

This is the step that produces the permanent DOI you cite in the manuscript Methods §2.1.

1. In the left sidebar, click **Registrations**.
2. Click **New Registration**.
3. Choose the schema: **OSF Preregistration** (the recently-renamed "Standard Pre-Data Collection Registration"). It is one of the templates OSF lists by default. If OSF offers you a choice between OSF Preregistration and OSF Preregistration (Open-Ended), pick **OSF Preregistration** — it has the structured fields that match my OSF_PREREGISTRATION.md layout.
4. OSF will open a multi-page form. Each page maps to a section in `OSF_PREREGISTRATION.md`. The mapping is below — for each OSF page, copy the matching section's body (everything under the section heading) into the OSF text box.

| OSF Preregistration page | Paste from `OSF_PREREGISTRATION.md` |
|--------------------------|-------------------------------------|
| Study Information / Title | Section A |
| Study Information / Description | Section C |
| Hypotheses | Section D (include H1, H1', H2, H3, H4 — the H1' addition is explicitly documented as pre-specified before analysis) |
| Design Plan / Study type | Section E |
| Sampling Plan | Section F |
| Variables / Manipulated and Measured | Section G |
| Analysis Plan | Section H |
| Other (anything else important to register) | Section I (Code, data, reproducibility) + Section J (Ethics) |

5. Below the form, OSF asks for a registration narrative. Paste **Section P** (Amendments since initial deposit) verbatim. This makes the amendments transparent on the registration record.
6. Choose embargo: I recommend **No embargo** for an independent-researcher submission — the OSF DOI being immediately resolvable is part of the credibility signal. If you prefer to embargo until manuscript acceptance, OSF supports an embargo of up to 4 years; pick that and Medical Physics will accept the registration cite either way.
7. Review the auto-generated preview. OSF will show you a snapshot of every file in the project at the moment of registration — this is why we want all the files in Part E uploaded BEFORE you create the registration.
8. Click **Register**. OSF will mint a DOI of the form `10.17605/OSF.IO/XXXX`. **DONE 2026-05-26 — Registration archived at `osf.io/9kt3c` with DOI `10.17605/OSF.IO/9KT3C`.** The DOI has been substituted into:
   - `overleaf_project/methods.tex` line 8 (the OSF DOI placeholder in §2.1) and `overleaf_project/supplementary/S2_strict10mm_sensitivity.tex` line 31 (the strict-10mm rationale paragraph) — committed in `0013589` and the follow-up commit.
   - `overleaf_project/OSF_PREREGISTRATION.md` header (Registration-status banner) and `README.md` (badge row plus two prose references).
   - Cover letter — optional; consider adding the DOI string `10.17605/OSF.IO/9KT3C` to `overleaf_project/COVER_LETTER.md` in the "Pre-registration and data availability" paragraph as a final credibility signal before submission.

---

## I. Recap — what to do in what order

1. **A** — paste Description into the Overview Metadata card. (~ 2 min)
2. **B** — fill Metadata fields (Resource Type, License, Tags, Subjects). (~ 5 min)
3. **C** — confirm Contributors is correct. (~ 1 min)
4. **D** — paste Wiki content. (~ 2 min)
5. **E** — upload available files (`Paper2_v1.zip`, `decisions.log`, `OSF_PREREGISTRATION.md`, `COVER_LETTER.md`). (~ 5 min)
6. **F** — optionally link GitHub once the repo is public. (~ 3 min)
7. **G** — leave Private until submission day.
8. **H** — create the Registration AFTER Round 6 supplementary files are uploaded, OR create it now and re-register with the supplements before submission (OSF allows multiple registrations from one project — the later one supersedes for citation purposes).

If you only have time for one pass right now, do A, B, C, D and stop. The Wiki content alone gives OSF readers enough context to understand the project. E and H can wait until Round 6 supplements are in hand.

---

## J. What I cannot do for you

I have no direct OSF API access, so I cannot fill any field on your behalf. Everything above is paste-ready text and tab-by-tab guidance. If any OSF page label has changed since this guide was written (OSF updates its UI roughly twice a year), the form fields still cover the same content — match Section A / B / etc. to whichever label OSF currently uses.
