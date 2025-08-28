#!/usr/bin/env python3
"""
Update Excel database with corrected technology definitions
"""

import pandas as pd
import numpy as np

def create_corrected_database():
    """Create corrected petrochemical MACC database with band-based structure"""
    
    # Baseline fuel and feedstock consumption data (2023 BAU structure)
    baseline_consumption_data = {
        'TechGroup': ['NCC'] * 3 + ['BTX'] * 3 + ['C4'] * 3,
        'Band': ['HT', 'MT', 'LT'] * 3,
        'TechKey': [
            'NCC_HT', 'NCC_MT', 'NCC_LT',  # Naphtha Cracking Complex
            'BTX_HT', 'BTX_MT', 'BTX_LT',  # BTX (Benzene, Toluene, Xylene)
            'C4_HT', 'C4_MT', 'C4_LT'     # C4 chemicals
        ],
        'Process_Description': [
            'Pyrolysis furnace (800°C+)', 'Distillation/reboilers (150-400°C)', 'Compression/refrigeration',
            'Catalytic reforming furnace', 'Separation columns', 'Product compression',
            'Butadiene extraction', 'C4 fractionation', 'Product cooling'
        ],
        'Activity_kt_product': [
            3500, 2800, 1200,  # NCC bands
            1200, 800, 1100,   # BTX bands  
            450, 350, 200      # C4 bands
        ],
        # Fuel consumption (GJ/t product)
        'NaturalGas_GJ_per_t': [
            22.0, 8.5, 2.1,    # NCC: HT high gas use, MT medium, LT low
            11.2, 5.8, 1.9,    # BTX: reforming gas consumption
            16.8, 7.2, 2.4     # C4: extraction heating
        ],
        'FuelOil_GJ_per_t': [
            4.5, 2.1, 0.0,     # NCC: some fuel oil in HT/MT, none in LT
            2.8, 1.5, 0.0,     # BTX: fuel oil backup
            3.2, 1.8, 0.0      # C4: fuel oil heating
        ],
        'Electricity_GJ_per_t': [
            2.0, 1.7, 6.6,     # NCC: LT is electricity-intensive (compression)
            1.2, 1.6, 4.5,     # BTX: LT compression
            2.1, 0.8, 4.8      # C4: LT cooling
        ],
        # Feedstock consumption (t feedstock/t product)
        'Naphtha_t_per_t': [
            1.45, 1.42, 1.38,  # NCC: cracking efficiency improves HT→LT
            0.0, 0.0, 0.0,     # BTX: no direct naphtha
            0.0, 0.0, 0.0      # C4: no direct naphtha
        ],
        'LPG_t_per_t': [
            0.0, 0.0, 0.0,     # NCC: no LPG feedstock
            0.0, 0.0, 0.0,     # BTX: no LPG feedstock  
            0.85, 0.82, 0.78   # C4: LPG cracking efficiency improves
        ],
        'Reformate_t_per_t': [
            0.0, 0.0, 0.0,     # NCC: no reformate
            1.25, 1.22, 1.18,  # BTX: reformate processing efficiency
            0.0, 0.0, 0.0      # C4: no reformate
        ]
    }
    
    # Time-varying emission factors (2023-2050)
    years = list(range(2023, 2051))
    emission_factors_timeseries = []
    
    for year in years:
        # Electricity emission factor declines due to renewable energy deployment
        # Korea targets: 2030: 30% renewable, 2040: 60%, 2050: 80%
        if year <= 2030:
            elec_ef = 0.1389 - (year - 2023) * (0.1389 - 0.090) / (2030 - 2023)  # Linear decline to 0.090
        elif year <= 2040:
            elec_ef = 0.090 - (year - 2030) * (0.090 - 0.045) / (2040 - 2030)     # Decline to 0.045
        else:
            elec_ef = 0.045 - (year - 2040) * (0.045 - 0.020) / (2050 - 2040)     # Decline to 0.020 by 2050
        
        # Green hydrogen (zero emissions) used throughout
        green_h2_ef = 0.0
        
        # Fossil fuel emission factors remain constant
        emission_factors_timeseries.append({
            'Year': year,
            'Natural_Gas_tCO2_per_GJ': 0.0561,
            'Fuel_Oil_tCO2_per_GJ': 0.0774,
            'Electricity_tCO2_per_GJ': elec_ef,
            'Green_Hydrogen_tCO2_per_GJ': green_h2_ef,
            'Naphtha_tCO2_per_t': 0.73,
            'LPG_tCO2_per_t': 0.68,
            'Reformate_tCO2_per_t': 0.71
        })
    
    # Time-varying fuel costs (2023-2050, USD)
    fuel_costs_timeseries = []
    
    for year in years:
        # Green hydrogen cost decline based on IEA projections
        if year <= 2030:
            green_h2_cost = 6.5 - (year - 2023) * (6.5 - 4.2) / (2030 - 2023)    # $6.5/kg to $4.2/kg by 2030
        elif year <= 2040:
            green_h2_cost = 4.2 - (year - 2030) * (4.2 - 2.8) / (2040 - 2030)    # $4.2/kg to $2.8/kg by 2040
        else:
            green_h2_cost = 2.8 - (year - 2040) * (2.8 - 2.0) / (2050 - 2040)    # $2.8/kg to $2.0/kg by 2050
        
        # Electricity cost decline due to renewables (USD/MWh)
        if year <= 2030:
            elec_cost = 118 - (year - 2023) * (118 - 95) / (2030 - 2023)          # $118 to $95/MWh by 2030
        elif year <= 2040:
            elec_cost = 95 - (year - 2030) * (95 - 75) / (2040 - 2030)            # $95 to $75/MWh by 2040
        else:
            elec_cost = 75 - (year - 2040) * (75 - 60) / (2050 - 2040)            # $75 to $60/MWh by 2050
        
        # Convert H2 cost from $/kg to $/GJ (1 kg H2 = 120 MJ = 0.12 GJ)
        green_h2_cost_per_gj = green_h2_cost / 0.12
        
        # Convert electricity cost from $/MWh to $/GJ (1 MWh = 3.6 GJ)
        elec_cost_per_gj = elec_cost / 3.6
        
        # Fossil fuel costs with moderate inflation
        inflation_factor = 1.02 ** (year - 2023)  # 2% annual inflation
        
        fuel_costs_timeseries.append({
            'Year': year,
            'Natural_Gas_USD_per_GJ': 12.5 * inflation_factor,
            'Fuel_Oil_USD_per_GJ': 16.8 * inflation_factor,
            'Electricity_USD_per_GJ': elec_cost_per_gj,
            'Green_Hydrogen_USD_per_GJ': green_h2_cost_per_gj,
            'Naphtha_USD_per_t': 650 * inflation_factor,
            'LPG_USD_per_t': 580 * inflation_factor,
            'Reformate_USD_per_t': 620 * inflation_factor
        })
    
    # Static emission factors for 2023 baseline (for backward compatibility)
    emission_factors_static = {
        'Fuel_Feedstock': ['Natural_Gas', 'Fuel_Oil', 'Electricity', 'Green_Hydrogen', 'Naphtha', 'LPG', 'Reformate'],
        'EmissionFactor_tCO2_per_GJ': [0.0561, 0.0774, 0.1389, 0.0, 0.0, 0.0, 0.0],  # Green H2: zero emissions
        'EmissionFactor_tCO2_per_t': [0.0, 0.0, 0.0, 0.0, 0.73, 0.68, 0.71],  # Feedstock combustion factors
        'Description': [
            'Natural gas combustion', 
            'Heavy fuel oil combustion',
            'Korean electricity grid (2023 baseline)',
            'Green hydrogen from renewable electrolysis',
            'Naphtha feedstock carbon content',
            'LPG feedstock carbon content', 
            'Reformate feedstock carbon content'
        ]
    }
    
    # Alternative technologies with fuel/feedstock consumption profiles
    alternatives_data = {
        'TechID': [
            # NCC HT band alternatives (Pyrolysis furnace)
            'NCC_HT_Electric', 'NCC_HT_Hydrogen', 
            # NCC MT band alternatives (Distillation/reboilers)  
            'NCC_MT_HeatPump', 'NCC_MT_ElecHeater',
            # NCC LT band alternatives (Compression)
            'NCC_LT_HeatPump', 'NCC_LT_ElecCompr',
            
            # BTX HT band alternatives (Reforming furnace)
            'BTX_HT_Electric', 'BTX_HT_Hydrogen',
            # BTX MT band alternatives (Separation columns)
            'BTX_MT_HeatPump', 'BTX_MT_ElecHeater', 
            # BTX LT band alternatives (Product compression)
            'BTX_LT_HeatPump', 'BTX_LT_ElecCompr',
            
            # C4 HT band alternatives (Extraction)
            'C4_HT_Electric', 'C4_HT_Hydrogen',
            # C4 MT band alternatives (Fractionation)
            'C4_MT_HeatPump', 'C4_MT_ElecHeater',
            # C4 LT band alternatives (Product cooling)
            'C4_LT_HeatPump', 'C4_LT_ElecCompr'
        ],
        'TechGroup': [
            'NCC', 'NCC', 'NCC', 'NCC', 'NCC', 'NCC',
            'BTX', 'BTX', 'BTX', 'BTX', 'BTX', 'BTX', 
            'C4', 'C4', 'C4', 'C4', 'C4', 'C4'
        ],
        'Band': [
            'HT', 'HT', 'MT', 'MT', 'LT', 'LT',  # NCC bands
            'HT', 'HT', 'MT', 'MT', 'LT', 'LT',  # BTX bands
            'HT', 'HT', 'MT', 'MT', 'LT', 'LT'   # C4 bands
        ],
        'TechnologyCategory': [
            'E-cracker', 'H2-furnace', 'Heat pump', 'Electric heater', 'Heat pump', 'Electric motor',
            'Electric furnace', 'H2-reformer', 'Heat pump', 'Electric heater', 'Heat pump', 'Electric motor',
            'Electric extraction', 'H2-process', 'Heat pump', 'Electric heater', 'Heat pump', 'Electric motor'
        ],
        # New fuel consumption profiles (GJ/t product)
        'NaturalGas_GJ_per_t': [
            # NCC alternatives: E-cracker eliminates gas, H2 reduces gas
            0.0, 12.0, 3.5, 5.0, 1.8, 1.8,  # NCC: E-cracker=0, H2-furnace reduced
            0.0, 8.5, 2.8, 3.2, 1.5, 1.5,   # BTX: Electric furnace=0
            0.0, 10.2, 3.6, 4.1, 2.0, 2.0   # C4: Electric extraction=0
        ],
        'FuelOil_GJ_per_t': [
            # Most alternatives eliminate fuel oil
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,    # NCC: all alternatives eliminate fuel oil
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,    # BTX: all alternatives eliminate fuel oil
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0     # C4: all alternatives eliminate fuel oil
        ],
        'Electricity_GJ_per_t': [
            # Alternative technologies increase electricity consumption
            28.0, 3.2, 6.5, 12.0, 9.2, 8.8,  # NCC: E-cracker very high electricity
            18.5, 2.8, 4.2, 8.5, 6.8, 6.2,  # BTX: Electric furnace high electricity
            22.0, 3.5, 5.8, 9.2, 7.5, 7.0   # C4: Electric extraction high electricity
        ],
        # Feedstock consumption (same as baseline - no change in feedstock efficiency)
        'Naphtha_t_per_t': [
            1.45, 1.45, 1.42, 1.42, 1.38, 1.38,  # NCC: same as baseline
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,        # BTX: no naphtha
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0         # C4: no naphtha
        ],
        'LPG_t_per_t': [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,        # NCC: no LPG
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,        # BTX: no LPG
            0.85, 0.85, 0.82, 0.82, 0.78, 0.78   # C4: same as baseline
        ],
        'Reformate_t_per_t': [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,        # NCC: no reformate
            1.25, 1.25, 1.22, 1.22, 1.18, 1.18, # BTX: same as baseline
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0         # C4: no reformate
        ],
        # Hydrogen consumption (GJ/t product) - only for H2-based technologies
        'Hydrogen_GJ_per_t': [
            0.0, 18.5, 0.0, 0.0, 0.0, 0.0,      # NCC: H2-furnace consumes H2
            0.0, 15.2, 0.0, 0.0, 0.0, 0.0,      # BTX: H2-reformer consumes H2
            0.0, 16.8, 0.0, 0.0, 0.0, 0.0       # C4: H2-process consumes H2
        ],
        'CommercialYear': [
            2028, 2030, 2026, 2025, 2024, 2023,  # NCC: E-cracker 2028, heat pumps earlier
            2030, 2032, 2026, 2025, 2024, 2023,  # BTX: Similar but later for HT
            2032, 2035, 2027, 2026, 2024, 2023   # C4: Later for novel processes
        ],
        'TechnicalReadiness': [
            6, 5, 8, 9, 9, 9,  # NCC: Electric/H2 lower TRL, heat pumps mature
            5, 4, 8, 9, 9, 9,  # BTX: HT alternatives less mature
            4, 3, 7, 8, 9, 9   # C4: Novel processes lowest TRL
        ],
        'Lifetime_years': [25] * 18,  # Standard industrial equipment lifetime
        'RampRate_per_year': [
            0.15, 0.12, 0.20, 0.25, 0.30, 0.35,  # NCC: Mature techs faster
            0.12, 0.10, 0.20, 0.25, 0.30, 0.35,  # BTX
            0.10, 0.08, 0.18, 0.22, 0.28, 0.33   # C4
        ]
    }
    
    # Alternative technology costs - Band-specific
    alt_costs_data = {
        'TechID': alternatives_data['TechID'],
        'CAPEX_Million_USD_per_kt_capacity': [
            # NCC costs: HT (high), MT (medium), LT (lower)
            280, 320,  # NCC HT: E-cracker, H2-furnace (very high for novel tech)
            80, 60,    # NCC MT: Heat pump, Electric heater (mature tech)
            45, 35,    # NCC LT: Heat pump, Electric motor (standard equipment)
            
            # BTX costs: Similar pattern but lower scale
            220, 260,  # BTX HT: Electric furnace, H2-reformer  
            70, 55,    # BTX MT: Heat pump, Electric heater
            40, 32,    # BTX LT: Heat pump, Electric motor
            
            # C4 costs: Specialized processes
            350, 380,  # C4 HT: Electric extraction, H2-process (novel)
            85, 65,    # C4 MT: Heat pump, Electric heater
            50, 38     # C4 LT: Heat pump, Electric motor
        ],
        'OPEX_Delta_USD_per_t': [
            # Operating cost changes vs baseline (negative = savings)
            # NCC: HT high energy costs, MT/LT often savings
            25, -15,   # NCC HT: Electric premium, H2 fuel savings
            -20, 10,   # NCC MT: Heat pump efficiency savings, electric cost
            -25, -30,  # NCC LT: Efficiency improvements
            
            # BTX: Similar pattern
            30, -10,   # BTX HT: Electric cost, H2 savings  
            -18, 8,    # BTX MT: Heat pump savings
            -22, -28,  # BTX LT: Motor efficiency
            
            # C4: Higher premiums for novel processes
            40, -5,    # C4 HT: Novel process premium, some H2 savings
            -15, 12,   # C4 MT: Heat pump benefits
            -20, -25   # C4 LT: Standard efficiency gains
        ],
        'MaintenanceCost_Pct': [
            # Maintenance costs by technology maturity
            0.035, 0.040,  # NCC HT: Higher for novel tech
            0.025, 0.022,  # NCC MT: Standard for mature tech
            0.020, 0.018,  # NCC LT: Lower for simple equipment
            
            0.038, 0.042,  # BTX HT: Novel processes
            0.025, 0.022,  # BTX MT: Standard
            0.020, 0.018,  # BTX LT: Simple
            
            0.045, 0.050,  # C4 HT: Highest for experimental
            0.028, 0.025,  # C4 MT: Standard  
            0.022, 0.020   # C4 LT: Standard motors
        ]
    }
    
    # Regional Facilities data (detailed facility-level information)
    regional_facilities_data = {
        'FacilityID': [
            # Yeosu facilities (largest region)
            'Yeosu_LG_Chem', 'Yeosu_GS_Caltex', 'Yeosu_Lotte_Chemical', 'Yeosu_Hanwha_Chemical',
            # Daesan facilities (second largest)  
            'Daesan_HD_Hyundai', 'Daesan_LG_Chem',
            # Ulsan facilities (smallest)
            'Ulsan_KPIC', 'Ulsan_SK_Innovation'
        ],
        'Region': [
            'Yeosu', 'Yeosu', 'Yeosu', 'Yeosu',
            'Daesan', 'Daesan', 
            'Ulsan', 'Ulsan'
        ],
        'Company': [
            'LG Chem', 'GS Caltex', 'Lotte Chemical', 'Hanwha Chemical',
            'HD Hyundai Chemical', 'LG Chem',
            'Korea Petrochemical Ind. Co.', 'SK Innovation'
        ],
        'NCC_Capacity_kt_per_year': [
            3380, 900, 1000, 850,  # Yeosu: LG Chem largest
            850, 600,              # Daesan
            900, 500               # Ulsan
        ],
        'BTX_Capacity_kt_per_year': [
            800, 600, 700, 400,    # Yeosu
            500, 300,              # Daesan  
            400, 300               # Ulsan
        ],
        'C4_Capacity_kt_per_year': [
            300, 200, 250, 150,    # Yeosu
            200, 100,              # Daesan
            150, 100               # Ulsan
        ],
        'Propylene_Capacity_kt_per_year': [
            1980, 970, 800, 450,   # Yeosu: LG Chem largest
            451, 300,              # Daesan
            560, 250               # Ulsan
        ],
        'TechnicalReadiness_Level': [
            9, 8, 9, 8,             # Yeosu: mature facilities
            8, 9,                  # Daesan
            8, 7                   # Ulsan: KPIC mature, SK newer
        ],
        'Infrastructure_Score': [
            95, 90, 95, 85,         # Yeosu: excellent infrastructure
            90, 88,                # Daesan: good
            85, 80                 # Ulsan: good but smaller
        ],
        'Labor_Cost_Index': [
            100, 100, 100, 100,    # Yeosu: baseline
            95, 95,                # Daesan: slightly lower
            90, 90                 # Ulsan: lower labor costs
        ],
        'Electricity_Price_USD_per_MWh': [
            118, 118, 118, 118,    # Yeosu: standard rate
            115, 115,              # Daesan: slightly lower
            112, 112               # Ulsan: lower industrial rate
        ],
        'Hydrogen_Access_Score': [
            80, 75, 85, 70,        # Yeosu: good access planned
            85, 80,                # Daesan: good access
            70, 65                 # Ulsan: moderate access
        ],
        'Year_Established': [
            1991, 1967, 1976, 1986, # Yeosu
            1980, 1995,             # Daesan
            1972, 1995              # Ulsan
        ],
        'Environmental_Compliance': [
            'High', 'High', 'High', 'Medium',  # Yeosu
            'High', 'High',                    # Daesan
            'High', 'Medium'                   # Ulsan
        ]
    }

    
    # Calculate baseline emissions from fuel and feedstock consumption
    baseline_emissions = 0.0
    emission_factors = {
        'Natural_Gas': 0.0561,    # tCO2/GJ
        'Fuel_Oil': 0.0774,      # tCO2/GJ  
        'Electricity': 0.1389,   # tCO2/GJ
        'Naphtha': 0.73,         # tCO2/t feedstock
        'LPG': 0.68,             # tCO2/t feedstock
        'Reformate': 0.71        # tCO2/t feedstock
    }
    
    for i in range(len(baseline_consumption_data['TechKey'])):
        activity = baseline_consumption_data['Activity_kt_product'][i]
        
        # Fuel emissions
        ng_emissions = activity * baseline_consumption_data['NaturalGas_GJ_per_t'][i] * emission_factors['Natural_Gas'] / 1000
        oil_emissions = activity * baseline_consumption_data['FuelOil_GJ_per_t'][i] * emission_factors['Fuel_Oil'] / 1000
        elec_emissions = activity * baseline_consumption_data['Electricity_GJ_per_t'][i] * emission_factors['Electricity'] / 1000
        
        # Feedstock emissions
        naphtha_emissions = activity * baseline_consumption_data['Naphtha_t_per_t'][i] * emission_factors['Naphtha'] / 1000
        lpg_emissions = activity * baseline_consumption_data['LPG_t_per_t'][i] * emission_factors['LPG'] / 1000
        reformate_emissions = activity * baseline_consumption_data['Reformate_t_per_t'][i] * emission_factors['Reformate'] / 1000
        
        total_process_emissions = ng_emissions + oil_emissions + elec_emissions + naphtha_emissions + lpg_emissions + reformate_emissions
        baseline_emissions += total_process_emissions
    
    targets_data = {
        'Year': [2030, 2035, 2040, 2045, 2050],
        'Target_MtCO2': [
            baseline_emissions * 0.85,  # 15% reduction by 2030
            baseline_emissions * 0.70,  # 30% reduction by 2035
            baseline_emissions * 0.50,  # 50% reduction by 2040
            baseline_emissions * 0.30,  # 70% reduction by 2045
            baseline_emissions * 0.20   # 80% reduction by 2050
        ],
        'Pathway': ['Linear', 'Linear', 'Linear', 'Linear', 'Linear'],
        'Sector': ['Petrochemicals'] * 5
    }
    
    # Create Excel file with fuel/feedstock-based structure and time-varying parameters
    with pd.ExcelWriter('data/Korea_Petrochemical_MACC_Database.xlsx', engine='openpyxl') as writer:
        # Baseline fuel and feedstock consumption (2023 BAU structure)
        pd.DataFrame(baseline_consumption_data).to_excel(writer, sheet_name='BaselineConsumption_2023', index=False)
        
        # Static emission factors for 2023 baseline (for backward compatibility)
        pd.DataFrame(emission_factors_static).to_excel(writer, sheet_name='EmissionFactors', index=False)
        
        # Time-varying emission factors (2023-2050)
        pd.DataFrame(emission_factors_timeseries).to_excel(writer, sheet_name='EmissionFactors_TimeSeries', index=False)
        
        # Time-varying fuel costs (2023-2050)
        pd.DataFrame(fuel_costs_timeseries).to_excel(writer, sheet_name='FuelCosts_TimeSeries', index=False)
        
        # Alternative technologies with fuel/feedstock consumption profiles
        pd.DataFrame(alternatives_data).to_excel(writer, sheet_name='AlternativeTechnologies', index=False)
        
        # Technology costs
        pd.DataFrame(alt_costs_data).to_excel(writer, sheet_name='AlternativeCosts', index=False)
        
        # Regional facilities (detailed facility-level data)
        pd.DataFrame(regional_facilities_data).to_excel(writer, sheet_name='RegionalFacilities', index=False)
        
        # Emissions targets
        pd.DataFrame(targets_data).to_excel(writer, sheet_name='EmissionsTargets', index=False)
    
    print("✅ Updated Korea_Petrochemical_MACC_Database.xlsx")
    print(f"   - Baseline emissions: {baseline_emissions:.1f} MtCO2 (calculated from fuel/feedstock consumption)")
    print(f"   - Technology groups: NCC, BTX, C4")
    print(f"   - Emission calculation: Based on fuel and feedstock consumption × emission factors")
    print(f"   - Alternative technologies: {len(alternatives_data['TechID'])} with fuel/feedstock profiles")
    print(f"   - Commercialization years: {min(alternatives_data['CommercialYear'])}-{max(alternatives_data['CommercialYear'])}")
    print("   - Technology types: E-cracker, H2-furnace, Heat pump, Electric heater, Electric motor")
    print("   - MaxApplicability removed: No artificial capacity constraints")
    print("   - Fuel/feedstock consumption profiles for each technology")

if __name__ == "__main__":
    create_corrected_database()