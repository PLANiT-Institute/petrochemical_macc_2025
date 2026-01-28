#!/usr/bin/env python3
"""
Create professional visualizations for stranded asset analysis.
Generates 6 charts as PNG files at 300 DPI.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.utils import save_figure_data
from modules.figure_style import apply_style, save_figure

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

apply_style()
# Colorblind-friendly palette (IBM Design Library) -- specific to this script
CHART_PALETTE = ['#648FFF', '#785EF0', '#DC267F', '#FE6100', '#FFB000', '#009E73', '#56B4E9', '#E69F00']
sns.set_palette(CHART_PALETTE)

# Common figure settings
FIGSIZE = (12, 8)
DPI = 300


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
    bars = ax.barh(y_pos, df['stranded_value_usd'], color=CHART_PALETTE[0], edgecolor='white', linewidth=0.5)

    # Highlight S-Oil Shaheen (largest)
    max_idx = df['stranded_value_usd'].idxmax()
    max_pos = df.index.get_loc(max_idx)
    bars[max_pos].set_color(CHART_PALETTE[2])

    # Labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['company'], fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_billions))

    # Add value labels on bars
    for i, (v, pct) in enumerate(zip(df['stranded_value_usd'], df['share_pct'])):
        label = f'${v/1e9:.2f}B ({pct:.1f}%)'
        ax.text(v + 0.1e9, i, label, va='center', fontsize=9, color='#333333')

    # Styling
    ax.set_xlabel('Stranded Asset Value (USD Billions)', fontsize=12)
    ax.set_title('Company-Level Stranded Assets\n(1.5°C Scenario, NCC-H2 Pathway)',
                 fontsize=14, fontweight='bold', pad=20)

    # Add note for highlighted company
    ax.annotate('Highest exposure: S-Oil Shaheen\n($6.94B, 25.7% share)',
                xy=(6.94e9, len(df)-1), xytext=(4e9, len(df)-3),
                fontsize=10, color=CHART_PALETTE[2],
                arrowprops=dict(arrowstyle='->', color=CHART_PALETTE[2], lw=1.5))

    ax.set_xlim(0, df['stranded_value_usd'].max() * 1.3)
    filepath = OUTPUT_DIR / "01_company_stranded_assets.png"
    save_figure(plt.gcf(), filepath, dpi=DPI)
    print(f"Saved: {filepath}")
    # CSV export
    tidy = df[['company', 'stranded_value_usd', 'share_pct']].copy()
    tidy = tidy.rename(columns={'company': 'category', 'stranded_value_usd': 'value'})
    tidy['unit'] = 'USD'
    save_figure_data(tidy, filepath, figure_type='bar')
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
    colors_pie = [CHART_PALETTE[0], CHART_PALETTE[1], CHART_PALETTE[3]]
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
    ax1.set_title('Regional Share of\nStranded Assets', fontsize=14, fontweight='bold')

    # Horizontal bar chart
    y_pos = np.arange(len(df_combined))
    bars = ax2.barh(y_pos, df_combined['stranded_value_usd'], color=colors_pie, edgecolor='white')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(df_combined['location'], fontsize=12)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(format_billions))

    # Add value labels
    for i, v in enumerate(df_combined['stranded_value_usd']):
        ax2.text(v + 0.2e9, i, f'${v/1e9:.2f}B', va='center', fontsize=11)

    ax2.set_xlabel('Stranded Asset Value (USD Billions)', fontsize=12)
    ax2.set_title('Regional Stranded Asset Values', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, df_combined['stranded_value_usd'].max() * 1.25)

    plt.suptitle('Regional Distribution of Stranded Assets', fontsize=16, fontweight='bold', y=1.02)
    filepath = OUTPUT_DIR / "02_regional_distribution.png"
    save_figure(plt.gcf(), filepath, dpi=DPI)
    print(f"Saved: {filepath}")
    # CSV export
    tidy = df_combined.rename(columns={'location': 'category', 'stranded_value_usd': 'value'})
    tidy['unit'] = 'USD'
    save_figure_data(tidy[['category', 'value', 'share_pct', 'unit']], filepath, figure_type='pie_bar')
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
    colors_bar = [CHART_PALETTE[0], CHART_PALETTE[4], CHART_PALETTE[2], CHART_PALETTE[3]]  # 1.5°C darker, 2.0°C lighter

    bars = ax.bar(x, scenario_totals['total_billion'], width=0.3, color=colors_bar, edgecolor='white', linewidth=1)

    # Add value labels on bars
    for bar, val in zip(bars, scenario_totals['total_billion']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'${val:.1f}B', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # X-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_totals['label'], fontsize=12)

    # Add group labels
    ax.text(0.175, -4, 'Hydrogen Pathway', ha='center', fontsize=12, fontweight='bold')
    ax.text(1.175, -4, 'Electrification Pathway', ha='center', fontsize=12, fontweight='bold')

    # Styling
    ax.set_ylabel('Total Stranded Assets (USD Billions)', fontsize=12)
    ax.set_title('Scenario Comparison: Stranded Asset Values by Technology & Temperature Target',
                 fontsize=14, fontweight='bold', pad=20)

    # Add annotation about 1.5°C scenarios
    ax.axhline(y=scenario_totals[scenario_totals['scenario'].str.contains('15c')]['total_billion'].mean(),
               color='red', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axhline(y=scenario_totals[scenario_totals['scenario'].str.contains('20c')]['total_billion'].mean(),
               color='orange', linestyle='--', alpha=0.5, linewidth=1.5)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CHART_PALETTE[0], label='1.5°C Target (H2)'),
        Patch(facecolor=CHART_PALETTE[4], label='2.0°C Target (H2)'),
        Patch(facecolor=CHART_PALETTE[2], label='1.5°C Target (Elec)'),
        Patch(facecolor=CHART_PALETTE[3], label='2.0°C Target (Elec)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    ax.set_ylim(0, scenario_totals['total_billion'].max() * 1.2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))

    filepath = OUTPUT_DIR / "03_scenario_comparison.png"
    save_figure(plt.gcf(), filepath, dpi=DPI)
    print(f"Saved: {filepath}")
    # CSV export
    tidy = scenario_totals[['scenario', 'total_billion']].rename(
        columns={'scenario': 'category', 'total_billion': 'value'})
    tidy['unit'] = 'billion_USD'
    save_figure_data(tidy, filepath, figure_type='grouped_bar')
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
                     color=CHART_PALETTE[0] if 'h2' in scenario else CHART_PALETTE[2],
                     alpha=0.8, edgecolor='white')

        ax.set_xlabel('Transition Year', fontsize=10)
        ax.set_ylabel('Capacity (kt/yr)', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')

        # Highlight 2026 immediate transitions for elec scenarios
        if 'elec' in scenario:
            for bar in bars:
                if bar.get_x() < 2027:
                    bar.set_color(CHART_PALETTE[2])
                    bar.set_alpha(1.0)

        ax.set_xlim(2024, 2052)
        ax.tick_params(axis='both', labelsize=10)

        # Add cumulative line
        ax2 = ax.twinx()
        cumulative = year_counts['capacity_ktpy'].cumsum()
        ax2.plot(year_counts['transition_year'], cumulative,
                color=CHART_PALETTE[3], linewidth=2, marker='o', markersize=4)
        ax2.set_ylabel('Cumulative Capacity (kt/yr)', fontsize=10, color=CHART_PALETTE[3])
        ax2.tick_params(axis='y', labelcolor=CHART_PALETTE[3], labelsize=10)

    plt.suptitle('Transition Timeline by Scenario\nCapacity Transitioning per Year',
                 fontsize=14, fontweight='bold', y=1.02)
    filepath = OUTPUT_DIR / "04_transition_timeline.png"
    save_figure(plt.gcf(), filepath, dpi=DPI)
    print(f"Saved: {filepath}")
    # CSV export
    tl_rows = []
    for scenario, title in scenarios:
        df_s = facility_df[facility_df['scenario'] == scenario]
        yc = df_s.groupby('transition_year').agg({
            'capacity_ktpy': 'sum',
            'total_stranded_value_million_usd': 'sum'
        }).reset_index()
        for _, row in yc.iterrows():
            tl_rows.append({'year': int(row['transition_year']), 'category': scenario,
                            'value': row['capacity_ktpy'], 'unit': 'kt_per_yr',
                            'panel': title})
    save_figure_data(pd.DataFrame(tl_rows), filepath, figure_type='multi_panel_bar')
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

    ax.set_xlabel('Product', fontsize=12)
    ax.set_ylabel('Region', fontsize=12)
    ax.set_title('Capacity Distribution by Region and Product\n(kt/yr)',
                 fontsize=14, fontweight='bold', pad=20)

    # Rotate x labels
    plt.xticks(rotation=0, fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    filepath = OUTPUT_DIR / "05_capacity_heatmap.png"
    save_figure(plt.gcf(), filepath, dpi=DPI)
    print(f"Saved: {filepath}")
    # CSV export
    tidy = pivot.reset_index().melt(id_vars='region', var_name='category', value_name='value')
    tidy['unit'] = 'kt_per_yr'
    save_figure_data(tidy, filepath, figure_type='heatmap')
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
                     color=CHART_PALETTE[0], label='Book Value', edgecolor='white')
    # Plot abandonment cost (stacked)
    bars2 = ax1.barh(y_pos, company_costs['abandonment_cost_million_usd'],
                     left=company_costs['book_value_million_usd'],
                     color=CHART_PALETTE[3], label='Abandonment Cost', edgecolor='white')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(company_costs['company'], fontsize=10)
    ax1.set_xlabel('Value (Million USD)', fontsize=12)
    ax1.set_title('Top 10 Companies: Cost Breakdown', fontsize=12, fontweight='bold')
    ax1.legend(loc='lower right', fontsize=10)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x/1000:.1f}B'))

    # Pie chart for overall breakdown
    total_book = df['book_value_million_usd'].sum()
    total_abandon = df['abandonment_cost_million_usd'].sum()

    sizes = [total_book, total_abandon]
    labels = [f'Book Value\n${total_book/1000:.1f}B\n({total_book/(total_book+total_abandon)*100:.1f}%)',
              f'Abandonment Cost\n${total_abandon/1000:.1f}B\n({total_abandon/(total_book+total_abandon)*100:.1f}%)']

    wedges, texts = ax2.pie(sizes, labels=labels, colors=[CHART_PALETTE[0], CHART_PALETTE[3]],
                            startangle=90, textprops={'fontsize': 11},
                            explode=[0.02, 0.05])

    ax2.set_title('Overall Cost Composition\n(NCC-H2, 1.5°C Scenario)', fontsize=12, fontweight='bold')

    plt.suptitle('Book Value vs Abandonment Cost Analysis', fontsize=14, fontweight='bold', y=1.02)
    filepath = OUTPUT_DIR / "06_cost_breakdown.png"
    save_figure(plt.gcf(), filepath, dpi=DPI)
    print(f"Saved: {filepath}")
    # CSV export
    cb_rows = []
    for _, row in company_costs.iterrows():
        cb_rows.append({'category': row['company'], 'subcategory': 'Book Value',
                        'value': row['book_value_million_usd'], 'unit': 'million_USD'})
        cb_rows.append({'category': row['company'], 'subcategory': 'Abandonment Cost',
                        'value': row['abandonment_cost_million_usd'], 'unit': 'million_USD'})
    save_figure_data(pd.DataFrame(cb_rows), filepath, figure_type='stacked_bar')
    return filepath


def create_bubble_chart():
    """Bubble chart: facility-level stranded asset exposure (NCC-Elec, 1.5°C).

    Self-contained — loads its own CSV so it works independently of load_data().

    Dimensions:
        X-axis: Year built (investment timeline)
        Y-axis: Stranded value (USD), LINEAR scale
        Bubble size: Capacity (kt)
        Color: Company (top 6 by total stranded value + "Others")

    Key insight: 90% of stranded value sits in facilities built after 2010.
    Linear scale makes the 100× gap between new ($5B) and old ($50M)
    facilities viscerally visible.
    """
    from matplotlib.lines import Line2D

    FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load and filter
    df = pd.read_csv(PROJECT_ROOT / "outputs" / "stranded_assets_facilities.csv")
    df = df[
        (df['scenario'] == 'shaheen_ncc_elec_rising_coupled')
        & (df['budget_scenario'] == '1.5C')
    ].copy()

    # Exclude rows with zero stranded value
    df = df[df['stranded_value_usd'] > 0].copy()

    # Identify top 6 companies by total stranded value
    company_totals = df.groupby('company')['stranded_value_usd'].sum().sort_values(ascending=False)
    top6 = company_totals.head(6).index.tolist()
    df['company_group'] = df['company'].where(df['company'].isin(top6), 'Others')

    # Assign colors: top 6 get distinct palette colors, Others = gray
    color_map = {name: CHART_PALETTE[i] for i, name in enumerate(top6)}
    color_map['Others'] = '#999999'
    df['color'] = df['company_group'].map(color_map)

    # Scale bubble sizes (min visible, max not overwhelming)
    cap = df['capacity_kt']
    size_min, size_max = 40, 800
    size_scaled = size_min + (cap - cap.min()) / (cap.max() - cap.min() + 1e-9) * (size_max - size_min)

    # Plot
    fig, ax = plt.subplots(figsize=FIGSIZE)

    ax.scatter(
        df['year_built'],
        df['stranded_value_usd'],
        s=size_scaled,
        c=df['color'],
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5,
    )

    ax.set_xlabel('Year Built')
    ax.set_ylabel('Stranded Asset Value (USD)')
    ax.set_title('Stranded Asset Exposure by Facility (NCC-Elec, 1.5°C)')

    # Format y-axis as $XB / $XM (linear scale)
    def _fmt_usd(x, _pos):
        if abs(x) >= 1e9:
            return f'${x / 1e9:.1f}B'
        if abs(x) >= 1e6:
            return f'${x / 1e6:.0f}M'
        return f'${x:,.0f}'

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_usd))
    ax.set_ylim(bottom=0)

    # Vertical reference line at 2010 with annotation
    post2010_value = df.loc[df['year_built'] > 2010, 'stranded_value_usd'].sum()
    total_value = df['stranded_value_usd'].sum()
    pct_post2010 = post2010_value / total_value * 100

    y_max = df['stranded_value_usd'].max() * 1.1
    ax.set_ylim(bottom=0, top=y_max)

    ax.axvline(x=2010, color='#555555', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(
        2010.5, y_max * 0.85,
        f'{pct_post2010:.0f}% of stranded value\nin facilities built after 2010',
        fontsize=8, color='#333333', fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', edgecolor='#999999', alpha=0.8),
    )

    # Company color legend
    legend_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[c],
               markersize=8, label=c)
        for c in top6 + ['Others']
    ]
    legend1 = ax.legend(handles=legend_handles, title='Company', loc='upper left',
                        fontsize=7, title_fontsize=8)
    ax.add_artist(legend1)

    # Size legend for capacity
    ref_caps = [200, 500, 1000, 2000]
    ref_sizes = [
        size_min + (rc - cap.min()) / (cap.max() - cap.min() + 1e-9) * (size_max - size_min)
        for rc in ref_caps
    ]
    size_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#cccccc',
               markeredgecolor='gray', markersize=np.sqrt(s) / 2, label=f'{rc} kt')
        for rc, s in zip(ref_caps, ref_sizes)
    ]
    ax.legend(handles=size_handles, title='Capacity', loc='lower left',
              fontsize=7, title_fontsize=8)
    ax.add_artist(legend1)  # re-add so both legends show

    filepath = FIGURES_DIR / "fig4_bubble_stranded.png"
    save_figure(fig, filepath, dpi=DPI)
    print(f"Saved: {filepath}")

    # CSV export
    tidy = df[['company', 'location', 'product', 'capacity_kt',
               'year_built', 'stranded_value_usd']].copy()
    save_figure_data(tidy, filepath, figure_type='scatter')
    return filepath


def main():
    """Generate all visualizations."""

    # Self-contained bubble chart (does not depend on load_data)
    try:
        create_bubble_chart()
    except Exception as e:
        print(f"WARNING: bubble chart failed: {e}")

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
