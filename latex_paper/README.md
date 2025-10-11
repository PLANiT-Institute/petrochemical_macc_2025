# Korean Petrochemical MACC Model - Academic Paper

This directory contains the LaTeX source files for the academic paper based on the Korean Petrochemical MACC Model.

## 📁 File Structure

```
latex_paper/
├── main.tex           # Main LaTeX document
├── references.bib     # Bibliography with all citations
└── README.md         # This file

../outputs/            # Model outputs (figures automatically linked)
├── module_01/        # Baseline emissions figures
├── module_02/        # MACC curve figures
└── module_03/        # Scenario analysis figures
```

## 🔗 Connecting to Overleaf

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub** (if not already done):
   ```bash
   git add latex_paper/
   git commit -m "Add LaTeX paper template"
   git push origin main
   ```

2. **Link Overleaf to GitHub**:
   - Go to [Overleaf](https://www.overleaf.com)
   - Click "New Project" → "Import from GitHub"
   - Select your repository: `petrochemical_macc_2025`
   - Overleaf will sync the entire repository

3. **Set Main File**:
   - In Overleaf, click "Menu" (top left)
   - Under "Main document", select: `latex_paper/main.tex`

4. **Compile**:
   - Overleaf will automatically compile the document
   - View the PDF output in the right panel

### Method 2: Direct Upload

1. Create a new project in Overleaf
2. Upload `main.tex` and `references.bib`
3. **Note**: Figures won't be available unless you also upload the `outputs/` directory

## 🖼️ Figure Integration

The paper automatically links to model output figures using relative paths:

```latex
\graphicspath{{../outputs/module_01/}{../outputs/module_02/}{../outputs/module_03/}}
```

### Available Figures

**Module 01 - Baseline Emissions**:
- `baseline_2025_by_product.png` - Emissions by product group
- `baseline_2025_by_facility.png` - Emissions by facility
- `baseline_2025_by_fuel.png` - Emissions by fuel type

**Module 02 - MACC Analysis**:
- `macc_2025.png`, `macc_2030.png`, `macc_2050.png` - MACC curves by year
- `cost_breakdown_*.png` - Technology cost decomposition
- `abatement_evolution.png` - Technology abatement over time

**Module 03 - Scenarios**:
- `emission_trajectories.png` - Emission pathways by scenario
- `technology_mix_*.png` - Technology deployment by scenario
- `cumulative_investment_*.png` - Investment requirements

### Updating Figures

When you regenerate model outputs:
1. Run the model: `python main.py`
2. New figures are saved to `outputs/`
3. If using GitHub-Overleaf sync:
   ```bash
   git add outputs/
   git commit -m "Update model outputs"
   git push
   ```
4. Overleaf will automatically sync new figures
5. Recompile the paper to see updates

## 📊 Table Data

Tables in the paper contain actual model data from the MACC analysis. To update tables with new results:

1. Check `outputs/module_02/macc_results_*.csv` for latest MACC data
2. Check `outputs/module_03/scenario_comparison.csv` for scenario results
3. Update table values in `main.tex` accordingly

## 🔨 Local Compilation

### Requirements
- TeX distribution (TeX Live, MiKTeX, or MacTeX)
- pdflatex, bibtex

### Compilation Steps

From the `latex_paper/` directory:

```bash
# First pass - generate aux files
pdflatex main.tex

# Process bibliography
bibtex main

# Second pass - resolve citations
pdflatex main.tex

# Third pass - resolve cross-references
pdflatex main.tex
```

Or use the provided script:

```bash
chmod +x compile.sh
./compile.sh
```

The output PDF will be `main.pdf`.

### Cleaning Auxiliary Files

```bash
rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz
```

## 📚 Bibliography Management

All references are stored in `references.bib`. Key citations:

- **Woo2025**: Main LCOE data source (Green Chemistry)
- **IEA2020, IEA2021NetZero**: IEA reports
- **KEEI2023, Korea10thPlan**: Korea-specific data
- **McKinsey2009, Kesicki2012**: MACC methodology
- **Technology papers**: Electric crackers, hydrogen, heat pumps, renewable energy

### Adding New References

1. Add entry to `references.bib`:
   ```bibtex
   @article{AuthorYear,
     title={Paper Title},
     author={Author Name},
     journal={Journal Name},
     year={2025}
   }
   ```

2. Cite in paper:
   ```latex
   \citep{AuthorYear}  % For (Author, Year)
   \citet{AuthorYear}  % For Author (Year)
   ```

3. Recompile with bibtex (see above)

## 📝 Paper Sections

The paper includes the following sections:

1. **Abstract**: Key findings and contributions
2. **Introduction**: Background, objectives, research gap
3. **Methodology**:
   - Baseline emissions inventory
   - Dual-methodology MACC framework
   - Scenario analysis approach
4. **Results**:
   - Baseline emissions (52 MtCO2/year)
   - MACC curve analysis by year
   - Cost breakdown and technology ranking
   - Scenario pathways (Conservative, Moderate, Aggressive)
5. **Discussion**:
   - Key findings interpretation
   - Sensitivity analysis
   - Policy implications
6. **Conclusion**: Summary and future work
7. **Appendix**: Detailed MACC calculations

## 🔄 Workflow for Paper Updates

1. **Run model** → Generates new figures in `outputs/`
2. **Review results** → Check if paper text needs updates
3. **Update LaTeX** → Modify text, update table values
4. **Commit changes**:
   ```bash
   git add latex_paper/ outputs/
   git commit -m "Update paper with new model results"
   git push
   ```
5. **Overleaf syncs** → Paper automatically updates
6. **Recompile** → Generate updated PDF

## 📞 Troubleshooting

### Figures Not Showing
- Check that `outputs/` directory exists and contains PNG files
- Verify graphicspath in main.tex matches your directory structure
- Ensure graphicx package is loaded: `\usepackage{graphicx}`

### Bibliography Not Compiling
- Run bibtex after first pdflatex pass
- Check for syntax errors in references.bib
- Ensure natbib package is loaded: `\usepackage{natbib}`

### Overleaf Sync Issues
- Check GitHub repository connection in Overleaf settings
- Manually trigger sync: Overleaf Menu → GitHub → Pull latest changes
- Verify you have write access to the repository

## 📈 Model Integration

This paper is designed to stay synchronized with the model:

- **Figures**: Automatically linked via `\graphicspath`
- **Tables**: Contains actual 2030 MACC data
- **Assumptions**: References data files in `data/` directory
- **Results**: Can be updated by rerunning model and recompiling paper

## 🎯 Next Steps

1. ✅ LaTeX template created with complete structure
2. ✅ Bibliography populated with key references
3. ✅ Figures integrated via relative paths
4. 🔄 **To Do**: Push to GitHub and connect to Overleaf
5. 🔄 **To Do**: Review and expand methodology section with detailed equations
6. 🔄 **To Do**: Add sensitivity analysis results when available
7. 🔄 **To Do**: Expand discussion with policy recommendations

## 📄 License

This paper is part of the Korean Petrochemical MACC Model project. Please ensure proper attribution when using model results or figures.
