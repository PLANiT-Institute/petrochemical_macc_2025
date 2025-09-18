#!/usr/bin/env python3
"""
Pre-analysis tool for baseline projections and MACC curve preview
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class BaselineAnalyzer:
    """Analyze baseline emissions, production shares, and project MACC curves"""
    
    def __init__(self, excel_file="data/Korea_Petrochemical_MACC_Database.xlsx"):
        self.excel_file = excel_file
        self.bands_data = None
        self.alternatives_data = None
        self.costs_data = None
        self.load_data()
    
    def load_data(self):
        """Load data from Excel file"""
        print("📂 Loading baseline data...")
        
        with pd.ExcelFile(self.excel_file) as xls:
            self.bands_data = pd.read_excel(xls, sheet_name='TechBands_2023')
            self.alternatives_data = pd.read_excel(xls, sheet_name='AlternativeTechnologies') 
            self.costs_data = pd.read_excel(xls, sheet_name='AlternativeCosts')
            
        print(f"   ✅ Loaded {len(self.bands_data)} baseline bands")
        print(f"   ✅ Loaded {len(self.alternatives_data)} alternative technologies")
    
    def analyze_baseline_emissions(self) -> pd.DataFrame:
        """Analyze baseline emissions by source"""
        print("\n🏭 Analyzing baseline emissions by source...")
        
        # Calculate emissions by band
        self.bands_data['Total_Emissions_tCO2'] = (
            self.bands_data['Activity_kt_product'] * 
            self.bands_data['EmissionIntensity_tCO2_per_t'] * 1000
        )
        
        # Summary by technology group
        group_summary = self.bands_data.groupby('TechGroup').agg({
            'Activity_kt_product': 'sum',
            'Total_Emissions_tCO2': 'sum'
        }).reset_index()
        
        group_summary['Emissions_MtCO2'] = group_summary['Total_Emissions_tCO2'] / 1e6
        group_summary['Emission_Intensity_avg'] = (
            group_summary['Total_Emissions_tCO2'] / 
            (group_summary['Activity_kt_product'] * 1000)
        )
        
        # Summary by band type
        band_summary = self.bands_data.groupby('Band').agg({
            'Activity_kt_product': 'sum', 
            'Total_Emissions_tCO2': 'sum'
        }).reset_index()
        
        band_summary['Emissions_MtCO2'] = band_summary['Total_Emissions_tCO2'] / 1e6
        band_summary['Share_pct'] = (
            band_summary['Total_Emissions_tCO2'] / 
            band_summary['Total_Emissions_tCO2'].sum() * 100
        )
        
        total_emissions = self.bands_data['Total_Emissions_tCO2'].sum() / 1e6
        
        print(f"   📊 Total baseline emissions: {total_emissions:.1f} MtCO2")
        print("   📈 By Technology Group:")
        for _, row in group_summary.iterrows():
            print(f"      {row['TechGroup']}: {row['Emissions_MtCO2']:.1f} MtCO2 ({row['Emissions_MtCO2']/total_emissions*100:.1f}%)")
        
        print("   🌡️  By Temperature Band:")
        for _, row in band_summary.iterrows():
            print(f"      {row['Band']}: {row['Emissions_MtCO2']:.1f} MtCO2 ({row['Share_pct']:.1f}%)")
        
        return {
            'detailed': self.bands_data[['TechGroup', 'Band', 'TechKey', 'Activity_kt_product', 
                                        'EmissionIntensity_tCO2_per_t', 'Total_Emissions_tCO2']],
            'by_group': group_summary,
            'by_band': band_summary,
            'total_mt': total_emissions
        }
    
    def analyze_production_shares(self) -> pd.DataFrame:
        """Analyze production shares by technology group and band"""
        print("\n📊 Analyzing production shares...")
        
        total_production = self.bands_data['Activity_kt_product'].sum()
        
        # Production shares by group
        group_shares = self.bands_data.groupby('TechGroup')['Activity_kt_product'].sum()
        group_shares_pct = group_shares / total_production * 100
        
        # Production shares by band within each group
        detailed_shares = []
        
        for group in self.bands_data['TechGroup'].unique():
            group_data = self.bands_data[self.bands_data['TechGroup'] == group]
            group_total = group_data['Activity_kt_product'].sum()
            
            for _, row in group_data.iterrows():
                detailed_shares.append({
                    'TechGroup': group,
                    'Band': row['Band'], 
                    'TechKey': row['TechKey'],
                    'Production_kt': row['Activity_kt_product'],
                    'Share_of_Group_pct': row['Activity_kt_product'] / group_total * 100,
                    'Share_of_Total_pct': row['Activity_kt_product'] / total_production * 100
                })
        
        detailed_df = pd.DataFrame(detailed_shares)
        
        print(f"   📏 Total production: {total_production:.0f} kt/year")
        print("   🏭 By Technology Group:")
        for group, share in group_shares_pct.items():
            print(f"      {group}: {group_shares[group]:.0f} kt/year ({share:.1f}%)")
        
        return {
            'detailed': detailed_df,
            'by_group': pd.DataFrame({
                'TechGroup': group_shares.index,
                'Production_kt': group_shares.values,
                'Share_pct': group_shares_pct.values
            })
        }
    
    def calculate_marginal_costs(self) -> pd.DataFrame:
        """Calculate marginal abatement costs for all alternative technologies"""
        print("\n💰 Calculating marginal abatement costs...")
        
        # Merge alternatives with costs
        merged_data = self.alternatives_data.merge(self.costs_data, on='TechID')
        
        macc_data = []
        
        for _, row in merged_data.iterrows():
            # Calculate annualized costs
            lifetime = row['Lifetime_years']
            discount_rate = 0.05  # Assume 5% discount rate
            
            # Capital Recovery Factor
            if discount_rate > 0:
                crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
            else:
                crf = 1.0 / lifetime
            
            # Annualized CAPEX (USD per tonne capacity per year)
            annual_capex_per_t = (row['CAPEX_Million_USD_per_kt_capacity'] * 1e6 / 1000) * crf
            
            # Total annual cost per tonne production
            annual_opex_per_t = row['OPEX_Delta_USD_per_t']
            total_annual_cost_per_t = annual_capex_per_t + annual_opex_per_t
            
            # Marginal abatement cost (USD per tCO2 abated)
            if row['EmissionReduction_tCO2_per_t'] > 0:
                mac_usd_per_tco2 = total_annual_cost_per_t / row['EmissionReduction_tCO2_per_t']
            else:
                mac_usd_per_tco2 = np.inf
            
            # Maximum abatement potential (tCO2/year)
            # Find corresponding baseline band
            baseline_band = self.bands_data[
                (self.bands_data['TechGroup'] == row['TechGroup']) & 
                (self.bands_data['Band'] == row['Band'])
            ]
            
            if not baseline_band.empty:
                baseline_activity = baseline_band.iloc[0]['Activity_kt_product'] * 1000  # Convert to tonnes
                max_abatement_potential = (
                    baseline_activity * 
                    row['MaxApplicability'] * 
                    row['EmissionReduction_tCO2_per_t']
                )
            else:
                max_abatement_potential = 0
            
            macc_data.append({
                'TechID': row['TechID'],
                'TechGroup': row['TechGroup'],
                'Band': row['Band'],
                'TechnologyCategory': row['TechnologyCategory'],
                'CommercialYear': row['CommercialYear'],
                'Annual_CAPEX_USD_per_t': annual_capex_per_t,
                'Annual_OPEX_USD_per_t': annual_opex_per_t,
                'Total_Annual_Cost_USD_per_t': total_annual_cost_per_t,
                'EmissionReduction_tCO2_per_t': row['EmissionReduction_tCO2_per_t'],
                'MAC_USD_per_tCO2': mac_usd_per_tco2,
                'MaxApplicability': row['MaxApplicability'],
                'Max_Abatement_Potential_tCO2_per_year': max_abatement_potential,
                'TechnicalReadiness': row['TechnicalReadiness']
            })
        
        macc_df = pd.DataFrame(macc_data)
        
        # Sort by MAC for MACC curve
        macc_df_sorted = macc_df[macc_df['MAC_USD_per_tCO2'] < np.inf].sort_values('MAC_USD_per_tCO2')
        
        print(f"   📈 Calculated MAC for {len(macc_df_sorted)} technologies")
        print("   💲 Top 5 most cost-effective options:")
        for i, (_, row) in enumerate(macc_df_sorted.head().iterrows()):
            print(f"      {i+1}. {row['TechID']}: {row['MAC_USD_per_tCO2']:.0f} USD/tCO2")
        
        return macc_df
    
    def project_macc_curve(self, macc_df: pd.DataFrame, target_year: int = 2030) -> Tuple[pd.DataFrame, plt.Figure]:
        """Project MACC curve for a target year"""
        print(f"\n📊 Projecting MACC curve for {target_year}...")
        
        # Filter technologies available by target year
        available_techs = macc_df[macc_df['CommercialYear'] <= target_year].copy()
        
        if available_techs.empty:
            print("   ⚠️  No technologies available by target year")
            return pd.DataFrame(), None
        
        # Sort by MAC and calculate cumulative abatement
        available_techs_sorted = available_techs.sort_values('MAC_USD_per_tCO2')
        available_techs_sorted['Cumulative_Abatement_MtCO2'] = (
            available_techs_sorted['Max_Abatement_Potential_tCO2_per_year'].cumsum() / 1e6
        )
        
        # Create MACC curve plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot step function for MACC curve
        x_vals = [0]  # Start from zero
        y_vals = [0]   # Start from zero cost
        
        for _, row in available_techs_sorted.iterrows():
            x_vals.extend([x_vals[-1], row['Cumulative_Abatement_MtCO2']])
            y_vals.extend([row['MAC_USD_per_tCO2'], row['MAC_USD_per_tCO2']])
        
        # Plot MACC curve
        ax.plot(x_vals, y_vals, 'b-', linewidth=2, label='MACC Curve')
        ax.fill_between(x_vals, 0, y_vals, alpha=0.3, color='skyblue')
        
        # Add technology labels
        for i, (_, row) in enumerate(available_techs_sorted.iterrows()):
            ax.annotate(
                f"{row['TechID']}\n({row['TechGroup']}-{row['Band']})",
                xy=(row['Cumulative_Abatement_MtCO2'], row['MAC_USD_per_tCO2']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8, rotation=45,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
            )
        
        ax.set_xlabel('Cumulative Abatement Potential (MtCO2/year)')
        ax.set_ylabel('Marginal Abatement Cost (USD/tCO2)')
        ax.set_title(f'Korea Petrochemical MACC Curve - {target_year}\n(Band-Specific Alternative Technologies)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set reasonable y-axis limits
        if not available_techs_sorted.empty:
            max_cost = available_techs_sorted['MAC_USD_per_tCO2'].max()
            ax.set_ylim(0, min(max_cost * 1.1, 1000))  # Cap at 1000 USD/tCO2 for readability
        
        plt.tight_layout()
        
        total_potential = available_techs_sorted['Cumulative_Abatement_MtCO2'].iloc[-1] if not available_techs_sorted.empty else 0
        print(f"   📏 Total abatement potential by {target_year}: {total_potential:.1f} MtCO2/year")
        
        return available_techs_sorted, fig
    
    def generate_baseline_report(self, output_dir="baseline_analysis"):
        """Generate comprehensive baseline analysis report"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📋 Generating comprehensive baseline analysis report...")
        
        # 1. Baseline emissions analysis
        emissions_analysis = self.analyze_baseline_emissions()
        
        # 2. Production shares analysis  
        production_analysis = self.analyze_production_shares()
        
        # 3. Marginal costs analysis
        macc_df = self.calculate_marginal_costs()
        
        # 4. MACC curves for key years
        macc_2030, fig_2030 = self.project_macc_curve(macc_df, 2030)
        macc_2040, fig_2040 = self.project_macc_curve(macc_df, 2040)  
        macc_2050, fig_2050 = self.project_macc_curve(macc_df, 2050)
        
        # Save data files
        emissions_analysis['detailed'].to_csv(f"{output_dir}/baseline_emissions_detailed.csv", index=False)
        emissions_analysis['by_group'].to_csv(f"{output_dir}/baseline_emissions_by_group.csv", index=False)
        emissions_analysis['by_band'].to_csv(f"{output_dir}/baseline_emissions_by_band.csv", index=False)
        
        production_analysis['detailed'].to_csv(f"{output_dir}/production_shares_detailed.csv", index=False)
        production_analysis['by_group'].to_csv(f"{output_dir}/production_shares_by_group.csv", index=False)
        
        macc_df.to_csv(f"{output_dir}/marginal_abatement_costs.csv", index=False)
        
        if not macc_2030.empty:
            macc_2030.to_csv(f"{output_dir}/macc_curve_2030.csv", index=False)
        if not macc_2040.empty:
            macc_2040.to_csv(f"{output_dir}/macc_curve_2040.csv", index=False)
        if not macc_2050.empty:
            macc_2050.to_csv(f"{output_dir}/macc_curve_2050.csv", index=False)
        
        # Save plots
        if fig_2030:
            fig_2030.savefig(f"{output_dir}/macc_curve_2030.png", dpi=300, bbox_inches='tight')
        if fig_2040:
            fig_2040.savefig(f"{output_dir}/macc_curve_2040.png", dpi=300, bbox_inches='tight')
        if fig_2050:
            fig_2050.savefig(f"{output_dir}/macc_curve_2050.png", dpi=300, bbox_inches='tight')
        
        # Generate baseline visualization
        self.create_baseline_visualizations(emissions_analysis, production_analysis, output_dir)
        
        print(f"   ✅ Baseline analysis report saved to '{output_dir}' directory")
        print(f"   📊 Generated: CSV data files + MACC curves + baseline charts")
        
        return {
            'emissions': emissions_analysis,
            'production': production_analysis, 
            'macc': macc_df,
            'macc_curves': {
                2030: macc_2030,
                2040: macc_2040,
                2050: macc_2050
            }
        }
    
    def create_baseline_visualizations(self, emissions_analysis, production_analysis, output_dir):
        """Create baseline visualization charts"""
        
        # 1. Emissions by source pie chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Emissions by technology group
        group_data = emissions_analysis['by_group']
        ax1.pie(group_data['Emissions_MtCO2'], labels=group_data['TechGroup'], autopct='%1.1f%%')
        ax1.set_title('Baseline Emissions by Technology Group')
        
        # Emissions by temperature band
        band_data = emissions_analysis['by_band']
        ax2.pie(band_data['Emissions_MtCO2'], labels=band_data['Band'], autopct='%1.1f%%')
        ax2.set_title('Baseline Emissions by Temperature Band')
        
        # Production shares by group
        prod_data = production_analysis['by_group']
        ax3.bar(prod_data['TechGroup'], prod_data['Production_kt'])
        ax3.set_title('Production by Technology Group')
        ax3.set_ylabel('Production (kt/year)')
        ax3.tick_params(axis='x', rotation=45)
        
        # Emission intensity by band
        detailed_data = emissions_analysis['detailed']
        band_intensity = detailed_data.groupby('Band')['EmissionIntensity_tCO2_per_t'].mean()
        ax4.bar(band_intensity.index, band_intensity.values)
        ax4.set_title('Average Emission Intensity by Band')
        ax4.set_ylabel('Emission Intensity (tCO2/t)')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/baseline_overview.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    analyzer = BaselineAnalyzer()
    report = analyzer.generate_baseline_report()
    
    print("\n" + "="*60)
    print("✅ BASELINE ANALYSIS COMPLETE")
    print("="*60)
    print("📁 Check 'baseline_analysis' directory for comprehensive results")