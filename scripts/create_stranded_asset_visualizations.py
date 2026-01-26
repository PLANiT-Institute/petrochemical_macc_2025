#!/usr/bin/env python3
"""
Create professional visualizations for stranded asset analysis.
Generates 6 charts as PNG files at 300 DPI.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Professional styling with colorblind-friendly palette
plt.style.use('seaborn-v0_8-whitegrid')
# Colorblind-friendly palette (IBM Design Library)
COLORS = ['#648FFF', '#785EF0', '#DC267F', '#FE6100', '#FFB000', '#009E73', '#56B4E9', '#E69F00']
sns.set_palette(COLORS)

# Common figure settings
FIGSIZE = (12, 8)
DPI = 300
TITLE_SIZE = 14
LABEL_SIZE = 12
TICK_SIZE = 10


def load_data():
    """Load all data files."""
    company_df = pd.read_csv(PROJECT_ROOT / "outputs/report_tables/table2_2_company_stranded.csv")
    regional_df = pd.read_csv(PROJECT_ROOT / "outputs/report_tables/table2_3_regional_stranded.csv")
    facility_df = pd.read_csv(PROJECT_ROOT / "outputs/professional/stranded_assets_ncc.csv")
    summary_df = pd.read_csv(PROJECT_ROOT / "outputs/stranded_assets_summary.csv")

    return company_df, regional_df, facility_df, summary_df


def format_billions(x, pos):
    """Format axis labels as billions."""
    return f'${x/1e9:.1f}B'


def create_company_bar_chart(company_df):
    """Chart 1: Company Stranded Assets Bar Chart."""
    fig, ax = plt.subplots(figsize=FIGSIZE)

    # Sort by stranded value
    df = company_df.sort_values('stranded_value_usd', ascending=True).copy()
    df = df[df['stranded_value_usd'] > 0]  # Exclude zero values

    # Create horizontal bar chart
    y_pos = np.arange(len(df))
    bars = ax.barh(y_pos, df['stranded_value_usd'], color=COLORS[0], edgecolor='white', linewidth=0.5)

    # Highlight S-Oil Shaheen (largest)
    max_idx = df['stranded_value_usd'].idxmax()
    max_pos = df.index.get_loc(max_idx)
    bars[max_pos].set_color(COLORS[2])

    # Labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['company'], fontsize=TICK_SIZE)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_billions))

    # Add value labels on bars
    for i, (v, pct) in enumerate(zip(df['stranded_value_usd'], df['share_pct'])):
        label = f'${v/1e9:.2f}B ({pct:.1f}%)'
        ax.text(v + 0.1e9, i, label, va='center', fontsize=9, color='#333333')

    # Styling
    ax.set_xlabel('Stranded Asset Value (USD Billions)', fontsize=LABEL_SIZE)
    ax.set_title('Company-Level Stranded Assets\n(1.5°C Scenario, NCC-H2 Pathway)',
                 fontsize=TITLE_SIZE, fontweight='bold', pad=20)

    # Add note for highlighted company
    ax.annotate('Highest exposure: S-Oil Shaheen\n($6.94B, 25.7% share)',
                xy=(6.94e9, len(df)-1), xytext=(4e9, len(df)-3),
                fontsize=10, color=COLORS[2],
                arrowprops=dict(arrowstyle='->', color=COLORS[2], lw=1.5))

    ax.set_xlim(0, df['stranded_value_usd'].max() * 1.3)
    plt.tight_layout()

    filepath = OUTPUT_DIR / "01_company_stranded_assets.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath


def create_regional_distribution(regional_df):
    """Chart 2: Regional Distribution Chart."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    # Combine Ulsan and Onsan into single region
    df = regional_df.copy()
    ulsan_onsan = df[df['location'].isin(['Ulsan', 'Onsan'])].agg({
        'stranded_value_usd': 'sum',
        'share_pct': 'sum'
    })
    df_combined = pd.DataFrame({
        'location': ['Yeosu', 'Ulsan/Onsan', 'Daesan'],
        'stranded_value_usd': [
            df[df['location'] == 'Yeosu']['stranded_value_usd'].values[0],
            ulsan_onsan['stranded_value_usd'],
            df[df['location'] == 'Daesan']['stranded_value_usd'].values[0]
        ],
        'share_pct': [
            df[df['location'] == 'Yeosu']['share_pct'].values[0],
            ulsan_onsan['share_pct'],
            df[df['location'] == 'Daesan']['share_pct'].values[0]
        ]
    })
    df_combined = df_combined.sort_values('stranded_value_usd', ascending=False)

    # Pie chart
    colors_pie = [COLORS[0], COLORS[1], COLORS[3]]
    wedges, texts, autotexts = ax1.pie(
        df_combined['share_pct'],
        labels=df_combined['location'],
        autopct=lambda pct: f'{pct:.1f}%',
        colors=colors_pie,
        explode=[0.02, 0.02, 0.02],
        startangle=90,
        textprops={'fontsize': 11}
    )
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
    ax1.set_title('Regional Share of\nStranded Assets', fontsize=TITLE_SIZE, fontweight='bold')

    # Horizontal bar chart
    y_pos = np.arange(len(df_combined))
    bars = ax2.barh(y_pos, df_combined['stranded_value_usd'], color=colors_pie, edgecolor='white')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(df_combined['location'], fontsize=LABEL_SIZE)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(format_billions))

    # Add value labels
    for i, v in enumerate(df_combined['stranded_value_usd']):
        ax2.text(v + 0.2e9, i, f'${v/1e9:.2f}B', va='center', fontsize=11)

    ax2.set_xlabel('Stranded Asset Value (USD Billions)', fontsize=LABEL_SIZE)
    ax2.set_title('Regional Stranded Asset Values', fontsize=TITLE_SIZE, fontweight='bold')
    ax2.set_xlim(0, df_combined['stranded_value_usd'].max() * 1.25)

    plt.suptitle('Regional Distribution of Stranded Assets', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    filepath = OUTPUT_DIR / "02_regional_distribution.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath


def create_scenario_comparison(facility_df):
    """Chart 3: Scenario Comparison (1.5°C vs 2.0°C)."""
    fig, ax = plt.subplots(figsize=FIGSIZE)

    # Calculate total stranded assets by scenario
    scenario_totals = facility_df.groupby('scenario')['total_stranded_value_million_usd'].sum().reset_index()
    scenario_totals['total_billion'] = scenario_totals['total_stranded_value_million_usd'] / 1000

    # Create readable labels
    scenario_labels = {
        'shaheen_ncc_h2_15c': 'NCC-H2\n1.5°C',
        'shaheen_ncc_h2_20c': 'NCC-H2\n2.0°C',
        'shaheen_ncc_elec_15c': 'NCC-Elec\n1.5°C',
        'shaheen_ncc_elec_20c': 'NCC-Elec\n2.0°C'
    }

    scenario_totals['label'] = scenario_totals['scenario'].map(scenario_labels)

    # Order scenarios
    order = ['shaheen_ncc_h2_15c', 'shaheen_ncc_h2_20c', 'shaheen_ncc_elec_15c', 'shaheen_ncc_elec_20c']
    scenario_totals['order'] = scenario_totals['scenario'].map({s: i for i, s in enumerate(order)})
    scenario_totals = scenario_totals.sort_values('order')

    # Create grouped bar positions
    x = np.array([0, 0.35, 1, 1.35])  # Group NCC-H2 and NCC-Elec
    colors_bar = [COLORS[0], COLORS[4], COLORS[2], COLORS[3]]  # 1.5°C darker, 2.0°C lighter

    bars = ax.bar(x, scenario_totals['total_billion'], width=0.3, color=colors_bar, edgecolor='white', linewidth=1)

    # Add value labels on bars
    for bar, val in zip(bars, scenario_totals['total_billion']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'${val:.1f}B', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # X-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_totals['label'], fontsize=LABEL_SIZE)

    # Add group labels
    ax.text(0.175, -4, 'Hydrogen Pathway', ha='center', fontsize=12, fontweight='bold')
    ax.text(1.175, -4, 'Electrification Pathway', ha='center', fontsize=12, fontweight='bold')

    # Styling
    ax.set_ylabel('Total Stranded Assets (USD Billions)', fontsize=LABEL_SIZE)
    ax.set_title('Scenario Comparison: Stranded Asset Values by Technology & Temperature Target',
                 fontsize=TITLE_SIZE, fontweight='bold', pad=20)

    # Add annotation about 1.5°C scenarios
    ax.axhline(y=scenario_totals[scenario_totals['scenario'].str.contains('15c')]['total_billion'].mean(),
               color='red', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axhline(y=scenario_totals[scenario_totals['scenario'].str.contains('20c')]['total_billion'].mean(),
               color='orange', linestyle='--', alpha=0.5, linewidth=1.5)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS[0], label='1.5°C Target (H2)'),
        Patch(facecolor=COLORS[4], label='2.0°C Target (H2)'),
        Patch(facecolor=COLORS[2], label='1.5°C Target (Elec)'),
        Patch(facecolor=COLORS[3], label='2.0°C Target (Elec)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    ax.set_ylim(0, scenario_totals['total_billion'].max() * 1.2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))

    plt.tight_layout()

    filepath = OUTPUT_DIR / "03_scenario_comparison.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath


def create_transition_timeline(facility_df):
    """Chart 4: Transition Timeline."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    scenarios = [
        ('shaheen_ncc_h2_15c', 'NCC-H2 (1.5°C)'),
        ('shaheen_ncc_h2_20c', 'NCC-H2 (2.0°C)'),
        ('shaheen_ncc_elec_15c', 'NCC-Elec (1.5°C)'),
        ('shaheen_ncc_elec_20c', 'NCC-Elec (2.0°C)')
    ]

    for ax, (scenario, title) in zip(axes.flat, scenarios):
        df = facility_df[facility_df['scenario'] == scenario].copy()

        # Count facilities by transition year
        year_counts = df.groupby('transition_year').agg({
            'capacity_ktpy': 'sum',
            'total_stranded_value_million_usd': 'sum'
        }).reset_index()

        # Bar chart for capacity transitioning
        bars = ax.bar(year_counts['transition_year'],
                     year_counts['capacity_ktpy'],
                     color=COLORS[0] if 'h2' in scenario else COLORS[2],
                     alpha=0.8, edgecolor='white')

        ax.set_xlabel('Transition Year', fontsize=TICK_SIZE)
        ax.set_ylabel('Capacity (kt/yr)', fontsize=TICK_SIZE)
        ax.set_title(title, fontsize=12, fontweight='bold')

        # Highlight 2026 immediate transitions for elec scenarios
        if 'elec' in scenario:
            for bar in bars:
                if bar.get_x() < 2027:
                    bar.set_color(COLORS[2])
                    bar.set_alpha(1.0)

        ax.set_xlim(2024, 2052)
        ax.tick_params(axis='both', labelsize=TICK_SIZE)

        # Add cumulative line
        ax2 = ax.twinx()
        cumulative = year_counts['capacity_ktpy'].cumsum()
        ax2.plot(year_counts['transition_year'], cumulative,
                color=COLORS[3], linewidth=2, marker='o', markersize=4)
        ax2.set_ylabel('Cumulative Capacity (kt/yr)', fontsize=TICK_SIZE, color=COLORS[3])
        ax2.tick_params(axis='y', labelcolor=COLORS[3], labelsize=TICK_SIZE)

    plt.suptitle('Transition Timeline by Scenario\nCapacity Transitioning per Year',
                 fontsize=TITLE_SIZE, fontweight='bold', y=1.02)
    plt.tight_layout()

    filepath = OUTPUT_DIR / "04_transition_timeline.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath


def create_capacity_heatmap(facility_df):
    """Chart 5: Capacity Distribution Heatmap."""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Use one scenario for capacity distribution (capacity same across scenarios)
    df = facility_df[facility_df['scenario'] == 'shaheen_ncc_h2_15c'].copy()

    # Create pivot table
    pivot = df.pivot_table(
        values='capacity_ktpy',
        index='region',
        columns='product',
        aggfunc='sum',
        fill_value=0
    )

    # Reorder columns
    col_order = ['Ethylene', 'Propylene', 'Butadiene', 'C-H']
    pivot = pivot[[c for c in col_order if c in pivot.columns]]

    # Create heatmap
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd',
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'Capacity (kt/yr)', 'shrink': 0.8},
                ax=ax)

    ax.set_xlabel('Product', fontsize=LABEL_SIZE)
    ax.set_ylabel('Region', fontsize=LABEL_SIZE)
    ax.set_title('Capacity Distribution by Region and Product\n(kt/yr)',
                 fontsize=TITLE_SIZE, fontweight='bold', pad=20)

    # Rotate x labels
    plt.xticks(rotation=0, fontsize=TICK_SIZE)
    plt.yticks(rotation=0, fontsize=TICK_SIZE)

    plt.tight_layout()

    filepath = OUTPUT_DIR / "05_capacity_heatmap.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath


def create_cost_breakdown(facility_df):
    """Chart 6: Book Value vs Abandonment Cost Breakdown."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    # Aggregate by company for 1.5°C scenario
    df = facility_df[facility_df['scenario'] == 'shaheen_ncc_h2_15c'].copy()

    company_costs = df.groupby('company').agg({
        'book_value_million_usd': 'sum',
        'abandonment_cost_million_usd': 'sum',
        'total_stranded_value_million_usd': 'sum'
    }).reset_index()

    # Sort by total value and take top 10
    company_costs = company_costs.sort_values('total_stranded_value_million_usd', ascending=False).head(10)

    # Stacked horizontal bar chart
    y_pos = np.arange(len(company_costs))

    # Plot book value
    bars1 = ax1.barh(y_pos, company_costs['book_value_million_usd'],
                     color=COLORS[0], label='Book Value', edgecolor='white')
    # Plot abandonment cost (stacked)
    bars2 = ax1.barh(y_pos, company_costs['abandonment_cost_million_usd'],
                     left=company_costs['book_value_million_usd'],
                     color=COLORS[3], label='Abandonment Cost', edgecolor='white')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(company_costs['company'], fontsize=TICK_SIZE)
    ax1.set_xlabel('Value (Million USD)', fontsize=LABEL_SIZE)
    ax1.set_title('Top 10 Companies: Cost Breakdown', fontsize=12, fontweight='bold')
    ax1.legend(loc='lower right', fontsize=10)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x/1000:.1f}B'))

    # Pie chart for overall breakdown
    total_book = df['book_value_million_usd'].sum()
    total_abandon = df['abandonment_cost_million_usd'].sum()

    sizes = [total_book, total_abandon]
    labels = [f'Book Value\n${total_book/1000:.1f}B\n({total_book/(total_book+total_abandon)*100:.1f}%)',
              f'Abandonment Cost\n${total_abandon/1000:.1f}B\n({total_abandon/(total_book+total_abandon)*100:.1f}%)']

    wedges, texts = ax2.pie(sizes, labels=labels, colors=[COLORS[0], COLORS[3]],
                            startangle=90, textprops={'fontsize': 11},
                            explode=[0.02, 0.05])

    ax2.set_title('Overall Cost Composition\n(NCC-H2, 1.5°C Scenario)', fontsize=12, fontweight='bold')

    plt.suptitle('Book Value vs Abandonment Cost Analysis', fontsize=TITLE_SIZE, fontweight='bold', y=1.02)
    plt.tight_layout()

    filepath = OUTPUT_DIR / "06_cost_breakdown.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath


def main():
    """Generate all visualizations."""
    print("Loading data...")
    company_df, regional_df, facility_df, summary_df = load_data()

    print("\nCreating visualizations...")

    # Generate all charts
    files = []
    files.append(create_company_bar_chart(company_df))
    files.append(create_regional_distribution(regional_df))
    files.append(create_scenario_comparison(facility_df))
    files.append(create_transition_timeline(facility_df))
    files.append(create_capacity_heatmap(facility_df))
    files.append(create_cost_breakdown(facility_df))

    print(f"\nAll {len(files)} visualizations saved to: {OUTPUT_DIR}")

    # Verify files exist
    print("\nVerifying files...")
    for f in files:
        if Path(f).exists():
            size_kb = Path(f).stat().st_size / 1024
            print(f"  OK: {Path(f).name} ({size_kb:.1f} KB)")
        else:
            print(f"  ERROR: {Path(f).name} not found!")

    return files


if __name__ == "__main__":
    main()
