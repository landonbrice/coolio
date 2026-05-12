# Boeing Project

## Remote

This directory is the working copy for the **`coolio`** GitHub repository.

- Repo: https://github.com/landonbrice/coolio
- Owner: `landonbrice`
- Visibility: public
- Default branch: `main`

## Local ↔ remote setup

First-time push from this directory:

```bash
git init
git branch -M main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/landonbrice/coolio.git
git push -u origin main
```

After the first push, normal flow:

```bash
git add <files>
git commit -m "..."
git push
```

## Contents

- `Boeing Project master.txt` — primary working document
- `Modern Startup Pitch Deck.pdf` — pitch deck reference
- `Manufacturing Consent by Chomsky 2002 (1).pdf` — reference reading

## Conventions

- Push directly to `main` (solo repo, no PR workflow).
- Large binaries (PDFs) are committed as-is; switch to Git LFS if the repo grows past ~50MB per file.
