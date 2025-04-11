import pandas as pd

def load_data(conn):
    """
    Charge et fusionne les données contract_basis et absence.
    Calcule le total des jours d'absence et le taux d'absence.
    """
    absence = pd.read_sql("SELECT * FROM absence", conn)
    contract = pd.read_sql("SELECT * FROM contract_basis", conn)

    df = contract.merge(absence, on=["firm_id", "person_id", "department_id", "category_id"], how="left")

    # Identifier les colonnes d'absence par code
    absence_columns = [col for col in df.columns if col.startswith("qty_") and col.endswith("_days")]

    # Nettoyage + conversion
    df[absence_columns] = df[absence_columns].fillna(0)
    for col in absence_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calcul total jours d'absence toutes causes
    df['total_absence_days'] = df[absence_columns].sum(axis=1)

    # Calcul taux d'absence
    df['absence_rate'] = df['total_absence_days'] / df['qty_working_days']
    df['absence_rate'] = df['absence_rate'].replace([float('inf'), -float('inf')], None)

    return df

def load_absence_type(conn):
    """
    Charge la table absence_type (référentiel des codes d’absence)
    """
    return pd.read_sql("SELECT * FROM absence_type", conn)


# === MESURES SÉMANTIQUES ===

def total_employees_by_firm(df):
    return df.groupby("firm_id")["person_id"].nunique().reset_index(name="employee_count")

def average_absence_rate_by_firm(df):
    return df.groupby("firm_id")["absence_rate"].mean().reset_index()

def contract_type_distribution_by_firm(df):
    return df.groupby(["firm_id", "contract_type"])["person_id"].count().reset_index(name="count")

def filter_by_contract_type(df, contract_type="CDI"):
    return df[df["contract_type"] == contract_type]


# === ENRICHISSEMENT AVEC absence_type ===

def enrich_absence_with_type(absence_df, absence_type_df):
    """
    Transforme les colonnes qty_*_days en format long et les relie aux types d'absences.
    """
    qty_columns = [col for col in absence_df.columns if col.startswith("qty_") and col.endswith("_days")]

    melted = absence_df.melt(
        id_vars=["firm_id", "department_id", "category_id", "person_id", "year", "month"],
        value_vars=qty_columns,
        var_name="absence_code_col",
        value_name="days"
    )

    # Extraire le code d'absence (ex: qty_p1_days → P1)
    melted["type_absence_code"] = melted["absence_code_col"].str.extract(r"qty_([a-z0-9]+)_days", expand=False).str.upper()

    # Patch : renommer la colonne pour pouvoir merger
    absence_type_df = absence_type_df.rename(columns={"type_absence": "type_absence_code"})

    # Merge avec référentiel
    enriched = melted.merge(absence_type_df, on="type_absence_code", how="left")

    # Garder uniquement les absences réelles
    enriched = enriched[enriched["days"] > 0]

    return enriched


def absences_by_type(enriched_absences_df):
    """
    Agrège les absences par type pour affichage.
    """
    return enriched_absences_df.groupby("type_absence_fr")["days"].sum().reset_index().sort_values(by="days", ascending=False)
