#!/usr/bin/env python3
"""
Supply Chain Visualization for Korean Petrochemical Facilities
Shows upstream -> downstream relationships by complex
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Setup
plt.rcParams['font.size'] = 9
plt.rcParams['figure.facecolor'] = 'white'

# Load data
data_dir = Path(__file__).parent.parent / 'data'
df = pd.read_csv(data_dir / 'facility_database_with_regions.csv')

# Output directory
output_dir = Path(__file__).parent.parent / 'outputs' / 'supply_chain_visualization'
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================
# SUPPLY CHAIN DEFINITIONS
# ============================================
supply_chain = {
    'Ethylene': ['LDPE', 'L-LDPE', 'HDPE', 'EDC', 'EG', 'SM', 'Ethanol', 'Acetic Acid', 'Vinyl Acetate', 'EPDM'],
    'Propylene': ['PP', 'AN', 'Phenol', 'Acetone', 'Octanol', 'Butanol', 'PPG', 'CPLM'],
    'Butadiene': ['SBR', 'S-SBR', 'BR', 'NBR', 'EPDM', 'ABS', 'SB-Latex'],
    'C-H': ['CPLM'],
    'Benzene': ['SM', 'Phenol', 'Acetone', 'CPLM', 'Alkylbenzene', 'MDI', 'TDI', 'AN'],
    'Toluene': ['TDI'],
    'Xylene': ['P-X', 'O-X', 'M-X'],
    'P-X': ['TPA', 'PIA', 'DMT'],
    'O-X': ['PA', 'MA'],
    'M-X': ['P-X'],
    'SM': ['PS', 'EPS', 'ABS', 'SB-Latex'],
    'EDC': ['VCM'],
    'VCM': ['PVC'],
    'Phenol': ['BPA', 'Epoxy Resin'],
    'Acetone': ['BPA', 'MMA'],
    'BPA': ['PC', 'Epoxy Resin'],
    'AN': ['ABS', 'NBR', 'NB-Latex'],
    'MMA': ['PMMA'],
}

# Category colors
category_colors = {
    'Primary Olefin': '#E74C3C',      # Red
    'Aromatics': '#F39C12',            # Orange
    'Intermediate': '#3498DB',         # Blue
    'Polymer': '#2ECC71',              # Green
    'Synthetic Rubber': '#9B59B6',     # Purple
    'Polyurethane/Resin': '#1ABC9C',   # Teal
    'Other': '#95A5A6'                 # Gray
}

def get_category(prod):
    if prod in ['Ethylene', 'Propylene', 'Butadiene', 'C-H']:
        return 'Primary Olefin'
    elif prod in ['Benzene', 'Toluene', 'Xylene', 'P-X', 'O-X', 'M-X']:
        return 'Aromatics'
    elif prod in ['SM', 'EDC', 'VCM', 'Phenol', 'Acetone', 'BPA', 'AN', 'MMA', 'EG', 'TPA']:
        return 'Intermediate'
    elif prod in ['LDPE', 'L-LDPE', 'HDPE', 'PP', 'PVC', 'PS', 'EPS', 'ABS', 'PC', 'PMMA']:
        return 'Polymer'
    elif prod in ['SBR', 'S-SBR', 'BR', 'NBR', 'NB-Latex', 'SB-Latex', 'EPDM']:
        return 'Synthetic Rubber'
    elif prod in ['TDI', 'MDI', 'PPG', 'Epoxy Resin']:
        return 'Polyurethane/Resin'
    else:
        return 'Other'


# ============================================
# Figure 1: Supply Chain Flow Diagram (Simplified)
# ============================================
def draw_supply_chain_overview():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define positions for each level
    levels = {
        0: ['Naphtha/Refinery'],
        1: ['Ethylene', 'Propylene', 'Butadiene', 'Benzene', 'Toluene', 'Xylene'],
        2: ['SM', 'EDC', 'Phenol', 'AN', 'P-X', 'O-X'],
        3: ['VCM', 'BPA', 'MMA', 'TPA'],
        4: ['PE Family', 'PP', 'PVC', 'PS/ABS', 'PC/Epoxy', 'Rubber', 'TDI/MDI', 'TPA/EG']
    }

    # Draw nodes
    node_positions = {}
    for level, products in levels.items():
        x = level * 2 + 1
        n = len(products)
        for i, prod in enumerate(products):
            y = 9 - (i * 8 / max(n-1, 1)) if n > 1 else 5
            node_positions[prod] = (x, y)

            if level == 0:
                color = '#34495E'
            else:
                color = category_colors.get(get_category(prod), '#95A5A6')

            bbox = dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.8, edgecolor='white')
            ax.text(x, y, prod, fontsize=9, ha='center', va='center',
                   bbox=bbox, color='white', fontweight='bold')

    # Draw arrows (simplified)
    arrows = [
        ('Naphtha/Refinery', 'Ethylene'),
        ('Naphtha/Refinery', 'Propylene'),
        ('Naphtha/Refinery', 'Butadiene'),
        ('Naphtha/Refinery', 'Benzene'),
        ('Naphtha/Refinery', 'Toluene'),
        ('Naphtha/Refinery', 'Xylene'),
        ('Ethylene', 'SM'), ('Ethylene', 'EDC'),
        ('Propylene', 'Phenol'), ('Propylene', 'AN'),
        ('Benzene', 'SM'), ('Benzene', 'Phenol'),
        ('Xylene', 'P-X'), ('Xylene', 'O-X'),
        ('SM', 'PS/ABS'), ('EDC', 'VCM'), ('Phenol', 'BPA'),
        ('AN', 'PS/ABS'), ('P-X', 'TPA'),
        ('VCM', 'PVC'), ('BPA', 'PC/Epoxy'),
        ('Ethylene', 'PE Family'), ('Propylene', 'PP'),
        ('Butadiene', 'Rubber'), ('Toluene', 'TDI/MDI'),
    ]

    for start, end in arrows:
        if start in node_positions and end in node_positions:
            x1, y1 = node_positions[start]
            x2, y2 = node_positions[end]
            ax.annotate('', xy=(x2-0.3, y2), xytext=(x1+0.3, y1),
                       arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5, lw=1))

    # Title and legend
    ax.set_title('Korean Petrochemical Supply Chain Overview', fontsize=14, fontweight='bold', pad=20)

    # Add level labels
    level_labels = ['Feedstock', 'Primary', 'Intermediate 1', 'Intermediate 2', 'Final Products']
    for i, label in enumerate(level_labels):
        ax.text(i*2 + 1, 9.8, label, fontsize=10, ha='center', va='bottom', style='italic')

    # Legend
    legend_elements = [mpatches.Patch(facecolor=color, label=cat, alpha=0.8)
                       for cat, color in category_colors.items() if cat != 'Other']
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8)

    plt.tight_layout()
    plt.savefig(output_dir / '01_supply_chain_overview.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: 01_supply_chain_overview.png')


# ============================================
# Figure 2: Supply Chain by Complex
# ============================================
def draw_complex_supply_chain():
    complexes = ['Ulsan Complex', 'Yeosu Complex', 'Daesan Complex', 'Other Regions']

    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    for idx, complex_name in enumerate(complexes):
        ax = axes[idx // 2, idx % 2]
        complex_df = df[df['complex'] == complex_name]

        # Get products in this complex
        products = complex_df['product'].unique()

        # Organize by supply chain level
        level_0 = [p for p in products if p in ['Ethylene', 'Propylene', 'Butadiene', 'C-H']]
        level_1 = [p for p in products if p in ['Benzene', 'Toluene', 'Xylene', 'P-X', 'O-X', 'M-X']]
        level_2 = [p for p in products if p in ['SM', 'EDC', 'VCM', 'Phenol', 'Acetone', 'AN', 'BPA', 'MMA', 'EG', 'TPA', 'PIA', 'DMT']]
        level_3 = [p for p in products if p not in level_0 + level_1 + level_2]

        all_levels = [level_0, level_1, level_2, level_3]
        level_names = ['Naphtha Cracker', 'BTX/Aromatics', 'Intermediate', 'Final Products']

        ax.set_xlim(-0.5, 3.5)
        max_items = max(len(l) for l in all_levels) if all_levels else 1
        ax.set_ylim(-0.5, max_items + 0.5)
        ax.axis('off')

        # Draw products
        for level_idx, (level_prods, level_name) in enumerate(zip(all_levels, level_names)):
            # Level label
            ax.text(level_idx, max_items + 0.3, level_name, fontsize=8, ha='center',
                   va='bottom', style='italic', color='gray')

            for i, prod in enumerate(sorted(level_prods)):
                cap = complex_df[complex_df['product'] == prod]['capacity_kt'].sum()
                color = category_colors.get(get_category(prod), '#95A5A6')

                # Size based on capacity
                fontsize = 7 + min(cap / 1000, 3)

                bbox = dict(boxstyle='round,pad=0.2', facecolor=color, alpha=0.7, edgecolor='white')
                ax.text(level_idx, max_items - i - 0.5, f'{prod}\n({cap:,.0f}kt)',
                       fontsize=fontsize, ha='center', va='center',
                       bbox=bbox, color='white')

        # Draw connections
        for up_prod in level_0 + level_1 + level_2:
            if up_prod not in products:
                continue
            downstream_prods = supply_chain.get(up_prod, [])
            for down_prod in downstream_prods:
                if down_prod in products:
                    # Find positions
                    for src_level, src_prods in enumerate(all_levels):
                        if up_prod in src_prods:
                            src_y = max_items - sorted(src_prods).index(up_prod) - 0.5
                            break
                    for dst_level, dst_prods in enumerate(all_levels):
                        if down_prod in dst_prods:
                            dst_y = max_items - sorted(dst_prods).index(down_prod) - 0.5
                            break

                    ax.annotate('', xy=(dst_level - 0.2, dst_y),
                               xytext=(src_level + 0.2, src_y),
                               arrowprops=dict(arrowstyle='->', color='gray',
                                             alpha=0.3, lw=0.5, connectionstyle='arc3,rad=0.1'))

        # Title
        total_cap = complex_df['capacity_kt'].sum()
        n_facilities = len(complex_df)
        ax.set_title(f'{complex_name}\n({n_facilities} facilities, {total_cap:,.0f} kt total)',
                    fontsize=11, fontweight='bold')

    plt.suptitle('Supply Chain Structure by Complex', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / '02_supply_chain_by_complex.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: 02_supply_chain_by_complex.png')


# ============================================
# Figure 3: Upstream-Downstream Capacity Balance
# ============================================
def draw_capacity_balance():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))

    # Key supply chain pairs to analyze
    pairs = [
        ('Ethylene', ['LDPE', 'L-LDPE', 'HDPE'], 'Ethylene → PE'),
        ('Propylene', ['PP'], 'Propylene → PP'),
        ('Butadiene', ['SBR', 'S-SBR', 'BR', 'NBR', 'EPDM'], 'Butadiene → Rubber'),
        ('Benzene', ['SM'], 'Benzene → SM'),
        ('SM', ['PS', 'EPS', 'ABS'], 'SM → Styrene Products'),
        ('EDC', ['VCM'], 'EDC → VCM → PVC'),
    ]

    for idx, (upstream, downstreams, title) in enumerate(pairs):
        ax = axes[idx // 3, idx % 3]

        complexes = ['Ulsan Complex', 'Yeosu Complex', 'Daesan Complex']
        x = np.arange(len(complexes))
        width = 0.35

        up_caps = []
        down_caps = []

        for comp in complexes:
            comp_df = df[df['complex'] == comp]
            up_cap = comp_df[comp_df['product'] == upstream]['capacity_kt'].sum()
            down_cap = comp_df[comp_df['product'].isin(downstreams)]['capacity_kt'].sum()
            up_caps.append(up_cap)
            down_caps.append(down_cap)

        bars1 = ax.bar(x - width/2, up_caps, width, label=upstream, color='#3498DB')
        bars2 = ax.bar(x + width/2, down_caps, width, label='+'.join(downstreams), color='#E74C3C')

        ax.set_ylabel('Capacity (kt)')
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['Ulsan', 'Yeosu', 'Daesan'], fontsize=8)
        ax.legend(fontsize=7)

        # Add value labels
        for bar in bars1:
            if bar.get_height() > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                       f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=7)
        for bar in bars2:
            if bar.get_height() > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                       f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=7)

    plt.suptitle('Upstream vs Downstream Capacity by Complex', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / '03_capacity_balance.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: 03_capacity_balance.png')


# ============================================
# Figure 4: Supply Chain Heatmap
# ============================================
def draw_supply_chain_heatmap():
    # Create adjacency matrix
    products = sorted(df['product'].unique())
    n = len(products)
    adjacency = np.zeros((n, n))

    for i, up in enumerate(products):
        for j, down in enumerate(products):
            if down in supply_chain.get(up, []):
                adjacency[i, j] = 1

    # Only show products that have connections
    has_connection = np.any(adjacency, axis=0) | np.any(adjacency, axis=1)
    connected_products = [p for i, p in enumerate(products) if has_connection[i]]
    connected_idx = [i for i, p in enumerate(products) if has_connection[i]]
    connected_matrix = adjacency[np.ix_(connected_idx, connected_idx)]

    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(connected_matrix, cmap='Blues', aspect='auto')

    ax.set_xticks(np.arange(len(connected_products)))
    ax.set_yticks(np.arange(len(connected_products)))
    ax.set_xticklabels(connected_products, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(connected_products, fontsize=8)

    ax.set_xlabel('Downstream Product', fontsize=10)
    ax.set_ylabel('Upstream Product', fontsize=10)
    ax.set_title('Supply Chain Adjacency Matrix\n(1 = Direct Supply Relationship)', fontsize=12, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Connection (0=No, 1=Yes)')

    plt.tight_layout()
    plt.savefig(output_dir / '04_supply_chain_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: 04_supply_chain_heatmap.png')


# ============================================
# Figure 5: Product Category Sankey-style
# ============================================
def draw_category_flow():
    fig, ax = plt.subplots(figsize=(14, 8))

    categories = ['Primary Olefin', 'Aromatics', 'Intermediate', 'Polymer', 'Synthetic Rubber', 'Polyurethane/Resin', 'Other']

    # Calculate capacity by category
    cat_capacity = {}
    for cat in categories:
        prods = [p for p in df['product'].unique() if get_category(p) == cat]
        cat_capacity[cat] = df[df['product'].isin(prods)]['capacity_kt'].sum()

    # Draw horizontal bars for each category
    y_positions = np.arange(len(categories))
    colors = [category_colors.get(cat, '#95A5A6') for cat in categories]
    capacities = [cat_capacity.get(cat, 0) for cat in categories]

    bars = ax.barh(y_positions, capacities, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(categories)
    ax.set_xlabel('Total Capacity (kt/year)')
    ax.set_title('Production Capacity by Product Category', fontsize=12, fontweight='bold')

    # Add value labels
    for bar, cap in zip(bars, capacities):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
               f'{cap:,.0f} kt', va='center', fontsize=9)

    # Add flow arrows between categories
    flows = [
        (0, 2, 'Ethylene→SM, EDC'),  # Primary Olefin → Intermediate
        (1, 2, 'Benzene→SM, Phenol'),  # Aromatics → Intermediate
        (2, 3, 'SM→PS, VCM→PVC'),  # Intermediate → Polymer
        (0, 3, 'Ethylene→PE, Propylene→PP'),  # Primary → Polymer (direct)
        (0, 4, 'Butadiene→Rubber'),  # Primary → Rubber
    ]

    plt.tight_layout()
    plt.savefig(output_dir / '05_category_capacity.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: 05_category_capacity.png')


# ============================================
# Run all visualizations
# ============================================
if __name__ == '__main__':
    print('Generating supply chain visualizations...\n')

    draw_supply_chain_overview()
    draw_complex_supply_chain()
    draw_capacity_balance()
    draw_supply_chain_heatmap()
    draw_category_flow()

    print('\n' + '='*50)
    print('All visualizations saved to:')
    print(f'  {output_dir}')
    print('='*50)
