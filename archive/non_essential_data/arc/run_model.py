#!/usr/bin/env python3
"""
Run the MACC model with updated Excel data
"""

import sys
import os
from pathlib import Path

# Add the petrochem package to path
sys.path.insert(0, str(Path(__file__).parent))

from petrochem.solver import main

if __name__ == "__main__":
    # Run with the updated Excel file
    excel_file = "data/Korea_Petrochemical_MACC_Database.xlsx"
    
    print(f"🚀 Running Korea Petrochemical MACC Model")
    print(f"📂 Using data file: {excel_file}")
    print("=" * 50)
    
    # Set up command line arguments  
    import sys
    sys.argv = [
        "run_model.py",
        "--excel", excel_file,
        "--years", "2030", "2050",  # Year range
        "--allow-slack",  # Allow shortfall with penalty
        "--solver", "glpk",  # Use GLPK solver  
        "--plots",  # Generate cost curves
        "--discount-rate", "0.05",  # 5% discount rate
        "--ramp-default", "0.15"  # 15% ramp rate default
    ]
    
    try:
        main()
        print("\n✅ Model completed successfully!")
        print("📊 Check the 'outputs' directory for results")
    except Exception as e:
        print(f"\n❌ Model failed: {str(e)}")
        sys.exit(1)