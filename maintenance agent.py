"""
Maintenance Agent - Milestone 2
Reads asset data, analyzes health, predicts maintenance needs,
and generates maintenance alerts / work orders.
"""

import pandas as pd

df = pd.read_csv("maintenance_data.csv")

print("=== Maintenance Agent Report ===\n")

total_assets = len(df)
avg_health = df["health_score"].mean()
critical = df[df["status"] == "Critical"]
at_risk = df[df["status"] == "At Risk"]
watch = df[df["status"] == "Watch"]
healthy = df[df["status"] == "Healthy"]

print(f"Total Assets Monitored: {total_assets}")
print(f"Average Health Score: {avg_health:.1f}/100")
print(f"\nStatus Breakdown:")
print(f"  Healthy:  {len(healthy)}")
print(f"  Watch:    {len(watch)}")
print(f"  At Risk:  {len(at_risk)}")
print(f"  Critical: {len(critical)}")

# Assets needing maintenance soon (within 14 days)
urgent = df[df["predicted_days_to_maintenance"] <= 14].sort_values("predicted_days_to_maintenance")

print(f"\n=== Urgent Maintenance Needed (next 14 days): {len(urgent)} assets ===")
for _, row in urgent.iterrows():
    print(f"  [{row['status']}] {row['asset_name']} ({row['zone']}) — "
          f"Health: {row['health_score']}, Due in {row['predicted_days_to_maintenance']} days")

# Generate work orders for critical + at-risk assets
work_orders = []
for _, row in df[df["status"].isin(["Critical", "At Risk"])].iterrows():
    reason = []
    if row["vibration_mm_s"] > 6:
        reason.append("high vibration")
    if abs(row["temp_deviation_c"]) > 8:
        reason.append("temperature anomaly")
    if row["days_since_maintenance"] > 120:
        reason.append("overdue maintenance")
    if not reason:
        reason.append("declining health score")

    work_orders.append({
        "asset_id": row["asset_id"],
        "asset_name": row["asset_name"],
        "zone": row["zone"],
        "priority": "HIGH" if row["status"] == "Critical" else "MEDIUM",
        "reason": ", ".join(reason),
        "due_in_days": row["predicted_days_to_maintenance"],
    })

wo_df = pd.DataFrame(work_orders)
wo_df.to_csv("work_orders.csv", index=False)

print(f"\n=== Work Orders Generated: {len(work_orders)} ===")
for wo in work_orders:
    print(f"  [{wo['priority']}] {wo['asset_name']} — {wo['reason']} (due in {wo['due_in_days']} days)")

# Save summary report
with open("maintenance_report.txt", "w") as f:
    f.write("MAINTENANCE AGENT REPORT\n")
    f.write(f"Total Assets: {total_assets}\n")
    f.write(f"Average Health Score: {avg_health:.1f}\n")
    f.write(f"Healthy: {len(healthy)}\n")
    f.write(f"Watch: {len(watch)}\n")
    f.write(f"At Risk: {len(at_risk)}\n")
    f.write(f"Critical: {len(critical)}\n")
    f.write(f"Urgent (next 14 days): {len(urgent)}\n")
    f.write(f"Work Orders Generated: {len(work_orders)}\n")

print("\n✅ Report saved as maintenance_report.txt")
print("✅ Work orders saved as work_orders.csv")
