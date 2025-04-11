import pandas as pd

def load_data(conn):
    """
    Charge les données principales avec jointure sur firm_id et person_id.
    Retourne un DataFrame enrichi.
    """
    # Lecture des tables
    contract = pd.read_sql("SELECT * FROM contract_basis", conn)
    absences = pd.read_sql("SELECT * FROM absence", conn)

    # Merge logique
    df = contract.merge(absences, on=["person_id", "firm_id"], how="left")

    # Calculs
    if 'absence_days' in df.columns and 'planned_days' in df.columns:
        df['absence_rate'] = df['absence_days'] / df['planned_days']
    else:
        df['absence_rate'] = None

    return df


# === MESURES SÉMANTIQUES ===

def total_employees_by_firm(df):
    """Nombre total d'employés par entreprise"""
    return df.groupby("firm_id")["person_id"].nunique().reset_index(name="employee_count")

def average_absence_rate_by_firm(df):
    """Taux d'absence moyen par entreprise"""
    return df.groupby("firm_id")["absence_rate"].mean().reset_index()

def contract_type_distribution_by_firm(df):
    """Répartition des types de contrats par entreprise"""
    return df.groupby(["firm_id", "contract_type"])["person_id"].count().reset_index(name="count")

def filter_by_contract_type(df, contract_type="CDI"):
    """Filtre le DataFrame pour un certain type de contrat"""
    return df[df["contract_type"] == contract_type]
