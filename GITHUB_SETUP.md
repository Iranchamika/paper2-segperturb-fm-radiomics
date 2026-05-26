# GitHub repo creation — one-time setup

The manuscript and OSF docs all reference a GitHub repository at
`https://github.com/Iranchamika/paper2-segperturb-fm-radiomics` as a placeholder.
This file walks you through actually creating it. ~10 minutes total.

## Prerequisites

- Git installed on your laptop (`git --version` should return something).
- A GitHub account. If you do not already have one, create one at
  https://github.com/signup. Pick a username you are happy citing in
  perpetuity — it will appear on the manuscript's GitHub URL.

## Step 1 — Create the empty repo on GitHub

1. Sign in at https://github.com.
2. Click the **+** button top-right → **New repository**.
3. Fill in:
   - **Repository name:** `paper2-segperturb-fm-radiomics`
   - **Description:** "Segmentation-perturbation propagation in FM embeddings vs IBSI radiomics on LIDC-IDRI. Code, environment, and LaTeX manuscript source for the Medical Physics submission."
   - **Visibility:** **Private** for now. Switch to Public at the moment of manuscript submission.
   - **Initialize repository with:** leave all three checkboxes UNTICKED (no README, no .gitignore, no LICENSE). We will push our own.
4. Click **Create repository**.

GitHub will show a "Quick setup" page with the repo URL. It will be something like:
`https://github.com/Iranchamika/paper2-segperturb-fm-radiomics`

Note your username — you will paste it into Step 4 below.

## Step 2 — Initialise the local git repo

Open PowerShell and run:

```powershell
cd "D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics"
git init
git branch -M main
```

## Step 3 — First commit (only the things the `.gitignore` allows)

```powershell
git add .
git status
```

Verify the `git status` output. You SHOULD see:

- `README.md`, `LICENSE`, `.gitignore`, `GITHUB_SETUP.md` at the root
- `code/` with all 12 .py files and `environment.yml`
- `overleaf_project/` with the .tex files, references.bib, figures/, supplementary/, COVER_LETTER.md, OSF_PREREGISTRATION.md, OSF_FILL_GUIDE.md
- `decisions.log` at the root
- Maybe `W1_USER_CHECKLIST.md`, `OSF_Preregistration_Template.md` (the old draft) at root
- Maybe `references/` with the Pai digests

You should NOT see (the .gitignore should have hidden these):

- `data/raw/`, `data/processed/`, `data/perturbations/` (LIDC DICOMs and derived masks — gigabytes)
- `data/labels.csv`, `data/labels_balanced.csv` (small but treated as data per the gitignore rule; if you want to commit them edit `.gitignore` and remove the `data/*.csv` line)
- `models/` (foundation-model weights)
- `results/*.parquet` (large feature parquets)
- `overleaf_project/Paper2_v1.zip` (a build artefact)
- Any `__pycache__/`, `.aux`, `.log`, `.out`

If `git status` shows any of the "should NOT see" items, edit `.gitignore` accordingly and re-run `git add .` then `git status` again.

Once `git status` looks right:

```powershell
git commit -m "Initial commit: Paper 2 — code, manuscript source, decisions log"
```

## Step 4 — Wire the remote and push

Replace `Iranchamika` with the GitHub username from Step 1:

```powershell
git remote add origin https://github.com/Iranchamika/paper2-segperturb-fm-radiomics.git
git push -u origin main
```

GitHub may ask for credentials. The recommended path is to use a Personal
Access Token rather than a password (passwords have been disabled for git
operations since 2021). Follow https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
if you do not already have a PAT.

## Step 5 — Update the four placeholder URLs in the project

Once the repo URL is real, the placeholder `https://github.com/Iranchamika/paper2-segperturb-fm-radiomics` in four files needs to be replaced with the actual URL. Either:

**Option A — let me do it in chat.** Reply with your GitHub username and I will run a find-and-replace across:

- `overleaf_project/main.tex` (Data availability section)
- `overleaf_project/methods.tex` (Reproducibility section, line ~52)
- `overleaf_project/OSF_PREREGISTRATION.md` (Section I)
- `overleaf_project/OSF_FILL_GUIDE.md` (two references)

then commit the change with a message like "Replace Iranchamika placeholder with real repo URL".

**Option B — do it yourself with PowerShell.** Replace `Iranchamika`:

```powershell
$dir = "D:\Research work\Paper2_SegPerturbation_FM_vs_Radiomics"
$old = "github.com/Iranchamika/paper2-segperturb-fm-radiomics"
$new = "github.com/Iranchamika/paper2-segperturb-fm-radiomics"
Get-ChildItem -Path $dir -Recurse -Include *.tex,*.md | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace [regex]::Escape($old), $new | Set-Content $_.FullName -NoNewline
}
git add .
git commit -m "Replace Iranchamika placeholder with real repo URL"
git push
```

## Step 6 (optional, recommended) — Link GitHub to OSF

Once the repo exists and the placeholder URLs are updated:

1. On `osf.io/3f76x`, click **Add-ons** in the left sidebar.
2. Find **GitHub** in the list, click **Connect**.
3. Authorise OSF to read your repo.
4. Select the `paper2-segperturb-fm-radiomics` repo from the dropdown.
5. Click **Save**.

OSF will now mirror the GitHub file tree under the **Linked Services** card on the Overview page. Reviewers can browse the code without leaving OSF.

## At manuscript submission day

Flip the repo Visibility from Private to Public:

1. On the GitHub repo page, **Settings** tab (top right).
2. Scroll to **Danger Zone** at the bottom.
3. Click **Change repository visibility** → **Make public** → type the repo name to confirm.

Do this AT submission, not before — the manuscript references the repo as available "at the time of submission" so the URL needs to be live on submission day.

## What this guide does NOT cover

- Releasing tagged versions (a `v1.0.0` git tag at submission day is a nice touch but not required).
- Generating a Zenodo DOI for the GitHub repo (some journals prefer this; *Medical Physics* accepts a GitHub URL directly so the Zenodo step is optional).
- Setting up GitHub Actions for continuous integration. We do not have a test suite, so CI offers no value at this scale.
- A GitHub Pages site for the figures. Adds polish, not value.

Stick to Steps 1-5 unless reviewers ask for a Zenodo DOI in revision.
