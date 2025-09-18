#!/usr/bin/env python3
"""
Emission Pathway Analysis for Korean Petrochemical Industry
Based on facility operation years and carbon intensity data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class EmissionPathwayAnalyzer:
    """Analyzes emission pathways for petrochemical facilities"""
    
    def __init__(self, data_file: str = "data/korean_petrochemical_macc_optimization.xlsx"):
        self.data_file = data_file
        self.facilities_df = None
        self.ci_df = None
        self.ci2_df = None
        self.pathway_25_df = None
        self.pathway_30_df = None
        self.load_data()
    
    def load_data(self):
        """Load and clean facility and carbon intensity data"""
        print("Loading data from Excel file...")
        
        # Load facilities data
        self.facilities_df = pd.read_excel(self.data_file, sheet_name='source')
        
        # Clean capacity data - replace '-' and NaN with 0
        self.facilities_df['capacity_1000_t'] = pd.to_numeric(
            self.facilities_df['capacity_1000_t'], errors='coerce'
        ).fillna(0)
        
        # Load carbon intensity data
        self.ci_df = pd.read_excel(self.data_file, sheet_name='CI')
        self.ci2_df = pd.read_excel(self.data_file, sheet_name='CI2')
        
        print(f"Loaded {len(self.facilities_df)} facilities")
        print(f"Facilities with capacity > 0: {(self.facilities_df['capacity_1000_t'] > 0).sum()}")
    
    def calculate_current_emissions(self):
        """Calculate current emissions using CI and CI2 data"""
        print("Calculating current emissions...")
        
        # Create mapping from CI data (energy consumption by product/process)
        ci_map = {}
        for _, row in self.ci_df.iterrows():
            key = (row['제품'], row['공정'])
            ci_map[key] = {
                'LNG_GJ_per_t': row.get('LNG(GJ/t)', 0) or 0,
                'electricity_kWh_per_t': row.get('전력(Baseline)(kWh/t)', 0) or 0,
                'fuel_gas_GJ_per_t': row.get('연료가스(Fuel gas mix)(GJ/t)', 0) or 0,
                'fuel_oil_GJ_per_t': row.get('중유(Fuel oil)(GJ/t)', 0) or 0
            }
        
        # Get emission factors from CI2 data (assuming first row contains factors)
        ef_row = self.ci2_df.iloc[0]
        emission_factors = {
            'LNG': ef_row.get('LNG( tCO₂/GJ )', 0.056),
            'electricity': ef_row.get('전력(Baseline)( tCO₂/kWh )', 0.0045),
            'fuel_gas': ef_row.get('연료가스(Fuel gas mix)( tCO₂/GJ )', 0.056),
            'fuel_oil': ef_row.get('중유(Fuel oil)( tCO₂/GJ )', 0.077)
        }
        
        # Calculate emissions for each facility
        emissions_data = []
        
        for _, facility in self.facilities_df.iterrows():
            if facility['capacity_1000_t'] == 0:
                continue
                
            product = facility['products']
            process = facility['process']
            capacity_kt = facility['capacity_1000_t']
            
            # Find matching CI data
            ci_key = (product, process)
            if ci_key not in ci_map:
                # Try to find approximate match
                product_matches = [k for k in ci_map.keys() if k[0] == product]
                if product_matches:
                    ci_key = product_matches[0]
                else:
                    # Default values for unknown products
                    ci_data = {
                        'LNG_GJ_per_t': 10.0,
                        'electricity_kWh_per_t': 500.0,
                        'fuel_gas_GJ_per_t': 5.0,
                        'fuel_oil_GJ_per_t': 2.0
                    }
            else:
                ci_data = ci_map[ci_key]
            
            # Calculate annual emissions (kt CO2)
            annual_production_kt = capacity_kt  # Assume full capacity utilization
            
            lng_emissions = (ci_data['LNG_GJ_per_t'] * annual_production_kt * 
                           emission_factors['LNG'])
            
            electricity_emissions = (ci_data['electricity_kWh_per_t'] * annual_production_kt * 
                                   emission_factors['electricity'])
            
            fuel_gas_emissions = (ci_data['fuel_gas_GJ_per_t'] * annual_production_kt * 
                                emission_factors['fuel_gas'])
            
            fuel_oil_emissions = (ci_data['fuel_oil_GJ_per_t'] * annual_production_kt * 
                                emission_factors['fuel_oil'])
            
            total_emissions_kt = (lng_emissions + electricity_emissions + 
                                fuel_gas_emissions + fuel_oil_emissions)
            
            emissions_data.append({
                'facility_id': f"{facility['company']}_{facility['location']}_{product}_{facility['year']}",
                'company': facility['company'],
                'location': facility['location'],
                'product': product,
                'process': process,
                'start_year': facility['year'],
                'capacity_kt': capacity_kt,
                'annual_emissions_kt_co2': total_emissions_kt,
                'emission_intensity_t_co2_per_t': total_emissions_kt / capacity_kt if capacity_kt > 0 else 0
            })
        
        self.emissions_df = pd.DataFrame(emissions_data)
        print(f"Calculated emissions for {len(self.emissions_df)} active facilities")
        
        return self.emissions_df
    
    def create_bau_pathway(self, facility_lifetime: int = 25, end_year: int = 2050):
        """Create BAU emission pathway with no shutdowns before 2029"""
        if self.emissions_df is None:
            self.calculate_current_emissions()
        
        print(f"Creating BAU pathway with {facility_lifetime}-year facility lifetime (no shutdowns before 2029)...")
        
        # Create annual emissions timeline
        years = list(range(2023, end_year + 1))
        annual_emissions = {year: 0.0 for year in years}
        
        # For each facility, add emissions during its operational period
        for _, facility in self.emissions_df.iterrows():
            start_year = int(facility['start_year'])
            # No shutdowns before 2029, regardless of theoretical lifetime
            theoretical_end_year = start_year + facility_lifetime
            actual_end_year = max(theoretical_end_year, 2029)  # Minimum operation until 2029
            annual_emissions_kt = facility['annual_emissions_kt_co2']
            
            for year in years:
                if start_year <= year < actual_end_year:
                    annual_emissions[year] += annual_emissions_kt
        
        # Convert to Mt CO2
        pathway_data = []
        for year in years:
            pathway_data.append({
                'year': year,
                'emissions_mt_co2': annual_emissions[year] / 1000,  # Convert kt to Mt
                'active_facilities': sum(1 for _, f in self.emissions_df.iterrows() 
                                       if int(f['start_year']) <= year < max(int(f['start_year']) + facility_lifetime, 2029))
            })
        
        pathway_df = pd.DataFrame(pathway_data)
        
        # Store both 25 and 30 year scenarios
        if facility_lifetime == 25:
            self.pathway_25_df = pathway_df
        elif facility_lifetime == 30:
            self.pathway_30_df = pathway_df
        
        return pathway_df
    
    def create_both_pathways(self, end_year: int = 2050):
        """Create both 25-year and 30-year facility lifetime pathways"""
        print("Creating both 25-year and 30-year BAU pathways...")
        
        # Create 25-year pathway
        pathway_25 = self.create_bau_pathway(facility_lifetime=25, end_year=end_year)
        
        # Create 30-year pathway  
        pathway_30 = self.create_bau_pathway(facility_lifetime=30, end_year=end_year)
        
        return pathway_25, pathway_30
    
    def analyze_facility_retirement(self):
        """Analyze when facilities retire under 25-year lifetime assumption"""
        if self.emissions_df is None:
            self.calculate_current_emissions()
        
        retirement_analysis = []
        
        for _, facility in self.emissions_df.iterrows():
            start_year = int(facility['start_year'])
            retirement_year = start_year + 25
            
            retirement_analysis.append({
                'facility_id': facility['facility_id'],
                'company': facility['company'],
                'product': facility['product'],
                'start_year': start_year,
                'retirement_year': retirement_year,
                'capacity_kt': facility['capacity_kt'],
                'annual_emissions_kt_co2': facility['annual_emissions_kt_co2']
            })
        
        retirement_df = pd.DataFrame(retirement_analysis)
        
        # Aggregate retirements by year
        retirement_by_year = retirement_df.groupby('retirement_year').agg({
            'capacity_kt': 'sum',
            'annual_emissions_kt_co2': 'sum',
            'facility_id': 'count'
        }).rename(columns={'facility_id': 'facilities_retiring'})
        
        return retirement_df, retirement_by_year
    
    def generate_summary_statistics(self):
        """Generate summary statistics for both emission pathways"""
        if self.pathway_25_df is None or self.pathway_30_df is None:
            self.create_both_pathways()
        
        # Current status (2023) - same for both scenarios
        current_emissions = self.pathway_25_df[self.pathway_25_df['year'] == 2023]['emissions_mt_co2'].iloc[0]
        current_facilities = self.pathway_25_df[self.pathway_25_df['year'] == 2023]['active_facilities'].iloc[0]
        
        # 25-year scenario
        peak_year_25 = self.pathway_25_df.loc[self.pathway_25_df['emissions_mt_co2'].idxmax(), 'year']
        peak_emissions_25 = self.pathway_25_df['emissions_mt_co2'].max()
        emissions_2050_25 = self.pathway_25_df[self.pathway_25_df['year'] == 2050]['emissions_mt_co2'].iloc[0]
        
        # 30-year scenario
        peak_year_30 = self.pathway_30_df.loc[self.pathway_30_df['emissions_mt_co2'].idxmax(), 'year']
        peak_emissions_30 = self.pathway_30_df['emissions_mt_co2'].max()
        emissions_2050_30 = self.pathway_30_df[self.pathway_30_df['year'] == 2050]['emissions_mt_co2'].iloc[0]
        
        # By product breakdown (current)
        product_breakdown = self.emissions_df.groupby('product')['annual_emissions_kt_co2'].sum().sort_values(ascending=False)
        
        summary = {
            'current_emissions_mt_co2': current_emissions,
            'current_active_facilities': current_facilities,
            'scenario_25_year': {
                'peak_year': peak_year_25,
                'peak_emissions_mt_co2': peak_emissions_25,
                'emissions_2050_mt_co2': emissions_2050_25,
                'natural_reduction_2050_pct': (1 - emissions_2050_25/current_emissions) * 100 if current_emissions > 0 else 0,
            },
            'scenario_30_year': {
                'peak_year': peak_year_30,
                'peak_emissions_mt_co2': peak_emissions_30,
                'emissions_2050_mt_co2': emissions_2050_30,
                'natural_reduction_2050_pct': (1 - emissions_2050_30/current_emissions) * 100 if current_emissions > 0 else 0,
            },
            'top_emitting_products': product_breakdown.head(10).to_dict()
        }
        
        return summary
    
    def save_results(self, output_dir: str = "outputs"):
        """Save analysis results to CSV files"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save facility emissions
        if self.emissions_df is not None:
            self.emissions_df.to_csv(f"{output_dir}/facility_emissions_final.csv", index=False)
        
        # Save both BAU pathways
        if self.pathway_25_df is not None:
            self.pathway_25_df.to_csv(f"{output_dir}/bau_emission_pathway_25yr_final.csv", index=False)
        
        if self.pathway_30_df is not None:
            self.pathway_30_df.to_csv(f"{output_dir}/bau_emission_pathway_30yr_final.csv", index=False)
        
        # Save retirement analysis
        retirement_df, retirement_by_year = self.analyze_facility_retirement()
        retirement_df.to_csv(f"{output_dir}/facility_retirement_schedule.csv", index=False)
        retirement_by_year.to_csv(f"{output_dir}/retirement_by_year.csv")
        
        print(f"Results saved to {output_dir}/")
    
    def plot_emission_pathway(self, output_dir: str = "outputs"):
        """Create visualization of both emission pathways"""
        if self.pathway_25_df is None or self.pathway_30_df is None:
            self.create_both_pathways()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Emission pathways comparison
        ax1.plot(self.pathway_25_df['year'], self.pathway_25_df['emissions_mt_co2'], 
                linewidth=2, color='red', label='25-year facility lifetime')
        ax1.plot(self.pathway_30_df['year'], self.pathway_30_df['emissions_mt_co2'], 
                linewidth=2, color='orange', label='30-year facility lifetime')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (Mt CO₂)')
        ax1.set_title('Korean Petrochemical Industry - BAU Emission Pathways\n(Corrected CI Data)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Active facilities comparison
        ax2.plot(self.pathway_25_df['year'], self.pathway_25_df['active_facilities'], 
                linewidth=2, color='blue', label='25-year lifetime')
        ax2.plot(self.pathway_30_df['year'], self.pathway_30_df['active_facilities'], 
                linewidth=2, color='green', label='30-year lifetime')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Number of Active Facilities')
        ax2.set_title('Active Facilities Over Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/bau_emission_pathways_final.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Emission pathway charts saved to {output_dir}/bau_emission_pathways_final.png")


def main():
    """Main execution function"""
    print("=== Korean Petrochemical Emission Pathway Analysis (Final Calibrated Data) ===")
    
    # Initialize analyzer
    analyzer = EmissionPathwayAnalyzer()
    
    # Calculate current emissions
    emissions_df = analyzer.calculate_current_emissions()
    
    # Create both BAU pathways
    pathway_25, pathway_30 = analyzer.create_both_pathways()
    
    # Generate summary
    summary = analyzer.generate_summary_statistics()
    
    # Print summary
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Current Emissions (2023): {summary['current_emissions_mt_co2']:.1f} Mt CO₂")
    print(f"Active Facilities (2023): {summary['current_active_facilities']}")
    
    print(f"\n25-YEAR FACILITY LIFETIME SCENARIO:")
    print(f"  Peak Year: {summary['scenario_25_year']['peak_year']} ({summary['scenario_25_year']['peak_emissions_mt_co2']:.1f} Mt CO₂)")
    print(f"  Emissions in 2050: {summary['scenario_25_year']['emissions_2050_mt_co2']:.1f} Mt CO₂")
    print(f"  Natural Reduction by 2050: {summary['scenario_25_year']['natural_reduction_2050_pct']:.1f}%")
    
    print(f"\n30-YEAR FACILITY LIFETIME SCENARIO:")
    print(f"  Peak Year: {summary['scenario_30_year']['peak_year']} ({summary['scenario_30_year']['peak_emissions_mt_co2']:.1f} Mt CO₂)")
    print(f"  Emissions in 2050: {summary['scenario_30_year']['emissions_2050_mt_co2']:.1f} Mt CO₂")
    print(f"  Natural Reduction by 2050: {summary['scenario_30_year']['natural_reduction_2050_pct']:.1f}%")
    
    print("\nTop Emitting Products:")
    for product, emissions in summary['top_emitting_products'].items():
        print(f"  {product}: {emissions/1000:.1f} Mt CO₂/year")
    
    # Save results
    analyzer.save_results()
    
    # Create visualization
    analyzer.plot_emission_pathway()
    
    print("\n=== Analysis Complete ===")


if __name__ == "__main__":
    main()