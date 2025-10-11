# Git Commands for LaTeX Paper Setup

## Quick Commands to Push to GitHub

```bash
# Make sure you're in the project root
cd /Users/jinsupark/jinsu-coding/petrochemical_macc_2025

# Add all LaTeX paper files
git add latex_paper/

# Commit with descriptive message
git commit -m "Add LaTeX paper template for academic publication

- Complete paper structure (Introduction, Methodology, Results, Discussion)
- Bibliography with 20+ references including Woo2025 (Green Chemistry)
- Automatic figure integration from outputs/ directory
- Tables with actual 2030 MACC data
- Compilation scripts (compile.sh + Makefile)
- Documentation for Overleaf connection"

# Push to GitHub
git push origin main
```

## Verify What Will Be Committed

Before committing, check what's new:

```bash
# See which files are new/modified
git status

# See detailed changes
git diff latex_paper/
```

## If You Want to Commit Report Generator Too

```bash
# Add report generator
git add generate_report.py

# Commit both report and paper
git commit -m "Add report generation and LaTeX paper template"

git push origin main
```

## After Pushing to GitHub

### Connect to Overleaf

1. **Go to Overleaf**: https://www.overleaf.com
2. **Create Project from GitHub**:
   - Click "New Project" (top left)
   - Select "Import from GitHub"
   - Authorize Overleaf to access your GitHub (first time only)
   - Select repository: `petrochemical_macc_2025`
   - Click "Import to Overleaf"

3. **Configure Main File**:
   - In Overleaf, click "Menu" (top left)
   - Under "Main document", select: `latex_paper/main.tex`
   - Click "Recompile"

4. **View Your Paper**:
   - PDF will appear in right panel
   - Edit LaTeX in left panel
   - Changes sync to GitHub automatically (if 2-way sync enabled)

### Enable Two-Way Sync (Optional)

To sync Overleaf edits back to GitHub:
- Overleaf Menu → GitHub
- Enable "Push to GitHub on save"
- Now edits in Overleaf automatically commit to GitHub

## Updating Paper with New Model Results

When you regenerate model outputs:

```bash
# Run the model
python main.py

# Commit new outputs
git add outputs/
git commit -m "Update model outputs with latest results"
git push origin main
```

Overleaf will automatically sync the new figures. Just click "Recompile" in Overleaf to see them in the paper.

## Common Git Workflows

### Scenario 1: Update Paper Text Only

```bash
# Edit latex_paper/main.tex locally
# Then:
git add latex_paper/main.tex
git commit -m "Update methodology section with detailed equations"
git push origin main
```

### Scenario 2: Update Data and Paper Together

```bash
# Update data files
git add data/fuel_price_trajectory.csv

# Update paper text
git add latex_paper/main.tex

# Commit both
git commit -m "Update fuel price assumptions and document in paper"
git push origin main
```

### Scenario 3: Add New Figures to Paper

```bash
# Generate new figure (e.g., sensitivity_analysis.png)
# Save to outputs/module_03/

# Add to paper:
# Edit latex_paper/main.tex and add:
# \includegraphics[width=0.7\textwidth]{sensitivity_analysis.png}

# Commit
git add outputs/module_03/sensitivity_analysis.png
git add latex_paper/main.tex
git commit -m "Add sensitivity analysis figure"
git push origin main
```

## Troubleshooting

### If git says files are too large:

Check your `.gitignore`:
```bash
cat .gitignore
```

LaTeX auxiliary files should already be ignored via `latex_paper/.gitignore`.

### If you want to see what will be pushed:

```bash
# See commits that will be pushed
git log origin/main..HEAD

# See files that changed
git diff origin/main..HEAD --name-only
```

### If you made a mistake in commit message:

```bash
# Amend the last commit message (before pushing)
git commit --amend -m "New better message"
```

## Branch Strategy (Optional)

If you want to work on paper separately:

```bash
# Create a paper branch
git checkout -b paper-draft

# Work on paper
git add latex_paper/
git commit -m "Draft methodology section"
git push origin paper-draft

# Later, merge to main
git checkout main
git merge paper-draft
git push origin main
```

## Summary

**Immediate action**:
```bash
cd /Users/jinsupark/jinsu-coding/petrochemical_macc_2025
git add latex_paper/
git commit -m "Add LaTeX paper template for academic publication"
git push origin main
```

**Then**: Go to Overleaf → Import from GitHub → Select `petrochemical_macc_2025` → Set main document to `latex_paper/main.tex` → Compile!

---

**Note**: Make sure you're on the correct branch (`macc_fac_v0.1` or `main`). Check with `git branch`.
