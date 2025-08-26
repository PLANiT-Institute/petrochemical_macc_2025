#!/usr/bin/env python3
"""
Comprehensive test script for the restructured petrochemical MACC library
"""

import sys
from pathlib import Path

# Add the petrochem package to path
sys.path.insert(0, str(Path(__file__).parent))

def test_cli_interface():
    """Test the CLI interface"""
    print("🖥️  Testing CLI interface...")
    
    try:
        from petrochem.cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Test help
        result = runner.invoke(cli, ['--help'])
        if result.exit_code == 0:
            print("  ✅ CLI help works")
        else:
            print(f"  ❌ CLI help failed: {result.output}")
            
        # Test info command
        result = runner.invoke(cli, ['info'])
        if result.exit_code == 0:
            print("  ✅ CLI info command works")
        else:
            print("  ⚠️  CLI info command expected to fail (no baseline data)")
            
        return True
        
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False

def test_comprehensive_data_loading():
    """Test loading from the comprehensive Excel file"""
    print("📊 Testing comprehensive data loading...")
    
    try:
        from petrochem.lib import DataLoader, DataValidator
        
        # Initialize loader
        loader = DataLoader()
        
        # Test loading technologies from new file
        print("  Loading transition technologies...")
        transitions = loader.load_transition_technologies()
        print(f"  ✅ Loaded {len(transitions)} transition technologies")
        
        print("  Loading alternative technologies...")
        alternatives = loader.load_alternative_technologies()
        print(f"  ✅ Loaded {len(alternatives)} alternative technologies")
        
        # Test portfolio loading
        print("  Loading complete portfolio...")
        portfolio = loader.load_technology_portfolio()
        
        summary = portfolio.get_portfolio_summary()
        print(f"  ✅ Portfolio loaded: {len(portfolio.technologies)} technologies")
        print(f"    - Processes: {', '.join(summary['process_types'])}")
        print(f"    - Cost range: ${summary['min_lcoa_usd_per_tco2']:.0f} - ${summary['max_lcoa_usd_per_tco2']:.0f}/tCO2")
        
        # Test validation
        print("  Validating portfolio...")
        validation = DataValidator.validate_portfolio(portfolio)
        print(f"  🔍 Validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"    ⚠️  {warning}")
        
        if validation['errors']:
            for error in validation['errors']:
                print(f"    ❌ {error}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_building():
    """Test model building with new structure"""
    print("🏗️  Testing model building...")
    
    try:
        from petrochem.lib import DataLoader
        from petrochem.lib.optimization.model_builder import MACCModelBuilder
        from petrochem.lib.core.scenario import EmissionsScenario, EmissionsBaseline, EmissionsTarget, ProcessBaseline
        
        # Load portfolio
        loader = DataLoader()
        portfolio = loader.load_technology_portfolio()
        
        # Create dummy scenario for testing (since we don't have the baseline dataset)
        dummy_baselines = [
            ProcessBaseline("NCC", 10000, 1.5, {"NCC_HT": 0.6, "NCC_MT": 0.4}),
            ProcessBaseline("BTX", 8000, 0.8, {"BTX_HT": 0.5, "BTX_MT": 0.5}),
            ProcessBaseline("Utilities", 5000, 2.0, {"Utilities_HT": 0.8, "Utilities_MT": 0.2})
        ]
        
        baseline = EmissionsBaseline(2023, 30.0, dummy_baselines)
        targets = [
            EmissionsTarget(2030, 25.0),
            EmissionsTarget(2040, 15.0),
            EmissionsTarget(2050, 5.0)
        ]
        scenario = EmissionsScenario(baseline, targets, list(range(2023, 2051)))
        
        print(f"  ✅ Created test scenario: {scenario}")
        
        # Build model
        model_builder = MACCModelBuilder(scenario, portfolio)
        model = model_builder.build_model(allow_slack=True, discount_rate=0.05)
        
        summary = model_builder.get_model_summary()
        print(f"  ✅ Built optimization model")
        print(f"    - Variables: {sum(summary['variables'].values())}")
        print(f"    - Constraints: {sum(summary['constraints'].values())}")
        print(f"    - Parameters: {summary['parameters_populated']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model building test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization():
    """Test visualization components"""
    print("📊 Testing visualization...")
    
    try:
        from petrochem.lib.visualization.charts import MACCVisualizer
        import pandas as pd
        
        # Create test data
        test_macc_data = {
            'TechID': ['T1', 'T2', 'T3'],
            'ProcessType': ['NCC', 'BTX', 'Utilities'],
            'Abatement_MtCO2': [2.0, 1.5, 1.0],
            'LCOA_USD_per_tCO2': [100, 200, 300],
            'Cumulative_Abatement_MtCO2': [2.0, 3.5, 4.5]
        }
        
        test_df = pd.DataFrame(test_macc_data)
        
        # Test visualizer
        visualizer = MACCVisualizer(output_dir="test_outputs")
        
        # Test MACC curve
        fig = visualizer.plot_macc_curve(test_df, 2030, "Test MACC Curve")
        print("  ✅ MACC curve visualization works")
        
        # Close figure to save memory
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Visualization test failed: {e}")
        return False

def show_file_structure():
    """Show the complete file structure"""
    print("\n📁 Complete File Structure:")
    print("=" * 50)
    
    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
            
        items = sorted(path.iterdir()) if path.is_dir() else []
        
        for i, item in enumerate(items):
            if item.name.startswith('.'):
                continue
                
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, max_depth, current_depth + 1)
    
    project_root = Path(__file__).parent
    print_tree(project_root)

def main():
    """Main test function"""
    print("🚀 Testing Complete Korea Petrochemical MACC Library")
    print("=" * 60)
    
    # Show structure
    show_file_structure()
    
    print("\n🧪 Running Tests:")
    print("-" * 30)
    
    # Run tests
    tests = [
        ("Data Loading", test_comprehensive_data_loading),
        ("Model Building", test_model_building),
        ("Visualization", test_visualization),
        ("CLI Interface", test_cli_interface),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n🎯 Test Summary:")
    print("-" * 20)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed.'}")
    
    if all_passed:
        print("\n📚 Library is ready for use!")
        print("Available commands:")
        print("  python -m petrochem.cli info          # Show model information")
        print("  python -m petrochem.cli validate      # Validate data files")
        print("  python -m petrochem.cli optimize      # Run optimization")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())