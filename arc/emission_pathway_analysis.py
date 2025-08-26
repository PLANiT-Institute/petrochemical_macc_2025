#!/usr/bin/env python3
"""
Emission Pathway Analysis: Baseline to 2050 with Technology Shares

This analysis shows the detailed emission reduction pathway from baseline (2023) 
to 2050 with specific technology adoption shares at each step.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def analyze_emission_pathway():
    """Analyze detailed emission pathway from baseline to 2050 with technology shares"""
    
    print("🛣️  EMISSION PATHWAY ANALYSIS: BASELINE TO 2050")
    print("=" * 65)
    
    # Load model results
    results_dir = Path("outputs_fixed_bands")
    
    band_summary = pd.read_csv(results_dir / "band_level_summary.csv")
    deployment = pd.read_csv(results_dir / "alternative_deployment_by_band.csv")
    emission_pathways = pd.read_csv(results_dir / "emission_pathways_by_source.csv")
    baseline_data = pd.read_csv(results_dir / "fixed_band_baseline.csv")
    
    # Create comprehensive pathway analysis
    pathway_analysis = create_detailed_pathway(band_summary, deployment, emission_pathways, baseline_data)
    
    # Generate visualizations
    create_pathway_visualizations(pathway_analysis, results_dir)
    
    return pathway_analysis

def create_detailed_pathway(band_summary, deployment, emission_pathways, baseline_data):
    """Create detailed emission pathway with technology shares"""
    
    print("\n📊 1. BASELINE EMISSION STRUCTURE (2023)")
    print("-" * 45)
    
    # Baseline analysis
    baseline_summary = {}
    total_baseline_emissions = 0
    total_baseline_production = 0
    
    for _, row in baseline_data.iterrows():
        band_key = row['Band_Key']
        emissions = row['Baseline_Emissions_tCO2'] / 1e6  # Convert to MtCO2
        production = row['Baseline_Activity_kt']
        emission_intensity = row['Baseline_Emission_Intensity_tCO2_per_t']
        
        baseline_summary[band_key] = {
            'emissions_mtco2': emissions,
            'production_kt': production,
            'emission_intensity': emission_intensity
        }
        
        total_baseline_emissions += emissions
        total_baseline_production += production
        
        print(f"  {band_key}: {emissions:.2f} MtCO2 from {production:.0f} kt ({emission_intensity:.2f} tCO2/t)")
    
    print(f"\n  🎯 TOTAL BASELINE: {total_baseline_emissions:.1f} MtCO2 from {total_baseline_production:.0f} kt")
    print(f"  📊 Average Intensity: {total_baseline_emissions*1e6/total_baseline_production/1000:.2f} tCO2/t")
    
    # Analyze pathway by key years
    pathway_data = []
    key_years = [2023, 2030, 2040, 2050]  # Include baseline year
    
    for year in key_years:
        print(f"\n🎯 {year} EMISSION PATHWAY ANALYSIS")
        print("-" * 45)
        
        if year == 2023:
            # Baseline year
            year_data = {
                'year': year,
                'total_emissions_mtco2': total_baseline_emissions,
                'total_abatement_mtco2': 0,
                'emission_reduction_pct': 0,
                'bands': {}
            }
            
            for band_key, data in baseline_summary.items():
                year_data['bands'][band_key] = {
                    'baseline_production_kt': data['production_kt'],
                    'alternative_production_kt': 0,
                    'alternative_share_pct': 0,
                    'emissions_mtco2': data['emissions_mtco2'],
                    'abatement_mtco2': 0,
                    'emission_reduction_pct': 0,
                    'technologies': {}
                }
            
            print(f"  📊 Baseline Emissions: {total_baseline_emissions:.1f} MtCO2")
            print(f"  ⚡ No alternative technologies deployed")
            
        else:
            # Future years with technology deployment
            year_band_data = band_summary[band_summary['Year'] == year]
            year_deployment = deployment[deployment['Year'] == year]
            year_pathways = emission_pathways[emission_pathways['Year'] == year]
            
            if year_pathways.empty:
                continue
                
            total_emissions = year_pathways['Total_Emissions_MtCO2'].iloc[0]
            total_abatement = year_pathways['Total_Abatement_MtCO2'].iloc[0]
            emission_reduction = year_pathways['Emission_Reduction_from_Baseline_pct'].iloc[0]
            
            year_data = {
                'year': year,
                'total_emissions_mtco2': total_emissions,
                'total_abatement_mtco2': total_abatement,
                'emission_reduction_pct': emission_reduction,
                'bands': {}
            }
            
            print(f"  📊 Total Emissions: {total_emissions:.1f} MtCO2")
            print(f"  ⚡ Total Abatement: {total_abatement:.1f} MtCO2")
            print(f"  📈 Reduction from Baseline: {emission_reduction:.1f}%")
            print(f"\n  🏭 BAND-LEVEL ANALYSIS:")
            
            for _, band_row in year_band_data.iterrows():
                band_key = band_row['Band_Key']
                
                # Band-level data
                baseline_prod = band_row['Baseline_Production_kt']
                alt_prod = band_row['Alternative_Production_kt']
                alt_share = band_row['Alternative_Share_pct']
                remaining_emissions = band_row['Remaining_Emissions_tCO2'] / 1e6
                abatement = band_row['Alternative_Abatement_tCO2'] / 1e6
                band_reduction = band_row['Band_Emission_Reduction_pct']
                
                # Get technologies for this band
                band_techs = year_deployment[year_deployment['Target_Band'] == band_key]
                
                tech_details = {}
                for _, tech_row in band_techs.iterrows():
                    if tech_row['Production_kt'] > 0.01:  # Only include active technologies
                        tech_id = tech_row['TechID']
                        tech_production = tech_row['Production_kt']
                        tech_penetration = tech_row['Penetration_Rate'] * 100
                        tech_abatement = tech_row['Abatement_tCO2'] / 1e6
                        
                        tech_details[tech_id] = {
                            'production_kt': tech_production,
                            'penetration_pct': tech_penetration,
                            'abatement_mtco2': tech_abatement
                        }
                
                year_data['bands'][band_key] = {
                    'baseline_production_kt': baseline_prod,
                    'alternative_production_kt': alt_prod,
                    'alternative_share_pct': alt_share,
                    'emissions_mtco2': remaining_emissions + (alt_prod * baseline_summary[band_key]['emission_intensity'] / 1000) - abatement,
                    'abatement_mtco2': abatement,
                    'emission_reduction_pct': band_reduction,
                    'technologies': tech_details
                }
                
                print(f"    {band_key}:")
                print(f"      Production: {baseline_prod:.0f} kt baseline → {alt_prod:.0f} kt alternative ({alt_share:.1f}%)")
                print(f"      Emissions: {remaining_emissions:.2f} MtCO2 remaining, {abatement:.2f} MtCO2 abated ({band_reduction:.1f}% reduction)")
                
                if tech_details:
                    print(f"      Technologies:")
                    for tech_id, tech_data in tech_details.items():
                        print(f"        • {tech_id}: {tech_data['penetration_pct']:.1f}% penetration → {tech_data['abatement_mtco2']:.3f} MtCO2")
        
        pathway_data.append(year_data)
    
    print(f"\n📈 2. EMISSION REDUCTION TRAJECTORY")
    print("-" * 45)
    
    print("Year | Total Emissions | Abatement | Reduction | Key Technology Adoptions")
    print("-" * 75)
    
    for data in pathway_data:
        year = data['year']
        emissions = data['total_emissions_mtco2']
        abatement = data['total_abatement_mtco2']
        reduction = data['emission_reduction_pct']
        
        # Find top 3 technology adoptions for this year
        tech_adoptions = []
        for band_key, band_data in data['bands'].items():
            for tech_id, tech_data in band_data['technologies'].items():
                if tech_data['abatement_mtco2'] > 0.01:
                    tech_adoptions.append((tech_id, tech_data['abatement_mtco2']))
        
        tech_adoptions.sort(key=lambda x: x[1], reverse=True)
        top_techs = ", ".join([f"{tech}({abate:.2f})" for tech, abate in tech_adoptions[:3]])
        
        print(f"{year} | {emissions:11.1f} | {abatement:8.1f} | {reduction:8.1f}% | {top_techs}")
    
    # Save detailed pathway data
    save_pathway_data(pathway_data, Path("outputs_fixed_bands"))
    
    return pathway_data

def save_pathway_data(pathway_data, output_dir):
    """Save detailed pathway data to CSV files"""
    
    # 1. Year-by-year summary
    summary_data = []
    for data in pathway_data:
        summary_data.append({
            'Year': data['year'],
            'Total_Emissions_MtCO2': data['total_emissions_mtco2'],
            'Total_Abatement_MtCO2': data['total_abatement_mtco2'],
            'Emission_Reduction_pct': data['emission_reduction_pct']
        })
    
    pd.DataFrame(summary_data).to_csv(output_dir / "emission_pathway_summary.csv", index=False)
    
    # 2. Detailed band-technology breakdown
    detailed_data = []
    for data in pathway_data:
        year = data['year']
        for band_key, band_data in data['bands'].items():
            
            # Band summary row
            detailed_data.append({
                'Year': year,
                'Band': band_key,
                'Technology': 'BAND_TOTAL',
                'Baseline_Production_kt': band_data['baseline_production_kt'],
                'Alternative_Production_kt': band_data['alternative_production_kt'],
                'Alternative_Share_pct': band_data['alternative_share_pct'],
                'Emissions_MtCO2': band_data['emissions_mtco2'],
                'Abatement_MtCO2': band_data['abatement_mtco2'],
                'Emission_Reduction_pct': band_data['emission_reduction_pct'],
                'Technology_Production_kt': band_data['alternative_production_kt'],
                'Technology_Penetration_pct': band_data['alternative_share_pct'],
                'Technology_Abatement_MtCO2': band_data['abatement_mtco2']
            })
            
            # Individual technology rows
            for tech_id, tech_data in band_data['technologies'].items():
                detailed_data.append({
                    'Year': year,
                    'Band': band_key,
                    'Technology': tech_id,
                    'Baseline_Production_kt': band_data['baseline_production_kt'],
                    'Alternative_Production_kt': band_data['alternative_production_kt'],
                    'Alternative_Share_pct': band_data['alternative_share_pct'],
                    'Emissions_MtCO2': band_data['emissions_mtco2'],
                    'Abatement_MtCO2': band_data['abatement_mtco2'],
                    'Emission_Reduction_pct': band_data['emission_reduction_pct'],
                    'Technology_Production_kt': tech_data['production_kt'],
                    'Technology_Penetration_pct': tech_data['penetration_pct'],
                    'Technology_Abatement_MtCO2': tech_data['abatement_mtco2']
                })
    
    pd.DataFrame(detailed_data).to_csv(output_dir / "detailed_emission_pathway_with_technologies.csv", index=False)

def create_pathway_visualizations(pathway_data, output_dir):
    """Create comprehensive pathway visualizations"""
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Overall emission trajectory (top left)
    ax1 = plt.subplot(3, 3, (1, 2))
    
    years = [data['year'] for data in pathway_data]
    emissions = [data['total_emissions_mtco2'] for data in pathway_data]
    abatements = [data['total_abatement_mtco2'] for data in pathway_data]
    
    ax1.plot(years, emissions, 'b-o', linewidth=3, markersize=8, label='Actual Emissions')
    ax1.bar(years, abatements, alpha=0.6, color='green', label='Abatement Achieved')
    
    baseline_emission = pathway_data[0]['total_emissions_mtco2']
    ax1.axhline(y=baseline_emission, color='red', linestyle='--', linewidth=2, label=f'Baseline ({baseline_emission:.1f} MtCO2)')
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (MtCO2)')
    ax1.set_title('Korea Petrochemical Emission Pathway: Baseline to 2050', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add reduction percentages as annotations
    for i, (year, emission, reduction_pct) in enumerate(zip(years[1:], emissions[1:], [d['emission_reduction_pct'] for d in pathway_data[1:]])):
        ax1.annotate(f'-{reduction_pct:.1f}%', 
                    (year, emission), 
                    xytext=(0, 10), textcoords='offset points', 
                    ha='center', fontsize=10, fontweight='bold')
    
    # 2. Technology adoption timeline (top right)
    ax2 = plt.subplot(3, 3, 3)
    
    # Collect all unique technologies
    all_techs = set()
    for data in pathway_data:
        for band_data in data['bands'].values():
            all_techs.update(band_data['technologies'].keys())
    
    # Plot adoption timeline for top technologies
    top_techs = list(all_techs)[:8]  # Top 8 technologies
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_techs)))
    
    for i, tech in enumerate(top_techs):
        tech_timeline = []
        for data in pathway_data:
            total_abatement = 0
            for band_data in data['bands'].values():
                if tech in band_data['technologies']:
                    total_abatement += band_data['technologies'][tech]['abatement_mtco2']
            tech_timeline.append(total_abatement)
        
        if max(tech_timeline) > 0.01:  # Only plot if significant
            ax2.plot(years, tech_timeline, 'o-', color=colors[i], label=tech.replace('_', ' '), linewidth=2)
    
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Abatement (MtCO2)')
    ax2.set_title('Technology Deployment Timeline')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # 3-5. Band-level emission reduction (middle row)
    band_groups = [['NCC_HT', 'NCC_MT', 'NCC_LT'], ['BTX_HT', 'BTX_MT', 'BTX_LT'], ['C4_HT', 'C4_MT', 'C4_LT']]
    group_titles = ['NCC (Naphtha Cracking)', 'BTX (Benzene-Toluene-Xylene)', 'C4 (C4 Chemicals)']
    
    for idx, (bands, title) in enumerate(zip(band_groups, group_titles)):
        ax = plt.subplot(3, 3, 4 + idx)
        
        width = 0.25
        x = np.arange(len(years))
        
        for i, band in enumerate(bands):
            band_emissions = []
            band_abatements = []
            
            for data in pathway_data:
                if band in data['bands']:
                    band_data = data['bands'][band]
                    # Calculate remaining emissions
                    baseline_emissions = baseline_emission * (band_data['baseline_production_kt'] / 11600) * (band_data.get('emission_intensity', 1.5) / 1.61)
                    remaining = baseline_emissions - band_data['abatement_mtco2']
                    band_emissions.append(remaining)
                    band_abatements.append(band_data['abatement_mtco2'])
                else:
                    band_emissions.append(0)
                    band_abatements.append(0)
            
            ax.bar(x + i*width - width, band_emissions, width, label=f'{band.split("_")[1]} Remaining', alpha=0.7)
            ax.bar(x + i*width - width, band_abatements, width, bottom=band_emissions, label=f'{band.split("_")[1]} Abated', alpha=0.9)
        
        ax.set_xlabel('Year')
        ax.set_ylabel('Emissions (MtCO2)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(years)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # 6-8. Technology share analysis (bottom row)
    years_analysis = [2030, 2040, 2050]
    
    for idx, analysis_year in enumerate(years_analysis):
        ax = plt.subplot(3, 3, 7 + idx)
        
        year_data = next((data for data in pathway_data if data['year'] == analysis_year), None)
        if not year_data:
            continue
        
        # Collect technology shares
        tech_shares = {}
        for band_key, band_data in year_data['bands'].items():
            for tech_id, tech_data in band_data['technologies'].items():
                if tech_data['abatement_mtco2'] > 0.01:
                    tech_shares[f"{tech_id}"] = tech_data['abatement_mtco2']
        
        if tech_shares:
            # Create pie chart for top technologies
            sorted_techs = sorted(tech_shares.items(), key=lambda x: x[1], reverse=True)[:6]
            other_sum = sum(tech_shares[tech] for tech in tech_shares if tech not in [t[0] for t in sorted_techs])
            
            if other_sum > 0:
                sorted_techs.append(('Others', other_sum))
            
            labels, values = zip(*sorted_techs)
            
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            for autotext in autotexts:
                autotext.set_fontsize(8)
            
            ax.set_title(f'{analysis_year} Technology Shares\n(by Abatement)')
    
    plt.tight_layout()
    plt.savefig(output_dir / "comprehensive_emission_pathway_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Comprehensive pathway visualization saved: {output_dir}/comprehensive_emission_pathway_analysis.png")

def main():
    """Main analysis function"""
    
    try:
        pathway_analysis = analyze_emission_pathway()
        
        print(f"\n" + "=" * 65)
        print("📊 PATHWAY SUMMARY: KEY INSIGHTS")
        print("=" * 65)
        
        baseline_emissions = pathway_analysis[0]['total_emissions_mtco2']
        final_emissions = pathway_analysis[-1]['total_emissions_mtco2']
        total_reduction = (1 - final_emissions/baseline_emissions) * 100
        
        print(f"🎯 2023 Baseline: {baseline_emissions:.1f} MtCO2")
        print(f"🎯 2050 Final: {final_emissions:.1f} MtCO2")
        print(f"📈 Total Reduction: {total_reduction:.1f}%")
        
        print(f"\n🚀 KEY MILESTONES:")
        for data in pathway_analysis[1:]:
            year = data['year']
            reduction = data['emission_reduction_pct']
            abatement = data['total_abatement_mtco2']
            print(f"  {year}: {reduction:.1f}% reduction ({abatement:.1f} MtCO2 abated)")
        
        print(f"\n✅ Detailed pathway files generated:")
        print(f"  • emission_pathway_summary.csv")
        print(f"  • detailed_emission_pathway_with_technologies.csv")
        print(f"  • comprehensive_emission_pathway_analysis.png")
        
    except Exception as e:
        print(f"❌ Error in pathway analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()