import pandas as pd

print("Loading UNSW-NB15 testing dataset...")
# Load the testing parquet file
df = pd.read_parquet('UNSW_NB15_testing-set.parquet')

# The exact features our GenClass model was trained on
features = ['sbytes', 'dbytes', 'sload', 'dload', 'rate']

# We will also keep the attack_cat column just so you can manually 
# verify if the model gets it right during the demo!
columns_to_keep = features + ['attack_cat']

# Drop any empty rows just to be safe
df = df.dropna(subset=columns_to_keep)

# Extract the first 150 rows. This gives you about 2.5 minutes of 
# simulated live traffic in the UI (at 1 row per second).
demo_df = df[columns_to_keep].head(150)

# Save it as a CSV
demo_df.to_csv('live_demo_traffic.csv', index=False)

print("Success! Created 'live_demo_traffic.csv' with 150 rows.")