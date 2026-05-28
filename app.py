import streamlit as st
import pandas as pd
import plotly.express as px

from database.db import (
    create_tables,
    insert_claim,
    fetch_all_claims,
    update_claim_status
)

from validation.validator import validate_claims

create_tables()
# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Expense Claim System",
    layout="wide"
)

st.title(
    "Employee Expense Claim Validation & Analytics Platform"
)

# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

portal = st.sidebar.selectbox(
    "Select Portal",
    [
        "Employee Portal",
        "Admin Portal"
    ]
)

# ==========================================================
# EMPLOYEE PORTAL
# ==========================================================

if portal == "Employee Portal":

    st.header("Employee Portal")

    with st.form("claim_form"):

        employee_id = st.text_input(
            "Employee ID"
        )

        department = st.selectbox(
            "Department",
            [
                "IT",
                "HR",
                "Finance",
                "Sales"
            ]
        )

        expense_category = st.selectbox(
            "Expense Category",
            [
                "Food",
                "Local Travel",
                "Hotel",
                "Internet",
                "Office Supplies"
            ]
        )

        claim_amount = st.number_input(
            "Claim Amount",
            min_value=0.0
        )

        expense_date = st.date_input(
            "Expense Date"
        )

        currency = st.selectbox(
            "Currency",
            [
                "INR",
                "USD"
            ]
        )

        bill = st.file_uploader(
            "Upload Bill",
            type=[
                "png",
                "jpg",
                "jpeg",
                "pdf"
            ]
        )

        submit_button = st.form_submit_button(
            "Submit Claim"
        )

        # ==================================================
        # SUBMIT CLAIM
        # ==================================================

        if submit_button:

            all_claims = fetch_all_claims()

            claim_id = f"C{len(all_claims)+1:03}"

            bill_available = (
                "Yes"
                if bill is not None
                else "No"
            )

            data = {
                "claim_id": [claim_id],
                "employee_id": [employee_id],
                "department": [department],
                "expense_date": [expense_date],
                "expense_category": [expense_category],
                "claim_amount": [claim_amount],
                "currency": [currency],
                "bill_available": [bill_available],
                "manager_approval": ["Pending"],
                "payment_status": ["Pending"]
            }

            df = pd.DataFrame(data)

            validated_df = validate_claims(df)

            insert_claim(validated_df)

            st.success(
                "Claim Submitted Successfully"
            )

            st.subheader("Claim Status")

            st.dataframe(validated_df)

    # ======================================================
    # VIEW EMPLOYEE CLAIMS
    # ======================================================

    st.subheader("Your Claims")

    all_claims = fetch_all_claims()

    employee_filter = st.text_input(
        "Enter Employee ID"
    )

    if employee_filter:

        filtered_df = all_claims[
            all_claims["employee_id"] == employee_filter
        ]

        # DISPLAY CLAIMS

        st.dataframe(filtered_df)

        # POLICY VIOLATION DETAILS

        st.subheader("Policy Violation Details")

        violation_df = filtered_df[
            filtered_df["policy_violation"] == "Yes"
        ]

        if len(violation_df) > 0:

            st.warning(
                "Some claims have policy violations"
            )

            st.dataframe(
                violation_df[
                    [
                        "claim_id",
                        "expense_category",
                        "claim_amount",
                        "violation_reason",
                        "final_claim_status"
                    ]
                ]
            )

        else:

            st.success(
                "No policy violations found"
            )

# ==========================================================
# ADMIN PORTAL
# ==========================================================

elif portal == "Admin Portal":

    st.header("Admin Portal")

    uploaded_file = st.file_uploader(
        "Upload CSV/Excel",
        type=["csv", "xlsx"]
    )

    validated_df = None

    if uploaded_file is not None:

        # ==================================================
        # READ FILE
        # ==================================================

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        else:

            df = pd.read_excel(uploaded_file)

        # ==================================================
        # RAW CLAIMS
        # ==================================================

        st.subheader("Raw Claims")

        st.dataframe(df)

        # ==================================================
        # VALIDATE CLAIMS
        # ==================================================

        validated_df = validate_claims(df)

        # ==================================================
        # INSERT INTO DATABASE
        # ==================================================

        insert_claim(validated_df)

        # ==================================================
        # VALIDATED CLAIMS
        # ==================================================

        st.subheader("Validated Claims")

        st.dataframe(validated_df)

        # ==================================================
        # KPI METRICS
        # ==================================================

        st.subheader("KPI Metrics")

        total_claims = len(validated_df)

        approved_amount = validated_df[
            validated_df["manager_approval"] == "Approved"
        ]["claim_amount"].sum()

        rejected_amount = validated_df[
            validated_df["manager_approval"] == "Rejected"
        ]["claim_amount"].sum()

        policy_violations = len(
            validated_df[
                validated_df["policy_violation"] == "Yes"
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Claims",
            total_claims
        )

        col2.metric(
            "Approved Amount",
            f"₹ {approved_amount}"
        )

        col3.metric(
            "Rejected Amount",
            f"₹ {rejected_amount}"
        )

        col4.metric(
            "Policy Violations",
            policy_violations
        )

        # ==================================================
        # ANALYTICS DASHBOARD
        # ==================================================

        st.subheader("Analytics Dashboard")

        # CATEGORY CHART

        category_data = validated_df.groupby(
            "expense_category"
        )["claim_amount"].sum().reset_index()

        fig1 = px.bar(
            category_data,
            x="expense_category",
            y="claim_amount",
            title="Expense By Category"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # DEPARTMENT CHART

        dept_data = validated_df.groupby(
            "department"
        )["claim_amount"].sum().reset_index()

        fig2 = px.pie(
            dept_data,
            names="department",
            values="claim_amount",
            title="Expense By Department"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # MONTHLY TREND

        monthly_data = validated_df.groupby(
            "expense_month"
        )["claim_amount"].sum().reset_index()

        fig3 = px.line(
            monthly_data,
            x="expense_month",
            y="claim_amount",
            title="Monthly Expense Trend"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # POLICY VIOLATION SUMMARY

        violation_data = validated_df[
            "policy_violation"
        ].value_counts().reset_index()

        violation_data.columns = [
            "Violation",
            "Count"
        ]

        fig4 = px.bar(
            violation_data,
            x="Violation",
            y="Count",
            title="Policy Violation Summary"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

        # ==================================================
        # DOWNLOAD REPORT
        # ==================================================

        csv = validated_df.to_csv(index=False)

        st.download_button(
            label="Download Validated Report",
            data=csv,
            file_name="validated_claims.csv",
            mime="text/csv"
        )

    # ======================================================
    # VIEW ALL CLAIMS
    # ======================================================

    st.subheader("All Employee Claims")

    all_claims = fetch_all_claims()

    st.dataframe(all_claims)

    # ======================================================
    # APPROVE / REJECT CLAIMS
    # ======================================================

    st.subheader("Approve / Reject Claims")

    selected_claim = st.selectbox(
        "Select Claim ID",
        all_claims["claim_id"].unique()
    )

    action = st.radio(
        "Choose Action",
        ["Approved", "Rejected"]
    )

    if st.button("Update Claim Status"):

        update_claim_status(
            selected_claim,
            action
        )

        st.success(
            f"Claim {selected_claim} marked as {action}"
        )

        updated_df = fetch_all_claims()

        updated_claim = updated_df[
            updated_df["claim_id"] == selected_claim
        ]

        st.subheader("Updated Claim")

        st.dataframe(updated_claim)
