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

# --- Connexion à la base SQLite ---
conn = sqlite3.connect("fabric_sim.db")
df = load_data(conn)

# --- UI ---
st.set_page_config(page_title="Dashboard RH", layout="wide")
st.title("📊 Dashboard RH - Simulation Power BI")

# --- Sélecteur entreprise ---
firm_ids = df['firm_id'].dropna().unique()
selected_firm = st.selectbox("Choisir une entreprise", sorted(firm_ids))

df_firm = df[df['firm_id'] == selected_firm]

# --- KPIs ---
col1, col2 = st.columns(2)

with col1:
    total_emp = total_employees_by_firm(df_firm)['employee_count'].values[0]
    st.metric("👥 Employés", total_emp)

with col2:
    avg_abs = average_absence_rate_by_firm(df_firm)['absence_rate'].values[0]
    st.metric("📉 Taux d'absence moyen", f"{avg_abs * 100:.2f} %")

# --- Graphique : Répartition des contrats ---
st.subheader("📑 Répartition des contrats")
contract_dist = contract_type_distribution_by_firm(df_firm)

fig = px.bar(contract_dist,
             x="contract_type",
             y="count",
             title=f"Types de contrats - Entreprise {selected_firm}",
             labels={"count": "Nombre d'employés", "contract_type": "Type de contrat"})

st.plotly_chart(fig, use_container_width=True)
