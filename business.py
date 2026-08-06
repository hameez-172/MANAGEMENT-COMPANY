import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import (
    add_deal,
    get_deals,
    update_deal,
    delete_deal,
    get_dashboard_stats
)


def business_tab():

    st.title("💼 Business Deals")

    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Revenue",
            f"Rs. {stats['Revenue']:,.0f}"
        )

    with col2:
        st.metric(
            "Profit",
            f"Rs. {stats['Profit']:,.0f}"
        )

    with col3:
        st.metric(
            "Received",
            f"Rs. {stats['Received']:,.0f}"
        )

    with col4:
        st.metric(
            "Remaining",
            f"Rs. {stats['Remaining']:,.0f}"
        )

    tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Deal",
    "📋 Manage Deals",
    "💰 Payments",
    "📊 Analytics"
    ])

    with tab4:
        business_analytics()
        
    with tab1:
        add_deal_tab()

    with tab2:
        manage_deals_tab()

    with tab3:
        payment_history_tab()

def add_deal_tab():

    st.subheader("Create New Deal")

    with st.form("add_deal_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:

            client_name = st.text_input(
                "Client Name"
            )

            service = st.text_input(
                "Service"
            )

            deal_value = st.number_input(
                "Deal Value (Rs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

            cost = st.number_input(
                "Cost (Rs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

        with col2:

            sent_payment = st.number_input(
                "Payment Received (Rs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "Bank Transfer",
                    "JazzCash",
                    "EasyPaisa",
                    "Credit Card",
                    "Other"
                ]
            )

            due_date = st.date_input(
                "Due Date"
            )

        notes = st.text_area(
            "Notes",
            height=120
        )

        submitted = st.form_submit_button(
            "💾 Save Deal",
            use_container_width=True
        )

        if submitted:

            if client_name.strip() == "":
                st.error("Client Name is required.")

            elif service.strip() == "":
                st.error("Service is required.")

            elif deal_value <= 0:
                st.error("Deal Value must be greater than zero.")

            else:

                add_deal(
                    client_name=client_name,
                    service=service,
                    deal_value=deal_value,
                    cost=cost,
                    sent_payment=sent_payment,
                    payment_method=payment_method,
                    due_date=str(due_date),
                    notes=notes
                )

                st.success("✅ Deal added successfully.")

                st.rerun()

def manage_deals_tab():

    st.subheader("Manage Business Deals")

    deals = get_deals()

    if deals.empty:
        st.info("No deals found.")
        return

    # -----------------------------
    # SUMMARY
    # -----------------------------

    revenue = deals["deal_value"].sum()
    received = deals["sent_payment"].sum()
    remaining = deals["remaining"].sum()
    profit = deals["profit"].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", f"Rs. {revenue:,.0f}")
    c2.metric("Received", f"Rs. {received:,.0f}")
    c3.metric("Remaining", f"Rs. {remaining:,.0f}")
    c4.metric("Profit", f"Rs. {profit:,.0f}")

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input(
            "Search Client / Service"
        )

    with col2:
        status = st.selectbox(
            "Status",
            [
                "All",
                "Pending",
                "Partial",
                "Paid"
            ]
        )

    with col3:
        payment = st.selectbox(
            "Payment Method",
            ["All"] +
            sorted(
                deals["payment_method"].dropna().unique().tolist()
            )
        )

    filtered = deals.copy()

    if search:

        search = search.lower()

        filtered = filtered[
            filtered["client_name"].str.lower().str.contains(search)
            |
            filtered["service"].str.lower().str.contains(search)
        ]

    if status != "All":

        filtered = filtered[
            filtered["status"] == status
        ]

    if payment != "All":

        filtered = filtered[
            filtered["payment_method"] == payment
        ]

    # -----------------------------
    # DISPLAY TABLE
    # -----------------------------

    display = filtered.copy()

    def highlight_remaining(value):

        if value > 0:
            return "background-color:#ffcccc;color:red;font-weight:bold"

        return ""

    styled = display.style.map(
        highlight_remaining,
        subset=["remaining"]
    )

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Export CSV",
        display.to_csv(index=False).encode("utf-8"),
        "business_deals.csv",
        "text/csv",
        use_container_width=True
    )

    st.divider()

    # -----------------------------
    # EDIT DEAL
    # -----------------------------

    st.subheader("Edit Deal")

    deal_id = st.selectbox(
        "Select Deal",
        display["id"]
    )

    row = display[
        display["id"] == deal_id
    ].iloc[0]

    with st.form("edit_deal"):

        client = st.text_input(
            "Client",
            row["client_name"]
        )

        service = st.text_input(
            "Service",
            row["service"]
        )

        c1, c2 = st.columns(2)

        with c1:

            value = st.number_input(
                "Deal Value",
                value=float(row["deal_value"])
            )

            cost = st.number_input(
                "Cost",
                value=float(row["cost"])
            )

            payment_received = st.number_input(
                "Received",
                value=float(row["sent_payment"])
            )

        with c2:

            method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "Bank Transfer",
                    "JazzCash",
                    "EasyPaisa",
                    "Credit Card",
                    "Other"
                ],
                index=[
                    "Cash",
                    "Bank Transfer",
                    "JazzCash",
                    "EasyPaisa",
                    "Credit Card",
                    "Other"
                ].index(row["payment_method"])
                if row["payment_method"] in [
                    "Cash",
                    "Bank Transfer",
                    "JazzCash",
                    "EasyPaisa",
                    "Credit Card",
                    "Other"
                ] else 0
            )

            due = st.text_input(
                "Due Date",
                str(row["due_date"])
            )

        notes = st.text_area(
            "Notes",
            row["notes"]
        )

        col1, col2 = st.columns(2)

        with col1:

            update = st.form_submit_button(
                "Update",
                use_container_width=True
            )

        with col2:

            delete = st.form_submit_button(
                "Delete",
                use_container_width=True
            )

        if update:

            update_deal(
                deal_id,
                client,
                service,
                value,
                cost,
                payment_received,
                method,
                due,
                notes
            )

            st.success("Deal updated successfully.")
            st.rerun()

        if delete:

            delete_deal(deal_id)

            st.success("Deal deleted successfully.")
            st.rerun()

def payment_history_tab():

    st.subheader("Payment History")

    deals = get_deals()

    if deals.empty:
        st.info("No deals available.")
        return

    deal_id = st.selectbox(
        "Select Deal",
        deals["id"]
    )

    deal = deals[
        deals["id"] == deal_id
    ].iloc[0]

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("### Client Information")

        st.write(f"**Client:** {deal['client_name']}")
        st.write(f"**Service:** {deal['service']}")
        st.write(f"**Due Date:** {deal['due_date']}")
        st.write(f"**Payment Method:** {deal['payment_method']}")

    with c2:

        st.markdown("### Payment Summary")

        st.metric(
            "Deal Value",
            f"Rs. {deal['deal_value']:,.0f}"
        )

        st.metric(
            "Received",
            f"Rs. {deal['sent_payment']:,.0f}"
        )

        st.metric(
            "Remaining",
            f"Rs. {deal['remaining']:,.0f}"
        )

        st.metric(
            "Status",
            deal["status"]
        )

    st.divider()

    st.subheader("Notes")

    if str(deal["notes"]).strip():

        st.info(deal["notes"])

    else:

        st.write("No notes available.")

    st.divider()

    st.subheader("Payment Progress")

    progress = 0

    if deal["deal_value"] > 0:

        progress = min(
            deal["sent_payment"] / deal["deal_value"],
            1.0
        )

    st.progress(progress)

    st.write(
        f"{progress*100:.1f}% Paid"
    )

    st.divider()

    export = deals[
        deals["id"] == deal_id
    ]

    st.download_button(
        "Download Payment Record",
        export.to_csv(index=False).encode("utf-8"),
        file_name=f"payment_{deal_id}.csv",
        mime="text/csv",
        use_container_width=True
    )

def business_analytics():

    st.header("📊 Business Analytics")

    deals = get_deals()

    if deals.empty:
        st.info("No data available.")
        return

    st.subheader("Revenue by Client")

    revenue = (
        deals.groupby("client_name")["deal_value"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8,4))

    revenue.plot(
        kind="bar",
        ax=ax
    )

    ax.set_ylabel("Revenue (Rs.)")
    ax.set_xlabel("Client")

    st.pyplot(fig)

    st.divider()

    st.subheader("Payment Status")

    status = (
        deals["status"]
        .value_counts()
    )

    fig2, ax2 = plt.subplots(figsize=(5,5))

    ax2.pie(
        status.values,
        labels=status.index,
        autopct="%1.1f%%"
    )

    st.pyplot(fig2)

    st.divider()

    st.subheader("Top Clients")

    top = deals.groupby("client_name").agg(
        Revenue=("deal_value","sum"),
        Profit=("profit","sum"),
        Remaining=("remaining","sum"),
        Deals=("id","count")
    )

    top = top.sort_values(
        "Revenue",
        ascending=False
    )

    st.dataframe(
        top,
        use_container_width=True
    )

    st.divider()

    st.subheader("Monthly Revenue")

    monthly = deals.copy()

    monthly["created_at"] = pd.to_datetime(
        monthly["created_at"]
    )

    monthly = monthly.groupby(
        monthly["created_at"].dt.strftime("%Y-%m")
    )["deal_value"].sum()

    fig3, ax3 = plt.subplots(figsize=(8,4))

    monthly.plot(
        marker="o",
        ax=ax3
    )

    ax3.set_ylabel("Revenue")

    st.pyplot(fig3)


    st.divider()

    st.subheader("Business Summary")

    summary = pd.DataFrame({

        "Metric": [
            "Total Deals",
            "Revenue",
            "Profit",
            "Received",
            "Remaining"
        ],

        "Value": [
            len(deals),
            deals["deal_value"].sum(),
            deals["profit"].sum(),
            deals["sent_payment"].sum(),
            deals["remaining"].sum()
        ]

    })

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

    csv = summary.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Summary",
        csv,
        "business_summary.csv",
        "text/csv",
        use_container_width=True
    )

import pandas as pd
from database import get_connection

def get_dashboard_summary():

    conn = get_connection()

    stats = {}

    queries = {
        "Revenue": "SELECT COALESCE(SUM(total),0) FROM sales",
        "Profit": "SELECT COALESCE(SUM(profit),0) FROM sales",
        "Purchases": "SELECT COALESCE(SUM(total),0) FROM purchases",
        "Expenses": "SELECT COALESCE(SUM(cost),0) FROM business_deals",
        "Customers": "SELECT COUNT(*) FROM customers",
        "Suppliers": "SELECT COUNT(*) FROM suppliers",
        "Products": "SELECT COUNT(*) FROM inventory",
        "Sales": "SELECT COUNT(*) FROM sales",
        "Purchase Orders": "SELECT COUNT(*) FROM purchases"
    }

    cur = conn.cursor()

    for key, query in queries.items():
        try:
            cur.execute(query)
            stats[key] = cur.fetchone()[0] or 0
        except:
            stats[key] = 0

    conn.close()

    return stats
