#!/usr/bin/env python3
"""
Run the corrected MACC model with band-based structure and generate comprehensive outputs
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add the petrochem package to path
sys.path.insert(0, str(Path(__file__).parent))

from petrochem.lib.core.technology import (
    TechnologyTransition, AlternativeTechnology, TechBand, TechType,
    CostStructure, TechnologyConstraints
)
from petrochem.lib.core.scenario import EmissionsScenario, EmissionsBaseline, EmissionsTarget, ProcessBaseline
from petrochem.lib.core.portfolio import TechnologyPortfolio
from petrochem.lib.optimization.model_builder_corrected import CorrectedMACCModelBuilder
from petrochem.model_pyomo import solve_model

def create_band_based_data():
    """Create test data based on the band structure from Excel"""
    
    # Technology bands from Excel structure
    bands_baseline = {
        'NCC_HT': {'activity_kt': 3500, 'emission_intensity': 2.85, 'sec_gj_per_t': 28.5},
        'NCC_MT': {'activity_kt': 2800, 'emission_intensity': 1.23, 'sec_gj_per_t': 12.3},
        'NCC_LT': {'activity_kt': 1200, 'emission_intensity': 0.65, 'sec_gj_per_t': 8.7},
        'BTX_HT': {'activity_kt': 1200, 'emission_intensity': 1.52, 'sec_gj_per_t': 15.2},
        'BTX_MT': {'activity_kt': 800, 'emission_intensity': 0.89, 'sec_gj_per_t': 8.9},
        'BTX_LT': {'activity_kt': 1100, 'emission_intensity': 0.48, 'sec_gj_per_t': 6.4},
        'C4_HT': {'activity_kt': 450, 'emission_intensity': 2.21, 'sec_gj_per_t': 22.1},
        'C4_MT': {'activity_kt': 350, 'emission_intensity': 0.98, 'sec_gj_per_t': 9.8},
        'C4_LT': {'activity_kt': 200, 'emission_intensity': 0.54, 'sec_gj_per_t': 7.2}
    }
    
    # Create process baselines
    process_baselines = []
    
    # NCC process
    ncc_total_production = sum(bands_baseline[k]['activity_kt'] for k in ['NCC_HT', 'NCC_MT', 'NCC_LT'])
    ncc_weighted_ei = sum(bands_baseline[k]['activity_kt'] * bands_baseline[k]['emission_intensity'] 
                         for k in ['NCC_HT', 'NCC_MT', 'NCC_LT']) / ncc_total_production
    
    process_baselines.append(ProcessBaseline(
        process_type="NCC",
        production_kt=ncc_total_production,
        emission_intensity_t_co2_per_t=ncc_weighted_ei,
        current_band_distribution={
            "NCC_HT": bands_baseline['NCC_HT']['activity_kt'] / ncc_total_production,
            "NCC_MT": bands_baseline['NCC_MT']['activity_kt'] / ncc_total_production,
            "NCC_LT": bands_baseline['NCC_LT']['activity_kt'] / ncc_total_production
        }
    ))
    
    # BTX process
    btx_total_production = sum(bands_baseline[k]['activity_kt'] for k in ['BTX_HT', 'BTX_MT', 'BTX_LT'])
    btx_weighted_ei = sum(bands_baseline[k]['activity_kt'] * bands_baseline[k]['emission_intensity'] 
                         for k in ['BTX_HT', 'BTX_MT', 'BTX_LT']) / btx_total_production
    
    process_baselines.append(ProcessBaseline(
        process_type="BTX", 
        production_kt=btx_total_production,
        emission_intensity_t_co2_per_t=btx_weighted_ei,
        current_band_distribution={
            "BTX_HT": bands_baseline['BTX_HT']['activity_kt'] / btx_total_production,
            "BTX_MT": bands_baseline['BTX_MT']['activity_kt'] / btx_total_production,
            "BTX_LT": bands_baseline['BTX_LT']['activity_kt'] / btx_total_production
        }
    ))
    
    # C4 process
    c4_total_production = sum(bands_baseline[k]['activity_kt'] for k in ['C4_HT', 'C4_MT', 'C4_LT'])
    c4_weighted_ei = sum(bands_baseline[k]['activity_kt'] * bands_baseline[k]['emission_intensity'] 
                        for k in ['C4_HT', 'C4_MT', 'C4_LT']) / c4_total_production
    
    process_baselines.append(ProcessBaseline(
        process_type="C4",
        production_kt=c4_total_production,
        emission_intensity_t_co2_per_t=c4_weighted_ei,
        current_band_distribution={
            "C4_HT": bands_baseline['C4_HT']['activity_kt'] / c4_total_production,
            "C4_MT": bands_baseline['C4_MT']['activity_kt'] / c4_total_production,
            "C4_LT": bands_baseline['C4_LT']['activity_kt'] / c4_total_production
        }
    ))
    
    total_emissions = sum(pb.total_emissions_mt for pb in process_baselines)
    
    baseline = EmissionsBaseline(
        year=2023,
        total_emissions_mt=total_emissions,
        process_baselines=process_baselines
    )
    
    # Create emissions targets (80% reduction by 2050)
    targets = [
        EmissionsTarget(year=2030, target_mt_co2=total_emissions * 0.85),  # 15% reduction
        EmissionsTarget(year=2040, target_mt_co2=total_emissions * 0.50),  # 50% reduction
        EmissionsTarget(year=2050, target_mt_co2=total_emissions * 0.20),  # 80% reduction
    ]
    
    scenario = EmissionsScenario(
        baseline=baseline,
        timeline=list(range(2023, 2051)),
        targets=targets
    )
    
    # Create alternative technologies (band-specific, matching Excel structure)
    technologies = []
    
    # NCC alternatives
    technologies.extend([
        AlternativeTechnology(
            tech_id="NCC_HT_Electric",
            name="NCC E-cracker",
            process_type="NCC",
            emission_factor=0.85,  # Low emissions
            cost_structure=CostStructure(
                capex_usd_per_kt=280000,  # $280/t from Excel
                opex_delta_usd_per_t=25,  # Operating cost premium
                maintenance_pct=0.035
            ),
            constraints=TechnologyConstraints(
                lifetime_years=25,
                start_year=2028,
                ramp_rate_per_year=0.15,
                max_applicability=0.4,
                technical_readiness_level=6
            )
        ),
        AlternativeTechnology(
            tech_id="NCC_MT_HeatPump", 
            name="NCC Heat Pump",
            process_type="NCC",
            emission_factor=0.43,  # Medium reduction
            cost_structure=CostStructure(
                capex_usd_per_kt=80000,   # $80/t from Excel
                opex_delta_usd_per_t=-20, # Operating savings
                maintenance_pct=0.025
            ),
            constraints=TechnologyConstraints(
                lifetime_years=25,
                start_year=2026,
                ramp_rate_per_year=0.20,
                max_applicability=0.6,
                technical_readiness_level=8
            )
        ),
        AlternativeTechnology(
            tech_id="BTX_HT_Hydrogen",
            name="BTX H2-reformer", 
            process_type="BTX",
            emission_factor=0.22,  # High reduction
            cost_structure=CostStructure(
                capex_usd_per_kt=260000,  # $260/t from Excel
                opex_delta_usd_per_t=-10, # H2 fuel savings
                maintenance_pct=0.042
            ),
            constraints=TechnologyConstraints(
                lifetime_years=25,
                start_year=2032,
                ramp_rate_per_year=0.10,
                max_applicability=0.4,
                technical_readiness_level=4
            )
        ),
        AlternativeTechnology(
            tech_id="C4_LT_HeatPump",
            name="C4 Heat Pump",
            process_type="C4",
            emission_factor=0.29,  # Moderate reduction
            cost_structure=CostStructure(
                capex_usd_per_kt=50000,   # $50/t from Excel
                opex_delta_usd_per_t=-20, # Efficiency savings
                maintenance_pct=0.022
            ),
            constraints=TechnologyConstraints(
                lifetime_years=25,
                start_year=2024,
                ramp_rate_per_year=0.28,
                max_applicability=0.7,
                technical_readiness_level=9
            )
        )
    ])
    
    portfolio = TechnologyPortfolio()
    for tech in technologies:
        portfolio.add_technology(tech)
    
    return scenario, portfolio

def generate_comprehensive_outputs(model, scenario, portfolio, output_dir="outputs_band_model"):
    """Generate comprehensive outputs for the band-based model"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n📊 Generating comprehensive outputs...")
    
    # 1. Technology deployment timeline
    deployment_data = []
    for tech in model.TECHS:
        for year in model.YEARS:
            install_val = model.install_capacity[tech, year].value or 0
            total_cap_val = model.total_capacity[tech, year].value or 0
            production_val = model.production[tech, year].value or 0
            abatement_val = model.abatement[tech, year].value or 0
            
            deployment_data.append({
                'TechID': tech,
                'Year': year,
                'Install_Capacity_kt': install_val,
                'Total_Capacity_kt': total_cap_val,
                'Production_kt': production_val,
                'Abatement_tCO2': abatement_val,
                'Capacity_Utilization': production_val / total_cap_val if total_cap_val > 0 else 0
            })
    
    deployment_df = pd.DataFrame(deployment_data)
    deployment_df.to_csv(f"{output_dir}/deployment_timeline.csv", index=False)
    print(f"   ✅ Deployment timeline saved")
    
    # 2. Emissions pathway
    emissions_data = []
    baseline_emissions = scenario.baseline.total_emissions_mt
    
    for year in model.YEARS:
        required_abatement = scenario.get_required_abatement(year)
        achieved_abatement = sum(model.abatement[tech, year].value or 0 
                               for tech in model.TECHS) / 1e6  # Convert to Mt
        shortfall = model.shortfall[year].value / 1e6 if hasattr(model, 'shortfall') else 0
        
        target_emissions = scenario.get_target_emissions(year)
        actual_emissions = baseline_emissions - achieved_abatement
        
        emissions_data.append({
            'Year': year,
            'Baseline_Emissions_Mt': baseline_emissions,
            'Target_Emissions_Mt': target_emissions,
            'Actual_Emissions_Mt': actual_emissions,
            'Required_Abatement_Mt': required_abatement,
            'Achieved_Abatement_Mt': achieved_abatement,
            'Shortfall_Mt': shortfall,
            'Target_Achievement_Pct': (achieved_abatement / required_abatement * 100) if required_abatement > 0 else 100
        })
    
    emissions_df = pd.DataFrame(emissions_data)
    emissions_df.to_csv(f"{output_dir}/emissions_pathway.csv", index=False)
    print(f"   ✅ Emissions pathway saved")
    
    # 3. Technology band analysis
    band_analysis = []
    
    # Group technologies by process and band
    tech_bands = {
        'NCC_HT': ['NCC_HT_Electric'],
        'NCC_MT': ['NCC_MT_HeatPump'], 
        'BTX_HT': ['BTX_HT_Hydrogen'],
        'C4_LT': ['C4_LT_HeatPump']
    }
    
    for year in [2030, 2040, 2050]:
        if year in model.YEARS:
            for band, tech_list in tech_bands.items():
                total_capacity = sum(model.total_capacity[tech, year].value or 0 
                                   for tech in tech_list if tech in model.TECHS)
                total_production = sum(model.production[tech, year].value or 0
                                     for tech in tech_list if tech in model.TECHS)
                total_abatement = sum(model.abatement[tech, year].value or 0
                                    for tech in tech_list if tech in model.TECHS)
                
                band_analysis.append({
                    'Year': year,
                    'Band': band,
                    'Technology_Group': band.split('_')[0],
                    'Temperature_Band': band.split('_')[1],
                    'Total_Capacity_kt': total_capacity,
                    'Total_Production_kt': total_production,
                    'Total_Abatement_tCO2': total_abatement,
                    'Penetration_Rate': total_capacity / 1000  # Simplified penetration
                })
    
    band_df = pd.DataFrame(band_analysis)
    band_df.to_csv(f"{output_dir}/band_analysis.csv", index=False)
    print(f"   ✅ Band analysis saved")
    
    # 4. Cost breakdown
    cost_data = []
    
    for year in [2030, 2040, 2050]:
        if year in model.YEARS:
            year_capex = 0
            year_opex = 0
            
            for tech in model.TECHS:
                install_cap = model.install_capacity[tech, year].value or 0
                production = model.production[tech, year].value or 0
                
                tech_obj = portfolio.technologies[tech]
                capex_per_kt = tech_obj.cost_structure.capex_usd_per_kt / 1e6  # Million USD/kt
                opex_per_t = tech_obj.cost_structure.opex_delta_usd_per_t
                
                # Annualized CAPEX
                crf = 0.05 / (1 - (1.05) ** -tech_obj.constraints.lifetime_years)
                annual_capex = install_cap * capex_per_kt * crf
                
                # Annual OPEX  
                annual_opex = production * opex_per_t / 1000  # Million USD
                
                year_capex += annual_capex
                year_opex += annual_opex
                
                if install_cap > 0 or production > 0:
                    cost_data.append({
                        'Year': year,
                        'TechID': tech,
                        'Annual_CAPEX_Million_USD': annual_capex,
                        'Annual_OPEX_Million_USD': annual_opex,
                        'Total_Annual_Cost_Million_USD': annual_capex + annual_opex,
                        'Install_Capacity_kt': install_cap,
                        'Production_kt': production
                    })
    
    cost_df = pd.DataFrame(cost_data)
    cost_df.to_csv(f"{output_dir}/cost_breakdown.csv", index=False)
    print(f"   ✅ Cost breakdown saved")
    
    # 5. Generate visualization plots
    generate_plots(emissions_df, deployment_df, band_df, cost_df, output_dir)
    
    return {
        'deployment': deployment_df,
        'emissions': emissions_df,
        'bands': band_df,
        'costs': cost_df
    }

def generate_plots(emissions_df, deployment_df, band_df, cost_df, output_dir):
    """Generate visualization plots"""
    
    plt.style.use('seaborn-v0_8')
    
    # 1. Emissions pathway plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.plot(emissions_df['Year'], emissions_df['Baseline_Emissions_Mt'], 
            'k--', linewidth=2, label='Baseline Emissions')
    ax.plot(emissions_df['Year'], emissions_df['Target_Emissions_Mt'], 
            'r-', linewidth=2, label='Target Emissions')
    ax.plot(emissions_df['Year'], emissions_df['Actual_Emissions_Mt'], 
            'g-', linewidth=2, label='Actual Emissions')
    
    ax.fill_between(emissions_df['Year'], emissions_df['Actual_Emissions_Mt'], 
                    emissions_df['Target_Emissions_Mt'], alpha=0.3, color='red', 
                    label='Shortfall')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2)')
    ax.set_title('Korea Petrochemical Emissions Pathway\n(Band-based MACC Model)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/emissions_pathway.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Technology deployment by band
    if not band_df.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Capacity by band
        pivot_cap = band_df.pivot(index='Year', columns='Band', values='Total_Capacity_kt')
        pivot_cap.plot(kind='bar', ax=ax1, stacked=True)
        ax1.set_title('Technology Capacity by Band')
        ax1.set_ylabel('Capacity (kt/year)')
        ax1.legend(title='Technology Band')
        
        # Abatement by band
        pivot_abate = band_df.pivot(index='Year', columns='Band', values='Total_Abatement_tCO2')
        pivot_abate.plot(kind='bar', ax=ax2, stacked=True)
        ax2.set_title('Abatement by Band')  
        ax2.set_ylabel('Abatement (tCO2)')
        ax2.legend(title='Technology Band')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/band_deployment.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Cost evolution
    if not cost_df.empty:
        yearly_costs = cost_df.groupby('Year')[['Annual_CAPEX_Million_USD', 'Annual_OPEX_Million_USD']].sum()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.bar(yearly_costs.index, yearly_costs['Annual_CAPEX_Million_USD'], 
               label='CAPEX', alpha=0.7)
        ax.bar(yearly_costs.index, yearly_costs['Annual_OPEX_Million_USD'], 
               bottom=yearly_costs['Annual_CAPEX_Million_USD'], label='OPEX', alpha=0.7)
        
        ax.set_xlabel('Year')
        ax.set_ylabel('Annual Cost (Million USD)')
        ax.set_title('Technology Investment and Operating Costs')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_evolution.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"   ✅ Plots generated")

def main():
    """Main function to run the band-based MACC model"""
    
    print("🚀 Running Band-Based Korea Petrochemical MACC Model")
    print("=" * 60)
    
    # Create test data
    print("1. Creating band-based test data...")
    scenario, portfolio = create_band_based_data()
    
    print(f"   - Technology groups: NCC, BTX, C4")
    print(f"   - Bands: HT (high temp), MT (medium temp), LT (low temp)")
    print(f"   - Technologies: {len(portfolio.technologies)}")
    print(f"   - Baseline emissions: {scenario.baseline.total_emissions_mt:.1f} MtCO2")
    print(f"   - Timeline: {min(scenario.timeline)}-{max(scenario.timeline)}")
    
    # Build model
    print("\n2. Building corrected optimization model...")
    builder = CorrectedMACCModelBuilder(scenario, portfolio)
    model = builder.build_model(allow_slack=True, discount_rate=0.05)
    
    print(f"   - Model variables: {sum(builder.get_model_summary()['variables'].values())}")
    print("   ✅ Model built with corrected scale units")
    
    # Solve model
    print("\n3. Solving optimization model...")
    solver_used, results = solve_model(model, solver="glpk")
    print(f"   ✅ Model solved with {solver_used}")
    
    # Generate outputs
    print("\n4. Generating comprehensive outputs...")
    outputs = generate_comprehensive_outputs(model, scenario, portfolio)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📈 MODEL RESULTS SUMMARY")
    print("=" * 60)
    
    for year in [2030, 2040, 2050]:
        if year in scenario.timeline:
            year_data = outputs['emissions'][outputs['emissions']['Year'] == year].iloc[0]
            print(f"{year}: {year_data['Target_Achievement_Pct']:.1f}% target achieved, "
                  f"{year_data['Shortfall_Mt']:.2f} MtCO2 shortfall")
    
    print(f"\n✅ Band-based MACC model completed successfully!")
    print(f"📁 Comprehensive outputs saved in 'outputs_band_model' directory")
    print(f"📊 Generated: CSV files + visualization plots")

if __name__ == "__main__":
    main()