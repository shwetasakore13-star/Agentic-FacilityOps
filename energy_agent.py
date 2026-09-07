"""
Energy Agent - reads energy data, finds problems, gives totals.
This is Milestone 1 of the Agentic FacilityOps project.
"""

import pandas as pd

# Step 1: Read the data file
df = pd.read_csv("data/4.data_2020.csv")

# Step 2: Clean column names
df.columns = [c.strip() for c in df.columns]

print("=== Energy Agent Report ===\n")

# Step 3: Basic totals
total_power = df["Power[kW]"].sum()
total_hvac = df["HVAC Actual [kW]"].sum()
total_lighting = df["HV light Power [kW]"].sum()
total_solar = df["PV panels power [kW]"].abs().sum()

print(f"Total Power Used: {total_power:.2f} kW")
print(f"Total HVAC Usage: {total_hvac:.2f} kW")
print(f"Total Lighting Usage: {total_lighting:.2f} kW")
print(f"Total Solar Generated: {total_solar:.2f} kW")

# Step 4: Efficiency score
efficiency_score = (total_solar / total_power) * 100
print(f"\nSolar Efficiency Score: {efficiency_score:.2f}%")

# Step 5: Find anomalies
average_power = df["Power[kW]"].mean()
std_power = df["Power[kW]"].std()
threshold = average_power + (2 * std_power)

anomalies = df[df["Power[kW]"] > threshold]
print(f"\nAnomalies found: {len(anomalies)} (out of {len(df)} readings)")

# Step 6: Save a summary report
with open("energy_report.txt", "w") as f:
    f.write("ENERGY AGENT REPORT\n")
    f.write(f"Total Power: {total_power:.2f} kW\n")
    f.write(f"Total HVAC: {total_hvac:.2f} kW\n")
    f.write(f"Total Lighting: {total_lighting:.2f} kW\n")
    f.write(f"Total Solar: {total_solar:.2f} kW\n")
    f.write(f"Efficiency Score: {efficiency_score:.2f}%\n")
    f.write(f"Anomalies Detected: {len(anomalies)}\n")

print("\n✅ Report saved as energy_report.txt")