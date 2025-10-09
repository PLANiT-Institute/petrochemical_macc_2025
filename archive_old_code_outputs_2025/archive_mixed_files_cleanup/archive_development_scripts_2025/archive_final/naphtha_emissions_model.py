#!/usr/bin/env python3
"""
Naphtha-Based Emissions Model for Korean Petrochemical Industry
Runs through naphtha consumption and alternative strategies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pulp import *
import warnings
warnings.filterwarnings('ignore')

class NaphthaEmissionsModel:
    def __init__(self, excel_file):
        """Initialize model with Excel configuration data"""
        self.excel_file = excel_file
        self.load_data()
        
    def load_data(self):
        """Load all data from Excel sheets"""
        print("📊 LOADING NAPHTHA EMISSIONS MODEL DATA")
        print("=" * 60)
        
        # Load all sheets
        self.baseline_data = pd.read_excel(self.excel_file, sheet_name='Baseline_Data')
        self.source_data = pd.read_excel(self.excel_file, sheet_name='source')
        self.ci_data = pd.read_excel(self.excel_file, sheet_name='CI')
        self.ci2_data = pd.read_excel(self.excel_file, sheet_name='CI2')
        self.emission_targets = pd.read_excel(self.excel_file, sheet_name='Emission_Targets')
        self.tech_options = pd.read_excel(self.excel_file, sheet_name='Technology_Options')
        self.naphtha_alternatives = pd.read_excel(self.excel_file, sheet_name='Naphtha_Alternatives')
        self.fuel_mix_scenarios = pd.read_excel(self.excel_file, sheet_name='Fuel_Mix_Scenarios')
        
        print(f"✅ Loaded {len(self.source_data)} facilities")
        print(f"✅ Loaded {len(self.tech_options)} technology options") 
        print(f"✅ Loaded {len(self.naphtha_alternatives)} naphtha alternatives")
        
    def calculate_facility_naphtha_emissions(self, year=2025):
        """Calculate detailed naphtha emissions by facility"""
        
        print(f"\n🛢️ CALCULATING FACILITY NAPHTHA EMISSIONS ({year})")
        print("=" * 60)
        
        results = []
        
        for idx, facility in self.source_data.iterrows():
            facility_code = facility['Facility_Code']
            company = facility['Company']
            process_type = facility['Process_Type']
            product = facility['Primary_Product']
            production = facility['Actual_Production_kt']
            
            # Get naphtha consumption
            feedstock_naphtha = facility['Naphtha_Consumption_kt']
            thermal_naphtha = facility['Thermal_Naphtha_kt']
            total_naphtha = facility['Total_Naphtha_kt']
            
            # Get emission factors from CI2 data
            naphtha_feedstock_ef = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Naphtha_Feedstock']['Lifecycle_Emissions_tCO2/t'].iloc[0]
            naphtha_thermal_ef = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Naphtha_Thermal']['Lifecycle_Emissions_tCO2/t'].iloc[0]
            
            # Calculate emissions
            feedstock_emissions = feedstock_naphtha * naphtha_feedstock_ef
            thermal_emissions = thermal_naphtha * naphtha_thermal_ef
            total_emissions = feedstock_emissions + thermal_emissions
            
            # Emission intensity
            emission_intensity = total_emissions / production if production > 0 else 0
            
            results.append({
                'Facility_Code': facility_code,
                'Company': company,
                'Process_Type': process_type,
                'Primary_Product': product,
                'Production_kt': production,
                'Feedstock_Naphtha_kt': feedstock_naphtha,
                'Thermal_Naphtha_kt': thermal_naphtha,
                'Total_Naphtha_kt': total_naphtha,
                'Feedstock_Emissions_ktCO2': feedstock_emissions,
                'Thermal_Emissions_ktCO2': thermal_emissions,
                'Total_Emissions_ktCO2': total_emissions,
                'Emission_Intensity_tCO2_per_t': emission_intensity,
                'Naphtha_Intensity_t_per_t': total_naphtha / production if production > 0 else 0
            })
        
        self.facility_results = pd.DataFrame(results)
        
        # Summary by process type
        print("📋 EMISSIONS BY PROCESS TYPE:")
        summary = self.facility_results.groupby('Process_Type').agg({
            'Production_kt': 'sum',
            'Total_Naphtha_kt': 'sum', 
            'Total_Emissions_ktCO2': 'sum'
        }).round(1)
        
        summary['Avg_Emission_Intensity'] = (summary['Total_Emissions_ktCO2'] / summary['Production_kt']).round(2)
        summary['Avg_Naphtha_Intensity'] = (summary['Total_Naphtha_kt'] / summary['Production_kt']).round(2)
        
        print(summary)
        
        return self.facility_results
    
    def analyze_naphtha_alternatives(self, year=2030, scenario='Moderate'):
        """Analyze impact of naphtha alternatives"""
        
        print(f"\n🌱 NAPHTHA ALTERNATIVES ANALYSIS ({year}, {scenario})")
        print("=" * 60)
        
        # Get fuel mix for scenario and year
        fuel_mix = self.fuel_mix_scenarios[
            (self.fuel_mix_scenarios['Year'] == year) & 
            (self.fuel_mix_scenarios['Scenario'] == scenario)
        ].iloc[0]
        
        # Current and alternative naphtha consumption
        conventional_naphtha = fuel_mix['Conventional_Naphtha_Mt'] * 1000  # Convert to kt
        bio_naphtha = fuel_mix['Bio_Naphtha_Mt'] * 1000
        recycled_naphtha = fuel_mix['Recycled_Naphtha_Mt'] * 1000
        
        print(f"📊 NAPHTHA MIX ({year}):")
        print(f"   Conventional: {conventional_naphtha:,.0f} kt ({conventional_naphtha/(conventional_naphtha+bio_naphtha+recycled_naphtha)*100:.1f}%)")
        print(f"   Bio-naphtha: {bio_naphtha:,.0f} kt ({bio_naphtha/(conventional_naphtha+bio_naphtha+recycled_naphtha)*100:.1f}%)")
        print(f"   Recycled: {recycled_naphtha:,.0f} kt ({recycled_naphtha/(conventional_naphtha+bio_naphtha+recycled_naphtha)*100:.1f}%)")
        
        # Calculate emissions by naphtha type
        emissions_results = {}
        
        # Get emission factors
        ef_conv_feedstock = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Naphtha_Feedstock']['Lifecycle_Emissions_tCO2/t'].iloc[0]
        ef_conv_thermal = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Naphtha_Thermal']['Lifecycle_Emissions_tCO2/t'].iloc[0]
        ef_bio_feedstock = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Bio_Naphtha_Feedstock']['Lifecycle_Emissions_tCO2/t'].iloc[0]
        ef_bio_thermal = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Bio_Naphtha_Thermal']['Lifecycle_Emissions_tCO2/t'].iloc[0]
        ef_recycled_feedstock = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Recycled_Naphtha_Feedstock']['Lifecycle_Emissions_tCO2/t'].iloc[0]
        ef_recycled_thermal = self.ci2_data[self.ci2_data['Fuel_Type'] == 'Recycled_Naphtha_Thermal']['Lifecycle_Emissions_tCO2/t'].iloc[0]
        
        # Assume 88% feedstock, 12% thermal use
        feedstock_ratio = 0.88
        thermal_ratio = 0.12
        
        # Calculate emissions for each type
        for naphtha_type, amount in [('Conventional', conventional_naphtha), ('Bio', bio_naphtha), ('Recycled', recycled_naphtha)]:
            feedstock_amount = amount * feedstock_ratio
            thermal_amount = amount * thermal_ratio
            
            if naphtha_type == 'Conventional':
                feedstock_emissions = feedstock_amount * ef_conv_feedstock
                thermal_emissions = thermal_amount * ef_conv_thermal
            elif naphtha_type == 'Bio':
                feedstock_emissions = feedstock_amount * ef_bio_feedstock
                thermal_emissions = thermal_amount * ef_bio_thermal
            else:  # Recycled
                feedstock_emissions = feedstock_amount * ef_recycled_feedstock
                thermal_emissions = thermal_amount * ef_recycled_thermal
            
            total_emissions = feedstock_emissions + thermal_emissions
            
            emissions_results[naphtha_type] = {
                'Total_Amount_kt': amount,
                'Feedstock_Amount_kt': feedstock_amount,
                'Thermal_Amount_kt': thermal_amount,
                'Feedstock_Emissions_ktCO2': feedstock_emissions,
                'Thermal_Emissions_ktCO2': thermal_emissions,
                'Total_Emissions_ktCO2': total_emissions,
                'Emission_Factor_avg_tCO2_per_t': total_emissions / amount if amount > 0 else 0
            }
        
        # Create summary
        alternatives_df = pd.DataFrame(emissions_results).T
        
        print(f"\n🌍 EMISSIONS BY NAPHTHA TYPE:")
        for naphtha_type in ['Conventional', 'Bio', 'Recycled']:
            data = emissions_results[naphtha_type]
            print(f"   {naphtha_type}: {data['Total_Emissions_ktCO2']:,.0f} ktCO2 ({data['Emission_Factor_avg_tCO2_per_t']:.2f} tCO2/t)")
        
        # Calculate total and savings
        total_emissions = sum([data['Total_Emissions_ktCO2'] for data in emissions_results.values()])
        baseline_emissions = (conventional_naphtha + bio_naphtha + recycled_naphtha) * ef_conv_feedstock * feedstock_ratio + \
                           (conventional_naphtha + bio_naphtha + recycled_naphtha) * ef_conv_thermal * thermal_ratio
        
        emission_reduction = baseline_emissions - total_emissions
        reduction_percentage = (emission_reduction / baseline_emissions) * 100 if baseline_emissions > 0 else 0
        
        print(f"\n📊 IMPACT SUMMARY:")
        print(f"   Baseline (all conventional): {baseline_emissions:,.0f} ktCO2")
        print(f"   With alternatives: {total_emissions:,.0f} ktCO2")
        print(f"   Reduction: {emission_reduction:,.0f} ktCO2 ({reduction_percentage:.1f}%)")
        
        return alternatives_df, emission_reduction
    
    def optimize_naphtha_strategy(self, target_year=2030, emission_reduction_target=0.25):
        """Optimize naphtha alternative deployment to meet emission targets"""
        
        print(f"\n🎯 OPTIMIZING NAPHTHA STRATEGY ({target_year})")
        print(f"Target: {emission_reduction_target*100:.0f}% emission reduction")
        print("=" * 60)
        
        # Create optimization problem
        prob = LpProblem("Naphtha_Strategy_Optimization", LpMinimize)
        
        # Total naphtha demand (from baseline)
        total_naphtha_demand = 30200  # kt/year
        
        # Decision variables - naphtha type deployment (kt)
        conv_naphtha = LpVariable("Conventional_Naphtha", 0, total_naphtha_demand, LpInteger)
        bio_naphtha = LpVariable("Bio_Naphtha", 0, None, LpInteger)
        recycled_naphtha = LpVariable("Recycled_Naphtha", 0, None, LpInteger)
        
        # Get availability constraints for target year
        bio_availability = 15000 if target_year >= 2030 else 5000  # kt
        recycled_availability = 20000 if target_year >= 2030 else 8000  # kt
        
        # Get costs (from naphtha alternatives sheet)
        bio_cost_premium = 1.8  # 180% premium
        recycled_cost_premium = 0.8  # 80% premium
        base_naphtha_cost = 800  # USD/tonne
        
        # Objective: Minimize total cost
        total_cost = (conv_naphtha * base_naphtha_cost + 
                     bio_naphtha * base_naphtha_cost * (1 + bio_cost_premium) +
                     recycled_naphtha * base_naphtha_cost * (1 + recycled_cost_premium))
        
        prob += total_cost
        
        # Constraints
        # 1. Meet total naphtha demand
        prob += conv_naphtha + bio_naphtha + recycled_naphtha == total_naphtha_demand
        
        # 2. Availability constraints
        prob += bio_naphtha <= bio_availability
        prob += recycled_naphtha <= recycled_availability
        
        # 3. Emission reduction constraint
        # Get emission factors
        ef_conv = 1.3  # Average of feedstock and thermal (weighted)
        ef_bio = 0.1   # Bio-naphtha average
        ef_recycled = 1.0  # Recycled naphtha average
        
        baseline_emissions = total_naphtha_demand * ef_conv
        target_emissions = baseline_emissions * (1 - emission_reduction_target)
        
        actual_emissions = (conv_naphtha * ef_conv + 
                           bio_naphtha * ef_bio + 
                           recycled_naphtha * ef_recycled)
        
        prob += actual_emissions <= target_emissions
        
        # Solve
        prob.solve(PULP_CBC_CMD(msg=0))
        
        if prob.status == 1:  # Optimal solution found
            results = {
                'Conventional_Naphtha_kt': conv_naphtha.varValue,
                'Bio_Naphtha_kt': bio_naphtha.varValue,
                'Recycled_Naphtha_kt': recycled_naphtha.varValue,
                'Total_Cost_Million_USD': value(prob.objective) / 1000000,
                'Actual_Emissions_ktCO2': (conv_naphtha.varValue * ef_conv + 
                                         bio_naphtha.varValue * ef_bio + 
                                         recycled_naphtha.varValue * ef_recycled),
                'Baseline_Emissions_ktCO2': baseline_emissions,
                'Emission_Reduction_%': ((baseline_emissions - (conv_naphtha.varValue * ef_conv + 
                                                              bio_naphtha.varValue * ef_bio + 
                                                              recycled_naphtha.varValue * ef_recycled)) / baseline_emissions) * 100
            }
            
            print("✅ OPTIMAL NAPHTHA STRATEGY:")
            print(f"   Conventional: {results['Conventional_Naphtha_kt']:,.0f} kt ({results['Conventional_Naphtha_kt']/total_naphtha_demand*100:.1f}%)")
            print(f"   Bio-naphtha: {results['Bio_Naphtha_kt']:,.0f} kt ({results['Bio_Naphtha_kt']/total_naphtha_demand*100:.1f}%)")
            print(f"   Recycled: {results['Recycled_Naphtha_kt']:,.0f} kt ({results['Recycled_Naphtha_kt']/total_naphtha_demand*100:.1f}%)")
            print(f"   Total Cost: ${results['Total_Cost_Million_USD']:,.0f} million")
            print(f"   Emission Reduction: {results['Emission_Reduction_%']:.1f}%")
            
            return results
        else:
            print("❌ No feasible solution found")
            return None
    
    def create_visualization(self):
        """Create comprehensive visualization of naphtha emissions and alternatives"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Facility-level emissions
        facility_summary = self.facility_results.groupby('Company')['Total_Emissions_ktCO2'].sum().sort_values(ascending=True)
        ax1.barh(facility_summary.index, facility_summary.values, color='steelblue')
        ax1.set_title('Naphtha Emissions by Company', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Emissions (ktCO2/year)')
        
        # 2. Process type breakdown
        process_summary = self.facility_results.groupby('Process_Type')[['Feedstock_Emissions_ktCO2', 'Thermal_Emissions_ktCO2']].sum()
        process_summary.plot(kind='bar', stacked=True, ax=ax2, color=['lightcoral', 'lightskyblue'])
        ax2.set_title('Emissions by Process Type and Naphtha Use', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Emissions (ktCO2/year)')
        ax2.legend(['Feedstock', 'Thermal'])
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Naphtha alternatives comparison
        alternatives_data = {
            'Conventional': {'Feedstock': 0.90, 'Thermal': 2.33},
            'Bio-naphtha': {'Feedstock': 0.15, 'Thermal': 0.00},
            'Recycled': {'Feedstock': 0.45, 'Thermal': 2.33}
        }
        
        alt_df = pd.DataFrame(alternatives_data).T
        alt_df.plot(kind='bar', ax=ax3, color=['lightcoral', 'lightskyblue'])
        ax3.set_title('Emission Factors by Naphtha Type', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Emission Factor (tCO2/tonne)')
        ax3.legend(['Feedstock', 'Thermal'])
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Scenario analysis (2030)
        scenarios = ['Conservative', 'Moderate', 'Aggressive']
        scenario_emissions = []
        
        for scenario in scenarios:
            _, reduction = self.analyze_naphtha_alternatives(2030, scenario)
            scenario_emissions.append(reduction)
        
        ax4.bar(scenarios, scenario_emissions, color=['lightgreen', 'orange', 'red'])
        ax4.set_title('Emission Reductions by Scenario (2030)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Emission Reduction (ktCO2)')
        
        plt.tight_layout()
        plt.savefig('naphtha_emissions_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📊 Visualization saved: naphtha_emissions_analysis.png")

def main():
    """Main execution"""
    
    print("🛢️ KOREAN PETROCHEMICAL NAPHTHA EMISSIONS MODEL")
    print("=" * 70)
    
    # Initialize model
    model = NaphthaEmissionsModel("korean_petrochemical_scenario_configuration.xlsx")
    
    # Calculate facility-level emissions
    facility_results = model.calculate_facility_naphtha_emissions(2025)
    
    # Analyze alternatives for different scenarios
    for scenario in ['Conservative', 'Moderate', 'Aggressive']:
        print(f"\n{'='*50}")
        model.analyze_naphtha_alternatives(2030, scenario)
    
    # Optimize strategy
    optimal_results = model.optimize_naphtha_strategy(2030, 0.25)
    
    # Create visualization
    model.create_visualization()
    
    print(f"\n✅ NAPHTHA EMISSIONS MODEL COMPLETE")
    print(f"📊 Analysis covers {len(facility_results)} facilities")
    print(f"🌱 {len(model.naphtha_alternatives)} alternative strategies evaluated")

if __name__ == "__main__":
    main()