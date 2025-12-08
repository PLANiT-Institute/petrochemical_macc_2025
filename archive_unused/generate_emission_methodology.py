"""
Emission Calculation Methodology Visualization
Shows exactly how emissions are calculated for each facility
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

OUTPUT_DIR = Path('outputs/visualizations')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_methodology_figure():
    """Create comprehensive emission methodology figure"""

    fig = plt.figure(figsize=(18, 14))

    # Title
    fig.suptitle('Emission Calculation Methodology\nPetrochemical MACC Model',
                 fontsize=18, fontweight='bold', y=0.98)

    # Create grid
    gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3,
                          left=0.05, right=0.95, top=0.92, bottom=0.05)

    # ========================================
    # Panel 1: Overall Formula
    # ========================================
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')

    formula_text = """
    EMISSION CALCULATION FORMULA (Per Facility, Per Year)

    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                              │
    │   Total Emissions (tCO₂) = Σ [ Energy Consumption × Emission Factor ]                       │
    │                                                                                              │
    │   For each fuel type:                                                                        │
    │                                                                                              │
    │   Emissions_fuel = (Intensity_fuel × Capacity × 1000) × EF_fuel                              │
    │                      ↑                  ↑        ↑           ↑                               │
    │                 GJ/tonne or         kt/year   tonnes     tCO₂/GJ                             │
    │                 kWh/tonne                     per kt    or tCO₂/kWh                          │
    │                                                                                              │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
    """
    ax1.text(0.5, 0.5, formula_text, transform=ax1.transAxes, fontsize=11,
             verticalalignment='center', horizontalalignment='center',
             fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    ax1.set_title('Step 1: Core Formula', fontsize=14, fontweight='bold', loc='left')

    # ========================================
    # Panel 2: Energy Intensities
    # ========================================
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.axis('off')

    intensity_data = [
        ['Fuel Type', 'Ethylene (NCC)', 'Propylene (NCC)', 'BTX Plants', 'Polymers'],
        ['Naphtha (GJ/t)', '29.0', '25.4', '15-20', '5-10'],
        ['Electricity (kWh/t)', '21.8', '48.8', '80-120', '150-300'],
        ['LNG (GJ/t)', '4.5', '3.9', '2-4', '1-3'],
        ['Fuel Gas (GJ/t)', '5.6', '5.2', '3-5', '0-2'],
        ['Byproduct Gas (GJ/t)', '1.1', '1.2', '0-1', '0'],
    ]

    table = ax2.table(cellText=intensity_data[1:], colLabels=intensity_data[0],
                      loc='center', cellLoc='center',
                      colColours=['#4ECDC4']*5,
                      colWidths=[0.22, 0.195, 0.195, 0.195, 0.195])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Color code cells
    for i in range(1, len(intensity_data)):
        for j in range(1, 5):
            if j <= 2:  # NCC columns
                table[(i, j)].set_facecolor('#FFE5E5')
            else:
                table[(i, j)].set_facecolor('#E5FFE5')

    ax2.set_title('Step 2: Energy Intensities by Product\n(Source: Literature & Korea industry data)',
                  fontsize=12, fontweight='bold', pad=10)

    # ========================================
    # Panel 3: Emission Factors
    # ========================================
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis('off')

    ef_data = [
        ['Fuel', 'Emission Factor', 'Unit', 'Source'],
        ['Naphtha', '0.0542', 'tCO₂/GJ', 'IPCC 2019'],
        ['LNG', '0.0561', 'tCO₂/GJ', 'IPCC 2019'],
        ['Fuel Gas', '0.050', 'tCO₂/GJ', 'API 2021'],
        ['Byproduct Gas', '0.048', 'tCO₂/GJ', 'API 2021'],
        ['LPG', '0.0631', 'tCO₂/GJ', 'IPCC 2019'],
        ['Fuel Oil', '0.0773', 'tCO₂/GJ', 'IPCC 2019'],
        ['Diesel', '0.0741', 'tCO₂/GJ', 'IPCC 2019'],
        ['Electricity (2025)', '0.436', 'tCO₂/MWh', 'Korea Grid'],
        ['Electricity (2050)', '0.070', 'tCO₂/MWh', 'Korea Grid'],
        ['Green H₂', '0.0', 'tCO₂/kg', 'Assumption'],
    ]

    table2 = ax3.table(cellText=ef_data[1:], colLabels=ef_data[0],
                       loc='center', cellLoc='center',
                       colColours=['#FF6B6B']*4,
                       colWidths=[0.28, 0.22, 0.22, 0.28])
    table2.auto_set_font_size(False)
    table2.set_fontsize(10)
    table2.scale(1, 1.8)

    ax3.set_title('Step 3: Emission Factors\n(Source: IPCC 2019, API Compendium 2021)',
                  fontsize=12, fontweight='bold', pad=10)

    # ========================================
    # Panel 4: Example Calculation
    # ========================================
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.axis('off')

    example_text = """
    EXAMPLE: Ethylene Facility (1,100 kt/year capacity)
    ═══════════════════════════════════════════════════════════════

    1. NAPHTHA:
       Energy = 29.0 GJ/t × 1,100 kt × 1000 = 31,900,000 GJ/year
       Emissions = 31,900,000 × 0.0542 = 1,729,000 tCO₂ = 1.73 MtCO₂

    2. ELECTRICITY:
       Energy = 21.8 kWh/t × 1,100 kt × 1000 = 23,980,000 kWh/year
       Emissions = 23,980 MWh × 0.436 = 10,455 tCO₂ = 0.01 MtCO₂

    3. LNG:
       Energy = 4.5 GJ/t × 1,100 kt × 1000 = 4,950,000 GJ/year
       Emissions = 4,950,000 × 0.0561 = 277,695 tCO₂ = 0.28 MtCO₂

    4. FUEL GAS:
       Energy = 5.6 GJ/t × 1,100 kt × 1000 = 6,160,000 GJ/year
       Emissions = 6,160,000 × 0.050 = 308,000 tCO₂ = 0.31 MtCO₂

    ───────────────────────────────────────────────────────────────
    TOTAL = 1.73 + 0.01 + 0.28 + 0.31 + ... ≈ 2.35 MtCO₂/year
    ═══════════════════════════════════════════════════════════════
    """
    ax4.text(0.02, 0.95, example_text, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    ax4.set_title('Step 4: Example Calculation (Single Facility)',
                  fontsize=12, fontweight='bold', loc='left')

    # ========================================
    # Panel 5: Normalization & Total
    # ========================================
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')

    normalization_text = """
    NORMALIZATION TO 52 MtCO₂ BASELINE
    ═══════════════════════════════════════════════════════

    Raw Calculated Total:     58.63 MtCO₂
    Target Baseline:          52.00 MtCO₂
    Normalization Factor:     52.00 / 58.63 = 0.8869

    ───────────────────────────────────────────────────────
    Each facility emission scaled:

    Normalized_Emission = Raw_Emission × 0.8869
    ───────────────────────────────────────────────────────

    WHY NORMALIZE?
    • Match Korea National GHG Inventory (52 MtCO₂)
    • Literature energy intensities may differ from actual
    • Ensures model aligns with official statistics
    • Relative distribution among facilities preserved

    ═══════════════════════════════════════════════════════
    FINAL: 248 Facilities × Normalized = 52.00 MtCO₂ (2025)
    ═══════════════════════════════════════════════════════
    """
    ax5.text(0.02, 0.95, normalization_text, transform=ax5.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    ax5.set_title('Step 5: Normalization to Official Baseline',
                  fontsize=12, fontweight='bold', loc='left')

    plt.savefig(OUTPUT_DIR / 'fig10_emission_methodology.png', dpi=300, bbox_inches='tight')
    print("Saved: fig10_emission_methodology.png")
    plt.close()


def create_emission_flow_diagram():
    """Create emission calculation flow diagram"""

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(8, 9.5, 'Emission Calculation Flow Diagram', fontsize=16, fontweight='bold',
            ha='center', va='center')

    # Box style
    box_style = dict(boxstyle='round,pad=0.3', facecolor='lightblue', edgecolor='black', linewidth=2)
    arrow_style = dict(arrowstyle='->', color='black', lw=2)

    # Input boxes (left column)
    ax.text(2, 8, 'FACILITY DATABASE\n248 Facilities\n• Product\n• Capacity (kt/yr)\n• Location\n• Company',
            fontsize=9, ha='center', va='center', bbox=box_style)

    ax.text(2, 5.5, 'ENERGY INTENSITIES\n• Naphtha (GJ/t)\n• Electricity (kWh/t)\n• LNG (GJ/t)\n• Fuel Gas (GJ/t)\n• etc.',
            fontsize=9, ha='center', va='center', bbox=box_style)

    ax.text(2, 3, 'EMISSION FACTORS\n• IPCC 2019\n• API Compendium\n• Korea Grid EF',
            fontsize=9, ha='center', va='center', bbox=box_style)

    # Process boxes (middle)
    process_box = dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='black', linewidth=2)

    ax.text(6, 6.75, 'ENERGY CALCULATION\n\nEnergy = Intensity × Capacity × 1000\n(for each fuel type)',
            fontsize=10, ha='center', va='center', bbox=process_box)

    ax.text(10, 6.75, 'EMISSION CALCULATION\n\nEmissions = Energy × EF\n(for each fuel type)',
            fontsize=10, ha='center', va='center', bbox=process_box)

    # Output boxes (right)
    output_box = dict(boxstyle='round,pad=0.3', facecolor='lightgreen', edgecolor='black', linewidth=2)

    ax.text(14, 6.75, 'FACILITY EMISSIONS\n\nTotal = Σ Emissions\n(all fuel types)',
            fontsize=10, ha='center', va='center', bbox=output_box)

    ax.text(14, 4, 'NORMALIZATION\n\nScaled to 52 MtCO₂\n(0.8869 factor)',
            fontsize=10, ha='center', va='center', bbox=output_box)

    ax.text(14, 1.5, 'FINAL OUTPUT\n\n248 Facilities\n52.00 MtCO₂ Total',
            fontsize=10, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FF6B6B', edgecolor='black', linewidth=2))

    # Arrows
    ax.annotate('', xy=(3.5, 6.75), xytext=(2, 7.5), arrowprops=arrow_style)
    ax.annotate('', xy=(3.5, 6.75), xytext=(2, 5.5), arrowprops=arrow_style)
    ax.annotate('', xy=(8.5, 6.75), xytext=(7.5, 6.75), arrowprops=arrow_style)
    ax.annotate('', xy=(3.5, 6.5), xytext=(2, 3.5), arrowprops=arrow_style)
    ax.annotate('', xy=(12.5, 6.75), xytext=(11.5, 6.75), arrowprops=arrow_style)
    ax.annotate('', xy=(14, 5), xytext=(14, 6), arrowprops=arrow_style)
    ax.annotate('', xy=(14, 2.5), xytext=(14, 3.5), arrowprops=arrow_style)

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='lightblue', edgecolor='black', label='Input Data'),
        mpatches.Patch(facecolor='lightyellow', edgecolor='black', label='Calculation'),
        mpatches.Patch(facecolor='lightgreen', edgecolor='black', label='Output'),
        mpatches.Patch(facecolor='#FF6B6B', edgecolor='black', label='Final Result'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10)

    plt.savefig(OUTPUT_DIR / 'fig11_emission_flow.png', dpi=300, bbox_inches='tight')
    print("Saved: fig11_emission_flow.png")
    plt.close()


def create_emission_breakdown():
    """Create emission breakdown by fuel type"""

    # Data based on actual model calculation (normalized to 52 MtCO2)
    fuels = ['Naphtha', 'Fuel Gas', 'LNG', 'Byproduct Gas', 'Electricity']
    emissions = [33.7, 8.4, 7.5, 1.7, 0.7]  # MtCO2, actual calculated values
    colors = ['#E74C3C', '#2ECC71', '#3498DB', '#9B59B6', '#F39C12']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    wedges, texts, autotexts = ax1.pie(emissions, labels=fuels, autopct='%1.1f%%',
                                        colors=colors, startangle=90, explode=[0.05]*5)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    ax1.set_title('2025 Baseline Emissions by Fuel Type\nTotal: 52 MtCO₂', fontsize=14, fontweight='bold')

    # Bar chart with values
    bars = ax2.barh(fuels, emissions, color=colors, edgecolor='black', linewidth=1.2)
    for bar, val in zip(bars, emissions):
        ax2.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f} MtCO₂',
                va='center', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Emissions (MtCO₂/year)', fontsize=12, fontweight='bold')
    ax2.set_title('Emission Breakdown by Fuel Type', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, max(emissions) * 1.3)
    ax2.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig12_emission_breakdown.png', dpi=300, bbox_inches='tight')
    print("Saved: fig12_emission_breakdown.png")
    plt.close()


def main():
    print("="*60)
    print("GENERATING EMISSION METHODOLOGY VISUALIZATIONS")
    print("="*60)

    create_methodology_figure()
    create_emission_flow_diagram()
    create_emission_breakdown()

    print("\nDone!")


if __name__ == '__main__':
    main()
