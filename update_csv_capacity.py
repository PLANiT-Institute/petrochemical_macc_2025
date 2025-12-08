import pandas as pd

# Load CSV
file_path = 'data/energy_intensities.csv'
df = pd.read_csv(file_path)

# Apply 1.10x Scalar to Capacity
# Note: We are creating a NEW baseline for 2024.
# We should probably backup the original first?
# The user asked to "update" the file.
# We will assume "update" means overwrite with new baseline.

SCALAR = 1.10

df['capacity_kt'] = df['capacity_kt'] * SCALAR
df['capacity_kt'] = df['capacity_kt'].round(2)

# Save
df.to_csv(file_path, index=False)
print(f"Updated {file_path}. Scaled capacity by {SCALAR}x.")
