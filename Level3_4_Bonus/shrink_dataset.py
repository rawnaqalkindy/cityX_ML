import pandas as pd

df = pd.read_csv("Competition_Dataset.csv")
df_small = df.sample(n=300, random_state=42)
df_small.to_csv("Competition_Dataset_small.csv", index=False)

print("Created Competition_Dataset_small.csv with 300 rows.") # Shrink dataset to random 300 entries for deployment purposes
