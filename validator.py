import pandas as pd

# ==========================================================
# POLICY LIMITS
# ==========================================================

policy_limits = {
    "Food": 1000,
    "Local Travel": 2500,
    "Hotel": 5000,
    "Internet": 1500,
    "Office Supplies": 3000
}


# ==========================================================
# VIOLATION REASON FUNCTION
# ==========================================================

def get_violation_reason(row):

    reasons = []

    # Amount exceeds policy
    if row["claim_amount"] > row["policy_limit"]:
        reasons.append("Amount Exceeds Policy Limit")

    # Missing bill
    if row["bill_available"] == "No":
        reasons.append("Missing Bill")

    # No violations
    if len(reasons) == 0:
        return "No Violation"

    return ", ".join(reasons)


# ==========================================================
# FRAUD DETECTION FUNCTION
# ==========================================================

def get_fraud_flag(row):

    if row["claim_amount"] > 4000:
        return "High Risk"

    return "Low Risk"


# ==========================================================
# MAIN VALIDATION FUNCTION
# ==========================================================

def validate_claims(df):

    # ======================================================
    # REMOVE DUPLICATES
    # ======================================================

    df = df.drop_duplicates(subset=["claim_id"])

    # ======================================================
    # CONVERT DATE
    # ======================================================

    df["expense_date"] = pd.to_datetime(
        df["expense_date"],
        errors="coerce"
    )

    # ======================================================
    # REMOVE INVALID DATES
    # ======================================================

    df = df[df["expense_date"].notnull()]

    # ======================================================
    # REMOVE NEGATIVE AMOUNTS
    # ======================================================

    df = df[df["claim_amount"] > 0]

    # ======================================================
    # STANDARDIZE CATEGORY NAMES
    # ======================================================

    df["expense_category"] = df[
        "expense_category"
    ].str.title()

    # ======================================================
    # APPLY POLICY LIMITS
    # ======================================================

    df["policy_limit"] = df[
        "expense_category"
    ].map(policy_limits)

    # ======================================================
    # POLICY VIOLATION FLAG
    # ======================================================

    df["policy_violation"] = df.apply(
        lambda row:
        "Yes"
        if row["claim_amount"] > row["policy_limit"]
        else "No",
        axis=1
    )

    # ======================================================
    # MISSING BILL FLAG
    # ======================================================

    df["missing_bill_flag"] = df[
        "bill_available"
    ].apply(
        lambda x:
        "Yes"
        if x == "No"
        else "No"
    )

    # ======================================================
    # VIOLATION REASON
    # ======================================================

    df["violation_reason"] = df.apply(
        get_violation_reason,
        axis=1
    )

    # ======================================================
    # FINAL CLAIM STATUS
    # ======================================================

    df["final_claim_status"] = "Pending"

    # ======================================================
    # APPROVED AMOUNT
    # ======================================================

    df["approved_amount"] = df.apply(
        lambda row:
        row["claim_amount"]
        if row["final_claim_status"] == "Approved"
        else 0,
        axis=1
    )

    # ======================================================
    # REJECTED AMOUNT
    # ======================================================

    df["rejected_amount"] = df.apply(
        lambda row:
        row["claim_amount"]
        if row["final_claim_status"] == "Rejected"
        else 0,
        axis=1
    )

    # ======================================================
    # EXPENSE MONTH
    # ======================================================

    df["expense_month"] = df[
        "expense_date"
    ].dt.strftime("%Y-%m")

    # ======================================================
    # FRAUD FLAG
    # ======================================================

    df["fraud_flag"] = df.apply(
        get_fraud_flag,
        axis=1
    )

    # ======================================================
    # RETURN VALIDATED DATAFRAME
    # ======================================================

    return df