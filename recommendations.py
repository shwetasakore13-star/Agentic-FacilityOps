"""
Generates simple energy-saving recommendations based on the data.
"""

import pandas as pd

df = pd.read_csv("data/4.data_2020.csv")
df.columns = [c.strip() for c in df.columns]

total_power = df["Power[kW]"].sum()
total_hvac = df["HVAC Actual [kW]"].sum()
total_lighting = df["HV light Power [kW]"].sum()

hvac_percent = (total_hvac / total_power) * 100
lighting_percent = (total_lighting / total_power) * 100

recommendations = []

if hvac_percent > 40:
    recommendations.append(f"HVAC uses {hvac_percent:.1f}% of total power - consider optimizing HVAC schedules during off-hours.")

if lighting_percent > 30:
    recommendations.append(f"Lighting uses {lighting_percent:.1f}% of total power - consider motion-sensor lighting or LED upgrades.")

recommendations.append("Install smart thermostats to reduce HVAC overuse automatically.")
recommendations.append("Shift high-consumption tasks to peak solar generation hours to maximize solar usage.")

print("=== Energy Efficiency Recommendations ===\n")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")

with open("recommendations.txt", "w") as f:
    for i, rec in enumerate(recommendations, 1):
        f.write(f"{i}. {rec}\n")

print("\n✅ Saved as recommendations.txt")