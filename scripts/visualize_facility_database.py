#!/usr/bin/env python3
"""
Visualization script for Korean Petrochemical Facility Database
248 Facilities with regional mapping
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Setup
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = 'white'

# Load data
data_path = Path(__file__).parent.parent / 'data' / 'facility_database_with_regions.csv'
df = pd.read_csv(data_path)

# Output directory
output_dir = Path(__file__).parent.parent / 'outputs' / 'facility_visualization'
output_dir.mkdir(parents=True, exist_ok=True)

# Color scheme for complexes
complex_colors = {
    'Ulsan Complex': '#E74C3C',    # Red
    'Yeosu Complex': '#3498DB',    # Blue
    'Daesan Complex': '#2ECC71',   # Green
    'Other Regions': '#9B59B6'     # Purple
}

# ============================================================
# Figure 1: Overview - Facilities by Complex (Pie + Bar)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 1a. Pie chart - Facility count by complex
complex_counts = df.groupby('complex').size()
colors = [complex_colors[c] for c in complex_counts.index]
axes[0].pie(complex_counts, labels=complex_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
axes[0].set_title('Facilities by Complex (n=248)', fontsize=12, fontweight='bold')

# 1b. Bar chart - Capacity by complex
complex_capacity = df.groupby('complex')['capacity_kt'].sum().sort_values(ascending=True)
colors = [complex_colors[c] for c in complex_capacity.index]
bars = axes[1].barh(complex_capacity.index, complex_capacity.values, color=colors)
axes[1].set_xlabel('Total Capacity (kt/year)')
axes[1].set_title('Production Capacity by Complex', fontsize=12, fontweight='bold')
for bar, val in zip(bars, complex_capacity.values):
    axes[1].text(val + 500, bar.get_y() + bar.get_height()/2,
                 f'{val:,.0f} kt', va='center', fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / '01_overview_by_complex.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 01_overview_by_complex.png')


# ============================================================
# Figure 2: Age Distribution by Complex
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))

age_bins = [0, 10, 20, 30, 40, 50, 100]
age_labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '50+']

complex_order = ['Ulsan Complex', 'Yeosu Complex', 'Daesan Complex', 'Other Regions']
x = np.arange(len(age_labels))
width = 0.2

for i, complex_name in enumerate(complex_order):
    subset = df[df['complex'] == complex_name]
    age_dist = pd.cut(subset['age_2025'], bins=age_bins, labels=age_labels).value_counts().sort_index()
    ax.bar(x + i*width, age_dist.values, width, label=complex_name, color=complex_colors[complex_name])

ax.set_xlabel('Age (years)')
ax.set_ylabel('Number of Facilities')
ax.set_title('Facility Age Distribution by Complex (Base Year: 2025)', fontsize=12, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(age_labels)
ax.legend(loc='upper right')
ax.axvline(x=3.5, color='red', linestyle='--', alpha=0.7, label='40-year lifespan threshold')

plt.tight_layout()
plt.savefig(output_dir / '02_age_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 02_age_distribution.png')


# ============================================================
# Figure 3: Top 20 Products by Capacity
# ============================================================
fig, ax = plt.subplots(figsize=(12, 8))

product_capacity = df.groupby('product')['capacity_kt'].sum().sort_values(ascending=True).tail(20)
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(product_capacity)))
bars = ax.barh(product_capacity.index, product_capacity.values, color=colors)
ax.set_xlabel('Total Capacity (kt/year)')
ax.set_title('Top 20 Products by Production Capacity', fontsize=12, fontweight='bold')

for bar, val in zip(bars, product_capacity.values):
    ax.text(val + 100, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / '03_top_products.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 03_top_products.png')


# ============================================================
# Figure 4: Top 15 Companies by Capacity
# ============================================================
fig, ax = plt.subplots(figsize=(12, 8))

company_capacity = df.groupby('company')['capacity_kt'].sum().sort_values(ascending=True).tail(15)
colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(company_capacity)))
bars = ax.barh(company_capacity.index, company_capacity.values, color=colors)
ax.set_xlabel('Total Capacity (kt/year)')
ax.set_title('Top 15 Companies by Production Capacity', fontsize=12, fontweight='bold')

for bar, val in zip(bars, company_capacity.values):
    ax.text(val + 100, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / '04_top_companies.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 04_top_companies.png')


# ============================================================
# Figure 5: Process Type Distribution
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

process_colors = {
    'Naphtha Cracker': '#E74C3C',
    'BTX Plant': '#3498DB',
    'Utility': '#2ECC71'
}

# 5a. By facility count
process_counts = df.groupby('process').size()
colors = [process_colors[p] for p in process_counts.index]
axes[0].pie(process_counts, labels=process_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
axes[0].set_title('Facilities by Process Type', fontsize=12, fontweight='bold')

# 5b. By capacity
process_capacity = df.groupby('process')['capacity_kt'].sum()
colors = [process_colors[p] for p in process_capacity.index]
axes[1].pie(process_capacity, labels=process_capacity.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
axes[1].set_title('Capacity by Process Type', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / '05_process_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 05_process_distribution.png')


# ============================================================
# Figure 6: Retirement Timeline (40-year lifespan assumption)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))

years = range(2025, 2065, 5)
complex_order = ['Ulsan Complex', 'Yeosu Complex', 'Daesan Complex', 'Other Regions']

retirement_data = {}
for complex_name in complex_order:
    subset = df[df['complex'] == complex_name]
    cumulative = [len(subset[subset['retirement_year_40yr'] <= year]) for year in years]
    retirement_data[complex_name] = cumulative

# Stacked area chart
bottom = np.zeros(len(years))
for complex_name in complex_order:
    ax.fill_between(years, bottom, bottom + retirement_data[complex_name],
                    label=complex_name, color=complex_colors[complex_name], alpha=0.7)
    bottom = bottom + np.array(retirement_data[complex_name])

ax.set_xlabel('Year')
ax.set_ylabel('Cumulative Facilities Reaching 40-Year Lifespan')
ax.set_title('Facility Retirement Timeline (40-Year Lifespan Assumption)', fontsize=12, fontweight='bold')
ax.legend(loc='upper left')
ax.axhline(y=248, color='black', linestyle='--', alpha=0.5)
ax.text(2063, 248, 'Total: 248', va='bottom', ha='right')
ax.set_xlim(2025, 2065)
ax.set_ylim(0, 260)

plt.tight_layout()
plt.savefig(output_dir / '06_retirement_timeline.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 06_retirement_timeline.png')


# ============================================================
# Figure 7: Location Detail within Complexes
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for idx, complex_name in enumerate(complex_order):
    ax = axes[idx // 2, idx % 2]
    subset = df[df['complex'] == complex_name]
    loc_capacity = subset.groupby('location')['capacity_kt'].sum().sort_values(ascending=True)

    colors = plt.cm.Set2(np.linspace(0, 1, len(loc_capacity)))
    bars = ax.barh(loc_capacity.index, loc_capacity.values, color=complex_colors[complex_name])
    ax.set_xlabel('Capacity (kt/year)')
    ax.set_title(f'{complex_name}', fontsize=11, fontweight='bold')

    for bar, val in zip(bars, loc_capacity.values):
        ax.text(val + 100, bar.get_y() + bar.get_height()/2,
                f'{val:,.0f}', va='center', fontsize=9)

plt.suptitle('Production Capacity by Location within Each Complex', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(output_dir / '07_location_detail.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 07_location_detail.png')


# ============================================================
# Figure 8: Year Built Distribution (Histogram)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))

for complex_name in complex_order:
    subset = df[df['complex'] == complex_name]
    ax.hist(subset['year_built'], bins=range(1970, 2030, 5), alpha=0.6,
            label=complex_name, color=complex_colors[complex_name])

ax.set_xlabel('Year Built')
ax.set_ylabel('Number of Facilities')
ax.set_title('Facility Construction Timeline by Complex', fontsize=12, fontweight='bold')
ax.legend()
ax.axvline(x=1985, color='gray', linestyle='--', alpha=0.5)
ax.text(1985, ax.get_ylim()[1]*0.9, '40 years ago', rotation=90, va='top', ha='right', fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / '08_construction_timeline.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 08_construction_timeline.png')


# ============================================================
# Figure 9: Summary Dashboard
# ============================================================
fig = plt.figure(figsize=(16, 12))

# Create grid
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Title
fig.suptitle('Korean Petrochemical Facility Database Overview (n=248)',
             fontsize=16, fontweight='bold', y=0.98)

# 9a. Complex pie chart
ax1 = fig.add_subplot(gs[0, 0])
complex_counts = df.groupby('complex').size()
colors = [complex_colors[c] for c in complex_counts.index]
ax1.pie(complex_counts, labels=None, autopct='%1.0f%%', colors=colors, startangle=90)
ax1.set_title('By Complex', fontsize=10, fontweight='bold')
ax1.legend(complex_counts.index, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)

# 9b. Process pie chart
ax2 = fig.add_subplot(gs[0, 1])
process_counts = df.groupby('process').size()
colors = [process_colors[p] for p in process_counts.index]
ax2.pie(process_counts, labels=None, autopct='%1.0f%%', colors=colors, startangle=90)
ax2.set_title('By Process', fontsize=10, fontweight='bold')
ax2.legend(process_counts.index, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=1, fontsize=8)

# 9c. Key stats
ax3 = fig.add_subplot(gs[0, 2])
ax3.axis('off')
stats_text = f"""
KEY STATISTICS
─────────────────
Total Facilities: 248
Total Capacity: {df['capacity_kt'].sum():,.0f} kt/year
Unique Products: {df['product'].nunique()}
Unique Companies: {df['company'].nunique()}
Locations: {df['location'].nunique()}

Average Age: {df['age_2025'].mean():.1f} years
Oldest: {df['age_2025'].max()} years
Newest: {df['age_2025'].min()} years

Past 40-yr lifespan: {len(df[df['age_2025'] > 40])} facilities
"""
ax3.text(0.1, 0.9, stats_text, transform=ax3.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))

# 9d. Capacity by complex (bar)
ax4 = fig.add_subplot(gs[1, 0:2])
complex_capacity = df.groupby('complex')['capacity_kt'].sum().sort_values()
colors = [complex_colors[c] for c in complex_capacity.index]
bars = ax4.barh(complex_capacity.index, complex_capacity.values, color=colors)
ax4.set_xlabel('Capacity (kt/year)')
ax4.set_title('Capacity by Complex', fontsize=10, fontweight='bold')
for bar, val in zip(bars, complex_capacity.values):
    ax4.text(val + 300, bar.get_y() + bar.get_height()/2, f'{val:,.0f}', va='center', fontsize=9)

# 9e. Age distribution
ax5 = fig.add_subplot(gs[1, 2])
age_bins = [0, 10, 20, 30, 40, 50, 100]
age_labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '50+']
age_dist = pd.cut(df['age_2025'], bins=age_bins, labels=age_labels).value_counts().sort_index()
colors = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(age_dist)))
ax5.bar(age_labels, age_dist.values, color=colors)
ax5.set_xlabel('Age (years)')
ax5.set_ylabel('Facilities')
ax5.set_title('Age Distribution', fontsize=10, fontweight='bold')
ax5.axvline(x=3.5, color='red', linestyle='--', alpha=0.7)

# 9f. Top 10 products
ax6 = fig.add_subplot(gs[2, 0:2])
top_products = df.groupby('product')['capacity_kt'].sum().sort_values(ascending=True).tail(10)
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(top_products)))
ax6.barh(top_products.index, top_products.values, color=colors)
ax6.set_xlabel('Capacity (kt/year)')
ax6.set_title('Top 10 Products', fontsize=10, fontweight='bold')

# 9g. Retirement timeline
ax7 = fig.add_subplot(gs[2, 2])
years = range(2025, 2055, 5)
total_retired = [len(df[df['retirement_year_40yr'] <= year]) for year in years]
ax7.plot(years, total_retired, 'o-', color='#E74C3C', linewidth=2, markersize=6)
ax7.fill_between(years, total_retired, alpha=0.3, color='#E74C3C')
ax7.set_xlabel('Year')
ax7.set_ylabel('Cumulative Retirements')
ax7.set_title('Retirement (40-yr)', fontsize=10, fontweight='bold')
ax7.axhline(y=248, color='gray', linestyle='--', alpha=0.5)

plt.savefig(output_dir / '09_summary_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved: 09_summary_dashboard.png')


print('\n' + '='*50)
print('All visualizations saved to:')
print(f'  {output_dir}')
print('='*50)
