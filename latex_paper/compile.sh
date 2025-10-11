#!/bin/bash

# LaTeX compilation script for Korean Petrochemical MACC paper
# This script compiles the paper with proper bibliography processing

echo "=========================================="
echo "Compiling LaTeX Paper"
echo "=========================================="

# Check if main.tex exists
if [ ! -f "main.tex" ]; then
    echo "ERROR: main.tex not found!"
    echo "Please run this script from the latex_paper/ directory"
    exit 1
fi

# First pass - generate aux files
echo ""
echo "Pass 1: Generating auxiliary files..."
pdflatex -interaction=nonstopmode main.tex

# Check if bibtex is needed
if [ -f "main.aux" ]; then
    echo ""
    echo "Processing bibliography..."
    bibtex main
fi

# Second pass - resolve citations
echo ""
echo "Pass 2: Resolving citations..."
pdflatex -interaction=nonstopmode main.tex

# Third pass - resolve cross-references
echo ""
echo "Pass 3: Resolving cross-references..."
pdflatex -interaction=nonstopmode main.tex

# Check if PDF was generated
if [ -f "main.pdf" ]; then
    echo ""
    echo "=========================================="
    echo "✓ Compilation successful!"
    echo "Output: main.pdf"
    echo "=========================================="

    # Optional: Open the PDF (uncomment for Mac)
    # open main.pdf

    # Optional: Open the PDF (uncomment for Linux)
    # xdg-open main.pdf
else
    echo ""
    echo "=========================================="
    echo "✗ Compilation failed!"
    echo "Check the log file for errors: main.log"
    echo "=========================================="
    exit 1
fi

# Ask if user wants to clean auxiliary files
echo ""
read -p "Clean auxiliary files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning auxiliary files..."
    rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz
    echo "✓ Cleanup complete!"
fi
