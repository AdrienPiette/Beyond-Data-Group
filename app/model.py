import pandas as pd

def load_data(conn):
    """Charge et fusionne les données contractuelles et d'absence."""
    absence = pd.read_sql("SELECT * FROM absence", conn)
    contract = pd.read_sql("SELECT * FROM contract_basis", conn)

    # Fusion sur les clés communes
    df = contract.merge(absence, on=["firm_id", "person_id", "department_id", "category_id"], how="left")

    # Forcer les colonnes d'absence à float
    absence_columns = [col for col in df.columns if col.startswith("qty_") and col.endswith("_days")]
    df[absence_columns] = df[absence_columns].fillna(0)

    for col in absence_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calcul du total de jours d'absence
    df['total_absence_days'] = df[absence_columns].sum(axis=1)

    # Calcul du taux d'absence
    df['absence_rate'] = df['total_absence_days'] / df['qty_working_days']

    df['absence_rate'] = df['absence_rate'].replace([float('inf'), -float('inf')], None)

    return df


# === MESURES SÉMANTIQUES ===

def total_employees_by_firm(df):
    return df.groupby("firm_id")["person_id"].nunique().reset_index(name="employee_count")

def average_absence_rate_by_firm(df):
    return df.groupby("firm_id")["absence_rate"].mean().reset_index()

def contract_type_distribution_by_firm(df):
    return df.groupby(["firm_id", "contract_type"])["person_id"].count().reset_index(name="count")

def filter_by_contract_type(df, contract_type="CDI"):
    return df[df["contract_type"] == contract_type]
