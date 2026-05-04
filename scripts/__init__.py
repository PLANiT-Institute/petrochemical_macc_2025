"""
Secondary Scripts for Petrochemical MACC Analysis
==================================================

This package contains utility and analysis scripts that support the main
scenario engine (run_scenarios.py) and dashboard (streamlit_app.py).

Available Scripts
-----------------

Report Generation:
    generate_outputs.py
        Multi-output generator for various report formats

    generate_professional_outputs.py
        Generate CSV outputs formatted for stakeholder presentations

    generate_report_data.py
        Generate figures and tables for reports

    generate_report_tables.py
        Generate structured tables for formal reports

    generate_emission_pathways.py
        Generate emission trajectory charts and pathway visualizations

    generate_professional_figures.py
        Generate academic-quality figures for publications

Analysis Scripts:
    analysis_energy_emission.py
        One-time energy and emission analysis

    generate_ncc_stranded_asset_report.py
        Korean NCC stranded asset analysis report

    create_stranded_asset_visualizations.py
        Stranded asset visualization utilities

    check_ncc_consistency.py
        NCC data consistency validation

Usage
-----
Run scripts from the project root directory:

    python scripts/generate_outputs.py
    python scripts/generate_professional_figures.py

Note: Most scripts read from scenario_results.csv and write to outputs/
"""
