#!/usr/bin/env python3
"""
Comprehensive emission pathway visualization with product and company breakdown
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import matplotlib.font_manager as fm

# Set Korean font for matplotlib
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EmissionPathwayVisualizer:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load baseline facility data
        self.facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        
        # Load emission pathways
        self.pathway_25yr = pd.read_csv("outputs/bau_emission_pathway_25yr_final.csv")
        self.pathway_30yr = pd.read_csv("outputs/bau_emission_pathway_30yr_final.csv")
        self.pathway_40yr = pd.read_csv("outputs/bau_emission_pathway_40yr_final.csv")
        self.pathway_50yr = pd.read_csv("outputs/bau_emission_pathway_50yr_final.csv")
        
        print("✓ Loaded all emission pathway data")
        
    def create_pathway_comparison(self):
        """Create comprehensive pathway comparison"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot all pathways
        scenarios = [
            (self.pathway_25yr, "25-year lifetime", "#e74c3c"),
            (self.pathway_30yr, "30-year lifetime", "#f39c12"), 
            (self.pathway_40yr, "40-year lifetime", "#3498db"),
            (self.pathway_50yr, "50-year lifetime", "#27ae60")
        ]
        
        # Main pathway comparison
        for pathway_df, label, color in scenarios:
            ax1.plot(pathway_df['year'], pathway_df['emissions_mt_co2'], 
                    label=label, linewidth=2.5, color=color)
        
        ax1.set_title("BAU Emission Pathways by Facility Lifetime", fontsize=14, fontweight='bold')
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Emissions (Mt CO₂)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(2023, 2050)
        
        # Facility count evolution
        for pathway_df, label, color in scenarios:
            ax2.plot(pathway_df['year'], pathway_df['active_facilities'], 
                    label=label, linewidth=2.5, color=color, linestyle='--')
        
        ax2.set_title("Active Facilities by Scenario", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Active Facilities")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(2023, 2050)
        
        # Cumulative emissions comparison (2023-2050)
        cumulative_data = []
        for pathway_df, label, color in scenarios:
            cumulative = pathway_df['emissions_mt_co2'].sum()
            cumulative_data.append({'Scenario': label, 'Cumulative_Mt_CO2': cumulative, 'Color': color})
        
        cum_df = pd.DataFrame(cumulative_data)
        bars = ax3.bar(cum_df['Scenario'], cum_df['Cumulative_Mt_CO2'], 
                       color=[row['Color'] for _, row in cum_df.iterrows()], alpha=0.7)
        ax3.set_title("Cumulative Emissions 2023-2050", fontsize=14, fontweight='bold')
        ax3.set_ylabel("Cumulative Mt CO₂")
        ax3.tick_params(axis='x', rotation=45)
        
        # Add values on bars
        for bar, value in zip(bars, cum_df['Cumulative_Mt_CO2']):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Emission reduction timeline
        baseline_2023 = 60.0  # Mt CO₂
        reduction_data = []
        
        for pathway_df, label, color in scenarios:
            emissions_2030 = pathway_df[pathway_df['year'] == 2030]['emissions_mt_co2'].iloc[0]
            emissions_2040 = pathway_df[pathway_df['year'] == 2040]['emissions_mt_co2'].iloc[0]
            emissions_2050 = pathway_df[pathway_df['year'] == 2050]['emissions_mt_co2'].iloc[0]
            
            reduction_2030 = (baseline_2023 - emissions_2030) / baseline_2023 * 100
            reduction_2040 = (baseline_2023 - emissions_2040) / baseline_2023 * 100  
            reduction_2050 = (baseline_2023 - emissions_2050) / baseline_2023 * 100
            
            reduction_data.append({
                'Scenario': label,
                '2030': reduction_2030,
                '2040': reduction_2040, 
                '2050': reduction_2050,
                'Color': color
            })
        
        red_df = pd.DataFrame(reduction_data)
        x = np.arange(len(red_df))
        width = 0.25
        
        ax4.bar(x - width, red_df['2030'], width, label='2030', alpha=0.8)
        ax4.bar(x, red_df['2040'], width, label='2040', alpha=0.8)
        ax4.bar(x + width, red_df['2050'], width, label='2050', alpha=0.8)
        
        ax4.set_title("Emission Reduction by Timeline", fontsize=14, fontweight='bold')
        ax4.set_ylabel("Reduction from 2023 baseline (%)")
        ax4.set_xticks(x)
        ax4.set_xticklabels([s.replace('-year lifetime', '') for s in red_df['Scenario']])
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "comprehensive_emission_pathways.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return cumulative_data, reduction_data
        
    def analyze_product_shares(self):
        """Analyze emission shares by product category"""
        
        # Product mapping
        product_mapping = {
            'Ethylene': ['Ethylene'],
            'Propylene': ['Propylene'],
            'BTX': ['벤젠', 'Toluene', 'O-X', 'P-X', 'M-X'],
            'Polyethylene': ['HDPE', 'LDPE', 'LLDPE'],
            'Polypropylene': ['PP'],
            'Others': ['TPA', 'C-H', 'Styrene', 'Acrylonitrile']
        }
        
        # Calculate product shares
        product_shares = {}
        for category, products in product_mapping.items():
            category_emissions = self.facility_data[
                self.facility_data['product'].isin(products)
            ]['annual_emissions_kt_co2'].sum() / 1000  # Convert kt to Mt
            product_shares[category] = category_emissions
        
        # Create product share visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie chart
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
        wedges, texts, autotexts = ax1.pie(product_shares.values(), 
                                          labels=product_shares.keys(),
                                          colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 10})
        
        ax1.set_title("2023 Baseline Emissions by Product Category\n(52.0 Mt CO₂ total)", 
                     fontsize=14, fontweight='bold')
        
        # Bar chart
        bars = ax2.bar(product_shares.keys(), product_shares.values(), 
                      color=colors, alpha=0.8)
        ax2.set_title("Product Category Emissions", fontsize=14, fontweight='bold')
        ax2.set_ylabel("Emissions (Mt CO₂)")
        ax2.tick_params(axis='x', rotation=45)
        
        # Add values on bars
        for bar, value in zip(bars, product_shares.values()):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "product_emission_shares.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return product_shares
        
    def analyze_company_shares(self):
        """Analyze emission shares by company"""
        
        # Get top companies by emissions
        company_emissions = self.facility_data.groupby('company')['annual_emissions_kt_co2'].sum().sort_values(ascending=False) / 1000  # Convert kt to Mt
        
        # Group smaller companies as "Others"
        top_companies = company_emissions.head(10)
        others_emissions = company_emissions.iloc[10:].sum()
        
        if others_emissions > 0:
            display_data = top_companies.copy()
            display_data['Others'] = others_emissions
        else:
            display_data = top_companies
        
        # Create company share visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie chart for top companies
        colors = plt.cm.Set3(np.linspace(0, 1, len(display_data)))
        wedges, texts, autotexts = ax1.pie(display_data.values, 
                                          labels=display_data.index,
                                          colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 9})
        
        ax1.set_title("2023 Baseline Emissions by Company\n(52.0 Mt CO₂ total)", 
                     fontsize=14, fontweight='bold')
        
        # Bar chart
        bars = ax2.bar(range(len(display_data)), display_data.values, 
                      color=colors, alpha=0.8)
        ax2.set_title("Company Emissions", fontsize=14, fontweight='bold')
        ax2.set_ylabel("Emissions (Mt CO₂)")
        ax2.set_xticks(range(len(display_data)))
        ax2.set_xticklabels(display_data.index, rotation=45, ha='right')
        
        # Add values on bars
        for bar, value in zip(bars, display_data.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "company_emission_shares.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return display_data
        
    def create_pathway_breakdown_table(self):
        """Create detailed pathway breakdown table"""
        
        scenarios = ['25yr', '30yr', '40yr', '50yr']
        pathways = [self.pathway_25yr, self.pathway_30yr, self.pathway_40yr, self.pathway_50yr]
        
        summary_data = []
        
        for scenario, pathway_df in zip(scenarios, pathways):
            # Key metrics
            baseline_2023 = pathway_df[pathway_df['year'] == 2023]['emissions_mt_co2'].iloc[0]
            emissions_2030 = pathway_df[pathway_df['year'] == 2030]['emissions_mt_co2'].iloc[0]
            emissions_2040 = pathway_df[pathway_df['year'] == 2040]['emissions_mt_co2'].iloc[0]
            emissions_2050 = pathway_df[pathway_df['year'] == 2050]['emissions_mt_co2'].iloc[0]
            
            facilities_2030 = pathway_df[pathway_df['year'] == 2030]['active_facilities'].iloc[0]
            facilities_2040 = pathway_df[pathway_df['year'] == 2040]['active_facilities'].iloc[0]
            facilities_2050 = pathway_df[pathway_df['year'] == 2050]['active_facilities'].iloc[0]
            
            cumulative_emissions = pathway_df['emissions_mt_co2'].sum()
            
            reduction_2030 = (baseline_2023 - emissions_2030) / baseline_2023 * 100
            reduction_2040 = (baseline_2023 - emissions_2040) / baseline_2023 * 100
            reduction_2050 = (baseline_2023 - emissions_2050) / baseline_2023 * 100
            
            summary_data.append({
                'Scenario': f'{scenario} lifetime',
                'Baseline_2023_Mt': f'{baseline_2023:.1f}',
                'Emissions_2030_Mt': f'{emissions_2030:.1f}',
                'Emissions_2040_Mt': f'{emissions_2040:.1f}',
                'Emissions_2050_Mt': f'{emissions_2050:.1f}',
                'Reduction_2030_%': f'{reduction_2030:.1f}%',
                'Reduction_2040_%': f'{reduction_2040:.1f}%',
                'Reduction_2050_%': f'{reduction_2050:.1f}%',
                'Facilities_2030': facilities_2030,
                'Facilities_2040': facilities_2040,
                'Facilities_2050': facilities_2050,
                'Cumulative_2023_2050_Mt': f'{cumulative_emissions:.0f}'
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Save detailed breakdown
        summary_df.to_csv(self.output_dir / "emission_pathway_summary_comparison.csv", index=False)
        
        print("\n=== EMISSION PATHWAY SUMMARY ===")
        print(summary_df.to_string(index=False))
        
        return summary_df
        
    def run_comprehensive_analysis(self):
        """Run complete emission pathway analysis"""
        
        print("🚀 Starting comprehensive emission pathway analysis...")
        
        # 1. Pathway comparison
        print("\n1. Creating pathway comparison...")
        cumulative_data, reduction_data = self.create_pathway_comparison()
        
        # 2. Product analysis  
        print("\n2. Analyzing product emission shares...")
        product_shares = self.analyze_product_shares()
        
        # 3. Company analysis
        print("\n3. Analyzing company emission shares...")
        company_shares = self.analyze_company_shares()
        
        # 4. Summary table
        print("\n4. Creating summary comparison table...")
        summary_df = self.create_pathway_breakdown_table()
        
        print("\n✅ COMPREHENSIVE ANALYSIS COMPLETE")
        print(f"📊 All visualizations saved to: {self.output_dir}")
        
        return {
            'pathways': summary_df,
            'products': product_shares,
            'companies': company_shares,
            'cumulative': cumulative_data,
            'reductions': reduction_data
        }

if __name__ == "__main__":
    visualizer = EmissionPathwayVisualizer()
    results = visualizer.run_comprehensive_analysis()