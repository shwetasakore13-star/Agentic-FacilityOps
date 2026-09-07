"""
Agentic FacilityOps AI Platform — Milestone 1
Energy Intelligence & Monitoring — Streamlit Dashboard

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Agentic FacilityOps AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM STYLING
# ============================================================
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .stApp { background-color: #0f172a; }
    [data-testid="stSidebar"] { background-color: #131c3a; }
    h1, h2, h3 { color: #38bdf8 !important; }
    p, span, label { color: #e2e8f0 !important; }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #263071 100%);
        padding: 20px; border-radius: 14px; border: 1px solid #2d3a63;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #263071 100%);
        padding: 18px; border-radius: 14px; border: 1px solid #2d3a63;
    }
    div[data-testid="stMetricLabel"] { color: #9AA3C7 !important; }
    div[data-testid="stMetricValue"] { color: #F9E795 !important; }
    .rec-box {
        background-color: #1e293b; border-left: 4px solid #38bdf8;
        padding: 14px 18px; border-radius: 8px; margin-bottom: 10px; color: #e2e8f0;
    }
    .alert-box {
        background-color: #3b1f1f; border-left: 4px solid #f87171;
        padding: 14px 18px; border-radius: 8px; margin-bottom: 10px; color: #fecaca;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING (cached so it only loads once)
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/4.data_2020.csv")
    df.columns = [c.strip() for c in df.columns]
    df["Time"] = pd.to_datetime(df["Time"], format="%d/%m/%Y %H:%M")
    df["hour"] = df["Time"].dt.hour
    df["date"] = df["Time"].dt.date
    df["day_of_week"] = df["Time"].dt.day_name()

    # Anomaly detection: z-score style threshold on total power
    mean_p = df["Power[kW]"].mean()
    std_p = df["Power[kW]"].std()
    df["is_anomaly"] = df["Power[kW]"] > (mean_p + 2 * std_p)

    return df


@st.cache_data
def compute_summary(df):
    total_power = df["Power[kW]"].sum()
    total_hvac = df["HVAC Actual [kW]"].sum()
    total_lighting = df["HV light Power [kW]"].sum()
    total_solar = df["PV panels power [kW]"].abs().sum()
    total_chiller = df["Chiller Power [kW]"].sum()
    efficiency = (total_solar / total_power) * 100
    anomalies = int(df["is_anomaly"].sum())
    return {
        "total_power": total_power,
        "total_hvac": total_hvac,
        "total_lighting": total_lighting,
        "total_solar": total_solar,
        "total_chiller": total_chiller,
        "efficiency": efficiency,
        "anomalies": anomalies,
        "records": len(df),
    }


def generate_recommendations(summary):
    recs = []
    hvac_pct = (summary["total_hvac"] / summary["total_power"]) * 100
    lighting_pct = (summary["total_lighting"] / summary["total_power"]) * 100

    if hvac_pct > 40:
        recs.append(f"HVAC accounts for {hvac_pct:.1f}% of total power. Consider optimizing schedules during off-hours to cut waste.")
    if lighting_pct > 30:
        recs.append(f"Lighting accounts for {lighting_pct:.1f}% of total power. Motion sensors or LED upgrades could reduce this significantly.")
    recs.append("Install smart thermostats to automatically reduce HVAC overuse during unoccupied hours.")
    recs.append("Shift high-consumption tasks toward peak solar generation hours to reduce grid dependency.")
    if summary["anomalies"] > 0:
        pct = (summary["anomalies"] / summary["records"]) * 100
        recs.append(f"{summary['anomalies']:,} anomalous readings detected ({pct:.1f}% of data) — recommend inspecting equipment during flagged periods.")
    return recs


# ============================================================
# LOAD DATA
# ============================================================
df = load_data()
summary = compute_summary(df)
recommendations = generate_recommendations(summary)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown("## ⚡ FacilityOps AI")
st.sidebar.markdown("**Agentic FacilityOps AI Platform**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview Dashboard", "🔍 Anomaly Analytics", "💡 AI Recommendations",
     "📈 Deep Insights", "🔧 Predictive Maintenance"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Milestone 1** — Energy Intelligence")
st.sidebar.progress(1.0, text="Status: Complete")
st.sidebar.markdown("**Milestone 2** — Predictive Maintenance")
st.sidebar.progress(1.0, text="Status: Complete")


# ============================================================
# PAGE 1: OVERVIEW DASHBOARD
# ============================================================
if page == "📊 Overview Dashboard":
    st.title("⚡ Energy Intelligence Dashboard")
    st.caption("Milestone 1 — Agentic FacilityOps AI Platform")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Power", f"{summary['total_power']/1e6:.2f}M kW")
    col2.metric("HVAC Usage", f"{summary['total_hvac']/1e6:.2f}M kW")
    col3.metric("Lighting Usage", f"{summary['total_lighting']/1e6:.2f}M kW")
    col4.metric("Solar Generated", f"{summary['total_solar']/1e6:.2f}M kW")

    col5, col6, col7 = st.columns(3)
    col5.metric("Efficiency Score", f"{summary['efficiency']:.1f}%")
    col6.metric("Anomalies Found", f"{summary['anomalies']:,}")
    col7.metric("Data Points Analyzed", f"{summary['records']:,}")

    st.markdown("---")

    # Daily power trend chart
    st.subheader("Power Consumption Trend")
    daily = df.groupby("date")["Power[kW]"].sum().reset_index()
    fig = px.line(daily, x="date", y="Power[kW]", template="plotly_dark")
    fig.update_traces(line_color="#38bdf8", line_width=2)
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=350)
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Energy Breakdown by System")
        breakdown = pd.DataFrame({
            "System": ["HVAC", "Lighting", "Chiller", "Other"],
            "Power (kW)": [
                summary["total_hvac"],
                summary["total_lighting"],
                summary["total_chiller"],
                max(summary["total_power"] - summary["total_hvac"] - summary["total_lighting"] - summary["total_chiller"], 0)
            ]
        })
        fig2 = px.pie(breakdown, names="System", values="Power (kW)", hole=0.5,
                       color_discrete_sequence=["#38bdf8", "#F9E795", "#F96167", "#9AA3C7"])
        fig2.update_layout(paper_bgcolor="#0f172a", font_color="white", height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.subheader("Average Power by Hour of Day")
        hourly = df.groupby("hour")["Power[kW]"].mean().reset_index()
        fig3 = px.bar(hourly, x="hour", y="Power[kW]", template="plotly_dark")
        fig3.update_traces(marker_color="#38bdf8")
        fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=350)
        st.plotly_chart(fig3, use_container_width=True)


# ============================================================
# PAGE 2: ANOMALY ANALYTICS
# ============================================================
elif page == "🔍 Anomaly Analytics":
    st.title("🔍 Anomaly Analytics")
    st.caption("Detection of abnormal energy consumption patterns")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", f"{summary['records']:,}")
    col2.metric("Anomalies Detected", f"{summary['anomalies']:,}")
    threshold = df["Power[kW]"].mean() + 2 * df["Power[kW]"].std()
    col3.metric("Anomaly Threshold", f"{threshold:.2f} kW")

    st.markdown("---")
    st.subheader("Power Readings with Anomalies Highlighted")

    sample = df.sample(min(5000, len(df)), random_state=42).sort_values("Time")
    fig = go.Figure()
    normal = sample[~sample["is_anomaly"]]
    anomalous = sample[sample["is_anomaly"]]

    fig.add_trace(go.Scatter(x=normal["Time"], y=normal["Power[kW]"], mode="markers",
                              marker=dict(color="#38bdf8", size=4), name="Normal"))
    fig.add_trace(go.Scatter(x=anomalous["Time"], y=anomalous["Power[kW]"], mode="markers",
                              marker=dict(color="#f87171", size=6), name="Anomaly"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detected Anomaly Events")
    anomaly_table = df[df["is_anomaly"]][["Time", "Power[kW]", "HVAC Actual [kW]", "HV light Power [kW]"]].head(20)
    st.dataframe(anomaly_table, use_container_width=True)


# ============================================================
# PAGE 3: AI RECOMMENDATIONS
# ============================================================
elif page == "💡 AI Recommendations":
    st.title("💡 AI Recommendations")
    st.caption("Smart suggestions generated by the Energy Agent")

    st.markdown("### Based on the analysis of your facility's energy data:")
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f'<div class="rec-box"><b>{i}.</b> {rec}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Potential Impact")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="alert-box"><b>⚠ High HVAC Usage</b><br>Reducing off-hours HVAC runtime by 20% could save an estimated 265,000+ kW over the year.</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="alert-box"><b>⚠ Lighting Waste</b><br>Motion-sensor lighting could reduce lighting energy use by up to 30%.</div>', unsafe_allow_html=True)


# ============================================================
# PAGE 4: DEEP INSIGHTS
# ============================================================
elif page == "📈 Deep Insights":
    st.title("📈 Deep Insights")
    st.caption("Additional patterns in facility energy behavior")

    st.subheader("Average Power by Day of Week")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df.groupby("day_of_week")["Power[kW]"].mean().reindex(dow_order).reset_index()
    fig = px.bar(dow, x="day_of_week", y="Power[kW]", template="plotly_dark")
    fig.update_traces(marker_color="#F9E795")
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Solar Generation vs Total Power (Daily)")
    daily2 = df.groupby("date").agg({"Power[kW]": "sum"}).reset_index()
    daily_solar = df.groupby("date")["PV panels power [kW]"].apply(lambda x: x.abs().sum()).reset_index()
    daily2 = daily2.merge(daily_solar, on="date")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=daily2["date"], y=daily2["Power[kW]"], name="Total Power", line=dict(color="#38bdf8")))
    fig2.add_trace(go.Scatter(x=daily2["date"], y=daily2["PV panels power [kW]"], name="Solar Generated", line=dict(color="#F9E795")))
    fig2.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Raw Data Sample")
    st.dataframe(df.head(50), use_container_width=True)

# ============================================================
# PAGE 5: PREDICTIVE MAINTENANCE (Milestone 2)
# ============================================================
elif page == "🔧 Predictive Maintenance":
    st.title("🔧 Predictive Maintenance")
    st.caption("Milestone 2 — Asset Health Monitoring & Maintenance Predictions")

    @st.cache_data
    def load_maintenance_data():
        mdf = pd.read_csv("maintenance_data.csv")
        return mdf

    mdf = load_maintenance_data()

    total_assets = len(mdf)
    avg_health = mdf["health_score"].mean()
    critical_count = len(mdf[mdf["status"] == "Critical"])
    at_risk_count = len(mdf[mdf["status"] == "At Risk"])
    watch_count = len(mdf[mdf["status"] == "Watch"])
    healthy_count = len(mdf[mdf["status"] == "Healthy"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Assets", total_assets)
    col2.metric("Avg Health Score", f"{avg_health:.1f}/100")
    col3.metric("Healthy", healthy_count)
    col4.metric("At Risk", at_risk_count)
    col5.metric("Critical", critical_count)

    st.markdown("---")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Asset Status Distribution")
        status_counts = mdf["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        color_map = {"Healthy": "#4ade80", "Watch": "#F9E795", "At Risk": "#fb923c", "Critical": "#f87171"}
        fig = px.pie(status_counts, names="Status", values="Count", hole=0.5,
                      color="Status", color_discrete_map=color_map)
        fig.update_layout(paper_bgcolor="#0f172a", font_color="white", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Health Score by Asset Type")
        type_health = mdf.groupby("asset_type")["health_score"].mean().reset_index().sort_values("health_score")
        fig2 = px.bar(type_health, x="health_score", y="asset_type", orientation="h", template="plotly_dark")
        fig2.update_traces(marker_color="#38bdf8")
        fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=350)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("⚠️ Urgent Maintenance Needed (Next 14 Days)")
    urgent = mdf[mdf["predicted_days_to_maintenance"] <= 14].sort_values("predicted_days_to_maintenance")
    if len(urgent) > 0:
        for _, row in urgent.iterrows():
            color = "#f87171" if row["status"] == "Critical" else "#fb923c"
            st.markdown(
                f'<div style="background-color:#1e293b; border-left:4px solid {color}; '
                f'padding:12px 16px; border-radius:8px; margin-bottom:8px;">'
                f'<b style="color:{color};">[{row["status"]}]</b> '
                f'<b>{row["asset_name"]}</b> — {row["zone"]}<br>'
                f'Health Score: {row["health_score"]} &nbsp;|&nbsp; '
                f'Due in {row["predicted_days_to_maintenance"]} days'
                f'</div>', unsafe_allow_html=True
            )
    else:
        st.success("No urgent maintenance needed in the next 14 days.")

    st.markdown("---")
    st.subheader("All Assets — Health Overview")
    display_df = mdf[["asset_id", "asset_name", "zone", "health_score", "status",
                       "days_since_maintenance", "predicted_days_to_maintenance"]].sort_values("health_score")
    st.dataframe(display_df, use_container_width=True, height=400)

    st.markdown("---")
    st.subheader("Vibration vs Temperature Deviation (Anomaly View)")
    fig3 = px.scatter(mdf, x="vibration_mm_s", y="temp_deviation_c", color="status",
                       hover_data=["asset_name", "zone"],
                       color_discrete_map={"Healthy": "#4ade80", "Watch": "#F9E795",
                                           "At Risk": "#fb923c", "Critical": "#f87171"},
                       template="plotly_dark")
    fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=400)
    st.plotly_chart(fig3, use_container_width=True)
