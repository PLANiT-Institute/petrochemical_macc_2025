# GitHub Repository Upload Instructions

## Files Created

✅ **ZIP file ready**: `petrochemical_macc_model_v1.0.zip` (1.7 MB)
📍 **Location**: `/Users/jinsupark/jinsu-coding/petrochemical_macc_2025/`

## What's Included

```
petrochemical_macc_model_v1.0.zip
├── README.md                          ← Professional GitHub README
├── LICENSE                            ← MIT License
├── requirements.txt                   ← Python dependencies
├── MODEL_DOCUMENTATION.md             ← Technical documentation
├── run_all_scenarios_v3.py           ← Main execution script
├── generate_professional_figures.py   ← Figure generation
│
├── data/                              ← All input parameters
│   ├── technology_parameters.csv      ← Tech CAPEX, OPEX, efficiency
│   ├── energy_intensities.csv
│   ├── fuel_price_trajectory.csv
│   ├── h2_price_trajectory_corrected.csv
│   ├── re_price_trajectory_corrected.csv
│   ├── grid_price_trajectory.csv
│   ├── facility_database.csv
│   └── ... (15 CSV files total)
│
├── modules/                           ← Core model code
│   ├── macc.py                        ← MACC calculation engine
│   ├── baseline.py                    ← Baseline emissions
│   ├── data_manager.py                ← Data loading/processing
│   ├── optimization_v2.py             ← Scenario optimization
│   └── utils.py                       ← Utility functions
│
└── outputs/figures/                   ← Publication figures
    ├── figure1.png                    ← Cumulative costs
    ├── figure3.png                    ← MACC comparison
    ├── figure4.png                    ← Energy demands
    ├── figure5.png                    ← Feasibility assessment
    ├── figure7.png                    ← Baseline emissions
    ├── figureS1.png                   ← Supplementary 1
    └── figureS2.png                   ← Supplementary 2
```

---

## Step-by-Step Upload Instructions

### Option A: Create New GitHub Repository (RECOMMENDED)

#### 1. Create Repository on GitHub.com

1. Go to https://github.com
2. Click **"New repository"** (green button, top right)
3. Fill in:
   - **Repository name**: `petrochemical-macc-2025` (or your preferred name)
   - **Description**: "Facility-level MACC model for petrochemical decarbonization (Carbon Neutrality journal, 2025)"
   - **Public** ✅ (required for open access journal)
   - **Add a README file**: ❌ NO (we have our own)
   - **Add .gitignore**: ❌ NO
   - **Choose a license**: ❌ NO (we have MIT License included)
4. Click **"Create repository"**

#### 2. Upload ZIP Contents

**Method 1: Web Upload (Easiest, 5 minutes)**

1. On your new repository page, click **"uploading an existing file"** link
2. Extract `petrochemical_macc_model_v1.0.zip` on your computer
3. Drag ALL files from the extracted `github_release_package` folder into GitHub
4. Add commit message: "Initial release v1.0 - Model code and data for Carbon Neutrality paper"
5. Click **"Commit changes"**

**Method 2: Command Line (If you prefer)**

```bash
# Navigate to the package folder
cd /Users/jinsupark/jinsu-coding/petrochemical_macc_2025
unzip petrochemical_macc_model_v1.0.zip
cd github_release_package

# Initialize git
git init
git add .
git commit -m "Initial release v1.0 - Model code and data for Carbon Neutrality paper"

# Connect to GitHub (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/petrochemical-macc-2025.git
git branch -M main
git push -u origin main
```

#### 3. Create a Release (For DOI later)

1. On GitHub repo page, click **"Releases"** (right sidebar)
2. Click **"Create a new release"**
3. Fill in:
   - **Tag version**: `v1.0`
   - **Release title**: `v1.0 - Initial Publication Release`
   - **Description**:
     ```
     Model code and data accompanying the paper:

     "Beyond Partial Equilibrium: Why Technology Costs and Energy System
     Constraints Diverge in Industrial Decarbonization Pathways"

     Published in Carbon Neutrality (Springer Nature), 2025

     Author: Jinsu Park, Plan/It Institute

     This release contains:
     - Full MACC model code (Python)
     - Input parameters and data
     - 6-scenario analysis results
     - Publication-quality figures
     ```
4. Click **"Publish release"**

---

### Option B: Link to Zenodo for DOI (BEST PRACTICE, +5 minutes)

If you want a permanent DOI:

1. Complete Option A above
2. Go to https://zenodo.org
3. Sign in with GitHub account
4. Go to **"Settings"** → **"GitHub"**
5. Find your `petrochemical-macc-2025` repository
6. Click **"ON"** to enable Zenodo archiving
7. Go back to GitHub and create a new release (see Step 3 above)
8. Zenodo will automatically:
   - Archive the release
   - Generate a DOI (e.g., 10.5281/zenodo.xxxxxx)
   - Create a badge you can add to README

---

## After Upload: Update Manuscript

Once you have your GitHub URL, send it to me and I'll update the LaTeX manuscript's Data Availability section.

### Current Placeholder (Line 413):
```latex
The MACC model code, input parameters, and scenario results are available on
GitHub at \url{https://github.com/[to-be-added]}.
```

### Will Update To:

**If GitHub only:**
```latex
The MACC model code, input parameters, and scenario results are available on
GitHub at \url{https://github.com/YOUR-USERNAME/petrochemical-macc-2025}.
```

**If GitHub + Zenodo (RECOMMENDED):**
```latex
The MACC model code, input parameters, and scenario results are archived at
Zenodo: \url{https://doi.org/10.5281/zenodo.XXXXXX} with development
repository at \url{https://github.com/YOUR-USERNAME/petrochemical-macc-2025}.
```

---

## What to Share With Me

Once you've uploaded to GitHub, just send me:

1. **GitHub repository URL** (e.g., `https://github.com/yourname/petrochemical-macc-2025`)
2. **Zenodo DOI** (optional, if you set it up)

I'll then:
- ✅ Update `manuscript.tex` line 413
- ✅ Recompile the PDF
- ✅ Verify all links work
- ✅ Confirm submission readiness

---

## Estimated Time

- **GitHub upload only**: 5-10 minutes
- **GitHub + Zenodo DOI**: 10-15 minutes total
- **LaTeX update + recompile**: 2 minutes (I'll do this)

---

## Notes

- ✅ ZIP file is **1.7 MB** (well under GitHub's limits)
- ✅ **No sensitive data** included (all public sources)
- ✅ **MIT License** included (open source)
- ✅ **Professional README** with citations, usage instructions
- ✅ **All publication figures** included (300 DPI PNG)
- ✅ **Model documentation** included

---

## Questions?

If you need help with any step, just let me know!

**Next steps:**
1. You: Create GitHub repo and upload
2. You: Share the URL with me
3. Me: Update manuscript.tex Data Availability section
4. Me: Recompile PDF
5. You: **Submit to Carbon Neutrality!** 🚀
