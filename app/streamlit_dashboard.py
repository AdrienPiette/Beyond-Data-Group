import streamlit as st
import sqlite3
import plotly.express as px
from model import (
    load_data,
    load_absence_type,
    enrich_absence_with_type,
    absences_by_type,
    total_employees_by_firm,
    average_absence_rate_by_firm,
    contract_type_distribution_by_firm,
    filter_by_contract_type
)

# Connexion DB
conn = sqlite3.connect(r"C:\Users\pieta\OneDrive\Bureau\Beyond Data Group\Beyond-Data-Group\notebooks\fabric_sim.db")
df = load_data(conn)
df_abs_type = load_absence_type(conn)

# UI
st.set_page_config(page_title="Dashboard RH", layout="wide")
st.title("📊 Dashboard RH - Simulation Power BI")

# Sélecteur entreprise
firm_ids = df['firm_id'].dropna().unique()
selected_firm = st.selectbox("🏢 Choisir une entreprise", sorted(firm_ids))

# Filtrage des données pour l'entreprise sélectionnée
df_firm = df[df['firm_id'] == selected_firm]

# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    total_emp = total_employees_by_firm(df_firm)['employee_count'].values[0]
    st.metric("👥 Employés", total_emp)

with col2:
    avg_abs = average_absence_rate_by_firm(df_firm)['absence_rate'].values[0]
    st.metric("📉 Taux d'absence moyen", f"{avg_abs * 100:.2f} %")

with col3:
    total_abs = df_firm['total_absence_days'].sum()
    st.metric("📆 Total jours d'absence", f"{int(total_abs)} j")

# Répartition des types de contrat
st.subheader("📑 Répartition des contrats")
contract_dist = contract_type_distribution_by_firm(df_firm)

fig_contract = px.bar(
    contract_dist,
    x="contract_type",
    y="count",
    title=f"Répartition des contrats - Entreprise {selected_firm}",
    labels={"count": "Nombre d'employés", "contract_type": "Type de contrat"},
    text_auto=True
)
st.plotly_chart(fig_contract, use_container_width=True)

# Répartition des types d'absence
st.subheader("💥 Types d'absence")
df_enriched_abs = enrich_absence_with_type(df_firm, df_abs_type)
absence_summary = absences_by_type(df_enriched_abs)

if not absence_summary.empty:
    fig_abs = px.pie(
        absence_summary,
        values="days",
        names="type_absence_fr",
        title="Répartition des absences par type",
        hole=0.3
    )
    st.plotly_chart(fig_abs, use_container_width=True)
else:
    st.info("Aucune absence enregistrée pour cette entreprise.")
