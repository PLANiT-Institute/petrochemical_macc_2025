#!/usr/bin/env python3
"""
Update Excel database with corrected technology definitions
"""

import pandas as pd
import numpy as np

def create_corrected_database():
    """Create corrected petrochemical MACC database with band-based structure"""
    
    # Technology bands baseline data (2023 BAU structure)
    bands_data = {
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
        'SEC_GJ_per_t': [
            28.5, 12.3, 8.7,   # NCC: HT high energy, MT medium, LT low
            15.2, 8.9, 6.4,    # BTX: HT furnace energy
            22.1, 9.8, 7.2     # C4: extraction energy
        ],
        'EmissionIntensity_tCO2_per_t': [
            2.85, 1.23, 0.65,  # NCC emissions by band
            1.52, 0.89, 0.48,  # BTX emissions by band
            2.21, 0.98, 0.54   # C4 emissions by band
        ],
        'Primary_Energy_Source': [
            'Natural gas/fuel oil', 'Steam/fuel gas', 'Electricity',  # NCC
            'Natural gas', 'Steam', 'Electricity',                   # BTX
            'Fuel gas', 'Steam', 'Electricity'                       # C4
        ]
    }
    
    # Alternative technologies - Band-specific options (NO CCUS)
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
        'EmissionReduction_tCO2_per_t': [
            # NCC: HT(high reduction), MT(medium), LT(low but some reduction)
            2.0, 2.2, 0.8, 1.0, 0.4, 0.3,
            # BTX: Similar pattern but lower absolute values
            1.2, 1.3, 0.6, 0.7, 0.3, 0.2,
            # C4: Medium reduction potential
            1.8, 1.9, 0.7, 0.8, 0.3, 0.3
        ],
        'MaxApplicability': [
            # HT bands: 30-50% (major technology shift possible)
            0.4, 0.5, 0.6, 0.7, 0.8, 0.9,  # NCC: MT/LT higher applicability
            0.3, 0.4, 0.6, 0.7, 0.8, 0.9,  # BTX
            0.3, 0.4, 0.5, 0.6, 0.7, 0.8   # C4
        ],
        'CommercialYear': [
            # Realistic commercialization timeline by technology type
            2028, 2030, 2026, 2025, 2024, 2023,  # NCC: E-cracker 2028, heat pumps earlier
            2030, 2032, 2026, 2025, 2024, 2023,  # BTX: Similar but later for HT
            2032, 2035, 2027, 2026, 2024, 2023   # C4: Later for novel processes
        ],
        'TechnicalReadiness': [
            # TRL by technology maturity
            6, 5, 8, 9, 9, 9,  # NCC: Electric/H2 lower TRL, heat pumps mature
            5, 4, 8, 9, 9, 9,  # BTX: HT alternatives less mature
            4, 3, 7, 8, 9, 9   # C4: Novel processes lowest TRL
        ],
        'Lifetime_years': [25] * 18,  # Standard industrial equipment lifetime
        'RampRate_per_year': [
            # Ramp rates based on technology maturity and scale
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
    
    # Regional constraints (Korea specific) - by Tech Group
    regional_data = {
        'Region': ['Korea'] * 3,
        'TechGroup': ['NCC', 'BTX', 'C4'],
        'ElectricityPrice_USD_per_MWh': [118, 118, 118],  # Korea industrial rate
        'HydrogenPrice_USD_per_kg': [5.2, 5.2, 5.2],     # Current Korea H2 price
        'NaturalGasPrice_USD_per_GJ': [12.5, 12.5, 12.5], # Korea NG price
        'CarbonPrice_USD_per_tCO2': [28, 28, 28],         # Korea K-ETS price
        'RegulatorySupport': ['High', 'Medium', 'Medium'], # NCC gets most support
        'InfrastructureReadiness': ['High', 'High', 'Medium']  # NCC/BTX mature, C4 developing
    }
    
    # Market constraints - by Tech Group
    market_data = {
        'TechGroup': ['NCC', 'BTX', 'C4'],
        'DemandGrowth_pct_per_year': [2.0, 1.5, 1.2],     # NCC highest growth
        'ProductPrice_USD_per_t': [1150, 975, 1600],      # Average prices
        'MarketVolatility': ['High', 'Medium', 'Very High'], # C4 most volatile
        'ImportDependency_pct': [20, 19, 35],             # C4 highest import dependency
        'CapacityUtilization_pct': [88, 85, 82]           # Current utilization rates
    }
    
    # Policy framework
    policy_data = {
        'Year': [2025, 2030, 2035, 2040, 2045, 2050],
        'CarbonPrice_USD_per_tCO2': [30, 50, 80, 120, 150, 200],
        'RenewableTarget_pct': [20, 30, 50, 70, 85, 100],
        'HydrogenInfrastructure': ['Limited', 'Developing', 'Moderate', 'Good', 'Extensive', 'Complete'],
        'TechSupport_Level': ['Medium', 'High', 'High', 'Medium', 'Medium', 'Low']
    }
    
    # Calculate baseline emissions from bands
    baseline_emissions = sum(bands_data['Activity_kt_product'][i] * bands_data['EmissionIntensity_tCO2_per_t'][i] 
                           for i in range(len(bands_data['TechKey']))) / 1000  # Convert to Mt
    
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
    
    # Create Excel file with corrected band-based structure
    with pd.ExcelWriter('data/Korea_Petrochemical_MACC_Database.xlsx', engine='openpyxl') as writer:
        # Technology bands baseline (2023 BAU structure)
        pd.DataFrame(bands_data).to_excel(writer, sheet_name='TechBands_2023', index=False)
        
        # Alternative technologies (band-specific, NO CCUS, NO transitions between bands)
        pd.DataFrame(alternatives_data).to_excel(writer, sheet_name='AlternativeTechnologies', index=False)
        
        # Technology costs
        pd.DataFrame(alt_costs_data).to_excel(writer, sheet_name='AlternativeCosts', index=False)
        
        # Regional constraints
        pd.DataFrame(regional_data).to_excel(writer, sheet_name='RegionalConstraints', index=False)
        
        # Market constraints  
        pd.DataFrame(market_data).to_excel(writer, sheet_name='MarketConstraints', index=False)
        
        # Policy framework
        pd.DataFrame(policy_data).to_excel(writer, sheet_name='PolicyFramework', index=False)
        
        # Emissions targets
        pd.DataFrame(targets_data).to_excel(writer, sheet_name='EmissionsTargets', index=False)
    
    print("✅ Updated Korea_Petrochemical_MACC_Database.xlsx")
    print(f"   - Baseline emissions: {baseline_emissions:.1f} MtCO2")
    print(f"   - Technology groups: NCC, BTX, C4")
    print(f"   - Bands per group: HT (high temp), MT (medium temp), LT (low temp)")
    print(f"   - Alternative technologies: {len(alternatives_data['TechID'])} (NO CCUS, NO band transitions)")
    print(f"   - Commercialization years: {min(alternatives_data['CommercialYear'])}-{max(alternatives_data['CommercialYear'])}")
    print("   - Technology types: E-cracker, H2-furnace, Heat pump, Electric heater, Electric motor")
    print("   - Band-specific alternatives only (no HT→MT→LT transitions)")
    print("   - Fixed Activity × SEC structure per band")

if __name__ == "__main__":
    create_corrected_database()