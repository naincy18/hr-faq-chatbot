import pandas as pd

# Load the knowledge base
df = pd.read_csv("data/hr_policies.csv")

# Basic sanity checks
print("Number of policies loaded:", len(df))
print("\nColumn names:", list(df.columns))
print("\nFirst policy:\n")
print(df.iloc[0])