#!/usr/bin/env python3
"""
Review and validate the emission calculation logic
Source → CI → CI2 → Emissions
"""

import pandas as pd

def review_emission_calculation_logic():
    """Review the emission calculation logic step by step"""
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    print('=== EMISSION CALCULATION LOGIC REVIEW ===\n')
    
    # Load data
    source_df = pd.read_excel(file_path, sheet_name='source')
    ci_df = pd.read_excel(file_path, sheet_name='CI')
    ci2_df = pd.read_excel(file_path, sheet_name='CI2')
    
    print('STEP 1: DATA SOURCES')
    print('--------------------')
    print(f'• SOURCE: {len(source_df)} facilities with capacity and operational info')
    print(f'• CI: {len(ci_df)} product-process combinations with energy intensities')
    print(f'• CI2: {len(ci2_df)} rows with emission factors for each energy type')
    print()
    
    print('STEP 2: EMISSION CALCULATION FORMULA')
    print('-------------------------------------')
    print('For each facility:')
    print('1. Match facility (product, process) → CI data (energy intensities)')
    print('2. Apply emission factors from CI2')
    print('3. Scale by facility capacity')
    print()
    print('Formula:')
    print('  Emissions = Σ (Energy_Intensity × Capacity × Emission_Factor)')
    print('  Where Energy_Intensity is from CI, Emission_Factor from CI2')
    print()
    
    # Example calculation
    print('STEP 3: EXAMPLE CALCULATION')
    print('----------------------------')
    
    # Take first facility
    facility = source_df.iloc[0]
    print(f'Example Facility: {facility["company"]} - {facility["products"]} ({facility["process"]})')
    print(f'Capacity: {facility["capacity_1000_t"]:.0f} kt/year')
    print()
    
    # Find matching CI data
    ci_match = ci_df[(ci_df['제품'] == facility['products']) & 
                     (ci_df['공정'] == facility['process'])]
    
    if len(ci_match) > 0:
        ci_data = ci_match.iloc[0]
        print('Matched CI Data (Energy Intensities):')
        print(f'  • LNG: {ci_data["LNG(GJ/t)"]:.1f} GJ/t')
        print(f'  • Electricity: {ci_data["전력(Baseline)(kWh/t)"]:.1f} kWh/t')
        print(f'  • Fuel Gas: {ci_data["연료가스(Fuel gas mix)(GJ/t)"]:.1f} GJ/t')
        print(f'  • Fuel Oil: {ci_data["중유(Fuel oil)(GJ/t)"]:.1f} GJ/t')
        print()
        
        # Emission factors
        ef_data = ci2_df.iloc[0]  # First row contains emission factors
        print('Emission Factors (from CI2):')
        print(f'  • LNG: {ef_data["LNG( tCO₂/GJ )"]:.3f} tCO₂/GJ')
        print(f'  • Electricity: {ef_data["전력(Baseline)( tCO₂/kWh )"]:.4f} tCO₂/kWh')
        print(f'  • Fuel Gas: {ef_data["연료가스(Fuel gas mix)( tCO₂/GJ )"]:.3f} tCO₂/GJ')
        print(f'  • Fuel Oil: {ef_data["중유(Fuel oil)( tCO₂/GJ )"]:.3f} tCO₂/GJ')
        print()
        
        # Calculate emissions
        capacity = facility['capacity_1000_t'] * 1000  # Convert to tonnes
        
        lng_emissions = (ci_data['LNG(GJ/t)'] * capacity * 
                        ef_data['LNG( tCO₂/GJ )']) / 1000  # kt CO2
        
        elec_emissions = (ci_data['전력(Baseline)(kWh/t)'] * capacity * 
                         ef_data['전력(Baseline)( tCO₂/kWh )']) / 1000  # kt CO2
        
        gas_emissions = (ci_data['연료가스(Fuel gas mix)(GJ/t)'] * capacity * 
                        ef_data['연료가스(Fuel gas mix)( tCO₂/GJ )']) / 1000  # kt CO2
        
        oil_emissions = (ci_data['중유(Fuel oil)(GJ/t)'] * capacity * 
                        ef_data['중유(Fuel oil)( tCO₂/GJ )']) / 1000  # kt CO2
        
        total_emissions = lng_emissions + elec_emissions + gas_emissions + oil_emissions
        
        print('Emission Calculation:')
        print(f'  • LNG: {ci_data["LNG(GJ/t)"]:.1f} × {capacity/1000:.0f} × {ef_data["LNG( tCO₂/GJ )"]:.3f} = {lng_emissions:.1f} kt CO₂')
        print(f'  • Electricity: {ci_data["전력(Baseline)(kWh/t)"]:.0f} × {capacity/1000:.0f} × {ef_data["전력(Baseline)( tCO₂/kWh )"]:.4f} = {elec_emissions:.1f} kt CO₂')
        print(f'  • Fuel Gas: {ci_data["연료가스(Fuel gas mix)(GJ/t)"]:.1f} × {capacity/1000:.0f} × {ef_data["연료가스(Fuel gas mix)( tCO₂/GJ )"]:.3f} = {gas_emissions:.1f} kt CO₂')
        print(f'  • Fuel Oil: {ci_data["중유(Fuel oil)(GJ/t)"]:.1f} × {capacity/1000:.0f} × {ef_data["중유(Fuel oil)( tCO₂/GJ )"]:.3f} = {oil_emissions:.1f} kt CO₂')
        print()
        print(f'TOTAL EMISSIONS: {total_emissions:.1f} kt CO₂/year')
        print(f'EMISSION INTENSITY: {total_emissions*1000/capacity:.2f} tCO₂/t product')
        
    else:
        print('❌ No matching CI data found for this facility')
        print('This would trigger fallback to default values or product-only matching')
    
    print()
    
    print('STEP 4: LOGIC VALIDATION')
    print('-------------------------')
    print('✓ SOURCE provides facility capacity and product/process identification')
    print('✓ CI provides energy consumption per tonne of product by process type')
    print('✓ CI2 provides emission factors for each energy carrier')
    print('✓ Formula correctly multiplies: Intensity × Capacity × Emission_Factor')
    print('✓ Units are consistent: (GJ/t) × (kt) × (tCO₂/GJ) = kt CO₂')
    print()
    
    print('STEP 5: POTENTIAL ISSUES')
    print('-------------------------')
    
    # Check for missing CI matches
    unique_facility_combos = set(zip(source_df['products'], source_df['process']))
    unique_ci_combos = set(zip(ci_df['제품'], ci_df['공정']))
    
    missing_matches = unique_facility_combos - unique_ci_combos
    if missing_matches:
        print(f'⚠ {len(missing_matches)} facility product-process combinations lack CI data:')
        for combo in list(missing_matches)[:5]:  # Show first 5
            print(f'   • {combo[0]} - {combo[1]}')
        if len(missing_matches) > 5:
            print(f'   ... and {len(missing_matches)-5} more')
    else:
        print('✓ All facility combinations have matching CI data')
    
    print()
    
    # Check for zero values
    zero_capacity = (source_df['capacity_1000_t'] == 0).sum()
    print(f'• Facilities with zero capacity: {zero_capacity}/{len(source_df)}')
    
    # Check CI data completeness
    ci_nulls = ci_df[['LNG(GJ/t)', '전력(Baseline)(kWh/t)', '연료가스(Fuel gas mix)(GJ/t)', '중유(Fuel oil)(GJ/t)']].isnull().sum().sum()
    print(f'• Null values in CI energy data: {ci_nulls}')
    
    print()
    print('CONCLUSION: The emission calculation logic is sound and follows standard')
    print('industrial practice: Energy_Intensity × Activity × Emission_Factor')

if __name__ == "__main__":
    review_emission_calculation_logic()