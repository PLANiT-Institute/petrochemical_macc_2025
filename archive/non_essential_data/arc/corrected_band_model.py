#!/usr/bin/env python3
"""
Corrected band-based MACC model ensuring no band transitions (HT/MT/LT are fixed)
Only alternative technologies can substitute within each band
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add the petrochem package to path
sys.path.insert(0, str(Path(__file__).parent))

from petrochem.lib.core.technology import (
    AlternativeTechnology, TechType, CostStructure, TechnologyConstraints
)
from petrochem.lib.core.scenario import EmissionsScenario, EmissionsBaseline, EmissionsTarget, ProcessBaseline
from petrochem.lib.core.portfolio import TechnologyPortfolio
from petrochem.lib.optimization.model_builder_corrected import CorrectedMACCModelBuilder
from petrochem.model_pyomo import solve_model

class BandBasedMACCModel:
    """
    MACC model that maintains fixed HT/MT/LT band structure
    Alternative technologies can only substitute within their specific band
    """
    
    def __init__(self, excel_file="data/Korea_Petrochemical_MACC_Database.xlsx"):
        self.excel_file = excel_file
        self.baseline_bands = {}  # Fixed band baseline data
        self.load_baseline_structure()
    
    def load_baseline_structure(self):
        """Load the fixed baseline band structure (HT/MT/LT cannot change)"""
        print("📂 Loading fixed baseline band structure...")
        
        with pd.ExcelFile(self.excel_file) as xls:
            bands_data = pd.read_excel(xls, sheet_name='TechBands_2023')
            
        # Store fixed baseline structure
        for _, row in bands_data.iterrows():
            band_key = f"{row['TechGroup']}_{row['Band']}"
            self.baseline_bands[band_key] = {
                'tech_group': row['TechGroup'],
                'band': row['Band'], 
                'activity_kt': row['Activity_kt_product'],
                'emission_intensity': row['EmissionIntensity_tCO2_per_t'],
                'sec_gj_per_t': row['SEC_GJ_per_t'],
                'process_description': row['Process_Description'],
                'energy_source': row['Primary_Energy_Source']
            }
            
        print(f"   ✅ Loaded {len(self.baseline_bands)} fixed baseline bands")
        print("   🔒 Band structure is FIXED - no HT↔MT↔LT transitions allowed")
        
        # Display fixed structure
        for tech_group in ['NCC', 'BTX', 'C4']:
            group_bands = [(k, v) for k, v in self.baseline_bands.items() if v['tech_group'] == tech_group]
            total_activity = sum(v['activity_kt'] for _, v in group_bands)
            print(f"   📊 {tech_group}: {total_activity:.0f} kt/year across {len(group_bands)} fixed bands")
    
    def create_scenario(self):
        """Create emissions scenario with fixed band baseline"""
        print("\n🏭 Creating emissions scenario with fixed band baseline...")
        
        # Create process baselines (aggregated by tech group)
        process_baselines = []
        
        for tech_group in ['NCC', 'BTX', 'C4']:
            group_bands = [(k, v) for k, v in self.baseline_bands.items() if v['tech_group'] == tech_group]
            
            total_production = sum(v['activity_kt'] for _, v in group_bands)
            total_emissions = sum(v['activity_kt'] * v['emission_intensity'] for _, v in group_bands)
            weighted_ei = total_emissions / total_production
            
            # Create band distribution (FIXED - cannot change)
            band_distribution = {}
            for band_key, band_data in group_bands:
                band_distribution[band_key] = band_data['activity_kt'] / total_production
            
            process_baselines.append(ProcessBaseline(
                process_type=tech_group,
                production_kt=total_production,
                emission_intensity_t_co2_per_t=weighted_ei,
                current_band_distribution=band_distribution
            ))
        
        total_emissions = sum(pb.total_emissions_mt for pb in process_baselines)
        
        baseline = EmissionsBaseline(
            year=2023,
            total_emissions_mt=total_emissions,
            process_baselines=process_baselines
        )
        
        # Create emissions targets
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
        
        print(f"   ✅ Baseline emissions: {total_emissions:.1f} MtCO2")
        print(f"   🎯 Targets: 2030(-15%), 2040(-50%), 2050(-80%)")
        
        return scenario
    
    def create_alternative_portfolio(self):
        """Create portfolio of alternative technologies (band-specific only)"""
        print("\n⚡ Creating alternative technology portfolio...")
        
        with pd.ExcelFile(self.excel_file) as xls:
            alternatives_data = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
            costs_data = pd.read_excel(xls, sheet_name='AlternativeCosts')
            
        merged_data = alternatives_data.merge(costs_data, on='TechID')
        
        technologies = []
        
        for _, row in merged_data.iterrows():
            # Get the specific baseline band this technology targets
            band_key = f"{row['TechGroup']}_{row['Band']}"
            
            if band_key not in self.baseline_bands:
                print(f"   ⚠️  Skipping {row['TechID']}: baseline band {band_key} not found")
                continue
            
            baseline_band = self.baseline_bands[band_key]
            baseline_ei = baseline_band['emission_intensity']
            
            # Alternative technology emission factor (reduced emissions)
            alt_emission_factor = baseline_ei - row['EmissionReduction_tCO2_per_t']
            
            tech = AlternativeTechnology(
                tech_id=row['TechID'],
                name=f"{row['TechGroup']} {row['Band']} {row['TechnologyCategory']}",
                process_type=row['TechGroup'],  # Maps to process baseline
                emission_factor=alt_emission_factor,
                cost_structure=CostStructure(
                    capex_usd_per_kt=row['CAPEX_Million_USD_per_kt_capacity'] * 1e6,
                    opex_delta_usd_per_t=row['OPEX_Delta_USD_per_t'],
                    maintenance_pct=row['MaintenanceCost_Pct']
                ),
                constraints=TechnologyConstraints(
                    lifetime_years=row['Lifetime_years'],
                    start_year=row['CommercialYear'], 
                    ramp_rate_per_year=row['RampRate_per_year'],
                    max_applicability=row['MaxApplicability'],
                    technical_readiness_level=row['TechnicalReadiness']
                )
            )
            
            # Add band-specific metadata
            tech.target_band = band_key
            tech.baseline_band_activity = baseline_band['activity_kt']
            
            technologies.append(tech)
        
        portfolio = TechnologyPortfolio()
        for tech in technologies:
            portfolio.add_technology(tech)
        
        print(f"   ✅ Created portfolio with {len(technologies)} band-specific alternatives")
        
        # Display by band
        band_counts = {}
        for tech in technologies:
            band = tech.target_band
            if band not in band_counts:
                band_counts[band] = 0
            band_counts[band] += 1
        
        for band_key, count in band_counts.items():
            baseline_activity = self.baseline_bands[band_key]['activity_kt']
            print(f"   📊 {band_key}: {count} alternatives targeting {baseline_activity:.0f} kt/year")
        
        return portfolio
    
    def create_corrected_model_builder(self, scenario, portfolio):
        """Create model builder that enforces fixed band structure"""
        
        class FixedBandMACCModelBuilder(CorrectedMACCModelBuilder):
            """Model builder that ensures bands cannot transition between each other"""
            
            def __init__(self, scenario, portfolio, baseline_bands):
                super().__init__(scenario, portfolio)
                self.baseline_bands = baseline_bands
            
            def _calculate_max_capacity(self, tech, year):
                """Calculate max capacity ensuring it targets specific baseline band"""
                
                if not hasattr(tech, 'target_band'):
                    return 0.0
                    
                # Max capacity is limited to the specific baseline band capacity
                if tech.target_band in self.baseline_bands:
                    baseline_capacity = self.baseline_bands[tech.target_band]['activity_kt']
                    return baseline_capacity * tech.constraints.max_applicability
                else:
                    return 0.0
            
            def _add_process_balance_constraints(self, m):
                """Add constraints ensuring band capacities remain fixed"""
                
                # Original process balance
                super()._add_process_balance_constraints(m)
                
                # Additional constraint: each band's total capacity is fixed
                print("   🔒 Adding fixed band constraints...")
                
                for band_key, band_data in self.baseline_bands.items():
                    baseline_capacity = band_data['activity_kt']
                    
                    def band_capacity_rule(model, year, band=band_key, capacity=baseline_capacity):
                        # Sum of all alternative tech production in this band
                        band_production = sum(
                            model.production[tech, year] 
                            for tech in model.TECHS
                            if hasattr(self.portfolio.technologies[tech], 'target_band') and
                            self.portfolio.technologies[tech].target_band == band
                        )
                        
                        # Total production (baseline + alternatives) cannot exceed band capacity
                        # Note: In reality, alternatives substitute baseline, so total stays ≤ baseline
                        return band_production <= capacity
                    
                    constraint_name = f"band_capacity_{band_key.replace('_', '')}"
                    setattr(m, constraint_name, 
                           __import__('pyomo.environ', fromlist=['Constraint']).Constraint(
                               m.YEARS, rule=band_capacity_rule
                           ))
                
                print(f"   ✅ Added {len(self.baseline_bands)} band capacity constraints")
        
        return FixedBandMACCModelBuilder(scenario, portfolio, self.baseline_bands)
    
    def run_model(self, output_dir="outputs_fixed_bands"):
        """Run the corrected band-based model"""
        
        print("🚀 Running Fixed Band MACC Model")
        print("=" * 50)
        print("🔒 Key Principle: HT/MT/LT bands are FIXED")
        print("⚡ Alternative technologies substitute within bands only")
        print("=" * 50)
        
        # Create scenario with fixed baseline
        scenario = self.create_scenario()
        
        # Create alternative technology portfolio
        portfolio = self.create_alternative_portfolio()
        
        # Create corrected model builder
        print("\n🔧 Building optimization model with fixed band constraints...")
        builder = self.create_corrected_model_builder(scenario, portfolio)
        model = builder.build_model(allow_slack=True, discount_rate=0.05)
        
        summary = builder.get_model_summary()
        print(f"   ✅ Model built: {sum(summary['variables'].values())} variables")
        
        # Solve model
        print("\n🎯 Solving optimization model...")
        solver_used, results = solve_model(model, solver="glpk")
        print(f"   ✅ Solved with {solver_used}")
        
        # Generate outputs
        print("\n📊 Generating fixed band outputs...")
        outputs = self.generate_fixed_band_outputs(model, scenario, portfolio, output_dir)
        
        # Print results summary
        print("\n" + "=" * 50)
        print("📈 FIXED BAND MODEL RESULTS")
        print("=" * 50)
        
        for year in [2030, 2040, 2050]:
            if year in scenario.timeline:
                required = scenario.get_required_abatement(year)
                achieved = sum(model.abatement[tech, year].value or 0 
                              for tech in model.TECHS) / 1e6
                achievement = (achieved / required * 100) if required > 0 else 100
                shortfall = max(0, required - achieved)
                
                print(f"{year}: {achievement:.1f}% target achieved, {shortfall:.2f} MtCO2 shortfall")
        
        print(f"\n✅ Fixed band model completed!")
        print(f"📁 Results in '{output_dir}' directory") 
        
        return outputs
    
    def generate_fixed_band_outputs(self, model, scenario, portfolio, output_dir):
        """Generate outputs showing fixed band structure"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Fixed band baseline summary
        band_baseline = []
        for band_key, band_data in self.baseline_bands.items():
            band_baseline.append({
                'Band_Key': band_key,
                'TechGroup': band_data['tech_group'],
                'Band': band_data['band'],
                'Baseline_Activity_kt': band_data['activity_kt'],
                'Baseline_Emission_Intensity_tCO2_per_t': band_data['emission_intensity'],
                'Baseline_Emissions_tCO2': band_data['activity_kt'] * band_data['emission_intensity'] * 1000,
                'SEC_GJ_per_t': band_data['sec_gj_per_t'],
                'Process_Description': band_data['process_description'],
                'Primary_Energy_Source': band_data['energy_source']
            })
        
        pd.DataFrame(band_baseline).to_csv(f"{output_dir}/fixed_band_baseline.csv", index=False)
        
        # 2. Alternative technology deployment (within bands)
        alt_deployment = []
        for tech in model.TECHS:
            tech_obj = portfolio.technologies[tech]
            if hasattr(tech_obj, 'target_band'):
                for year in [2030, 2040, 2050]:
                    if year in model.YEARS:
                        install_cap = model.install_capacity[tech, year].value or 0
                        total_cap = model.total_capacity[tech, year].value or 0
                        production = model.production[tech, year].value or 0
                        abatement = model.abatement[tech, year].value or 0
                        
                        if total_cap > 0 or production > 0:
                            band_data = self.baseline_bands[tech_obj.target_band]
                            penetration_rate = production / band_data['activity_kt'] if band_data['activity_kt'] > 0 else 0
                            
                            alt_deployment.append({
                                'Year': year,
                                'TechID': tech,
                                'Target_Band': tech_obj.target_band,
                                'TechGroup': band_data['tech_group'],
                                'Band': band_data['band'],
                                'Install_Capacity_kt': install_cap,
                                'Total_Capacity_kt': total_cap,
                                'Production_kt': production,
                                'Abatement_tCO2': abatement,
                                'Band_Baseline_kt': band_data['activity_kt'],
                                'Penetration_Rate': penetration_rate,
                                'Substitution_Rate': production / band_data['activity_kt'] if band_data['activity_kt'] > 0 else 0
                            })
        
        pd.DataFrame(alt_deployment).to_csv(f"{output_dir}/alternative_deployment_by_band.csv", index=False)
        
        # 3. Band-level summary
        band_summary = []
        for year in [2030, 2040, 2050]:
            if year in model.YEARS:
                for band_key, band_data in self.baseline_bands.items():
                    
                    # Find all technologies targeting this band
                    band_techs = [tech for tech in model.TECHS 
                                 if hasattr(portfolio.technologies[tech], 'target_band') and
                                 portfolio.technologies[tech].target_band == band_key]
                    
                    total_alt_production = sum(model.production[tech, year].value or 0 
                                             for tech in band_techs)
                    total_alt_abatement = sum(model.abatement[tech, year].value or 0 
                                            for tech in band_techs)
                    
                    # Remaining baseline production
                    baseline_production = band_data['activity_kt']
                    remaining_baseline = max(0, baseline_production - total_alt_production)
                    remaining_baseline_emissions = remaining_baseline * band_data['emission_intensity'] * 1000
                    
                    band_summary.append({
                        'Year': year,
                        'Band_Key': band_key,
                        'TechGroup': band_data['tech_group'],
                        'Band': band_data['band'],
                        'Baseline_Production_kt': baseline_production,
                        'Alternative_Production_kt': total_alt_production,
                        'Remaining_Baseline_kt': remaining_baseline,
                        'Alternative_Share_pct': (total_alt_production / baseline_production * 100) if baseline_production > 0 else 0,
                        'Alternative_Abatement_tCO2': total_alt_abatement,
                        'Remaining_Emissions_tCO2': remaining_baseline_emissions,
                        'Band_Emission_Reduction_pct': (total_alt_abatement / (baseline_production * band_data['emission_intensity'] * 1000) * 100) if baseline_production > 0 else 0
                    })
        
        pd.DataFrame(band_summary).to_csv(f"{output_dir}/band_level_summary.csv", index=False)
        
        # 4. Generate emission pathways by source
        emission_pathways = self.generate_emission_pathways(model, scenario, portfolio, output_dir)
        
        # 5. Generate technological change timeline
        tech_changes = self.generate_technological_changes(model, scenario, portfolio, output_dir)
        
        # 6. Generate cost comparison analysis
        cost_comparison = self.generate_cost_comparison_analysis(model, scenario, portfolio, output_dir)
        
        # 7. Create visualization
        self.create_band_visualization(band_summary, output_dir)
        
        print(f"   ✅ Fixed band outputs generated")
        print(f"   ✅ Emission pathways by source generated")
        print(f"   ✅ Technological change timeline generated")
        
        return {
            'baseline': band_baseline,
            'deployment': alt_deployment, 
            'summary': band_summary,
            'emission_pathways': emission_pathways,
            'tech_changes': tech_changes,
            'cost_comparison': cost_comparison
        }
    
    def create_band_visualization(self, band_summary, output_dir):
        """Create visualization showing fixed band structure with alternatives"""
        
        if not band_summary:
            return
            
        df = pd.DataFrame(band_summary)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Alternative penetration by band (2050)
        df_2050 = df[df['Year'] == 2050]
        if not df_2050.empty:
            ax1.barh(df_2050['Band_Key'], df_2050['Alternative_Share_pct'])
            ax1.set_xlabel('Alternative Technology Share (%)')
            ax1.set_title('Alternative Technology Penetration by Band (2050)')
            ax1.grid(True, alpha=0.3)
        
        # 2. Abatement by band over time
        for band_key in df['Band_Key'].unique():
            band_data = df[df['Band_Key'] == band_key]
            ax2.plot(band_data['Year'], band_data['Alternative_Abatement_tCO2']/1e6, 
                    marker='o', label=band_key)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Abatement (MtCO2)')
        ax2.set_title('Abatement by Fixed Band')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Production mix by technology group (2050)
        if not df_2050.empty:
            group_data = df_2050.groupby('TechGroup').agg({
                'Baseline_Production_kt': 'sum',
                'Alternative_Production_kt': 'sum',
                'Remaining_Baseline_kt': 'sum'
            })
            
            x = range(len(group_data))
            width = 0.35
            
            ax3.bar([i - width/2 for i in x], group_data['Remaining_Baseline_kt'], 
                   width, label='Remaining Baseline', alpha=0.7)
            ax3.bar([i + width/2 for i in x], group_data['Alternative_Production_kt'], 
                   width, label='Alternative Technologies', alpha=0.7)
            
            ax3.set_xlabel('Technology Group')
            ax3.set_ylabel('Production (kt/year)')
            ax3.set_title('Production Mix by Technology Group (2050)')
            ax3.set_xticks(x)
            ax3.set_xticklabels(group_data.index)
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Emission reduction by band (2050)
        if not df_2050.empty:
            ax4.bar(df_2050['Band_Key'], df_2050['Band_Emission_Reduction_pct'])
            ax4.set_xlabel('Band')
            ax4.set_ylabel('Emission Reduction (%)')
            ax4.set_title('Emission Reduction by Fixed Band (2050)')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/fixed_band_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_emission_pathways(self, model, scenario, portfolio, output_dir):
        """Generate detailed emission pathways by source and technology"""
        
        emission_pathways = []
        
        for year in model.YEARS:
            # Calculate emissions by source (baseline + alternatives)
            year_data = {'Year': year}
            
            total_baseline_emissions = 0
            total_alternative_abatement = 0
            
            # Process each baseline band
            for band_key, band_data in self.baseline_bands.items():
                tech_group = band_data['tech_group']
                band = band_data['band']
                baseline_activity = band_data['activity_kt']
                baseline_ei = band_data['emission_intensity']
                
                # Find alternative technologies targeting this band
                band_techs = [tech for tech in model.TECHS 
                             if hasattr(portfolio.technologies[tech], 'target_band') and
                             portfolio.technologies[tech].target_band == band_key]
                
                # Alternative production in this band
                alt_production = sum(model.production[tech, year].value or 0 for tech in band_techs)
                alt_abatement = sum(model.abatement[tech, year].value or 0 for tech in band_techs)
                
                # Remaining baseline production and emissions
                remaining_baseline = max(0, baseline_activity - alt_production)
                remaining_emissions = remaining_baseline * baseline_ei * 1000  # Convert to tCO2
                
                # Alternative emissions (baseline - abatement)
                alt_emissions = (alt_production * baseline_ei * 1000) - alt_abatement
                
                total_band_emissions = remaining_emissions + alt_emissions
                
                year_data.update({
                    f'{band_key}_Baseline_Production_kt': remaining_baseline,
                    f'{band_key}_Alternative_Production_kt': alt_production,
                    f'{band_key}_Baseline_Emissions_tCO2': remaining_emissions,
                    f'{band_key}_Alternative_Emissions_tCO2': alt_emissions,
                    f'{band_key}_Total_Emissions_tCO2': total_band_emissions,
                    f'{band_key}_Abatement_tCO2': alt_abatement,
                    f'{band_key}_Alternative_Share_pct': (alt_production / baseline_activity * 100) if baseline_activity > 0 else 0
                })
                
                total_baseline_emissions += remaining_emissions
                total_alternative_abatement += alt_abatement
            
            # Summary totals
            total_emissions = sum(year_data[key] for key in year_data.keys() 
                                if key.endswith('_Total_Emissions_tCO2'))
            total_abatement = sum(year_data[key] for key in year_data.keys() 
                                if key.endswith('_Abatement_tCO2'))
            
            year_data.update({
                'Total_Emissions_MtCO2': total_emissions / 1e6,
                'Total_Abatement_MtCO2': total_abatement / 1e6,
                'Baseline_Emissions_MtCO2': scenario.baseline.total_emissions_mt,
                'Target_Emissions_MtCO2': scenario.get_target_emissions(year),
                'Emission_Reduction_from_Baseline_pct': ((scenario.baseline.total_emissions_mt * 1e6 - total_emissions) / (scenario.baseline.total_emissions_mt * 1e6) * 100) if scenario.baseline.total_emissions_mt > 0 else 0,
                'Target_Achievement_pct': (total_abatement / (scenario.get_required_abatement(year) * 1e6) * 100) if scenario.get_required_abatement(year) > 0 else 100
            })
            
            emission_pathways.append(year_data)
        
        pathways_df = pd.DataFrame(emission_pathways)
        pathways_df.to_csv(f"{output_dir}/emission_pathways_by_source.csv", index=False)
        
        return pathways_df
    
    def generate_technological_changes(self, model, scenario, portfolio, output_dir):
        """Generate technological change timeline showing adoption patterns"""
        
        tech_changes = []
        
        for year in model.YEARS:
            for tech in model.TECHS:
                tech_obj = portfolio.technologies[tech]
                
                if not hasattr(tech_obj, 'target_band'):
                    continue
                    
                install_cap = model.install_capacity[tech, year].value or 0
                total_cap = model.total_capacity[tech, year].value or 0
                production = model.production[tech, year].value or 0
                
                if install_cap > 0 or total_cap > 0 or production > 0:
                    band_data = self.baseline_bands[tech_obj.target_band]
                    
                    # Calculate technology metrics
                    capacity_utilization = production / total_cap if total_cap > 0 else 0
                    market_penetration = production / band_data['activity_kt'] if band_data['activity_kt'] > 0 else 0
                    
                    # Calculate cumulative installed capacity
                    cumulative_install = sum(
                        model.install_capacity[tech, y].value or 0 
                        for y in model.YEARS if y <= year
                    )
                    
                    # Technology maturity indicators
                    years_since_commercial = max(0, year - tech_obj.constraints.start_year)
                    is_mature = years_since_commercial >= 5
                    
                    tech_changes.append({
                        'Year': year,
                        'TechID': tech,
                        'TechGroup': band_data['tech_group'],
                        'Band': band_data['band'],
                        'Technology_Category': tech_obj.name,
                        'Commercial_Year': tech_obj.constraints.start_year,
                        'Years_Since_Commercial': years_since_commercial,
                        'Technology_Maturity': 'Mature' if is_mature else 'Emerging',
                        'Annual_Install_Capacity_kt': install_cap,
                        'Cumulative_Install_Capacity_kt': cumulative_install,
                        'Total_Available_Capacity_kt': total_cap,
                        'Annual_Production_kt': production,
                        'Capacity_Utilization_pct': capacity_utilization * 100,
                        'Market_Penetration_pct': market_penetration * 100,
                        'Band_Baseline_Capacity_kt': band_data['activity_kt'],
                        'Max_Potential_Penetration_pct': tech_obj.constraints.max_applicability * 100,
                        'Technical_Readiness_Level': tech_obj.constraints.technical_readiness_level,
                        'Ramp_Rate_per_year': tech_obj.constraints.ramp_rate_per_year,
                        'Investment_Phase': self._get_investment_phase(install_cap, total_cap, cumulative_install),
                        'Deployment_Status': self._get_deployment_status(market_penetration, tech_obj.constraints.max_applicability)
                    })
        
        tech_changes_df = pd.DataFrame(tech_changes)
        if not tech_changes_df.empty:
            tech_changes_df = tech_changes_df.sort_values(['Year', 'TechGroup', 'Band', 'TechID'])
        
        tech_changes_df.to_csv(f"{output_dir}/technological_changes_timeline.csv", index=False)
        
        # Generate technology adoption curves
        self.create_technology_adoption_plots(tech_changes_df, output_dir)
        
        return tech_changes_df
    
    def generate_cost_comparison_analysis(self, model, scenario, portfolio, output_dir):
        """Generate comprehensive cost comparison between alternative technologies and baseline costs 2025-2050"""
        
        cost_comparison = []
        
        # Timeline for cost comparison (2025-2050)
        cost_years = list(range(2025, 2051))
        
        for year in cost_years:
            for tech in portfolio.technologies.keys():
                tech_obj = portfolio.technologies[tech]
                
                if not hasattr(tech_obj, 'target_band'):
                    continue
                
                band_key = tech_obj.target_band
                if band_key not in self.baseline_bands:
                    continue
                
                band_data = self.baseline_bands[band_key]
                
                # Technology costs (alternative)
                alt_capex_per_kt = tech_obj.cost_structure.capex_usd_per_kt  # USD per kt capacity
                alt_opex_delta = tech_obj.cost_structure.opex_delta_usd_per_t  # USD per t production
                alt_maintenance_pct = tech_obj.cost_structure.maintenance_pct
                
                # Baseline costs (assume baseline has minimal CAPEX for existing facilities, but OPEX for fuel/energy)
                baseline_capex_per_kt = 0  # Existing facilities
                baseline_opex_per_t = 0  # Reference point (alternative is delta)
                
                # Calculate lifecycle costs for 1 kt capacity over technology lifetime
                lifetime = tech_obj.constraints.lifetime_years
                discount_rate = 0.05
                capacity_kt = 1.0  # Calculate per kt capacity
                
                # Alternative technology costs
                alt_total_capex = alt_capex_per_kt * capacity_kt
                alt_annual_maintenance = alt_total_capex * (alt_maintenance_pct / 100)
                
                # Assume capacity utilization of 85% for production calculations
                utilization_rate = 0.85
                annual_production_t = capacity_kt * 1000 * utilization_rate  # Convert kt to tonnes
                
                alt_annual_opex = annual_production_t * alt_opex_delta + alt_annual_maintenance
                
                # Calculate NPV of alternative technology costs
                alt_npv_total = alt_total_capex
                for y in range(1, lifetime + 1):
                    discount_factor = 1 / ((1 + discount_rate) ** y)
                    alt_npv_total += alt_annual_opex * discount_factor
                
                # Baseline technology costs (minimal for existing facilities)
                baseline_total_capex = baseline_capex_per_kt * capacity_kt
                baseline_annual_opex = annual_production_t * baseline_opex_per_t
                
                baseline_npv_total = baseline_total_capex
                for y in range(1, lifetime + 1):
                    discount_factor = 1 / ((1 + discount_rate) ** y)
                    baseline_npv_total += baseline_annual_opex * discount_factor
                
                # Cost differential and ratios
                capex_differential = alt_total_capex - baseline_total_capex
                opex_differential = alt_annual_opex - baseline_annual_opex
                npv_differential = alt_npv_total - baseline_npv_total
                
                # Cost per tonne of abatement
                emission_reduction_per_t = tech_obj.emission_factor - band_data['emission_intensity'] if hasattr(tech_obj, 'emission_factor') else 0
                annual_abatement_tco2 = annual_production_t * abs(emission_reduction_per_t)
                
                cost_per_tco2_capex = capex_differential / (annual_abatement_tco2 * lifetime) if annual_abatement_tco2 > 0 else 0
                cost_per_tco2_opex = opex_differential / annual_abatement_tco2 if annual_abatement_tco2 > 0 else 0
                cost_per_tco2_total = npv_differential / (annual_abatement_tco2 * lifetime) if annual_abatement_tco2 > 0 else 0
                
                # Check if technology is deployed in the optimal solution
                is_deployed = False
                deployment_level = 0
                if year in model.YEARS:
                    total_cap = model.total_capacity[tech, year].value or 0
                    production = model.production[tech, year].value or 0
                    is_deployed = total_cap > 0.01  # kt threshold
                    deployment_level = production / band_data['activity_kt'] if band_data['activity_kt'] > 0 else 0
                
                cost_comparison.append({
                    'Year': year,
                    'TechID': tech,
                    'TechGroup': band_data['tech_group'],
                    'Band': band_data['band'],
                    'Technology_Name': tech_obj.name,
                    'Target_Band': band_key,
                    'Commercial_Year': tech_obj.constraints.start_year,
                    'Technology_Lifetime_years': lifetime,
                    
                    # Baseline costs (per kt capacity)
                    'Baseline_CAPEX_M_USD_per_kt': baseline_capex_per_kt / 1e6,
                    'Baseline_OPEX_USD_per_t': baseline_opex_per_t,
                    'Baseline_NPV_Total_M_USD_per_kt': baseline_npv_total / 1e6,
                    
                    # Alternative technology costs (per kt capacity)
                    'Alternative_CAPEX_M_USD_per_kt': alt_capex_per_kt / 1e6,
                    'Alternative_OPEX_USD_per_t': alt_opex_delta,
                    'Alternative_Annual_OPEX_M_USD_per_kt': alt_annual_opex / 1e6,
                    'Alternative_Maintenance_pct': alt_maintenance_pct,
                    'Alternative_NPV_Total_M_USD_per_kt': alt_npv_total / 1e6,
                    
                    # Cost differentials
                    'CAPEX_Differential_M_USD_per_kt': capex_differential / 1e6,
                    'OPEX_Differential_USD_per_t': alt_opex_delta - baseline_opex_per_t,
                    'NPV_Differential_M_USD_per_kt': npv_differential / 1e6,
                    'Cost_Premium_pct': ((alt_npv_total / baseline_npv_total - 1) * 100) if baseline_npv_total > 0 else 0,
                    
                    # Abatement metrics
                    'Emission_Reduction_tCO2_per_t': abs(emission_reduction_per_t),
                    'Annual_Abatement_Potential_tCO2_per_kt': annual_abatement_tco2 / capacity_kt,
                    'Cost_per_tCO2_CAPEX_USD': cost_per_tco2_capex,
                    'Cost_per_tCO2_OPEX_USD': cost_per_tco2_opex,
                    'Cost_per_tCO2_Total_USD': cost_per_tco2_total,
                    
                    # Deployment status
                    'Is_Deployed_in_Solution': is_deployed,
                    'Deployment_Level_pct': deployment_level * 100,
                    'Band_Baseline_Capacity_kt': band_data['activity_kt'],
                    'Max_Applicability_pct': tech_obj.constraints.max_applicability * 100,
                    'Technical_Readiness_Level': tech_obj.constraints.technical_readiness_level
                })
        
        cost_comparison_df = pd.DataFrame(cost_comparison)
        cost_comparison_df.to_csv(f"{output_dir}/cost_comparison_alternative_vs_baseline.csv", index=False)
        
        # Generate cost comparison visualizations
        self.create_cost_comparison_plots(cost_comparison_df, output_dir)
        
        # Generate summary tables
        self.generate_cost_summary_tables(cost_comparison_df, output_dir)
        
        return cost_comparison_df
    
    def create_cost_comparison_plots(self, cost_df, output_dir):
        """Create visualizations for cost comparison analysis"""
        
        if cost_df.empty:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Cost per tCO2 by technology and year
        key_years = [2025, 2030, 2040, 2050]
        plot_data = cost_df[cost_df['Year'].isin(key_years)]
        
        # Filter out infinite or very high costs for visualization
        plot_data_filtered = plot_data[
            (plot_data['Cost_per_tCO2_Total_USD'] < 1000) & 
            (plot_data['Cost_per_tCO2_Total_USD'] > -500)
        ]
        
        if not plot_data_filtered.empty:
            for tech_group in plot_data_filtered['TechGroup'].unique():
                group_data = plot_data_filtered[plot_data_filtered['TechGroup'] == tech_group]
                avg_cost_by_year = group_data.groupby('Year')['Cost_per_tCO2_Total_USD'].mean()
                ax1.plot(avg_cost_by_year.index, avg_cost_by_year.values, 
                        marker='o', label=tech_group, linewidth=2)
        
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Cost per tCO2 (USD)')
        ax1.set_title('Average Abatement Cost by Technology Group')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        # 2. CAPEX vs OPEX comparison (2030)
        data_2030 = plot_data[plot_data['Year'] == 2030]
        if not data_2030.empty:
            scatter_data = data_2030[data_2030['Is_Deployed_in_Solution'] == True]
            if not scatter_data.empty:
                scatter = ax2.scatter(scatter_data['Alternative_CAPEX_M_USD_per_kt'], 
                                    scatter_data['Alternative_OPEX_USD_per_t'],
                                    c=scatter_data['Cost_per_tCO2_Total_USD'], 
                                    cmap='RdYlBu_r', s=60, alpha=0.7)
                
                ax2.set_xlabel('CAPEX (M USD per kt capacity)')
                ax2.set_ylabel('OPEX (USD per t production)')
                ax2.set_title('CAPEX vs OPEX for Deployed Technologies (2030)')
                ax2.grid(True, alpha=0.3)
                
                # Add colorbar
                cbar = plt.colorbar(scatter, ax=ax2)
                cbar.set_label('Cost per tCO2 (USD)')
        
        # 3. Cost premium over time by band
        for band in ['HT', 'MT', 'LT']:
            band_data = plot_data_filtered[plot_data_filtered['Band'] == band]
            if not band_data.empty:
                avg_premium = band_data.groupby('Year')['Cost_Premium_pct'].mean()
                ax3.plot(avg_premium.index, avg_premium.values, 
                        marker='s', label=f'{band} Band', linewidth=2)
        
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Cost Premium (%)')
        ax3.set_title('Technology Cost Premium by Temperature Band')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        # 4. Deployment vs cost effectiveness (2050)
        data_2050 = plot_data[plot_data['Year'] == 2050]
        if not data_2050.empty:
            deployed_data = data_2050[data_2050['Deployment_Level_pct'] > 0]
            if not deployed_data.empty:
                ax4.scatter(deployed_data['Cost_per_tCO2_Total_USD'], 
                           deployed_data['Deployment_Level_pct'],
                           alpha=0.7, s=60)
                
                ax4.set_xlabel('Cost per tCO2 (USD)')
                ax4.set_ylabel('Deployment Level (%)')
                ax4.set_title('Deployment vs Cost Effectiveness (2050)')
                ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_comparison_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_cost_summary_tables(self, cost_df, output_dir):
        """Generate summary tables for cost comparison"""
        
        if cost_df.empty:
            return
        
        # 1. Technology cost summary by band (2030)
        summary_2030 = cost_df[cost_df['Year'] == 2030].groupby(['TechGroup', 'Band']).agg({
            'Alternative_CAPEX_M_USD_per_kt': 'mean',
            'Alternative_OPEX_USD_per_t': 'mean',
            'Cost_per_tCO2_Total_USD': 'mean',
            'Cost_Premium_pct': 'mean',
            'Deployment_Level_pct': 'mean'
        }).round(2)
        
        summary_2030.to_csv(f"{output_dir}/cost_summary_by_band_2030.csv")
        
        # 2. Most cost-effective technologies by year
        key_years = [2025, 2030, 2040, 2050]
        cost_effective = []
        
        for year in key_years:
            year_data = cost_df[cost_df['Year'] == year]
            if not year_data.empty:
                # Filter reasonable costs
                reasonable_costs = year_data[
                    (year_data['Cost_per_tCO2_Total_USD'] > -200) & 
                    (year_data['Cost_per_tCO2_Total_USD'] < 500)
                ]
                
                if not reasonable_costs.empty:
                    # Top 3 most cost-effective per band
                    for band in reasonable_costs['Band'].unique():
                        band_data = reasonable_costs[reasonable_costs['Band'] == band]
                        top_3 = band_data.nsmallest(3, 'Cost_per_tCO2_Total_USD')
                        
                        for idx, row in top_3.iterrows():
                            cost_effective.append({
                                'Year': year,
                                'Band': band,
                                'TechID': row['TechID'],
                                'Technology_Name': row['Technology_Name'],
                                'Cost_per_tCO2_USD': row['Cost_per_tCO2_Total_USD'],
                                'CAPEX_M_USD_per_kt': row['Alternative_CAPEX_M_USD_per_kt'],
                                'OPEX_USD_per_t': row['Alternative_OPEX_USD_per_t'],
                                'Is_Deployed': row['Is_Deployed_in_Solution'],
                                'Ranking': top_3.index.get_loc(idx) + 1
                            })
        
        if cost_effective:
            pd.DataFrame(cost_effective).to_csv(f"{output_dir}/most_cost_effective_technologies.csv", index=False)
    
    def _get_investment_phase(self, install_cap, total_cap, cumulative_install):
        """Determine investment phase based on capacity metrics"""
        if install_cap > 100:  # kt/year
            return 'High Investment'
        elif install_cap > 10:
            return 'Moderate Investment'
        elif install_cap > 0:
            return 'Initial Investment'
        elif total_cap > 0:
            return 'Operational'
        else:
            return 'Not Active'
    
    def _get_deployment_status(self, market_penetration, max_applicability):
        """Determine deployment status based on market penetration"""
        penetration_ratio = market_penetration / max_applicability if max_applicability > 0 else 0
        
        if penetration_ratio >= 0.9:
            return 'Saturated'
        elif penetration_ratio >= 0.5:
            return 'Scaling'
        elif penetration_ratio >= 0.1:
            return 'Early Deployment'
        elif penetration_ratio > 0:
            return 'Demonstration'
        else:
            return 'Pre-Commercial'
    
    def create_technology_adoption_plots(self, tech_changes_df, output_dir):
        """Create plots showing technology adoption curves"""
        
        if tech_changes_df.empty:
            return
        
        # Focus on key years for visualization
        key_years = [2025, 2030, 2035, 2040, 2045, 2050]
        plot_data = tech_changes_df[tech_changes_df['Year'].isin(key_years)]
        
        if plot_data.empty:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Market penetration by technology category over time
        tech_categories = plot_data['Technology_Category'].unique()
        for category in tech_categories[:6]:  # Limit to top 6 for readability
            cat_data = plot_data[plot_data['Technology_Category'] == category]
            if not cat_data.empty:
                ax1.plot(cat_data['Year'], cat_data['Market_Penetration_pct'], 
                        marker='o', label=category, linewidth=2)
        
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Market Penetration (%)')
        ax1.set_title('Technology Market Penetration Over Time')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Cumulative capacity installation by band
        for band in ['HT', 'MT', 'LT']:
            band_data = plot_data[plot_data['Band'] == band].groupby('Year')['Cumulative_Install_Capacity_kt'].sum()
            if not band_data.empty:
                ax2.plot(band_data.index, band_data.values, marker='s', label=f'{band} Band', linewidth=2)
        
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Cumulative Installed Capacity (kt)')
        ax2.set_title('Cumulative Capacity Installation by Temperature Band')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Investment phase distribution (2050)
        data_2050 = plot_data[plot_data['Year'] == 2050]
        if not data_2050.empty:
            phase_counts = data_2050['Investment_Phase'].value_counts()
            ax3.pie(phase_counts.values, labels=phase_counts.index, autopct='%1.1f%%')
            ax3.set_title('Investment Phase Distribution (2050)')
        
        # 4. Technology readiness vs market penetration (2050)
        if not data_2050.empty:
            scatter_data = data_2050[data_2050['Market_Penetration_pct'] > 0]
            if not scatter_data.empty:
                scatter = ax4.scatter(scatter_data['Technical_Readiness_Level'], 
                                    scatter_data['Market_Penetration_pct'],
                                    c=scatter_data['Years_Since_Commercial'], 
                                    cmap='viridis', s=60, alpha=0.7)
                
                ax4.set_xlabel('Technical Readiness Level')
                ax4.set_ylabel('Market Penetration (%)')
                ax4.set_title('Technology Maturity vs Market Adoption (2050)')
                ax4.grid(True, alpha=0.3)
                
                # Add colorbar
                cbar = plt.colorbar(scatter, ax=ax4)
                cbar.set_label('Years Since Commercial')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/technology_adoption_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    model = BandBasedMACCModel()
    outputs = model.run_model()