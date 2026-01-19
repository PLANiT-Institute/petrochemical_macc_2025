import pandas as pd
from modules.utils import DataLoader, EmissionCalculator, PriceCalculator, TechnologyCostCalculator

# Mocks/Stubs to avoid loading all CSVs if possible, or just load them if fast enough.
# We will use the real DataLoader to be sure.

def test_fuel_savings_logic():
    print("Loading data...")
    loader = DataLoader('data')
    
    # Load necessary input data
    # methods: load_energy_intensities, load_emission_factors, etc.
    try:
        intensities = loader.load_energy_intensities()
        emission_factors = loader.load_emission_factors()
        fuel_prices_df = pd.read_csv('data/fuel_price_trajectory.csv')
    except FileNotFoundError:
        print("Data files not found, cannot run full test.")
        return

    # Setup Calculators
    emission_calc = EmissionCalculator(emission_factors)
    # Price calculator
    # Mock H2/RE prices just for initialization (we won't check them specifically yet)
    h2_prices = pd.DataFrame({'year': [2030], 'h2_price_usd_per_kg': [2.0]})
    re_prices = pd.DataFrame({'year': [2030], 're_price_usd_per_mwh': [100.0]})
    price_calc = PriceCalculator(h2_prices, re_prices, fuel_prices_df)

    # 1. Select a Naphtha Cracker facility
    # Let's mock a facility row and intensity row
    facility_row = {
        'capacity_kt': 1000, # 1,000,000 tonnes
        'process': 'Naphtha Cracker'
    }
    
    # Mock intensity: Suppose it consumes Naphtha, Fuel Gas, and Electricity
    # Values from data inspection:
    # Naphtha: ~29 GJ/t
    # Fuel Gas: ~1.12 GJ/t
    # Electricity: ~85 kWh/t
    intensity_row = {
        'Naphtha_GJ_per_tonne': 29.0,
        'Fuel_Gas_GJ_per_tonne': 1.12,
        'Electricity_kWh_per_tonne': 85.0,
        # Others 0
    }
    
    operating_rate = 1.0
    
    # Calculate baseline
    print("\nCalculating Baseline Metrics...")
    baseline = emission_calc.calculate_baseline_metrics(facility_row, intensity_row, operating_rate)
    
    print(f"Production: {baseline['production_t']} tonnes")
    print(f"Naphtha Emissions: {baseline['emissions_by_source'].get('naphtha', 0):.2f} tCO2")
    
    # 2. Check Fuel Prices for 2030
    year = 2030
    prices = price_calc.get_fuel_prices(year)
    print(f"\nFuel Prices ({year}):")
    print(prices)
    
    naphtha_price = prices.get('naphtha_usd_per_gj', 0)
    fuel_gas_price = prices.get('fuel_gas_usd_per_gj', 0)
    
    # 3. Calculate "Avoided Cost" MANUALLY
    # If we replace ALL combustion energy (Naphtha + Fuel Gas)
    # Energy to replace:
    naphtha_gj = intensity_row['Naphtha_GJ_per_tonne'] * baseline['production_t']
    fuel_gas_gj = intensity_row['Fuel_Gas_GJ_per_tonne'] * baseline['production_t']
    
    avoided_naphtha_cost = naphtha_gj * naphtha_price
    avoided_gas_cost = fuel_gas_gj * fuel_gas_price
    
    total_savings = avoided_naphtha_cost + avoided_gas_cost
    print(f"\nExpected Fuel Savings (Manual):")
    print(f"  Naphtha: ${avoided_naphtha_cost:,.2f}")
    print(f"  Fuel Gas: ${avoided_gas_cost:,.2f}")
    print(f"  Total:    ${total_savings:,.2f}")
    
    return total_savings

if __name__ == "__main__":
    test_fuel_savings_logic()
