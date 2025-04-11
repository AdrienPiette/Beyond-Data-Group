import sqlite3
import plotly.express as px
import streamlit as st

from model import (
    absences_by_type,
    average_absence_rate_by_firm,
    average_age_by_firm,
    contract_type_distribution_by_firm,
    enrich_absence_with_type,
    gender_distribution_by_firm,
    load_absence_type,
    load_data,
    total_employees_by_firm,
)

# Database connection
conn = sqlite3.connect(
    r"C:\Users\pieta\OneDrive\Bureau\Beyond Data Group\Beyond-Data-Group\notebooks\fabric_sim.db"
)
df = load_data(conn)
df_abs_type = load_absence_type(conn)

# UI
st.set_page_config(page_title="HR Dashboard", layout="wide")
st.title("📊 HR Dashboard - Power BI Simulation")

# Company selector
firm_ids = df["firm_id"].dropna().unique()
selected_firm = st.selectbox("🏢 Choose a company", sorted(firm_ids))

# Data filtering
df_firm = df[df["firm_id"] == selected_firm]

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_emp = total_employees_by_firm(df_firm)["employee_count"].values[0]
    st.metric("👥 Employees", total_emp)

with col2:
    avg_abs = average_absence_rate_by_firm(df_firm)["absence_rate"].values[0]
    st.metric("📉 Absence rate", f"{avg_abs * 100:.2f} %")

with col3:
    total_abs = df_firm["total_absence_days"].sum()
    st.metric("📆 Absence days", f"{int(total_abs)} d")

with col4:
    avg_age = average_age_by_firm(df_firm)["average_age"].values[0]
    st.metric("🎂 Average age", f"{avg_age:.1f} years")

# Chart: contract distribution
st.subheader("📑 Contract distribution")
contract_dist = contract_type_distribution_by_firm(df_firm)

fig_contract = px.bar(
    contract_dist,
    x="contract_type",
    y="count",
    title="Contract types",
    labels={"count": "Count", "contract_type": "Contract"},
    text_auto=True,
)
st.plotly_chart(fig_contract, use_container_width=True)

# Chart: gender distribution
st.subheader("🧑‍🤝‍🧑 Gender distribution")
gender_dist = gender_distribution_by_firm(df_firm)

fig_gender = px.bar(
    gender_dist,
    x="gender",
    y="employee_count",
    title="Gender distribution",
    labels={"employee_count": "Count", "gender": "Gender"},
    text_auto=True,
)
st.plotly_chart(fig_gender, use_container_width=True)

# Chart: absence types
st.subheader("💥 Absence types")
df_enriched_abs = enrich_absence_with_type(df_firm, df_abs_type)
absence_summary = absences_by_type(df_enriched_abs)

if not absence_summary.empty:
    fig_abs = px.pie(
        absence_summary,
        values="days",
        names="type_absence_fr",
        title="Absence distribution by type",
        hole=0.3,
    )
    st.plotly_chart(fig_abs, use_container_width=True)
else:
    st.info("No absences recorded for this company.")
