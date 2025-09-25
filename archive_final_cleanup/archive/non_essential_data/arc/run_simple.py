#!/usr/bin/env python3
"""
Simple run script for the MACC model
"""

import sys
import os
from pathlib import Path

# Add the petrochem package to path
sys.path.insert(0, str(Path(__file__).parent))

from petrochem.data_io import read_excel, baseline_total_mt, targets_map, build_timeseries, parse_links
from petrochem.model_pyomo import build_model, solve_model
import pandas as pd

def run_macc_model():
    """Run the MACC model with updated data"""
    
    excel_file = "data/Korea_Petrochemical_MACC_Database.xlsx"
    print(f"🚀 Running Korea Petrochemical MACC Model")
    print(f"📂 Using data file: {excel_file}")
    print("=" * 50)
    
    try:
        # Read Excel data
        print("📖 Reading Excel data...")
        sheets = read_excel(excel_file)
        
        # Get timeline and targets
        years_all, tmap = targets_map(sheets, None)
        years_model = [2030, 2040, 2050]  # Focus on key years
        
        print(f"📅 Model timeline: {years_model}")
        
        # Calculate baseline
        baseline_mt = baseline_total_mt(sheets)
        print(f"🏭 Baseline emissions: {baseline_mt:.1f} MtCO2")
        
        # Build technology data
        print("🔧 Building technology parameters...")
        tech_ids, params = build_timeseries(sheets, years_model, ramp_default=0.15)
        groups, depends = parse_links(sheets)
        
        print(f"⚡ Technologies loaded: {len(tech_ids)}")
        
        # Build optimization model
        print("📊 Building optimization model...")
        model = build_model(
            years_model, baseline_mt, tmap, tech_ids, params, groups, depends,
            allow_slack=True, slack_penalty=1e15, discount_rate=0.05, 
            base_year=min(years_model)
        )
        
        # Solve model
        print("🎯 Solving optimization model...")
        solver_used, results = solve_model(model, solver="glpk")
        
        print(f"✅ Model solved with {solver_used}")
        
        # Create outputs directory
        os.makedirs("outputs", exist_ok=True)
        
        # Export results
        print("💾 Exporting results...")
        summary = []
        for y in years_model:
            rows = []
            for i in tech_ids:
                rows.append({
                    "TechID": i, "Year": y,
                    "Build_share": float(model.build[i,y].value or 0.0),
                    "Share": float(model.share[i,y].value or 0.0),
                    "Abatement_tCO2": float(model.abate[i,y].value or 0.0),
                    "Activity": float(model.activity[i,y].value),
                    "Cap": float(model.cap[i,y].value),
                    "Abate_per_activity": float(model.abat[i,y].value)
                })
            df = pd.DataFrame(rows).sort_values(["Year","TechID"])
            df.to_csv(f"outputs/plan_{y}.csv", index=False, encoding="utf-8-sig")
            
            achieved = df["Abatement_tCO2"].sum()
            shortfall = float(model.shortfall[y].value or 0.0) if hasattr(model,"shortfall") else 0.0
            summary.append({
                "Year": y,
                "Baseline_MtCO2e": baseline_mt,
                "Target_MtCO2e": float(tmap.get(y, baseline_mt)),
                "Required_Abatement_MtCO2": float(model.req[y].value/1e6),
                "Achieved_Abatement_MtCO2": achieved/1e6,
                "Shortfall_MtCO2": shortfall/1e6,
                "Solver": solver_used,
                "Achievement_Rate": (achieved/1e6) / (float(model.req[y].value/1e6)) * 100 if model.req[y].value > 0 else 100
            })
        
        # Save summary
        pd.DataFrame(summary).to_csv("outputs/summary.csv", index=False, encoding="utf-8-sig")
        
        # Print summary results
        print("\n📈 RESULTS SUMMARY:")
        for s in summary:
            print(f"  {s['Year']}: {s['Achievement_Rate']:.1f}% target achieved, {s['Shortfall_MtCO2']:.1f} MtCO2 shortfall")
        
        print(f"\n✅ Model completed successfully!")
        print(f"📁 Results saved in 'outputs' directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_macc_model()
    sys.exit(0 if success else 1)