"""
Centralized figure styling for the Korea Petrochemical MACC Model.

Consolidates color palettes, matplotlib rcParams, and save helpers
used across all visualization scripts.
"""

from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Okabe-Ito colorblind-friendly palette (from K-Dense skill)
# ---------------------------------------------------------------------------
OKABE_ITO_COLORS = [
    '#E69F00',  # Orange
    '#56B4E9',  # Sky Blue
    '#009E73',  # Bluish Green
    '#F0E442',  # Yellow
    '#0072B2',  # Blue
    '#D55E00',  # Vermillion
    '#CC79A7',  # Reddish Purple
    '#000000',  # Black
]


# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------

# Technology colors (used in generate_macc_visualizations, generate_emission_pathways, generate_outputs)
TECH_COLORS = {
    'Baseline': '#808080',
    'NCC-H2': '#2E86AB',
    'NCC-Electricity': '#A23B72',
    'Heat_Pump': '#C73E1D',
    'RDH': '#F18F01',
}

# Region colors (generate_emission_pathways, generate_outputs)
REGION_COLORS = {
    'Yeosu': '#1f77b4',
    'Daesan': '#ff7f0e',
    'Ulsan': '#2ca02c',
    'Other': '#d62728',
}

# Fuel colors (generate_emission_pathways)
FUEL_COLORS = {
    'Naphtha': '#8B4513',
    'LNG': '#4169E1',
    'LPG': '#32CD32',
    'Fuel_Gas': '#FFD700',
    'Byproduct_Gas': '#9370DB',
    'Fuel_Oil': '#DC143C',
    'Electricity': '#FF69B4',
}

# Accent palette (generate_professional_figures)
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#E74C3C',
    'accent1': '#3498DB',
    'accent2': '#27AE60',
    'accent3': '#F39C12',
    'accent4': '#9B59B6',
    'accent5': '#1ABC9C',
    'light_gray': '#ECF0F1',
    'medium_gray': '#BDC3C7',
}

# Scenario colors -- merged across scripts
SCENARIO_COLORS = {
    # 6-scenario (generate_professional_figures / generate_emission_pathways)
    'shaheen_ncc_h2': '#1f77b4',
    'shaheen_ncc_elec': '#aec7e8',
    'restructure_25pct_ncc_h2': '#2ca02c',
    'restructure_25pct_ncc_elec': '#98df8a',
    'restructure_40pct_ncc_h2': '#ff7f0e',
    'restructure_40pct_ncc_elec': '#ffbb78',
    # 4-scenario (generate_macc_visualizations)
    'shaheen_ncc_h2_15c': '#2E86AB',
    'shaheen_ncc_h2_20c': '#5DADE2',
    'shaheen_ncc_elec_15c': '#A23B72',
    'shaheen_ncc_elec_20c': '#D98880',
    # 8-scenario (generate_outputs)
    'shaheen_ncc_h2_flat_coupled': '#2E86AB',
    'shaheen_ncc_h2_flat_decoupled': '#5DADE2',
    'shaheen_ncc_h2_rising_coupled': '#1f77b4',
    'shaheen_ncc_h2_rising_decoupled': '#aec7e8',
    'shaheen_ncc_elec_flat_coupled': '#A23B72',
    'shaheen_ncc_elec_flat_decoupled': '#D98880',
    'shaheen_ncc_elec_rising_coupled': '#ff7f0e',
    'shaheen_ncc_elec_rising_decoupled': '#ffbb78',
}

# Company colors (generate_professional_figures)
COMPANY_COLORS = {
    'LG Chem': '#1f77b4',
    'Lotte Chemical': '#ff7f0e',
    'Yeochon NCC': '#2ca02c',
    'Hanwha TotalEnergies': '#d62728',
    'GS Caltex': '#9467bd',
    'Others': '#7f7f7f',
}

# ---------------------------------------------------------------------------
# Scenario display names -- merged across scripts
# ---------------------------------------------------------------------------

SCENARIO_NAMES = {
    # 6-scenario (generate_emission_pathways)
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_elec': 'Shaheen + NCC-Elec',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_elec': 'Restructure 25% + NCC-Elec',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_elec': 'Restructure 40% + NCC-Elec',
    # 4-scenario (generate_macc_visualizations)
    'shaheen_ncc_h2_15c': 'NCC-H2 (1.5\u00b0C)',
    'shaheen_ncc_h2_20c': 'NCC-H2 (2.0\u00b0C)',
    'shaheen_ncc_elec_15c': 'NCC-Elec (1.5\u00b0C)',
    'shaheen_ncc_elec_20c': 'NCC-Elec (2.0\u00b0C)',
    # 8-scenario (generate_outputs)
    'shaheen_ncc_h2_flat_coupled': 'NCC-H2 (Flat + Coupled)',
    'shaheen_ncc_h2_flat_decoupled': 'NCC-H2 (Flat + Decoupled)',
    'shaheen_ncc_h2_rising_coupled': 'NCC-H2 (Rising + Coupled)',
    'shaheen_ncc_h2_rising_decoupled': 'NCC-H2 (Rising + Decoupled)',
    'shaheen_ncc_elec_flat_coupled': 'NCC-Elec (Flat + Coupled)',
    'shaheen_ncc_elec_flat_decoupled': 'NCC-Elec (Flat + Decoupled)',
    'shaheen_ncc_elec_rising_coupled': 'NCC-Elec (Rising + Coupled)',
    'shaheen_ncc_elec_rising_decoupled': 'NCC-Elec (Rising + Decoupled)',
}

# Korean scenario names (generate_outputs)
SCENARIO_NAMES_KR = {
    'shaheen_ncc_h2_flat_coupled': 'NCC-H2 (\uace0\uc815 + \uc5f0\ub3d9)',
    'shaheen_ncc_h2_flat_decoupled': 'NCC-H2 (\uace0\uc815 + \ube44\uc5f0\ub3d9)',
    'shaheen_ncc_h2_rising_coupled': 'NCC-H2 (\uc0c1\uc2b9 + \uc5f0\ub3d9)',
    'shaheen_ncc_h2_rising_decoupled': 'NCC-H2 (\uc0c1\uc2b9 + \ube44\uc5f0\ub3d9)',
    'shaheen_ncc_elec_flat_coupled': 'NCC-Elec (\uace0\uc815 + \uc5f0\ub3d9)',
    'shaheen_ncc_elec_flat_decoupled': 'NCC-Elec (\uace0\uc815 + \ube44\uc5f0\ub3d9)',
    'shaheen_ncc_elec_rising_coupled': 'NCC-Elec (\uc0c1\uc2b9 + \uc5f0\ub3d9)',
    'shaheen_ncc_elec_rising_decoupled': 'NCC-Elec (\uc0c1\uc2b9 + \ube44\uc5f0\ub3d9)',
}

# Technology order for stacking (generate_macc_visualizations)
TECH_ORDER = ['Baseline', 'NCC-H2', 'NCC-Electricity', 'Heat_Pump', 'RDH']


# ---------------------------------------------------------------------------
# apply_style -- publication-quality rcParams
# ---------------------------------------------------------------------------

def apply_style():
    """Apply publication-quality matplotlib rcParams.

    Uses the K-Dense scientific-visualization skill's ``get_base_style()``
    settings (Okabe-Ito palette, tight save defaults, smaller font sizes)
    with ``figure.dpi`` overridden to 150 for interactive display.
    """
    style = {
        # Figure
        'figure.dpi': 150,               # override skill default (100)
        'figure.facecolor': 'white',
        'figure.autolayout': False,
        'figure.constrained_layout.use': True,

        # Font
        'font.size': 8,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],

        # Axes
        'axes.linewidth': 0.5,
        'axes.labelsize': 9,
        'axes.titlesize': 9,
        'axes.labelweight': 'normal',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.edgecolor': 'black',
        'axes.labelcolor': 'black',
        'axes.axisbelow': True,
        'axes.prop_cycle': mpl.cycler(color=OKABE_ITO_COLORS),
        'axes.grid': False,

        # Ticks
        'xtick.major.size': 3,
        'xtick.minor.size': 2,
        'xtick.major.width': 0.5,
        'xtick.minor.width': 0.5,
        'xtick.labelsize': 7,
        'xtick.direction': 'out',
        'ytick.major.size': 3,
        'ytick.minor.size': 2,
        'ytick.major.width': 0.5,
        'ytick.minor.width': 0.5,
        'ytick.labelsize': 7,
        'ytick.direction': 'out',

        # Lines
        'lines.linewidth': 1.5,
        'lines.markersize': 4,
        'lines.markeredgewidth': 0.5,

        # Legend
        'legend.fontsize': 7,
        'legend.frameon': False,
        'legend.loc': 'best',

        # Savefig
        'savefig.dpi': 300,
        'savefig.format': 'pdf',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'savefig.transparent': False,
        'savefig.facecolor': 'white',

        # Image
        'image.cmap': 'viridis',
        'image.aspect': 'auto',
    }
    plt.rcParams.update(style)


# ---------------------------------------------------------------------------
# save_figure -- PNG + PDF export
# ---------------------------------------------------------------------------

def save_figure(fig, output_path, dpi=300, close=True):
    """Save a matplotlib figure as PNG and PDF.

    Adopts the tight-bbox pattern from the K-Dense skill's
    ``save_publication_figure()`` for consistent whitespace handling.

    Args:
        fig: matplotlib Figure object.
        output_path: Path (or str) for the PNG file.
        dpi: Resolution for raster export (default 300).
        close: Whether to close the figure after saving (default True).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    save_kwargs = dict(
        bbox_inches='tight',
        pad_inches=0.1,
        facecolor='white',
        edgecolor='none',
    )

    # PNG
    fig.savefig(output_path, dpi=dpi, **save_kwargs)
    # PDF (same stem, .pdf suffix)
    pdf_path = output_path.with_suffix('.pdf')
    fig.savefig(pdf_path, **save_kwargs)

    if close:
        plt.close(fig)
