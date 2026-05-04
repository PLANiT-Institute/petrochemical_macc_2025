import pandas as pd
from pathlib import Path

file_path = Path('data/demand_growth_trajectory.csv')
print(f"Reading {file_path}")

try:
    df = pd.read_csv(file_path)
    print("Columns:", df.columns.tolist())
    print("Head:", df.head(3))
    print("Tail:", df.tail(3))
    print("Years:", df['year'].unique())
    print("Types:", df.dtypes)
    
    val = df[df['year']==2050]
    print(f"Filter 2050 len: {len(val)}")
    if len(val) > 0:
        print("Value:", val.iloc[0]['cumulative_capacity_multiplier'])
    else:
        print("2050 not found!")

except Exception as e:
    print(e)
