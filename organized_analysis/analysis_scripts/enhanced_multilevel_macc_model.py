#!/usr/bin/env python3
"""
Enhanced Multi-Level MACC Model for Korean Petrochemical Industry
Incorporates facility age, depreciation, and retirement prioritization
Multi-level analysis: Region -> Company -> Facility
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedMultiLevelMACCModel:
    def __init__(self, excel_path):
        """
        Initialize Enhanced Multi-Level MACC Model

        Args:
            excel_path: Path to corrected MACC Excel model
        """
        self.excel_path = excel_path
        self.facilities_df = None
        self.ci_df = None
        self.ci2_df = None
        self.macc_df = None

        # Multi-level results
        self.facility_results = None
        self.company_results = None
        self.region_results = None

        # Depreciation and retirement parameters
        self.current_year = 2025
        self.economic_life_years = {'Naphtha Cracker': 30, 'BTX Plant': 25, 'Utility': 20}
        self.retirement_threshold_age = {'Naphtha Cracker': 40, 'BTX Plant': 35, 'Utility': 30}

        self._load_data()
        self._prepare_multilevel_structure()

    def _load_data(self):
        """Load all required data from Excel"""
        print("📊 Loading enhanced multi-level data...")

        # Load facility data with age calculations
        self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')
        self.facilities_df['age_years'] = self.current_year - self.facilities_df['year']
        self.facilities_df['facility_id'] = range(len(self.facilities_df))

        # Load CI and CI2 matrices
        self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
        self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)
        self.macc_df = pd.read_excel(self.excel_path, sheet_name='MACC_Template_Corrected', index_col=0)

        print(f"   Facilities: {len(self.facilities_df)}")
        print(f"   Companies: {self.facilities_df['company'].nunique()}")
        print(f"   Regions: {self.facilities_df['location'].nunique()}")

    def _prepare_multilevel_structure(self):
        """Prepare multi-level hierarchical structure"""
        print("\n🏗️  Preparing multi-level structure...")

        # Create hierarchical mapping
        self.facilities_df['region'] = self.facilities_df['location']
        self.facilities_df['process_simplified'] = self.facilities_df['process'].map({
            'Naphtha Cracker': 'NCC',
            'BTX Plant': 'BTX',
            'Utility': 'Utility'
        })

        # Calculate depreciation factors
        self.facilities_df['depreciation_factor'] = self._calculate_depreciation_factor()
        self.facilities_df['retirement_priority'] = self._calculate_retirement_priority()
        self.facilities_df['remaining_life'] = self._calculate_remaining_life()

        print(f"   Age range: {self.facilities_df['age_years'].min():.0f} - {self.facilities_df['age_years'].max():.0f} years")
        print(f"   Facilities near retirement: {len(self.facilities_df[self.facilities_df['retirement_priority'] > 0.7])}")

    def _calculate_depreciation_factor(self):
        """Calculate depreciation factor based on age and economic life"""
        depreciation_factors = []

        for _, facility in self.facilities_df.iterrows():
            process = facility['process']
            age = facility['age_years']
            economic_life = self.economic_life_years.get(process, 25)

            if age <= 0:  # Future facilities
                factor = 1.0
            elif age >= economic_life:
                # Fully depreciated, higher incentive for retirement
                factor = 0.1 + (0.2 * min(age - economic_life, 10) / 10)  # 0.1-0.3 range
            else:
                # Linear depreciation
                factor = 1.0 - (age / economic_life)

            depreciation_factors.append(max(0.1, factor))  # Minimum 10% value

        return np.array(depreciation_factors)

    def _calculate_retirement_priority(self):
        """Calculate retirement priority (0-1, higher = retire first)"""
        priorities = []

        for _, facility in self.facilities_df.iterrows():
            process = facility['process']
            age = facility['age_years']
            threshold = self.retirement_threshold_age.get(process, 30)

            if age >= threshold:
                # High priority for retirement
                priority = 0.7 + (0.3 * min(age - threshold, 15) / 15)
            elif age >= threshold * 0.8:
                # Medium priority
                priority = 0.4 + (0.3 * (age - threshold * 0.8) / (threshold * 0.2))
            else:
                # Low priority
                priority = min(0.4, age / (threshold * 0.8))

            priorities.append(min(1.0, priority))

        return np.array(priorities)

    def _calculate_remaining_life(self):
        """Calculate remaining economic life"""
        remaining_lives = []

        for _, facility in self.facilities_df.iterrows():
            process = facility['process']
            age = facility['age_years']
            economic_life = self.economic_life_years.get(process, 25)

            remaining = max(0, economic_life - age)
            remaining_lives.append(remaining)

        return np.array(remaining_lives)

    def calculate_facility_level_analysis(self):
        """Calculate facility-level emissions, costs, and retirement factors"""
        print("\n🏭 FACILITY-LEVEL ANALYSIS")
        print("=" * 60)

        facility_results = []

        # Get emission factors from CI2
        emission_factors = self._extract_emission_factors()
        fuel_prices = self._get_fuel_prices()

        for idx, facility in self.facilities_df.iterrows():
            # Map facility to product type
            product = self._map_facility_to_product(facility['process'])

            if product not in self.ci_df.index:
                continue

            product_row = self.ci_df.loc[product]
            capacity = facility['capacity_1000_t'] * 1000  # Convert to tonnes

            if capacity <= 0:
                continue

            # Calculate emissions for each fuel type
            facility_emissions = 0
            facility_fuel_cost = 0
            fuel_breakdown = {}

            fuel_types = [
                ('LNG_GJ_per_t', 'LNG_tCO2_per_GJ', 'LNG', 12.0),
                ('Fuel_Oil_GJ_per_t', 'Fuel_Oil_tCO2_per_GJ', 'Heavy Oil', 15.0),
                ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ', 'Naphtha Feedstock', 18.0),
                ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ', 'Naphtha Thermal', 18.0),
                ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh', 'Electricity', 0.12)
            ]

            for consumption_col, emission_col, fuel_name, fuel_price in fuel_types:
                if consumption_col in product_row.index:
                    consumption_per_t = product_row[consumption_col]
                    if pd.notna(consumption_per_t) and consumption_per_t > 0:
                        total_consumption = consumption_per_t * capacity

                        # Emissions
                        if emission_col in emission_factors:
                            emission_factor = emission_factors[emission_col]
                            fuel_emissions = total_consumption * emission_factor
                            facility_emissions += fuel_emissions

                            # Costs
                            fuel_cost = total_consumption * fuel_price
                            facility_fuel_cost += fuel_cost

                            fuel_breakdown[fuel_name] = {
                                'consumption': total_consumption,
                                'emissions_tco2': fuel_emissions,
                                'cost_usd': fuel_cost
                            }

            # Calculate retirement economics
            stranded_asset_risk = self._calculate_stranded_asset_risk(facility)
            replacement_benefit = self._calculate_replacement_benefit(facility, facility_emissions)

            result = {
                'facility_id': facility['facility_id'],
                'facility_name': f"{facility['company']}_{facility['process']}_{idx}",
                'company': facility['company'],
                'region': facility['region'],
                'process_type': facility['process'],
                'capacity_t': capacity,
                'age_years': facility['age_years'],
                'operational_year': facility['year'],
                'emissions_tco2': facility_emissions,
                'fuel_cost_usd': facility_fuel_cost,
                'emission_intensity': facility_emissions / capacity if capacity > 0 else 0,
                'cost_intensity': facility_fuel_cost / capacity if capacity > 0 else 0,
                'depreciation_factor': facility['depreciation_factor'],
                'retirement_priority': facility['retirement_priority'],
                'remaining_life': facility['remaining_life'],
                'stranded_asset_risk': stranded_asset_risk,
                'replacement_benefit': replacement_benefit,
                'fuel_breakdown': fuel_breakdown
            }

            facility_results.append(result)

        self.facility_results = pd.DataFrame(facility_results)

        # Summary statistics
        total_emissions = self.facility_results['emissions_tco2'].sum()
        total_fuel_cost = self.facility_results['fuel_cost_usd'].sum()

        print(f"✅ Facility Analysis Complete:")
        print(f"   Total Emissions: {total_emissions:,.0f} tCO2/year")
        print(f"   Total Fuel Cost: ${total_fuel_cost:,.0f}/year")
        print(f"   Facilities Analyzed: {len(self.facility_results)}")
        print(f"   Near Retirement (>70% priority): {len(self.facility_results[self.facility_results['retirement_priority'] > 0.7])}")

        return self.facility_results

    def calculate_company_level_analysis(self):
        """Aggregate to company level with strategic insights"""
        print("\n🏢 COMPANY-LEVEL ANALYSIS")
        print("=" * 60)

        if self.facility_results is None:
            self.calculate_facility_level_analysis()

        company_aggregation = {
            'capacity_t': 'sum',
            'emissions_tco2': 'sum',
            'fuel_cost_usd': 'sum',
            'age_years': 'mean',
            'retirement_priority': 'mean',
            'remaining_life': 'mean',
            'stranded_asset_risk': 'mean',
            'replacement_benefit': 'sum'
        }

        company_results = self.facility_results.groupby('company').agg(company_aggregation).round(2)

        # Add facility count separately
        company_results['facility_count'] = self.facility_results.groupby('company').size()

        # Add derived metrics
        company_results['emission_intensity'] = (
            company_results['emissions_tco2'] / company_results['capacity_t']
        ).round(4)

        company_results['cost_intensity'] = (
            company_results['fuel_cost_usd'] / company_results['capacity_t']
        ).round(2)

        # Calculate investment requirements (placeholder - would need detailed technology mapping)
        company_results['estimated_investment_musd'] = (
            company_results['emissions_tco2'] * 0.0003  # $300/tCO2 average
        ).round(1)

        # Process type distribution by company
        process_dist = self.facility_results.groupby(['company', 'process_type']).size().unstack(fill_value=0)
        company_results = pd.concat([company_results, process_dist.add_suffix('_facilities')], axis=1)

        # Add region presence
        region_presence = self.facility_results.groupby('company')['region'].apply(
            lambda x: list(x.unique())
        )
        company_results['regions'] = region_presence

        self.company_results = company_results.sort_values('emissions_tco2', ascending=False)

        # Show top companies
        print("🏆 TOP 10 COMPANIES BY EMISSIONS:")
        top_companies = self.company_results.head(10)[
            ['facility_count', 'emissions_tco2', 'emission_intensity',
             'retirement_priority', 'estimated_investment_musd']
        ]
        print(top_companies.to_string(float_format='%.1f'))

        return self.company_results

    def calculate_region_level_analysis(self):
        """Aggregate to region level for policy analysis"""
        print("\n🌍 REGION-LEVEL ANALYSIS")
        print("=" * 60)

        if self.facility_results is None:
            self.calculate_facility_level_analysis()

        region_aggregation = {
            'capacity_t': 'sum',
            'emissions_tco2': 'sum',
            'fuel_cost_usd': 'sum',
            'age_years': 'mean',
            'retirement_priority': 'mean',
            'remaining_life': 'mean',
            'stranded_asset_risk': 'mean',
            'replacement_benefit': 'sum'
        }

        region_results = self.facility_results.groupby('region').agg(region_aggregation).round(2)

        # Add facility count separately
        region_results['facility_count'] = self.facility_results.groupby('region').size()

        # Add derived metrics
        region_results['emission_intensity'] = (
            region_results['emissions_tco2'] / region_results['capacity_t']
        ).round(4)

        region_results['companies_count'] = self.facility_results.groupby('region')['company'].nunique()

        # Process type distribution by region
        process_dist = self.facility_results.groupby(['region', 'process_type']).size().unstack(fill_value=0)
        region_results = pd.concat([region_results, process_dist.add_suffix('_facilities')], axis=1)

        self.region_results = region_results.sort_values('emissions_tco2', ascending=False)

        # Show all regions
        print("🌍 ALL REGIONS ANALYSIS:")
        region_display = self.region_results[
            ['facility_count', 'companies_count', 'emissions_tco2',
             'emission_intensity', 'retirement_priority']
        ]
        print(region_display.to_string(float_format='%.2f'))

        return self.region_results

    def create_retirement_optimization_model(self, emission_reduction_target=0.3):
        """Create retirement-prioritized technology deployment model"""
        print(f"\n⚙️  RETIREMENT-OPTIMIZED DEPLOYMENT ({emission_reduction_target*100}% reduction)")
        print("=" * 70)

        if self.facility_results is None:
            self.calculate_facility_level_analysis()

        # Sort facilities by retirement priority (highest first)
        facilities_sorted = self.facility_results.sort_values('retirement_priority', ascending=False)

        total_baseline_emissions = facilities_sorted['emissions_tco2'].sum()
        target_reduction = total_baseline_emissions * emission_reduction_target

        print(f"Total Baseline Emissions: {total_baseline_emissions:,.0f} tCO2/year")
        print(f"Target Reduction: {target_reduction:,.0f} tCO2/year")

        # Retirement-based deployment strategy
        retirement_results = []
        cumulative_reduction = 0
        cumulative_cost = 0

        # Technology costs (simplified for retirement prioritization)
        tech_costs = {
            'Early_Retirement': 50,      # Low cost for early retirement
            'Efficiency_Upgrade': 100,   # Medium cost for efficiency
            'Fuel_Switch': 200,          # Higher cost for fuel switching
            'Process_Replacement': 400   # Highest cost for new technology
        }

        for idx, facility in facilities_sorted.iterrows():
            if cumulative_reduction >= target_reduction:
                break

            # Determine optimal technology based on retirement priority and age
            retirement_priority = facility['retirement_priority']
            age = facility['age_years']
            emissions = facility['emissions_tco2']

            if retirement_priority > 0.8:
                # High priority: Early retirement
                tech = 'Early_Retirement'
                abatement = emissions * 0.9  # 90% reduction
            elif retirement_priority > 0.6:
                # Medium-high priority: Process replacement
                tech = 'Process_Replacement'
                abatement = emissions * 0.75  # 75% reduction
            elif age > 20:
                # Older facilities: Fuel switch
                tech = 'Fuel_Switch'
                abatement = emissions * 0.5  # 50% reduction
            else:
                # Newer facilities: Efficiency upgrade
                tech = 'Efficiency_Upgrade'
                abatement = emissions * 0.2  # 20% reduction

            tech_cost = tech_costs[tech]
            total_tech_cost = abatement * tech_cost

            retirement_results.append({
                'facility_id': facility['facility_id'],
                'facility_name': facility['facility_name'],
                'company': facility['company'],
                'region': facility['region'],
                'process_type': facility['process_type'],
                'age_years': age,
                'retirement_priority': retirement_priority,
                'baseline_emissions': emissions,
                'technology': tech,
                'abatement_tco2': abatement,
                'cost_per_tco2': tech_cost,
                'total_cost_usd': total_tech_cost,
                'cumulative_abatement': cumulative_reduction + abatement,
                'cumulative_cost': cumulative_cost + total_tech_cost
            })

            cumulative_reduction += abatement
            cumulative_cost += total_tech_cost

        retirement_df = pd.DataFrame(retirement_results)

        print(f"\n✅ Retirement Optimization Results:")
        print(f"   Achieved Reduction: {cumulative_reduction:,.0f} tCO2 ({cumulative_reduction/total_baseline_emissions*100:.1f}%)")
        print(f"   Total Investment: ${cumulative_cost:,.0f}")
        print(f"   Average Cost: ${cumulative_cost/cumulative_reduction:.0f}/tCO2")
        print(f"   Facilities Involved: {len(retirement_df)}")

        # Technology breakdown
        tech_summary = retirement_df.groupby('technology').agg({
            'facility_id': 'count',
            'abatement_tco2': 'sum',
            'total_cost_usd': 'sum'
        }).rename(columns={'facility_id': 'facility_count'})

        print(f"\n🔧 Technology Deployment Summary:")
        for tech, data in tech_summary.iterrows():
            print(f"   {tech}: {data['facility_count']} facilities, "
                  f"{data['abatement_tco2']:,.0f} tCO2, ${data['total_cost_usd']:,.0f}")

        return retirement_df

    def _calculate_stranded_asset_risk(self, facility):
        """Calculate stranded asset risk based on age and carbon policies"""
        age = facility['age_years']
        process = facility['process']

        # Base risk from age
        age_risk = min(0.8, age / 40)

        # Process-specific risk
        process_risk = {'Naphtha Cracker': 0.7, 'BTX Plant': 0.5, 'Utility': 0.3}.get(process, 0.4)

        # Combined risk
        return min(1.0, (age_risk + process_risk) / 2)

    def _calculate_replacement_benefit(self, facility, emissions):
        """Calculate economic benefit of facility replacement"""
        age = facility['age_years']
        remaining_life = facility['remaining_life']

        if remaining_life <= 5:
            # High benefit for near-retirement facilities
            return emissions * 150  # $150/tCO2 benefit
        elif age > 25:
            # Medium benefit for older facilities
            return emissions * 100  # $100/tCO2 benefit
        else:
            # Lower benefit for newer facilities
            return emissions * 50   # $50/tCO2 benefit

    def _extract_emission_factors(self):
        """Extract emission factors from CI2 matrix"""
        factors = {}
        for col in self.ci2_df.columns:
            factors[col] = self.ci2_df[col].iloc[0] if not self.ci2_df[col].empty else 0.0
        return factors

    def _get_fuel_prices(self):
        """Get fuel price assumptions ($/GJ or $/kWh)"""
        return {
            'LNG': 12.0,
            'Heavy Oil': 15.0,
            'Naphtha': 18.0,
            'Electricity': 0.12
        }

    def _map_facility_to_product(self, process_type):
        """Map facility process to CI matrix product"""
        mapping = {
            'Naphtha Cracker': 'Ethylene',
            'BTX Plant': 'Benzene',
            'Utility': 'Steam'
        }
        return mapping.get(process_type, 'Ethylene')

    def create_comprehensive_visualization(self):
        """Create comprehensive multi-level visualization"""
        print("\n📊 Creating comprehensive multi-level visualization...")

        fig = plt.figure(figsize=(24, 18))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)

        # Plot 1: Facility age distribution by process (top-left)
        ax1 = fig.add_subplot(gs[0, 0])
        for process in ['Naphtha Cracker', 'BTX Plant', 'Utility']:
            process_data = self.facilities_df[self.facilities_df['process'] == process]['age_years']
            ax1.hist(process_data, alpha=0.7, label=process, bins=15)
        ax1.set_xlabel('Facility Age (years)')
        ax1.set_ylabel('Count')
        ax1.set_title('Facility Age Distribution by Process')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Regional emissions comparison (top-middle)
        ax2 = fig.add_subplot(gs[0, 1])
        if self.region_results is not None:
            top_regions = self.region_results.head(8)
            bars = ax2.bar(range(len(top_regions)), top_regions['emissions_tco2']/1e6)
            ax2.set_xticks(range(len(top_regions)))
            ax2.set_xticklabels(top_regions.index, rotation=45, ha='right')
            ax2.set_ylabel('Emissions (MtCO₂/year)')
            ax2.set_title('Regional Emissions Distribution')

        # Plot 3: Company emissions vs retirement priority (top-right)
        ax3 = fig.add_subplot(gs[0, 2:])
        if self.company_results is not None:
            top_companies = self.company_results.head(15)
            scatter = ax3.scatter(top_companies['emissions_tco2']/1e6,
                                top_companies['retirement_priority'],
                                s=top_companies['facility_count']*20,
                                alpha=0.7)
            ax3.set_xlabel('Emissions (MtCO₂/year)')
            ax3.set_ylabel('Average Retirement Priority')
            ax3.set_title('Company Emissions vs Retirement Priority (bubble size = facility count)')
            ax3.grid(True, alpha=0.3)

        # Plot 4: Retirement priority distribution (second row, left)
        ax4 = fig.add_subplot(gs[1, 0])
        if self.facility_results is not None:
            ax4.hist(self.facility_results['retirement_priority'], bins=20, alpha=0.7, color='orange')
            ax4.axvline(0.7, color='red', linestyle='--', label='High Priority Threshold')
            ax4.set_xlabel('Retirement Priority')
            ax4.set_ylabel('Number of Facilities')
            ax4.set_title('Retirement Priority Distribution')
            ax4.legend()
            ax4.grid(True, alpha=0.3)

        # Plot 5: Age vs emissions intensity (second row, middle)
        ax5 = fig.add_subplot(gs[1, 1])
        if self.facility_results is not None:
            colors = {'Naphtha Cracker': 'red', 'BTX Plant': 'blue', 'Utility': 'green'}
            for process in colors:
                process_data = self.facility_results[self.facility_results['process_type'] == process]
                ax5.scatter(process_data['age_years'], process_data['emission_intensity'],
                           c=colors[process], label=process, alpha=0.6)
            ax5.set_xlabel('Facility Age (years)')
            ax5.set_ylabel('Emission Intensity (tCO₂/t)')
            ax5.set_title('Age vs Emission Intensity by Process')
            ax5.legend()
            ax5.grid(True, alpha=0.3)

        # Plot 6: Regional capacity and age analysis (second row, right)
        ax6 = fig.add_subplot(gs[1, 2:])
        if self.region_results is not None:
            regions = self.region_results.head(10)
            x = np.arange(len(regions))
            width = 0.35

            ax6_twin = ax6.twinx()
            bars1 = ax6.bar(x - width/2, regions['capacity_t']/1e6, width, label='Capacity (Mt)', alpha=0.7)
            bars2 = ax6_twin.bar(x + width/2, regions['age_years'], width, label='Avg Age (years)',
                               color='orange', alpha=0.7)

            ax6.set_xlabel('Region')
            ax6.set_ylabel('Capacity (Mt/year)')
            ax6_twin.set_ylabel('Average Age (years)')
            ax6.set_title('Regional Capacity and Average Facility Age')
            ax6.set_xticks(x)
            ax6.set_xticklabels(regions.index, rotation=45, ha='right')

            # Combine legends
            lines1, labels1 = ax6.get_legend_handles_labels()
            lines2, labels2 = ax6_twin.get_legend_handles_labels()
            ax6.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Plot 7: Technology deployment by retirement priority (third row, full width)
        ax7 = fig.add_subplot(gs[2, :])
        # Create sample retirement optimization for visualization
        retirement_results = self.create_retirement_optimization_model(0.3)
        if not retirement_results.empty:
            tech_deployment = retirement_results.groupby('technology').agg({
                'abatement_tco2': 'sum',
                'total_cost_usd': 'sum'
            })

            x = np.arange(len(tech_deployment))
            width = 0.35

            ax7_twin = ax7.twinx()
            bars1 = ax7.bar(x - width/2, tech_deployment['abatement_tco2']/1e6, width,
                           label='Abatement (MtCO₂)', alpha=0.7)
            bars2 = ax7_twin.bar(x + width/2, tech_deployment['total_cost_usd']/1e9, width,
                               label='Investment (Billion $)', color='green', alpha=0.7)

            ax7.set_xlabel('Technology')
            ax7.set_ylabel('Abatement (MtCO₂)')
            ax7_twin.set_ylabel('Investment (Billion $)')
            ax7.set_title('Technology Deployment for 30% Emission Reduction (Age-Prioritized)')
            ax7.set_xticks(x)
            ax7.set_xticklabels(tech_deployment.index, rotation=45, ha='right')

            lines1, labels1 = ax7.get_legend_handles_labels()
            lines2, labels2 = ax7_twin.get_legend_handles_labels()
            ax7.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Plot 8: Multi-level emission breakdown (bottom row)
        ax8 = fig.add_subplot(gs[3, :2])
        if self.facility_results is not None:
            # Create nested pie chart for multi-level breakdown
            process_emissions = self.facility_results.groupby('process_type')['emissions_tco2'].sum()

            # Outer ring: by process type
            ax8.pie(process_emissions.values, labels=process_emissions.index, autopct='%1.1f%%',
                   startangle=90, radius=1.0, wedgeprops=dict(width=0.3))

            # Inner ring: by age category
            age_categories = pd.cut(self.facility_results['age_years'],
                                  bins=[0, 20, 30, 100], labels=['Young (<20y)', 'Medium (20-30y)', 'Old (>30y)'])
            age_emissions = self.facility_results.groupby(age_categories)['emissions_tco2'].sum()

            ax8.pie(age_emissions.values, labels=age_emissions.index, autopct='%1.1f%%',
                   startangle=90, radius=0.7, wedgeprops=dict(width=0.3))

            ax8.set_title('Multi-Level Emission Breakdown\n(Outer: Process Type, Inner: Age Category)')

        # Plot 9: Investment requirement by company (bottom right)
        ax9 = fig.add_subplot(gs[3, 2:])
        if self.company_results is not None:
            top_companies = self.company_results.head(12)
            bars = ax9.barh(range(len(top_companies)), top_companies['estimated_investment_musd'])
            ax9.set_yticks(range(len(top_companies)))
            ax9.set_yticklabels([name[:15] + '...' if len(name) > 15 else name
                               for name in top_companies.index], fontsize=8)
            ax9.set_xlabel('Estimated Investment (Million $)')
            ax9.set_title('Investment Requirements by Company')

            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, top_companies['estimated_investment_musd'])):
                ax9.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                        f'${value:.0f}M', ha='left', va='center', fontsize=8)

        plt.suptitle('Enhanced Multi-Level Korean Petrochemical MACC Analysis\nwith Age-Based Retirement Prioritization',
                    fontsize=20, fontweight='bold', y=0.98)

        # Save visualization
        output_path = Path("../outputs/enhanced_multilevel_macc_analysis.png")
        output_path.parent.mkdir(exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved comprehensive visualization to: {output_path}")

        plt.show()

    def export_multilevel_results(self):
        """Export all multi-level results"""
        print("\n💾 Exporting multi-level results...")

        output_dir = Path("../outputs")
        output_dir.mkdir(exist_ok=True)

        # Export facility-level results
        if self.facility_results is not None:
            facility_path = output_dir / "facility_level_analysis_with_age.csv"
            self.facility_results.to_csv(facility_path, index=False)
            print(f"   Facility results: {facility_path}")

        # Export company-level results
        if self.company_results is not None:
            company_path = output_dir / "company_level_analysis_with_age.csv"
            self.company_results.to_csv(company_path, index=True)
            print(f"   Company results: {company_path}")

        # Export region-level results
        if self.region_results is not None:
            region_path = output_dir / "region_level_analysis_with_age.csv"
            self.region_results.to_csv(region_path, index=True)
            print(f"   Region results: {region_path}")

        # Export retirement optimization
        retirement_results = self.create_retirement_optimization_model(0.5)  # 50% reduction
        retirement_path = output_dir / "retirement_prioritized_deployment.csv"
        retirement_results.to_csv(retirement_path, index=False)
        print(f"   Retirement optimization: {retirement_path}")

        print("✅ Multi-level export complete!")

    def run_complete_enhanced_analysis(self):
        """Run complete enhanced multi-level MACC analysis"""
        print("🚀 ENHANCED MULTI-LEVEL KOREAN PETROCHEMICAL MACC ANALYSIS")
        print("=" * 80)
        print("📅 Current Year: 2025")
        print("⚙️  Key Features: Age-based retirement, depreciation, multi-level analysis")
        print()

        # Step 1: Facility-level analysis
        facility_results = self.calculate_facility_level_analysis()

        # Step 2: Company-level aggregation
        company_results = self.calculate_company_level_analysis()

        # Step 3: Region-level aggregation
        region_results = self.calculate_region_level_analysis()

        # Step 4: Retirement optimization
        retirement_results = self.create_retirement_optimization_model(0.3)

        # Step 5: Comprehensive visualization
        self.create_comprehensive_visualization()

        # Step 6: Export results
        self.export_multilevel_results()

        # Summary
        print(f"\n✅ ENHANCED ANALYSIS COMPLETE")
        print(f"🎯 Key Results:")
        print(f"   - Total Facilities: {len(facility_results)}")
        print(f"   - Companies: {len(company_results)}")
        print(f"   - Regions: {len(region_results)}")
        print(f"   - Total Emissions: {facility_results['emissions_tco2'].sum():,.0f} tCO2/year")
        print(f"   - Average Facility Age: {facility_results['age_years'].mean():.1f} years")
        print(f"   - Facilities Near Retirement: {len(facility_results[facility_results['retirement_priority'] > 0.7])}")

        return {
            'facility_results': facility_results,
            'company_results': company_results,
            'region_results': region_results,
            'retirement_optimization': retirement_results
        }

def main():
    """Main execution function"""
    excel_path = "../data/Korean_Petrochemical_MACC_Model_Corrected_with_Naphtha.xlsx"

    try:
        # Initialize enhanced model
        model = EnhancedMultiLevelMACCModel(excel_path)

        # Run complete analysis
        results = model.run_complete_enhanced_analysis()

        print(f"\n🎉 SUCCESS! Enhanced multi-level MACC analysis complete with:")
        print(f"   ✅ Facility-level analysis with age and depreciation")
        print(f"   ✅ Company-level strategic aggregation")
        print(f"   ✅ Region-level policy analysis")
        print(f"   ✅ Age-based retirement prioritization")
        print(f"   ✅ Multi-level visualizations")
        print(f"   ✅ Comprehensive result exports")

    except Exception as e:
        print(f"❌ Error in enhanced analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()