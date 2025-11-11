import pandas as pd
import joblib

# Load data
df = pd.read_csv("scholarsipdatamine.csv")

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Normalize criteria values
def clean(val):
    if isinstance(val, str):
        return val.strip().lower()
    return val

df = df.applymap(clean)

# Save to use in API
joblib.dump(df, "scholarship_rules.pkl")
print("Rules saved.")
