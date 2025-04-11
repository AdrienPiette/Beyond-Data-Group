from datetime import datetime

import pandas as pd


def load_data(conn):
    """
    Loads and processes data from a database connection.
    This function retrieves data from two database tables, `absence` and 
    `contract_basis`, merges them, and performs data cleaning and calculations 
    to compute total absence days and absence rate for each record.
    Args:
        conn (sqlalchemy.engine.Connection or similar): 
            A database connection object used to execute SQL queries.
    Returns:
        pandas.DataFrame: 
            A DataFrame containing the merged and processed data with the 
            following additional columns:
            - `total_absence_days`: Total absence days calculated by summing 
              all absence-related columns.
            - `absence_rate`: Absence rate calculated as the ratio of total 
              absence days to working days. Infinite values are replaced with 
              None.
    """

    absence = pd.read_sql("SELECT * FROM absence", conn)
    contract = pd.read_sql("SELECT * FROM contract_basis", conn)

    df = contract.merge(
        absence,
        on=["firm_id", "person_id", "department_id", "category_id"],
        how="left",
    )

    # Identify absence columns by code
    absence_columns = [
        col for col in df.columns if col.startswith("qty_") and col.endswith("_days")
    ]

    # Cleaning + conversion
    df[absence_columns] = df[absence_columns].fillna(0)
    for col in absence_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate total absence days for all causes
    df["total_absence_days"] = df[absence_columns].sum(axis=1)

    # Calculate absence rate
    df["absence_rate"] = df["total_absence_days"] / df["qty_working_days"]
    df["absence_rate"] = df["absence_rate"].replace(
        [float("inf"), -float("inf")], None
    )

    return df


def load_absence_type(conn):
    """
    Fetches all records from the 'absence_type' table in the database.
    Args:
        conn (sqlite3.Connection or sqlalchemy.engine.base.Connection): 
            A database connection object.
    Returns:
        pandas.DataFrame: A DataFrame containing all rows from the 'absence_type' table.
    """

    return pd.read_sql("SELECT * FROM absence_type", conn)


# === SEMANTIC MEASURES ===


def total_employees_by_firm(df):
    """
    Calculate the total number of unique employees for each firm.

    This function groups the input DataFrame by the 'firm_id' column and counts
    the number of unique 'person_id' values for each firm. The result is a new
    DataFrame with two columns: 'firm_id' and 'employee_count'.

    Args:
        df (pandas.DataFrame): A DataFrame containing at least the columns 
            'firm_id' and 'person_id'. 'firm_id' represents the firm identifier, 
            and 'person_id' represents the unique identifier for each employee.

    Returns:
        pandas.DataFrame: A DataFrame with two columns:
            - 'firm_id': The unique identifier for each firm.
            - 'employee_count': The total number of unique employees in each firm.
    """
    return (
        df.groupby("firm_id")["person_id"]
        .nunique()
        .reset_index(name="employee_count")
    )


def average_absence_rate_by_firm(df):
    """
    Calculate the average absence rate for each firm.

    This function groups the input DataFrame by the "firm_id" column and computes
    the mean of the "absence_rate" column for each firm. The result is returned
    as a new DataFrame with "firm_id" and the corresponding average absence rate.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing at least the columns "firm_id" 
                           and "absence_rate".

    Returns:
    pandas.DataFrame: A DataFrame with two columns:
                      - "firm_id": The unique identifier for each firm.
                      - "absence_rate": The average absence rate for the firm.
    """
    return df.groupby("firm_id")["absence_rate"].mean().reset_index()


def contract_type_distribution_by_firm(df):
    return (
        df.groupby(["firm_id", "contract_type"])["person_id"]
        .count()
        .reset_index(name="count")
    )


def filter_by_contract_type(df, contract_type="CDI"):
    return df[df["contract_type"] == contract_type]


# === ENRICHMENT WITH absence_type ===


def enrich_absence_with_type(absence_df, absence_type_df):
    """
    Enriches an absence DataFrame with absence type information.
    This function processes an absence DataFrame by melting it into a long format,
    extracting absence codes, and merging it with a reference DataFrame containing
    absence type information. It filters out rows where the number of absence days
    is zero or less.
    Args:
        absence_df (pd.DataFrame): A DataFrame containing absence data. It must include
            columns for firm, department, category, person, year, month, and columns
            with absence quantities (e.g., "qty_p1_days").
        absence_type_df (pd.DataFrame): A reference DataFrame containing absence type
            information. It must include a column named "type_absence" that maps to
            absence codes.
    Returns:
        pd.DataFrame: A DataFrame in long format with enriched absence data, including
        absence type information. The resulting DataFrame contains only rows with
        positive absence days.
    """

    qty_columns = [
        col
        for col in absence_df.columns
        if col.startswith("qty_") and col.endswith("_days")
    ]

    melted = absence_df.melt(
        id_vars=[
            "firm_id",
            "department_id",
            "category_id",
            "person_id",
            "year",
            "month",
        ],
        value_vars=qty_columns,
        var_name="absence_code_col",
        value_name="days",
    )

    # Extract absence code (e.g., qty_p1_days → P1)
    melted["type_absence_code"] = (
        melted["absence_code_col"]
        .str.extract(r"qty_([a-z0-9]+)_days", expand=False)
        .str.upper()
    )

    # Rename column for merging
    absence_type_df = absence_type_df.rename(
        columns={"type_absence": "type_absence_code"}
    )

    # Merge with reference table
    enriched = melted.merge(absence_type_df, on="type_absence_code", how="left")

    # Keep only actual absences
    enriched = enriched[enriched["days"] > 0]

    return enriched


def absences_by_type(enriched_absences_df):
    """
    Summarizes absences by type and sorts them in descending order of total days.
    Args:
        enriched_absences_df (pd.DataFrame): A DataFrame containing absence data with at least 
            the columns 'type_absence_fr' (type of absence) and 'days' (number of days).
    Returns:
        pd.DataFrame: A DataFrame with two columns:
            - 'type_absence_fr': The type of absence.
            - 'days': The total number of days for each type of absence, sorted in descending order.
    """

    return (
        enriched_absences_df.groupby("type_absence_fr")["days"]
        .sum()
        .reset_index()
        .sort_values(by="days", ascending=False)
    )


def gender_distribution_by_firm(df):
    """
    Calculate the distribution of employees by gender for each firm.

    This function groups the input DataFrame by 'firm_id' and 'gender', 
    counts the unique 'person_id' values within each group, and returns 
    a new DataFrame with the employee count for each gender in each firm.

    Args:
        df (pandas.DataFrame): A DataFrame containing the following columns:
            - 'firm_id': Identifier for the firm.
            - 'gender': Gender of the employee.
            - 'person_id': Unique identifier for the employee.

    Returns:
        pandas.DataFrame: A DataFrame with the following columns:
            - 'firm_id': Identifier for the firm.
            - 'gender': Gender of the employees.
            - 'employee_count': Count of unique employees for each gender in each firm.
    """
    return (
        df.groupby(["firm_id", "gender"])["person_id"]
        .nunique()
        .reset_index(name="employee_count")
    )


def average_age_by_firm(df):
    """
    Calculate the average age of individuals grouped by firm.

    This function computes the age of individuals based on their birth dates
    and calculates the average age for each firm.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing at least the following columns:
            - 'birth_date' (str or datetime): The birth date of individuals.
            - 'firm_id' (int or str): The identifier for the firm.

    Returns:
        pd.DataFrame: A DataFrame with two columns:
            - 'firm_id': The identifier for the firm.
            - 'average_age': The average age of individuals in the firm, rounded to one decimal place.

    Notes:
        - Invalid or missing birth dates will be coerced to NaT.
        - The age is calculated as the difference between the current date and the birth date,
          divided by 365.25 to account for leap years.
    """
    today = pd.Timestamp(datetime.today())
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    df["age"] = ((today - df["birth_date"]).dt.days / 365.25).round(1)
    return df.groupby("firm_id")["age"].mean().reset_index(name="average_age")
