import streamlit as st
import sqlite3
import plotly.express as px
from model import (
    load_data,
    total_employees_by_firm,
    average_absence_rate_by_firm,
    contract_type_distribution_by_firm,
    filter_by_contract_type
)

# Connexion à la base
conn = sqlite3.connect(r"C:\Users\pieta\OneDrive\Bureau\Beyond Data Group\Beyond-Data-Group\notebooks\fabric_sim.db")
df = load_data(conn)

# UI Streamlit
st.set_page_config(page_title="Dashboard RH", layout="wide")
st.title("📊 Dashboard RH - Simulation Power BI")

# Sélecteur d'entreprise
firm_ids = df['firm_id'].dropna().unique()
selected_firm = st.selectbox("🏢 Choisir une entreprise", sorted(firm_ids))

# Filtrage
df_firm = df[df['firm_id'] == selected_firm]

# --- KPIs principaux ---
col1, col2, col3 = st.columns(3)

with col1:
    total_emp = total_employees_by_firm(df_firm)['employee_count'].values[0]
    st.metric("👥 Nombre d'employés", total_emp)

with col2:
    avg_abs = average_absence_rate_by_firm(df_firm)['absence_rate'].values[0]
    st.metric("📉 Taux d'absence moyen", f"{avg_abs * 100:.2f} %")

with col3:
    total_abs = df_firm['total_absence_days'].sum()
    st.metric("📆 Jours d'absence total", f"{int(total_abs)} j")

# --- Graphique : répartition des contrats ---
st.subheader("📑 Répartition des types de contrat")
contract_dist = contract_type_distribution_by_firm(df_firm)

fig = px.bar(
    contract_dist,
    x="contract_type",
    y="count",
    title=f"Répartition des contrats - Entreprise {selected_firm}",
    labels={"count": "Nombre d'employés", "contract_type": "Type de contrat"},
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)
