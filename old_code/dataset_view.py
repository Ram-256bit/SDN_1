import pandas as pd

# Path to your dataset file
file_path = 'UNSW_NB15_training-set.parquet'

try:
    # 1. Load the dataset
    # Pandas handles the parquet format automatically if pyarrow is installed
    df = pd.read_parquet(file_path)

    # 2. Display the first 10 rows
    print("--- First 10 Rows of the Dataset ---")
    print(df.head(10))

    # 3. Optional: Display column names and types for your PPT reference
    print("\n--- Dataset Info (Features) ---")
    print(df.info())

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the path.")
except Exception as e:
    print(f"An error occurred: {e}")