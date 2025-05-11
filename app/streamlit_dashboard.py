"""
Streamlit Dashboard for HR Analytics.

This dashboard provides insights into employee data, including absence rates,
contract distribution, gender distribution, and more. It connects to a SQLite
database and uses Plotly for visualizations.
"""

import sqlite3
import plotly.express as px
import streamlit as st
import pandas as pd

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
df_salary = pd.read_sql("SELECT * FROM salary_statement", conn)
print(df_salary.dtypes)
print(df_salary.head(3))


df_salary["net_salary"] = (
    df_salary["net_salary"]
    .astype(str)  # au cas où il y a des NaN
    .str.replace(",", ".", regex=False)  # remplace les virgules décimales
    .str.extract(r"([-+]?\d*\.\d+|\d+)")  # extrait le premier nombre valide
    .astype(float)
)

df_salary["gross_salary_108"] = (
    df_salary["gross_salary_108"]
    .fillna("")  # Remplace les NaN par des chaînes vides
    .astype(str)  # Convertit en chaîne
    .str.replace(",", ".", regex=False)  # Remplace les virgules décimales
    .str.extract(r"([-+]?\d*\.\d+|\d+)")  # Extrait le premier nombre valide
    .astype(float)  # Convertit en float
)

df_salary["gross_salary"] = (
    df_salary["gross_salary"]
    .fillna("")
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"([-+]?\d*\.\d+|\d+)")
    .astype(float)
)



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

# ----------------------------
# 💰 Salary Analysis Section
# ----------------------------
st.markdown("## 💰 Salary Analysis")

if df_salary["net_salary"].notna().sum() == 0:
    st.info("No salary data available.")
else:
    # Average salary
    avg_salary = df_salary["net_salary"].mean()
    st.metric("💶 Average Net Salary", f"{avg_salary:.2f} €")

    # Trend over time
    st.subheader("📈 Net Salary Trend Over Time")
    df_salary["period"] = pd.to_datetime(df_salary["period"], errors="coerce")
    df_trend = (
        df_salary.dropna(subset=["period"])
        .groupby("period")["net_salary"]
        .mean()
        .reset_index()
        .sort_values("period")
    )

    fig_trend = px.line(
        df_trend,
        x="period",
        y="net_salary",
        title="Average Net Salary Over Time",
        markers=True,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Distribution
    filtered = df_salary[(df_salary["gross_salary"] >= 300) & (df_salary["gross_salary"] <= 5000)]

    st.subheader("📊 Gross Salary distribution")

    fig_dist = px.histogram(
        filtered,
        x="gross_salary",
        nbins=30,
        title="Gross Salary Distribution (300€–5000€)",
    )

    st.plotly_chart(fig_dist, use_container_width=True)







    filtered = df_salary[(df_salary["net_salary"] >= 300) & (df_salary["net_salary"] <= 5000)]

    st.subheader("📊 Net Salary Distribution (Filtered)")
    fig_dist = px.histogram(
        filtered,
        x="net_salary",
        nbins=30,
        title="Net Salary Distribution (300€–5000€)",
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    st.subheader("📊 Gross Salary 108 Distribution (Filtered)")

    filtered_108 = df_salary[
    (df_salary["gross_salary_108"] >= 300) & (df_salary["gross_salary_108"] <= 5000)
    ]

   
    fig_dist_108 = px.histogram(
        filtered_108,
        x="gross_salary_108",
        nbins=30,
        title="Gross Salary 108 Distribution (300€–5000€)",
    )
    st.plotly_chart(fig_dist_108, use_container_width=True)




    
