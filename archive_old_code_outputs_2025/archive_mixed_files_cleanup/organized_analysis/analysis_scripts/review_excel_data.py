#!/usr/bin/env python3
"""
Review Excel Data for Naphtha Emissions and Technology Analysis
Focus on understanding current emission calculations and naphtha treatment
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def analyze_excel_data():
    """Comprehensive review of Excel data files"""
    
    print("🔍 REVIEWING EXCEL DATA FILES")
    print("=" * 80)
    
    # Define data files to examine
    data_files = [
        '../data/korean_petrochemical_macc_enhanced.xlsx'
    ]
    
    for file_path in data_files:
        if Path(file_path).exists():
            print(f"\n📊 ANALYZING: {file_path}")
            print("-" * 60)
            
            try:
                # Read all sheets
                xlsx_file = pd.ExcelFile(file_path)
                sheet_names = xlsx_file.sheet_names
                print(f"📋 Sheets found: {sheet_names}")
                
                # Examine each sheet
                for sheet in sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    print(f"\n📈 Sheet: {sheet}")
                    print(f"   Shape: {df.shape}")
                    print(f"   Columns: {list(df.columns)}")
                    
                    # Look for naphtha-related columns
                    naphtha_cols = [col for col in df.columns if 'naphtha' in str(col).lower()]
                    if naphtha_cols:
                        print(f"   🛢️  Naphtha columns: {naphtha_cols}")
                        
                        # Check naphtha emission values
                        for col in naphtha_cols:
                            if df[col].dtype in ['float64', 'int64']:
                                print(f"      {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")
                    
                    # Look for emission-related columns
                    emission_cols = [col for col in df.columns if any(term in str(col).lower() 
                                   for term in ['emission', 'co2', 'ghg', 'carbon'])]
                    if emission_cols:
                        print(f"   🌍 Emission columns: {emission_cols}")
                        
                        # Check emission values
                        for col in emission_cols:
                            if df[col].dtype in ['float64', 'int64']:
                                print(f"      {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, sum={df[col].sum():.2f}")
                    
                    # Look for process type information
                    process_cols = [col for col in df.columns if any(term in str(col).lower() 
                                  for term in ['process', 'facility', 'plant', 'type'])]
                    if process_cols:
                        print(f"   🏭 Process columns: {process_cols}")
                        
                        # Show process distribution
                        for col in process_cols:
                            if df[col].dtype == 'object':
                                value_counts = df[col].value_counts()
                                print(f"      {col}: {dict(value_counts.head())}")
                
            except Exception as e:
                print(f"❌ Error reading {file_path}: {str(e)}")
        else:
            print(f"❌ File not found: {file_path}")

def examine_naphtha_emissions():
    """Specific analysis of naphtha emission calculations"""
    
    print("\n\n🛢️  NAPHTHA EMISSION ANALYSIS")
    print("=" * 80)
    
    try:
        # Load the main data file
        df_facilities = pd.read_excel('../data/korean_petrochemical_macc_enhanced.xlsx', 
                                    sheet_name='facilities')
        
        print("📊 Facilities Data Summary:")
        print(f"   Total facilities: {len(df_facilities)}")
        
        # Check for naphtha consumption and emissions
        naphtha_related = df_facilities.filter(regex='naphtha|Naphtha', axis=1)
        if not naphtha_related.empty:
            print(f"\n🛢️  Naphtha-related columns:")
            for col in naphtha_related.columns:
                values = naphtha_related[col]
                if values.dtype in ['float64', 'int64']:
                    print(f"   {col}: {values.describe()}")
                else:
                    print(f"   {col}: {values.value_counts().to_dict()}")
        
        # Check process types and their emissions
        if 'process_type' in df_facilities.columns:
            print(f"\n🏭 Process Type Distribution:")
            process_dist = df_facilities['process_type'].value_counts()
            print(process_dist)
            
            # Emission by process type
            if 'scope1_emissions_tco2' in df_facilities.columns:
                emissions_by_process = df_facilities.groupby('process_type')['scope1_emissions_tco2'].agg(['count', 'sum', 'mean'])
                print(f"\n🌍 Emissions by Process Type:")
                print(emissions_by_process)
        
        # Look for NCC facilities specifically
        ncc_facilities = df_facilities[df_facilities['process_type'].str.contains('NCC', na=False)]
        if not ncc_facilities.empty:
            print(f"\n🏭 NCC Facilities Analysis:")
            print(f"   Number of NCC facilities: {len(ncc_facilities)}")
            if 'scope1_emissions_tco2' in ncc_facilities.columns:
                print(f"   Total NCC emissions: {ncc_facilities['scope1_emissions_tco2'].sum():.2f} tCO2")
                print(f"   Average NCC emissions: {ncc_facilities['scope1_emissions_tco2'].mean():.2f} tCO2")
    
    except Exception as e:
        print(f"❌ Error in naphtha analysis: {str(e)}")

def create_emission_summary():
    """Create summary of current emission calculation approach"""
    
    print("\n\n📋 EMISSION CALCULATION SUMMARY")
    print("=" * 80)
    
    try:
        # Load data
        df_facilities = pd.read_excel('../data/korean_petrochemical_macc_enhanced.xlsx', 
                                    sheet_name='facilities')
        
        # Total emission summary
        total_emissions = df_facilities['scope1_emissions_tco2'].sum()
        print(f"🌍 Total Current Emissions: {total_emissions:,.0f} tCO2")
        
        # By process type
        emission_breakdown = df_facilities.groupby('process_type')['scope1_emissions_tco2'].sum().sort_values(ascending=False)
        print(f"\n📊 Emissions by Process Type:")
        for process, emissions in emission_breakdown.items():
            percentage = (emissions / total_emissions) * 100
            print(f"   {process}: {emissions:,.0f} tCO2 ({percentage:.1f}%)")
        
        # Check for zero emissions
        zero_emission_facilities = df_facilities[df_facilities['scope1_emissions_tco2'] == 0]
        if not zero_emission_facilities.empty:
            print(f"\n⚠️  Facilities with Zero Emissions: {len(zero_emission_facilities)}")
            zero_by_process = zero_emission_facilities['process_type'].value_counts()
            print(zero_by_process)
        
        # Identify potential issues
        print(f"\n🔍 POTENTIAL ISSUES IDENTIFIED:")
        print(f"   - Total emissions: {total_emissions:,.0f} tCO2")
        print(f"   - Zero emission facilities: {len(zero_emission_facilities)}")
        print(f"   - Need to check if naphtha feedstock emissions are included")
        print(f"   - Need to add external GHG factors for scope 3 emissions")
        
    except Exception as e:
        print(f"❌ Error in emission summary: {str(e)}")

if __name__ == "__main__":
    analyze_excel_data()
    examine_naphtha_emissions()
    create_emission_summary()
    
    print("\n\n✅ EXCEL DATA REVIEW COMPLETE")
    print("🎯 Key findings will inform the simplified technology analysis")