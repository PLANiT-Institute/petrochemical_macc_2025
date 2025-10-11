# Makefile for Korean Petrochemical MACC Paper

# Main LaTeX file (without extension)
MAIN = main

# Output PDF
PDF = $(MAIN).pdf

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Compilation flags
LATEX_FLAGS = -interaction=nonstopmode

# Auxiliary files to clean
AUX_FILES = *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz *.bcf *.run.xml *.nav *.snm *.vrb

# Default target
all: $(PDF)

# Full compilation with bibliography
$(PDF): $(MAIN).tex references.bib
	@echo "=========================================="
	@echo "Compiling LaTeX Paper"
	@echo "=========================================="
	@echo "Pass 1: Generating auxiliary files..."
	@$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Processing bibliography..."
	@$(BIBTEX) $(MAIN)
	@echo "Pass 2: Resolving citations..."
	@$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Pass 3: Resolving cross-references..."
	@$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "=========================================="
	@echo "✓ Compilation successful!"
	@echo "Output: $(PDF)"
	@echo "=========================================="

# Quick compilation (no bibliography)
quick:
	@echo "Quick compilation (no bibliography)..."
	@$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

# Clean auxiliary files (keep PDF)
clean:
	@echo "Cleaning auxiliary files..."
	@rm -f $(AUX_FILES)
	@echo "✓ Cleanup complete!"

# Clean everything including PDF
cleanall: clean
	@echo "Removing PDF..."
	@rm -f $(PDF)
	@echo "✓ Full cleanup complete!"

# View PDF (Mac)
view: $(PDF)
	@open $(PDF)

# View PDF (Linux)
view-linux: $(PDF)
	@xdg-open $(PDF)

# Help message
help:
	@echo "Korean Petrochemical MACC Paper - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make           - Full compilation with bibliography (default)"
	@echo "  make quick     - Quick compilation without bibliography"
	@echo "  make clean     - Remove auxiliary files (keep PDF)"
	@echo "  make cleanall  - Remove all generated files including PDF"
	@echo "  make view      - Open PDF (Mac)"
	@echo "  make view-linux - Open PDF (Linux)"
	@echo "  make help      - Show this help message"

.PHONY: all quick clean cleanall view view-linux help
