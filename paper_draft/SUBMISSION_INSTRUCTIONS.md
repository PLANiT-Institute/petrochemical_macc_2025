# Final Submission Instructions

**Date**: 2025-11-11
**Status**: ✅ **ALL FILES READY - ONLY COMPILATION NEEDED**

---

## ✅ What's Done (You Can Review Now)

### 1. LaTeX Manuscript
- **File**: `manuscript.tex`
- **Status**: ✅ Complete (5,050 words)
- **Contains**: Abstract, Intro, Methods (5 equations), Results, Discussion, Conclusion
- **References**: Uses `references.bib` with 19 citations

### 2. BibTeX References
- **File**: `references.bib`
- **Status**: ✅ Complete (19 references from your literature review)
- **Format**: BibTeX, compatible with natbib package

### 3. Figures for Submission
- **Location**: `paper_draft/figures_for_submission/`
- **Status**: ✅ All 7 figures copied and ready
- **Files**:
  - `figure1.png` (184K) - Six-scenario cost comparison
  - `figure3.png` (144K) - MACC curves evolution
  - `figure4.png` (273K) - **Electricity demand (KEY FINDING)**
  - `figure5.png` (253K) - Hydrogen demand
  - `figure7.png` (200K) - Baseline emissions structure
  - `figureS1.png` (403K) - Technology deployment (supplementary)
  - `figureS2.png` (311K) - Emissions trajectories (supplementary)

---

## 📋 To Answer Your Question

### **Q: Should I upload figures separately?**

### **A: YES! ✅**

Here's exactly how it works:

1. **You upload TWO things to the journal**:
   - One PDF file: `manuscript.pdf` (compiled from `manuscript.tex`)
   - Seven PNG files: `figure1.png` through `figureS2.png`

2. **The manuscript PDF**:
   - Contains ALL text, equations, tables
   - Contains figure REFERENCES like "see Figure 4"
   - Does NOT contain the actual figure images

3. **The figure files**:
   - Upload each separately in the journal portal
   - Portal will ask: "Upload Figure 1", "Upload Figure 3", etc.
   - You upload the corresponding PNG file

4. **The journal will**:
   - Take your manuscript text
   - Insert your figures at the right places
   - Create the final typeset version

This is standard practice for ALL academic journals using Editorial Manager.

---

## 🚀 Next Step: Compile LaTeX → PDF

You need to turn `manuscript.tex` into `manuscript.pdf`.

### **Option 1: Overleaf (Easiest - RECOMMENDED)** ⭐

**Why Overleaf**: No installation needed, handles everything automatically, free

**Steps**:
1. Go to https://www.overleaf.com
2. Click "Register" (free account, use your email)
3. Click "New Project" → "Upload Project"
4. Select these 2 files from your `paper_draft/` folder:
   - `manuscript.tex`
   - `references.bib`
5. Overleaf uploads and compiles automatically
6. Click green "Recompile" button if needed
7. Download `manuscript.pdf` (top right corner)

**Time**: 5 minutes
**Result**: `manuscript.pdf` ready to upload

### **Option 2: Local LaTeX** (if you already have TeX installed)

```bash
cd /Users/jinsupark/jinsu-coding/petrochemical_macc_2025/paper_draft

# Compile (run 4 times for references)
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

**Result**: `manuscript.pdf` created in same folder

---

## 📤 Submission Process

### Step 1: Create Journal Account (5 min)

1. Go to: https://www.editorialmanager.com/cneu/
2. Click "Register" (top right)
3. Fill in: Name, email, affiliation, country
4. Verify email
5. Log in

### Step 2: Start New Submission (2 min)

1. Click "Submit New Manuscript"
2. Select "Original Article"
3. Confirm authorship, ethics, etc. (check all boxes)
4. Click "Next"

### Step 3: Upload Files (10 min)

**Main Manuscript**:
- Click "Choose File"
- Upload: `manuscript.pdf`
- File designation: "Main Document"

**Figures** (one at a time):
- Click "Upload Figure"
- Upload: `figure1.png` → Label as "Figure 1"
- Upload: `figure3.png` → Label as "Figure 3"
- Upload: `figure4.png` → Label as "Figure 4"
- Upload: `figure5.png` → Label as "Figure 5"
- Upload: `figure7.png` → Label as "Figure 7"
- Upload: `figureS1.png` → Label as "Supplementary Figure S1"
- Upload: `figureS2.png` → Label as "Supplementary Figure S2"

**Cover Letter**:
- Use text from `COVER_LETTER_TEMPLATE.md`
- Fill in your details (name, email, funding, reviewers)
- Paste into cover letter box OR upload as PDF

### Step 4: Enter Metadata (10 min)

**Article Information**:
- **Title**: Energy System Constraints on Industrial Decarbonization Pathways: Why Grid Capacity Favors Hydrogen Over Electrification for Petrochemical Sector
- **Abstract**: Copy from manuscript (the paragraph starting "Industrial decarbonization pathways...")
- **Keywords**: Industrial decarbonization, petrochemicals, MACC methodology, energy system constraints, hydrogen economy, electrification, South Korea, renewable energy

**Author Information**:
- **Your name**: [Fill in]
- **Affiliation**: [Your institution]
- **Email**: [Your contact email]
- **ORCID**: [Get from orcid.org if you don't have - takes 2 min to create]

**Funding**:
- Choose: "No funding" OR "Funded by [Grant name]"

**Data Availability**:
- Choose: "Upon reasonable request" OR "Available at [GitHub URL]"

**Competing Interests**:
- Select: "No competing interests"

**Suggested Reviewers**:
- Add 3-5 experts (names + emails)
- See template in `COVER_LETTER_TEMPLATE.md`

### Step 5: Review and Submit (5 min)

1. System generates PDF proof
2. Review: Check title, authors, abstract correct
3. Click "Approve PDF"
4. Click "Submit"
5. Save manuscript number (e.g., CNEU-D-25-00XXX)

**Done!** 🎉

---

## ⚡ Quick Checklist

Before submission, verify:

### Files Ready:
- [ ] `manuscript.pdf` (compiled from manuscript.tex) ⏳ **NEED TO COMPILE**
- [x] `figure1.png` through `figureS2.png` (7 files) ✅ **READY**
- [ ] Cover letter (personalized) ⏳ **FILL IN YOUR DETAILS**

### Manuscript Content:
- [ ] Your name in author line (line 17 of manuscript.tex) ⏳
- [ ] Your affiliation (line 18) ⏳
- [ ] Your email (line 19) ⏳
- [x] Abstract present ✅
- [x] All sections included ✅
- [x] References formatted ✅
- [x] Equations numbered (5 equations) ✅

### Submission Form:
- [ ] Journal account created
- [ ] Manuscript title entered
- [ ] Abstract pasted
- [ ] Keywords entered
- [ ] Your author info filled in
- [ ] Funding statement provided
- [ ] Data availability statement
- [ ] 3-5 reviewers suggested
- [ ] Competing interests: None

---

## 🎯 The Critical Part: Manuscript.tex → Manuscript.pdf

**This is the ONLY step remaining before you can submit.**

### Before You Compile:

**IMPORTANT**: Edit `manuscript.tex` to add your details:

```latex
Line 17: Replace [Your Name] with your actual name
Line 18: Replace [Your Department], [Your Institution], [City, Country]
Line 19: Replace [your.email@institution.edu] with your email
```

### Then Compile:

**Easiest way**: Overleaf
1. Upload manuscript.tex + references.bib
2. Click "Recompile"
3. Download PDF

**You'll get**: A beautiful formatted manuscript with:
- Title page with your name
- Abstract
- All sections with proper headings
- Equations numbered (1) through (5)
- Citations like "[Smith et al., 2024]"
- References at the end
- Figure placeholders showing "Figure 1", "Figure 4", etc.

---

## 📊 What the Journal Receives

### Your Submission Package:
1. `manuscript.pdf` (35-40 pages estimated)
   - Contains: All text, equations, references
   - Shows: "Figure 1", "Figure 4" as text placeholders

2. Seven PNG files:
   - `figure1.png` - Cost comparison
   - `figure3.png` - MACC curves
   - `figure4.png` - **Electricity demand (YOUR KEY FINDING)**
   - `figure5.png` - Hydrogen demand
   - `figure7.png` - Baseline structure
   - `figureS1.png` - Tech deployment (supplement)
   - `figureS2.png` - Emissions (supplement)

3. Cover letter (text or PDF)

### What Journal Does:
1. Editor reviews manuscript + cover letter
2. Assigns to 2-3 peer reviewers
3. Reviewers evaluate content, methodology, figures
4. Editor makes decision (accept/revise/reject)
5. If accepted → Production team inserts figures and typesets

**Timeline**:
- Review: 2-3 months
- Revisions: 1-2 months (if needed)
- Publication: 1-2 months after acceptance

---

## 💡 Why Separate Figures?

You might wonder: "Why not just embed figures in the PDF?"

**Reasons**:
1. **Quality**: Separate high-res files maintain quality better than PDF embedding
2. **Flexibility**: Easy to replace figures if revisions needed
3. **Production**: Typesetters need individual files to format properly
4. **Standard**: All Springer journals use this system
5. **File size**: Manuscript PDF smaller and faster to review

**Bottom line**: This is how academic publishing works. Your approach is correct!

---

## 📞 Need Help?

### If Overleaf won't compile:
- Check that both `manuscript.tex` AND `references.bib` are uploaded
- Click "Logs and output files" to see error message
- Most common: Missing reference → Add to references.bib

### If figures look wrong in PDF:
- They should NOT appear in the PDF (that's correct!)
- You'll see text like "Figure 1" where figures will go
- Journal inserts actual images later

### If you get submission errors:
- Manuscript file must be PDF (not .tex)
- Each figure must be <10 MB (yours are ~200-400 KB each, perfect)
- Cover letter can be text OR PDF (both work)

---

## ✅ Final Checklist

**Ready when**:
- [x] Figures copied to `figures_for_submission/` ✅ **DONE**
- [ ] Your details added to manuscript.tex ⏳ **5 MINUTES**
- [ ] manuscript.tex compiled → manuscript.pdf ⏳ **5 MINUTES VIA OVERLEAF**
- [ ] Cover letter personalized ⏳ **10 MINUTES**
- [ ] Journal account created ⏳ **5 MINUTES**
- [ ] Ready to upload! 🚀

**Total time remaining**: ~30 minutes

---

## 🎉 You're Almost There!

**What we've accomplished together**:
✅ Complete 5,050-word quantitative manuscript
✅ Literature-validated parameters (19 references)
✅ All 7 figures at 300 DPI ready
✅ LaTeX source formatted for journal
✅ BibTeX references prepared
✅ Cover letter template
✅ Submission guide

**What remains**:
1. Fill in your name/email in manuscript.tex (2 minutes)
2. Compile to PDF via Overleaf (5 minutes)
3. Submit to journal (20 minutes)

**The answer to your question**: Yes, upload figures separately - they're ready in `figures_for_submission/` folder. You just need to compile the manuscript PDF and you're good to go!

Ready to make academic history? 🚀
