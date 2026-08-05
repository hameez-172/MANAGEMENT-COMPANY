import streamlit as st
import pandas as pd

from auth import (
    initialize_auth,
    login_form,
    logout_button,
    show_user_info,
    is_logged_in
)

from analytics import (
    get_dashboard_summary
)

from customer import *
from supplier import *
from inventory import *
from purchase import *
from sales import *
from business import *

from pdf_generator import *

from utils import set_page


# ==========================================
# PAGE CONFIG
# ==========================================

set_page("Enterprise ERP")


# ==========================================
# INITIALIZE
# ==========================================

initialize_auth()


# ==========================================
# LOGIN
# ==========================================

if not is_logged_in():

    login_form()

    st.stop()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🏢 Enterprise ERP")

show_user_info()

menu = st.sidebar.radio(

    "Navigation",

    [

        "📊 Dashboard",

        "👥 Customers",

        "🚚 Suppliers",

        "📦 Inventory",

        "🛒 Purchases",

        "💰 Sales",

        "💼 Business Deals",

        "📈 Analytics",

        "📄 Invoice",

        "📝 Quotation",

        "🚛 Delivery Challan",

        "💾 Backup",

        "👤 Users"

    ]

)

st.sidebar.divider()

logout_button()


# ==========================================
# PAGE TITLE
# ==========================================

st.title(menu)

# ==========================================
# DASHBOARD
# ==========================================

if menu == "📊 Dashboard":

    st.header("📊 Dashboard")

    stats = get_dashboard_summary()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "💰 Revenue",
            f"PKR {stats['Revenue']:,.2f}"
        )

        st.metric(
            "📈 Profit",
            f"PKR {stats['Profit']:,.2f}"
        )

        st.metric(
            "🛒 Sales",
            stats["Sales"]
        )

    with col2:

        st.metric(
            "📦 Purchases",
            f"PKR {stats['Purchases']:,.2f}"
        )

        st.metric(
            "💸 Expenses",
            f"PKR {stats['Expenses']:,.2f}"
        )

        st.metric(
            "👥 Customers",
            stats["Customers"]
        )

    with col3:

        st.metric(
            "🚚 Suppliers",
            stats["Suppliers"]
        )

        st.metric(
            "📦 Products",
            stats["Products"]
        )

        st.metric(
            "📄 Purchase Orders",
            stats["Purchase Orders"]
        )

    st.divider()

    st.subheader("📈 Business Overview")

    c1, c2 = st.columns(2)

    with c1:

        monthly_sales = get_monthly_sales()

        if not monthly_sales.empty:

            st.line_chart(
                monthly_sales.set_index("Month")
            )

        else:

            st.info("No sales data available.")

    with c2:

        monthly_profit = get_monthly_profit()

        if not monthly_profit.empty:

            st.bar_chart(
                monthly_profit.set_index("Month")
            )

        else:

            st.info("No profit data available.")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("🏆 Top Customers")

        top_customers = get_top_customers()

        if not top_customers.empty:

            st.dataframe(
                top_customers,
                use_container_width=True
            )

        else:

            st.info("No customer records.")

    with c2:

        st.subheader("🔥 Top Selling Products")

        top_products = get_top_selling_products()

        if not top_products.empty:

            st.dataframe(
                top_products,
                use_container_width=True
            )

        else:

            st.info("No sales records.")

    st.divider()

    st.subheader("⚠️ Low Stock Products")

    low_stock = get_low_stock_products()

    if not low_stock.empty:

        st.dataframe(
            low_stock,
            use_container_width=True
        )

    else:

        st.success("No low-stock products.")

# ==========================================
# CUSTOMERS
# ==========================================

elif menu == "👥 Customers":

    st.header("👥 Customer Management")

    tab1, tab2 = st.tabs([
        "➕ Add Customer",
        "📋 View Customers"
    ])

    # ======================================
    # ADD CUSTOMER
    # ======================================

    with tab1:

        with st.form("customer_form"):

            customer_name = st.text_input(
                "Customer Name"
            )

            phone = st.text_input(
                "Phone"
            )

            email = st.text_input(
                "Email"
            )

            address = st.text_area(
                "Address"
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Save Customer"
            )

            if submitted:

                if customer_name.strip() == "":

                    st.error(
                        "Customer name is required."
                    )

                else:

                    add_customer(
                        customer_name,
                        phone,
                        email,
                        address,
                        notes
                    )

                    st.success(
                        "Customer added successfully."
                    )

                    st.rerun()

    # ======================================
    # VIEW CUSTOMERS
    # ======================================

    with tab2:

        customers = get_customers()

        if customers.empty:

            st.info(
                "No customers found."
            )

        else:

            keyword = st.text_input(
                "🔍 Search Customer"
            )

            if keyword:

                customers = customers[
                    customers.astype(str)
                    .apply(
                        lambda col:
                        col.str.contains(
                            keyword,
                            case=False,
                            na=False
                        )
                    )
                    .any(axis=1)
                ]

            st.dataframe(
                customers,
                use_container_width=True
            )

            st.divider()

            st.subheader(
                "Delete Customer"
            )

            customer_ids = customers["id"].tolist()

            if customer_ids:

                selected_id = st.selectbox(
                    "Select Customer ID",
                    customer_ids
                )

                if st.button(
                    "Delete Customer",
                    type="secondary"
                ):

                    delete_customer(
                        selected_id
                    )

                    st.success(
                        "Customer deleted successfully."
                    )

                    st.rerun()
