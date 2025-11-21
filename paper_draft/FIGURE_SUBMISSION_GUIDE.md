# Figure Submission Guide for LaTeX Manuscript

## How to Handle Figures in Journal Submission

### Two Options for Figure Submission:

**Option 1: Separate Files (RECOMMENDED for initial submission)**
- Upload manuscript WITHOUT embedded figures
- Upload each figure as a separate file
- Use `\ref{fig:label}` in text to reference figures
- Journal will place figures during typesetting

**Option 2: Embedded (for final version after acceptance)**
- Place figures in text using `\includegraphics`
- Requires figures in same directory or subdirectory
- Usually requested only for final camera-ready version

---

## Current Setup in manuscript.tex

Your LaTeX file is set up for **Option 1 (separate files)**:

```latex
% In the text, you reference figures like:
Figure~\ref{fig:costs} presents cumulative costs...
Figure~\ref{fig:electricity} shows electricity demands...

% Figures are NOT embedded in manuscript.tex
% They will be uploaded separately to the journal portal
```

---

## Step-by-Step Submission Process

### Step 1: Prepare Figure Files

Your figures are already at 300 DPI in `/outputs/paper_figures/`. You need to:

1. **Copy figures to paper_draft folder**:
```bash
cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/*.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures/
```

2. **Rename for clarity** (optional but recommended):
   - `figure1_six_scenario_costs.png`
   - `figure3_macc_curves.png`
   - `figure4_electricity_demand.png`
   - `figure5_hydrogen_demand.png`
   - `figure7_baseline_emissions.png`
   - `figureS1_technology_deployment.png` (supplementary)
   - `figureS2_emissions_trajectories.png` (supplementary)

3. **Convert to PDF** (preferred by many journals):
```bash
# If needed, convert PNG to PDF using ImageMagick or similar
convert figure1.png figure1.pdf
```

### Step 2: Upload to Journal Portal

When you submit via Editorial Manager (https://www.editorialmanager.com/cneu/):

1. **Upload main manuscript**: `manuscript.pdf` (compiled from manuscript.tex)

2. **Upload figures separately**:
   - Main Text Figures → Upload Figure 1, Figure 3, Figure 4, Figure 5, Figure 7
   - Supplementary Figures → Upload Figure S1, Figure S2

3. **System will ask for**:
   - Figure number (1, 3, 4, 5, 7, S1, S2)
   - Figure caption (copy from FIGURE_CAPTIONS.md)
   - File format (PNG or PDF)

### Step 3: Figure Labels in LaTeX

The manuscript.tex uses these labels:
```latex
\ref{fig:baseline}     → Figure 7 (Baseline emissions)
\ref{fig:costs}        → Figure 1 (Six-scenario costs)
\ref{fig:electricity}  → Figure 4 (Electricity demand)
\ref{fig:hydrogen}     → Figure 5 (Hydrogen demand)
```

These `\ref` commands create placeholder text like "Figure 1" in the PDF. The journal will insert actual figures during typesetting.

---

## If You Want to See Figures in Your Draft

To compile a version WITH figures for your own review (not for submission):

### Create figures/ subdirectory:
```bash
mkdir -p paper_draft/figures
```

### Copy your figures there:
```bash
cp outputs/paper_figures/figure1_six_scenario_costs.png paper_draft/figures/figure1.png
cp outputs/paper_figures/figure3_macc_curves_evolution.png paper_draft/figures/figure3.png
# ... etc
```

### Add figure environment to manuscript.tex (after relevant paragraphs):

```latex
% After paragraph mentioning costs
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/figure1.png}
\caption{Cumulative decarbonization costs across six scenarios (2025--2050).
Technology pathway choice shows minimal cost difference (6--11\%), while
production pathway choice dominates total costs (58\% variation).}
\label{fig:costs}
\end{figure}

% After paragraph mentioning electricity demands
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/figure4.png}
\caption{Electricity demand trajectories by scenario (2025--2050).
Shaheen + NCC-Electricity requires 164.5 TWh/yr by 2050 (29.5\% of
Korea's current grid, 96.8\% of 2036 renewable target).}
\label{fig:electricity}
\end{figure}

% ... etc for other figures
```

---

## Compilation Instructions

### To compile manuscript.tex:

**Option A: Command line (if you have LaTeX installed)**
```bash
cd /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

**Option B: Overleaf (online, easier)**
1. Go to https://www.overleaf.com
2. Create free account
3. New Project → Upload Project
4. Upload manuscript.tex and references.bib
5. Click "Recompile" to generate PDF

**Option C: TeXShop, TeXworks, or other LaTeX editor**
- Open manuscript.tex in your editor
- Click "Typeset" or "Build"

---

## What the Journal Sees

When you submit:

**Manuscript PDF** (generated from manuscript.tex):
- Shows all text, equations, tables
- Shows "Figure X" placeholders where you reference figures
- Shows figure captions in the figure list (if you include them)

**Separate Figure Files**:
- figure1.png (or .pdf) - Six-scenario costs
- figure3.png - MACC curves
- figure4.png - Electricity demand
- figure5.png - Hydrogen demand
- figure7.png - Baseline emissions
- figureS1.png - Technology deployment (supplementary)
- figureS2.png - Emissions trajectories (supplementary)

**Journal production team will**:
- Take your manuscript PDF
- Insert figures at appropriate locations
- Format to journal style
- Create final typeset version

---

## Figure Quality Checklist

Before uploading, verify each figure:
- [ ] Resolution: 300 DPI minimum ✅ (already done)
- [ ] Format: PNG, PDF, or TIFF ✅
- [ ] Size: Fits in column width (3.5" single, 7" double)
- [ ] Labels: Readable at 100% scale
- [ ] Font: Consistent and professional
- [ ] Colors: Colorblind-friendly if using color
- [ ] Caption: Matches figure content
- [ ] Numbering: Correct sequence (1, 3, 4, 5, 7, S1, S2)

---

## Common Issues and Solutions

### Issue 1: LaTeX can't find figures
**Solution**: Make sure figures/ directory exists and contains files, or remove `\includegraphics` commands for submission version

### Issue 2: Figure numbers wrong
**Solution**: Check `\label{fig:xxx}` matches your `\ref{fig:xxx}` in text

### Issue 3: BibTeX errors
**Solution**: Make sure references.bib is in same directory as manuscript.tex

### Issue 4: Journal asks for EPS format
**Solution**: Convert PNG to EPS:
```bash
convert figure1.png figure1.eps
```

### Issue 5: Figures too large for column width
**Solution**: Adjust `\includegraphics[width=0.8\textwidth]` to `width=\columnwidth` or smaller

---

## Summary: What You Need to Do

### For Submission:

1. **Compile manuscript.tex to PDF**:
   - Using command line, Overleaf, or LaTeX editor
   - This creates `manuscript.pdf`

2. **Prepare figure files**:
   - Copy from `/outputs/paper_figures/`
   - Rename clearly (figure1.png, figure3.png, etc.)
   - Ensure 300 DPI (already done)

3. **Go to submission portal**:
   - Upload manuscript.pdf (main document)
   - Upload each figure separately
   - Add figure captions when prompted
   - Complete submission form

4. **Figures are uploaded separately, NOT embedded in manuscript.tex**

### For Your Own Review (Optional):

1. Add `\begin{figure}...\end{figure}` environments to manuscript.tex
2. Place figures in `figures/` subdirectory
3. Recompile to see figures in your PDF
4. Remove figure environments before submission (or keep them, journal will ignore)

---

## Files You Need

**Essential for submission**:
- ✅ `manuscript.tex` (created)
- ✅ `references.bib` (created)
- ✅ Figure files from `/outputs/paper_figures/` (already exist at 300 DPI)

**Optional for your review**:
- LaTeX editor (Overleaf recommended for beginners)
- Figure files copied to `paper_draft/figures/` directory

---

**Current Status**:
✅ LaTeX manuscript ready
✅ References in BibTeX format ready
✅ Figures exist at 300 DPI
⏳ Need to compile manuscript.tex to PDF
⏳ Need to prepare for submission portal

**Next step**: Would you like me to help you set up Overleaf, or do you have LaTeX installed locally?
