import pandas as pd

# Read CSV into a DataFrame
df = pd.read_csv("live_demo_traffic_2.csv")

# Delete the last column
df = df.iloc[:, :-1]

# Save the updated DataFrame to a new CSV file
df.to_csv("live_demo_traffic_new.csv", index=False)