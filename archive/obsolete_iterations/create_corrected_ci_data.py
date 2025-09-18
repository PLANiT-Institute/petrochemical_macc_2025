#!/usr/bin/env python3
"""
Create corrected CI and CI2 data for realistic Korean petrochemical emissions
Target: ~50 Mt CO₂ total emissions
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook

def create_corrected_ci_data():
    """Create corrected carbon intensity data"""
    
    # Load original data
    original_file = "data/petro_data_v1.0.xlsx"
    ci_df = pd.read_excel(original_file, sheet_name='CI')
    ci2_df = pd.read_excel(original_file, sheet_name='CI2')
    
    print("Creating corrected CI data...")
    
    # Create corrected CI data with realistic energy intensities
    # Key principle: Only count primary process energy, avoid double counting
    
    corrected_ci = ci_df.copy()
    
    # PRIMARY PROCESSES - Include full energy requirements
    primary_corrections = {
        # Steam Crackers - Major energy consumers
        ('Ethylene', 'Naphtha Cracker'): {
            'LNG(GJ/t)': 28.0,  # Cracker furnace energy
            '연료가스(Fuel gas mix)(GJ/t)': 4.0,  # Additional process heating
            '전력(Baseline)(kWh/t)': 600,  # Compressors, cooling, etc.
        },
        ('Propylene', 'Naphtha Cracker'): {
            'LNG(GJ/t)': 25.0,  # Shared cracker energy (allocated)
            '연료가스(Fuel gas mix)(GJ/t)': 3.5,
            '전력(Baseline)(kWh/t)': 550,
        },
        ('Butadiene', 'Naphtha Cracker'): {
            'LNG(GJ/t)': 15.0,  # Extraction and purification
            '연료가스(Fuel gas mix)(GJ/t)': 9.0,  # Keep existing
            '전력(Baseline)(kWh/t)': 400,
        },
        
        # BTX Plant - Reforming and separation
        ('벤젠', 'BTX Plant'): {
            'LNG(GJ/t)': 12.0,  # Reformer and separation energy
            '연료가스(Fuel gas mix)(GJ/t)': 8.0,
            '전력(Baseline)(kWh/t)': 450,
        },
        ('톨루엔', 'BTX Plant'): {
            'LNG(GJ/t)': 10.0,
            '연료가스(Fuel gas mix)(GJ/t)': 7.0,
            '전력(Baseline)(kWh/t)': 350,
        },
        ('자일렌', 'BTX Plant'): {
            'LNG(GJ/t)': 11.0,
            '연료가스(Fuel gas mix)(GJ/t)': 6.0,
            '전력(Baseline)(kWh/t)': 400,
        },
    }
    
    # DOWNSTREAM PROCESSES - Lower energy (avoid double counting)
    # These get feedstock from primary processes, so only incremental energy
    downstream_corrections = {
        # Aromatics derivatives
        ('P-X', 'Utility'): {
            'LNG(GJ/t)': 8.0,  # p-Xylene separation energy
            '전력(Baseline)(kWh/t)': 350,
        },
        ('O-X', 'Utility'): {
            'LNG(GJ/t)': 6.0,
            '전력(Baseline)(kWh/t)': 280,
        },
        ('M-X', 'Utility'): {
            'LNG(GJ/t)': 6.0,
            '전력(Baseline)(kWh/t)': 280,
        },
        
        # Polymers - polymerization energy only
        ('LDPE', 'Utility'): {
            'LNG(GJ/t)': 2.5,  # Polymerization heating
            '전력(Baseline)(kWh/t)': 800,  # High pressure process
        },
        ('HDPE', 'Utility'): {
            'LNG(GJ/t)': 2.0,
            '전력(Baseline)(kWh/t)': 600,
        },
        ('L-LDPE', 'Utility'): {
            'LNG(GJ/t)': 2.2,
            '전력(Baseline)(kWh/t)': 700,
        },
        ('PP', 'Utility'): {
            'LNG(GJ/t)': 2.8,
            '전력(Baseline)(kWh/t)': 650,
        },
        ('PS', 'Utility'): {
            'LNG(GJ/t)': 3.2,
            '전력(Baseline)(kWh/t)': 550,
        },
        ('EPS', 'Utility'): {
            'LNG(GJ/t)': 3.5,
            '전력(Baseline)(kWh/t)': 600,
        },
        ('ABS', 'Utility'): {
            'LNG(GJ/t)': 4.0,
            '전력(Baseline)(kWh/t)': 700,
        },
        ('PVC', 'Utility'): {
            'LNG(GJ/t)': 1.8,
            '전력(Baseline)(kWh/t)': 500,
        },
        
        # Aromatics derivatives
        ('TPA', 'Utility'): {
            'LNG(GJ/t)': 7.5,  # Oxidation process
            '전력(Baseline)(kWh/t)': 400,
        },
        ('EG', 'Utility'): {
            'LNG(GJ/t)': 9.0,  # Hydrolysis
            '전력(Baseline)(kWh/t)': 350,
        },
        ('SM', 'Utility'): {
            'LNG(GJ/t)': 5.5,  # Dehydrogenation
            '전력(Baseline)(kWh/t)': 300,
        },
        
        # Rubber and specialties
        ('SBR', 'Utility'): {
            'LNG(GJ/t)': 3.8,
            '전력(Baseline)(kWh/t)': 650,
        },
        ('BR', 'Utility'): {
            'LNG(GJ/t)': 3.5,
            '전력(Baseline)(kWh/t)': 600,
        },
        ('NBR', 'Utility'): {
            'LNG(GJ/t)': 4.2,
            '전력(Baseline)(kWh/t)': 700,
        },
        
        # Chemicals
        ('EDC', 'Utility'): {
            'LNG(GJ/t)': 6.0,  # Oxychlorination
            '전력(Baseline)(kWh/t)': 300,
        },
        ('VCM', 'Utility'): {
            'LNG(GJ/t)': 4.5,  # Cracking
            '전력(Baseline)(kWh/t)': 250,
        },
        ('AN', 'Utility'): {
            'LNG(GJ/t)': 8.5,  # Ammoxidation
            '전력(Baseline)(kWh/t)': 400,
        },
    }
    
    # Apply corrections
    corrections = {**primary_corrections, **downstream_corrections}
    
    for _, row in corrected_ci.iterrows():
        product = row['제품']
        process = row['공정']
        key = (product, process)
        
        if key in corrections:
            idx = corrected_ci[(corrected_ci['제품'] == product) & (corrected_ci['공정'] == process)].index[0]
            
            for energy_type, value in corrections[key].items():
                if energy_type in corrected_ci.columns:
                    corrected_ci.loc[idx, energy_type] = value
        else:
            # For unlisted products, apply moderate increases
            idx = corrected_ci[(corrected_ci['제품'] == product) & (corrected_ci['공정'] == process)].index[0]
            
            # Default increases for unlisted utilities
            if process == 'Utility':
                current_lng = corrected_ci.loc[idx, 'LNG(GJ/t)'] or 0
                current_elec = corrected_ci.loc[idx, '전력(Baseline)(kWh/t)'] or 0
                
                # Moderate energy for specialty chemicals
                if current_lng < 2:
                    corrected_ci.loc[idx, 'LNG(GJ/t)'] = 3.0
                if current_elec < 200:
                    corrected_ci.loc[idx, '전력(Baseline)(kWh/t)'] = 400
    
    return corrected_ci

def create_corrected_ci2_data():
    """Create corrected emission factors for Korean conditions"""
    
    original_file = "data/petro_data_v1.0.xlsx"
    ci2_df = pd.read_excel(original_file, sheet_name='CI2')
    
    # Korean-specific emission factors (2023)
    corrected_factors = {
        'LNG( tCO₂/GJ )': 0.056,  # Standard LNG factor
        '부생가스( tCO₂/GJ )': 0.058,  # Slightly higher for refinery gas
        'LPG-프로판( tCO₂/GJ )': 0.063,  # Propane
        'LPG-부탄( tCO₂/GJ )': 0.065,  # Butane
        '연료가스(Fuel gas mix)( tCO₂/GJ )': 0.058,  # Mixed refinery gas
        '중유(Fuel oil)( tCO₂/GJ )': 0.077,  # Heavy fuel oil
        '디젤( tCO₂/GJ )': 0.074,  # Diesel
        '전력(Baseline)( tCO₂/kWh )': 0.452,  # Korean grid 2023 (CRITICAL FIX)
    }
    
    corrected_ci2 = ci2_df.copy()
    
    # Apply corrections to all rows
    for col, factor in corrected_factors.items():
        if col in corrected_ci2.columns:
            corrected_ci2[col] = factor
    
    return corrected_ci2

def save_corrected_data():
    """Save corrected data to new Excel file"""
    
    # Create corrected data
    corrected_ci = create_corrected_ci_data()
    corrected_ci2 = create_corrected_ci2_data()
    
    # Load original workbook to preserve other sheets
    original_file = "data/petro_data_v1.0.xlsx"
    
    # Read all sheets first
    with pd.ExcelFile(original_file) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            if sheet_name not in ['CI', 'CI2']:
                all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Add corrected sheets
    all_sheets['CI'] = corrected_ci
    all_sheets['CI2'] = corrected_ci2
    
    # Save to new file
    output_file = "data/petro_data_v1.0_corrected.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Corrected data saved to {output_file}")
    
    # Print summary of changes
    print("\n=== KEY CORRECTIONS MADE ===")
    print("1. Electricity emission factor: 0.0045 → 0.452 tCO₂/kWh (100x increase)")
    print("2. Steam cracker energy: Added 25-30 GJ/t thermal energy")
    print("3. BTX plant energy: Added 10-12 GJ/t thermal energy") 
    print("4. Downstream processes: Moderate increases to avoid double counting")
    print("5. Primary process electricity: Increased to 400-600 kWh/t")
    
    return output_file

if __name__ == "__main__":
    save_corrected_data()