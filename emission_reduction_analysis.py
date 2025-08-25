#!/usr/bin/env python3
"""
Analysis of Emission Reduction Mechanics in the MACC Model

This analysis examines how emissions are actually reduced through technology adoption 
and clarifies whether the model is about technology adoption vs production decisions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_emission_reduction_mechanism():
    """Analyze the fundamental emission reduction logic in the MACC model"""
    
    print("🔍 EMISSION REDUCTION MECHANISM ANALYSIS")
    print("=" * 60)
    
    # Load model results
    results_dir = Path("outputs_fixed_bands")
    
    # Load key data files
    band_summary = pd.read_csv(results_dir / "band_level_summary.csv")
    deployment = pd.read_csv(results_dir / "alternative_deployment_by_band.csv") 
    emission_pathways = pd.read_csv(results_dir / "emission_pathways_by_source.csv")
    baseline = pd.read_csv(results_dir / "fixed_band_baseline.csv")
    
    print("\n📊 1. BASELINE EMISSION STRUCTURE")
    print("-" * 40)
    
    # Analyze baseline structure
    total_baseline_emissions = baseline['Baseline_Emissions_tCO2'].sum() / 1e6  # Convert to MtCO2
    total_baseline_production = baseline['Baseline_Activity_kt'].sum()
    
    print(f"Total Baseline Emissions: {total_baseline_emissions:.1f} MtCO2/year")
    print(f"Total Baseline Production: {total_baseline_production:.0f} kt/year")
    print(f"Average Emission Intensity: {total_baseline_emissions*1e6/total_baseline_production/1000:.2f} tCO2/t")
    
    # Emissions by band
    print("\n📋 Baseline Emissions by Temperature Band:")
    for band in ['HT', 'MT', 'LT']:
        band_data = baseline[baseline['Band'] == band]
        band_emissions = band_data['Baseline_Emissions_tCO2'].sum() / 1e6
        band_production = band_data['Baseline_Activity_kt'].sum()
        print(f"  {band}: {band_emissions:.1f} MtCO2 ({band_emissions/total_baseline_emissions*100:.1f}%) from {band_production:.0f} kt")
    
    print("\n⚡ 2. TECHNOLOGY ADOPTION vs PRODUCTION LOGIC")
    print("-" * 50)
    
    # Examine the model logic
    print("🎯 KEY MODEL LOGIC:")
    print("1. CAPACITY INSTALLATION: Model decides to install alternative technology capacity (kt/year)")
    print("2. PRODUCTION SUBSTITUTION: Alternative technologies substitute baseline production")
    print("3. EMISSION REDUCTION: Emissions reduced = Production_alt × (EI_baseline - EI_alt)")
    print()
    print("✅ Model Focus: TECHNOLOGY ADOPTION driving PRODUCTION SUBSTITUTION")
    print("   - Investment decisions: Install alternative capacity")
    print("   - Operational decisions: Use alternative capacity to substitute baseline")
    print("   - Emission outcome: Lower emission intensity × same production volume")
    
    print("\n🔄 3. SUBSTITUTION MECHANISM ANALYSIS")
    print("-" * 45)
    
    # Analyze substitution patterns for key years
    for year in [2030, 2040, 2050]:
        year_data = band_summary[band_summary['Year'] == year]
        
        print(f"\n📅 {year} SUBSTITUTION PATTERNS:")
        
        total_baseline = year_data['Baseline_Production_kt'].sum()
        total_alternative = year_data['Alternative_Production_kt'].sum()
        total_remaining = year_data['Remaining_Baseline_kt'].sum()
        
        print(f"  Total Production Capacity: {total_baseline:.0f} kt/year (FIXED)")
        print(f"  Alternative Production: {total_alternative:.0f} kt/year ({total_alternative/total_baseline*100:.1f}%)")
        print(f"  Remaining Baseline: {total_remaining:.0f} kt/year ({total_remaining/total_baseline*100:.1f}%)")
        
        # Show band-by-band substitution
        print("  📊 Band-level Substitution:")
        for _, row in year_data.iterrows():
            band_key = row['Band_Key']
            alt_share = row['Alternative_Share_pct']
            emission_reduction = row['Band_Emission_Reduction_pct']
            print(f"    {band_key}: {alt_share:.1f}% substitution → {emission_reduction:.1f}% emission reduction")
    
    print("\n📈 4. EMISSION REDUCTION PATHWAYS")
    print("-" * 40)
    
    # Analyze emission reduction over time
    key_years = [2030, 2040, 2050]
    
    for year in key_years:
        year_pathways = emission_pathways[emission_pathways['Year'] == year]
        
        if not year_pathways.empty:
            total_emissions = year_pathways['Total_Emissions_MtCO2'].iloc[0]
            total_abatement = year_pathways['Total_Abatement_MtCO2'].iloc[0]
            baseline_emissions = year_pathways['Baseline_Emissions_MtCO2'].iloc[0]
            reduction_pct = year_pathways['Emission_Reduction_from_Baseline_pct'].iloc[0]
            
            print(f"\n📊 {year} EMISSION REDUCTION:")
            print(f"  Baseline Emissions: {baseline_emissions:.1f} MtCO2")
            print(f"  Actual Emissions: {total_emissions:.1f} MtCO2")
            print(f"  Total Abatement: {total_abatement:.1f} MtCO2")
            print(f"  Reduction from Baseline: {reduction_pct:.1f}%")
            
            # Show reduction by source (band)
            print("  🏭 Reduction by Source:")
            for band_key in ['NCC_HT', 'NCC_MT', 'NCC_LT', 'BTX_HT', 'BTX_MT', 'BTX_LT', 'C4_HT', 'C4_MT', 'C4_LT']:
                abate_col = f'{band_key}_Abatement_tCO2'
                share_col = f'{band_key}_Alternative_Share_pct'
                
                if abate_col in year_pathways.columns and share_col in year_pathways.columns:
                    abatement = year_pathways[abate_col].iloc[0] / 1e6  # Convert to MtCO2
                    alt_share = year_pathways[share_col].iloc[0]
                    
                    if abatement > 0.01:  # Only show significant contributions
                        print(f"    {band_key}: {abatement:.2f} MtCO2 ({alt_share:.1f}% tech adoption)")
    
    print("\n🎯 5. ADOPTION vs EMISSION EFFECTIVENESS")
    print("-" * 45)
    
    # Analyze technology adoption effectiveness
    deployment_2050 = deployment[deployment['Year'] == 2050]
    
    if not deployment_2050.empty:
        print("📋 2050 Technology Adoption Effectiveness:")
        
        # Sort by abatement achieved
        effectiveness = deployment_2050[['TechID', 'Target_Band', 'Penetration_Rate', 'Abatement_tCO2']].copy()
        effectiveness['Abatement_MtCO2'] = effectiveness['Abatement_tCO2'] / 1e6
        effectiveness = effectiveness.sort_values('Abatement_MtCO2', ascending=False)
        
        print("  🥇 Top Emission Reducers (by total abatement):")
        for _, row in effectiveness.head(8).iterrows():
            tech_id = row['TechID']
            target_band = row['Target_Band'] 
            penetration = row['Penetration_Rate'] * 100
            abatement = row['Abatement_MtCO2']
            print(f"    {tech_id} → {target_band}: {penetration:.1f}% adoption = {abatement:.2f} MtCO2")
    
    return create_emission_reduction_visualization(band_summary, emission_pathways, baseline)

def create_emission_reduction_visualization(band_summary, emission_pathways, baseline):
    """Create comprehensive visualization of emission reduction mechanisms"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Technology Adoption vs Emission Reduction (2050)
    data_2050 = band_summary[band_summary['Year'] == 2050]
    
    if not data_2050.empty:
        ax1.scatter(data_2050['Alternative_Share_pct'], 
                   data_2050['Band_Emission_Reduction_pct'],
                   s=100, alpha=0.7, c=data_2050['Baseline_Production_kt'], 
                   cmap='viridis')
        
        # Add band labels
        for _, row in data_2050.iterrows():
            ax1.annotate(row['Band_Key'], 
                        (row['Alternative_Share_pct'], row['Band_Emission_Reduction_pct']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax1.set_xlabel('Technology Adoption Rate (%)')
        ax1.set_ylabel('Emission Reduction (%)')
        ax1.set_title('Technology Adoption vs Emission Reduction (2050)')
        ax1.grid(True, alpha=0.3)
        
        # Add diagonal reference line
        max_val = max(data_2050['Alternative_Share_pct'].max(), 
                     data_2050['Band_Emission_Reduction_pct'].max())
        ax1.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='1:1 ratio')
        ax1.legend()
    
    # 2. Emission Reduction Timeline
    key_years = [2030, 2040, 2050]
    pathway_years = emission_pathways[emission_pathways['Year'].isin(key_years)]
    
    if not pathway_years.empty:
        baseline_emissions = pathway_years['Baseline_Emissions_MtCO2'].iloc[0]
        
        ax2.plot(pathway_years['Year'], 
                pathway_years['Total_Emissions_MtCO2'], 
                'b-o', linewidth=3, label='Actual Emissions')
        ax2.axhline(y=baseline_emissions, color='r', linestyle='--', 
                   label=f'Baseline ({baseline_emissions:.1f} MtCO2)')
        
        ax2.fill_between(pathway_years['Year'], 
                        pathway_years['Total_Emissions_MtCO2'],
                        baseline_emissions, alpha=0.3, label='Emission Reduction')
        
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Emissions (MtCO2)')
        ax2.set_title('Emission Reduction Timeline')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # 3. Band-wise Emission Contribution (2050)
    if not data_2050.empty:
        # Calculate remaining emissions by band
        data_2050['Remaining_Emissions_MtCO2'] = data_2050['Remaining_Emissions_tCO2'] / 1e6
        data_2050['Abated_Emissions_MtCO2'] = data_2050['Alternative_Abatement_tCO2'] / 1e6
        
        bands = data_2050['Band_Key']
        remaining = data_2050['Remaining_Emissions_MtCO2']
        abated = data_2050['Abated_Emissions_MtCO2']
        
        x = range(len(bands))
        width = 0.35
        
        ax3.bar([i - width/2 for i in x], remaining, width, 
               label='Remaining Emissions', alpha=0.7, color='red')
        ax3.bar([i + width/2 for i in x], abated, width, 
               label='Abated Emissions', alpha=0.7, color='green')
        
        ax3.set_xlabel('Technology Band')
        ax3.set_ylabel('Emissions (MtCO2)')
        ax3.set_title('Emissions by Band: Remaining vs Abated (2050)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(bands, rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # 4. Substitution Mechanism Illustration
    years = [2030, 2040, 2050]
    total_alternative = []
    total_baseline = []
    
    for year in years:
        year_data = band_summary[band_summary['Year'] == year]
        if not year_data.empty:
            total_alternative.append(year_data['Alternative_Production_kt'].sum())
            total_baseline.append(year_data['Remaining_Baseline_kt'].sum())
    
    if total_alternative and total_baseline:
        width = 0.35
        x = range(len(years))
        
        ax4.bar([i - width/2 for i in x], total_baseline, width, 
               label='Baseline Production', alpha=0.7)
        ax4.bar([i + width/2 for i in x], total_alternative, width, 
               label='Alternative Production', alpha=0.7)
        
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Production (kt/year)')
        ax4.set_title('Production Substitution: Baseline → Alternative')
        ax4.set_xticks(x)
        ax4.set_xticklabels(years)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs_fixed_bands/emission_reduction_mechanism_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Visualization saved: outputs_fixed_bands/emission_reduction_mechanism_analysis.png")

def main():
    """Main analysis function"""
    
    try:
        analyze_emission_reduction_mechanism()
        
        print("\n" + "=" * 60)
        print("🎯 CONCLUSION: MODEL LOGIC CLARIFICATION")
        print("=" * 60)
        print()
        print("✅ PRIMARY FOCUS: TECHNOLOGY ADOPTION")
        print("   • Model optimizes WHEN and HOW MUCH alternative capacity to install")
        print("   • Investment decisions drive technology deployment")
        print("   • Production follows from installed capacity")
        print()
        print("🔄 EMISSION REDUCTION MECHANISM:")
        print("   1. Install alternative technology capacity (kt/year)")
        print("   2. Alternative production substitutes baseline production")
        print("   3. Same production volume × lower emission intensity = emission reduction")
        print()
        print("📊 KEY INSIGHT:")
        print("   • Model is about RETROFITTING existing production capacity")
        print("   • NOT about changing total production volumes")
        print("   • Emission reduction = Technology adoption × Emission intensity improvement")
        print()
        print("🎯 Model answers: WHICH technologies to deploy WHEN for cost-optimal decarbonization")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()