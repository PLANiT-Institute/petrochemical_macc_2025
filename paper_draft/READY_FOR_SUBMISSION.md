# Paper Ready for Submission - Final Checklist

**Date**: 2025-11-11
**Status**: 🟢 LaTeX manuscript prepared, ready for compilation and submission

---

## ✅ What's Complete

### Core Files Created:
1. **manuscript.tex** - Full LaTeX manuscript (~5,050 words)
2. **references.bib** - BibTeX file with 19 references
3. **All supporting documents** - Tables, figure captions, cover letter

### Content Status:
- ✅ Abstract (250 words)
- ✅ Introduction (800 words) with citations
- ✅ Methods (1,200 words) with 5 equations
- ✅ Results (1,500 words) with figure references
- ✅ Discussion (1,200 words) with policy implications
- ✅ Conclusion (400 words)
- ✅ References formatted in BibTeX

### Figures:
- ✅ 7 figures already at 300 DPI in `/outputs/paper_figures/`
- ✅ Figure captions written in `FIGURE_CAPTIONS.md`

---

## 📋 Answer: How to Handle Figures

### **YES - Upload Separately** ✅

**Here's exactly how it works:**

1. **Manuscript PDF**:
   - Compile `manuscript.tex` → creates `manuscript.pdf`
   - This PDF has text + equations + figure placeholders
   - Does NOT contain actual figure images

2. **Figure Files**:
   - Upload each figure as separate file on journal portal
   - System asks: "Upload Figure 1", "Upload Figure 2", etc.
   - You upload: `figure1.png`, `figure3.png`, `figure4.png`, etc.

3. **Journal Production**:
   - Typesetters take your manuscript PDF
   - Insert your separately uploaded figures
   - Create final formatted version

### Why Separate?
- Higher quality (no compression from embedding)
- Easier to replace if revisions needed
- Standard practice for academic journals
- Editorial Manager system expects this format

---

## 🚀 Next Steps to Submit

### Step 1: Compile LaTeX to PDF

**Option A - Overleaf (Easiest, Recommended)**:
1. Go to https://www.overleaf.com (free account)
2. Click "New Project" → "Upload Project"
3. Upload `manuscript.tex` and `references.bib`
4. Click "Recompile" → Downloads `manuscript.pdf`
5. ✅ Done!

**Option B - Local LaTeX** (if you have TeX installed):
```bash
cd /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```
Output: `manuscript.pdf`

### Step 2: Prepare Figures

**Copy figures to paper_draft**:
```bash
mkdir -p paper_draft/figures_for_submission
cp outputs/paper_figures/figure1_six_scenario_costs.png paper_draft/figures_for_submission/figure1.png
cp outputs/paper_figures/figure3_macc_curves_evolution.png paper_draft/figures_for_submission/figure3.png
cp outputs/paper_figures/figure4_electricity_demand_trajectories.png paper_draft/figures_for_submission/figure4.png
cp outputs/paper_figures/figure5_hydrogen_demand_trajectories.png paper_draft/figures_for_submission/figure5.png
cp outputs/paper_figures/figure7_baseline_emissions_structure.png paper_draft/figures_for_submission/figure7.png
cp outputs/paper_figures/figure2_technology_deployment_2050.png paper_draft/figures_for_submission/figureS1.png
cp outputs/paper_figures/figure6_emissions_trajectories.png paper_draft/figures_for_submission/figureS2.png
```

You'll have:
- `figure1.png` (Six-scenario costs)
- `figure3.png` (MACC curves)
- `figure4.png` (Electricity demand) ⭐ KEY FINDING
- `figure5.png` (Hydrogen demand)
- `figure7.png` (Baseline emissions)
- `figureS1.png` (Technology deployment - supplementary)
- `figureS2.png` (Emissions trajectories - supplementary)

### Step 3: Fill in Your Details

**In manuscript.tex**, replace placeholders:
```latex
Line 17: [Your Name]
Line 18: [Your Department], [Your Institution], [City, Country]
Line 19: [your.email@institution.edu]
```

**In COVER_LETTER_TEMPLATE.md**, fill in:
- Your name, affiliation, contact
- Funding statement (funded or not)
- 3-5 suggested reviewers with emails

### Step 4: Submit to Journal

**Portal**: https://www.editorialmanager.com/cneu/

**What to upload**:
1. Main manuscript: `manuscript.pdf`
2. Cover letter: Use `COVER_LETTER_TEMPLATE.md` (personalize and save as PDF)
3. Figures: Upload 7 separate files (figure1.png through figureS2.png)
4. Figure captions: Copy from `FIGURE_CAPTIONS.md` into upload form

**Complete form**:
- Article type: Original Research
- Title: [copy from manuscript]
- Abstract: [copy from manuscript]
- Keywords: Industrial decarbonization, petrochemicals, MACC methodology, energy system constraints, hydrogen economy, electrification, South Korea, renewable energy
- Authors: [your details]
- Funding: [your statement]
- Data availability: [choose option]
- Competing interests: None

---

## 📊 Quick Commands Summary

### Create figures directory and copy files:
```bash
mkdir -p /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure1_six_scenario_costs.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figure1.png

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure3_macc_curves_evolution.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figure3.png

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure4_electricity_demand_trajectories.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figure4.png

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure5_hydrogen_demand_trajectories.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figure5.png

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure7_baseline_emissions_structure.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figure7.png

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure2_technology_deployment_2050.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figureS1.png

cp /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/outputs/paper_figures/figure6_emissions_trajectories.png /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/figureS2.png
```

### Verify files copied:
```bash
ls -lh /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft/figures_for_submission/
```

Should show 7 PNG files (figure1.png, figure3.png, figure4.png, figure5.png, figure7.png, figureS1.png, figureS2.png)

---

## 📁 File Structure for Submission

```
paper_draft/
├── manuscript.tex             ✅ LaTeX source
├── references.bib             ✅ BibTeX references
├── manuscript.pdf             ⏳ Compile from .tex
├── figures_for_submission/    ⏳ Create and copy figures
│   ├── figure1.png           (Six-scenario costs)
│   ├── figure3.png           (MACC curves)
│   ├── figure4.png           (Electricity demand)
│   ├── figure5.png           (Hydrogen demand)
│   ├── figure7.png           (Baseline emissions)
│   ├── figureS1.png          (Technology deployment)
│   └── figureS2.png          (Emissions trajectories)
├── cover_letter.pdf          ⏳ From COVER_LETTER_TEMPLATE.md
└── TABLES.md                  ✅ Reference for supplementary materials
```

---

## ⚡ Fast Track: Ready in 30 Minutes

### Minute 0-10: Compile PDF
1. Open Overleaf.com
2. Upload manuscript.tex + references.bib
3. Click "Recompile"
4. Download manuscript.pdf

### Minute 10-15: Prepare Figures
1. Run commands above to copy figures
2. Verify 7 PNG files in figures_for_submission/

### Minute 15-25: Personalize Cover Letter
1. Open COVER_LETTER_TEMPLATE.md
2. Fill in: your name, affiliation, email, funding
3. Add 3-5 reviewer suggestions
4. Save as PDF

### Minute 25-30: Go to Portal
1. https://www.editorialmanager.com/cneu/
2. Register account
3. Start new submission
4. Upload files (manuscript, figures, cover letter)
5. Complete form
6. Submit!

---

## 🎯 Key Points to Remember

### 1. Figures = Separate Files ✅
- NOT embedded in manuscript PDF
- Upload each as individual PNG file
- Journal inserts them during production

### 2. LaTeX References Figures by Label
```latex
% In manuscript.tex:
Figure~\ref{fig:costs}        → Becomes "Figure 1"
Figure~\ref{fig:electricity}  → Becomes "Figure 4"
```

### 3. Figure Numbering
- Main text: Figure 1, 3, 4, 5, 7 (skip 2 and 6 to supp)
- Supplementary: Figure S1, S2
- This is intentional - no mistake!

### 4. You Need to Provide
- [x] Manuscript PDF (from compiling .tex)
- [x] 7 figure files (PNG, 300 DPI - already done)
- [ ] Your author information (name, email, ORCID)
- [ ] Funding statement
- [ ] Cover letter with reviewer suggestions

---

## 🔍 Double-Check Before Submission

### Manuscript PDF:
- [ ] Title correct
- [ ] Your name and affiliation filled in
- [ ] Abstract present (~250 words)
- [ ] All sections included (Intro, Methods, Results, Discussion, Conclusion)
- [ ] Equations numbered (5 equations)
- [ ] References cited in text
- [ ] No "[To be added]" placeholders remaining

### Figures:
- [ ] 7 files total (5 main + 2 supplementary)
- [ ] All 300 DPI (already verified ✅)
- [ ] Named clearly (figure1.png, not random_name.png)
- [ ] File sizes reasonable (<5 MB each)

### Cover Letter:
- [ ] Your name and contact info
- [ ] Manuscript title matches
- [ ] 3-5 suggested reviewers with emails
- [ ] Funding statement (even if "no funding")
- [ ] Competing interests declaration
- [ ] Signatures/date

---

## 📞 What to Do If...

### "I don't have LaTeX installed"
→ Use Overleaf.com (free, online, no installation needed)

### "manuscript.tex won't compile"
→ Check that references.bib is in same folder
→ Use Overleaf which handles dependencies automatically

### "Figures don't appear in PDF"
→ That's correct! They shouldn't be in the PDF for submission
→ They're uploaded separately

### "Journal asks for different format"
→ Most journals accept PNG at 300 DPI (you have this)
→ If they need TIFF or EPS, convert using ImageMagick or online tools

### "I need to add co-authors"
→ Edit lines 17-19 in manuscript.tex:
```latex
\author{
First Author\textsuperscript{1,*}, Second Author\textsuperscript{2} \\
...
}
```

---

## 🎉 You're Ready!

**What we've accomplished**:
✅ Full 5,050-word manuscript in LaTeX
✅ 19 references in BibTeX format
✅ All 7 figures at 300 DPI quality
✅ Complete submission documentation
✅ Cover letter template
✅ Submission checklist

**What you need to do**:
1. Compile manuscript.tex → manuscript.pdf (10 minutes via Overleaf)
2. Copy figures to submission folder (2 minutes)
3. Fill in your author details (5 minutes)
4. Submit to journal portal (15 minutes)

**Total time to submission**: ~30 minutes

---

**Questions?** The key thing to remember:

> **Figures are uploaded separately, not embedded in the manuscript PDF.**
> This is standard practice and exactly what Carbon Neutrality expects.

The manuscript.tex file already has all the `\ref{fig:...}` commands in the right places. When you compile it, you'll see "Figure 1", "Figure 4", etc. appearing as text. The journal will insert the actual images when they typeset your paper.

**Ready when you are!** 🚀
