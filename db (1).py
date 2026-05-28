import sqlite3
import pandas as pd

DB_NAME = "database.db"


def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():

    conn = create_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_claims (

        claim_id TEXT,
        employee_id TEXT,
        department TEXT,
        expense_date TEXT,
        expense_category TEXT,
        claim_amount REAL,
        currency TEXT,
        bill_available TEXT,
        manager_approval TEXT,
        payment_status TEXT,

        policy_limit REAL,
        policy_violation TEXT,
        missing_bill_flag TEXT,
        violation_reason TEXT,
        fraud_flag TEXT,

        final_claim_status TEXT,
        approved_amount REAL,
        rejected_amount REAL,
        expense_month TEXT
    )
    """)

    conn.commit()

    conn.close()


def insert_claim(df):

    conn = create_connection()

    # KEEP ONLY REQUIRED COLUMNS
    required_columns = [
        "claim_id",
        "employee_id",
        "department",
        "expense_date",
        "expense_category",
        "claim_amount",
        "currency",
        "bill_available",
        "manager_approval",
        "payment_status",
        "policy_limit",
        "policy_violation",
        "missing_bill_flag",
        "violation_reason",
        "fraud_flag",
        "final_claim_status",
        "approved_amount",
        "rejected_amount",
        "expense_month"
    ]

    df = df[required_columns]

    df.to_sql(
        "employee_claims",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()


def fetch_all_claims():

    conn = create_connection()

    query = "SELECT * FROM employee_claims"

    df = pd.read_sql(query, conn)

    conn.close()

    return df
# ======================================================
# UPDATE CLAIM STATUS
# ======================================================

# ======================================================
# UPDATE CLAIM STATUS
# ======================================================

def update_claim_status(claim_id, status):

    conn = create_connection()

    cursor = conn.cursor()

    payment_status = (
        "Paid"
        if status == "Approved"
        else "Rejected"
    )

    cursor.execute(
        """
        UPDATE employee_claims

        SET
            manager_approval = ?,
            payment_status = ?,
            final_claim_status = ?

        WHERE claim_id = ?
        """,
        (
            status,
            payment_status,
            status,
            claim_id
        )
    )

    conn.commit()

    conn.close()