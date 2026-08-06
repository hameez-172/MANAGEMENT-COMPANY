import streamlit as st
import pandas as pd
import datetime
import hashlib
from analytics import get_dashboard_summary

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

from business import business_analytics

from customer import *
from supplier import *
from inventory import *
from purchase import *
from sales import *
from business import *

from pdf_generator import *

from utils import set_page

from auth import (
    initialize_auth,
    login_form,
    logout_button,
    show_user_info,
    is_logged_in,
    is_admin,
    is_manager,
    has_role
)


# ==========================================
# CUSTOM ERP STYLE
# ==========================================

def load_custom_css():

    st.markdown(

        """
        <style>

        .main {

            background-color:#f8f9fa;

        }


        .stMetric {


            background:white;

            padding:15px;

            border-radius:12px;

            box-shadow:0px 2px 8px rgba(0,0,0,0.08);

        }



        div[data-testid="stSidebar"] {


            background:#111827;

        }



        div[data-testid="stSidebar"] * {


            color:white;

        }



        .block-container {


            padding-top:2rem;

        }



        h1,h2,h3 {


            font-weight:700;

        }


        </style>

        """,

        unsafe_allow_html=True

    )



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
# PDF INVOICE GENERATOR
# ==========================================

def generate_invoice_pdf(invoice):


    file_name = f"invoice_{invoice['id']}.pdf"


    doc = SimpleDocTemplate(

        file_name,

        pagesize=A4

    )


    styles = getSampleStyleSheet()


    content = []



    title = Paragraph(

        "ENTERPRISE ERP INVOICE",

        styles["Title"]

    )


    content.append(title)


    content.append(
        Spacer(1,20)
    )



    details = [

        ["Customer", invoice["customer_name"]],

        ["Date", str(invoice["date"])],

        ["Invoice ID", str(invoice["id"])],

        ["Total", f"Rs. {invoice['total']}"]

    ]



    table = Table(details)



    table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),0.5,None)

        ])

    )


    content.append(table)


    content.append(

        Spacer(1,20)

    )



    product_data = [

        [

            "Product",

            "Quantity",

            "Amount"

        ],


        [

            invoice["product_name"],

            invoice["quantity"],

            invoice["total"]

        ]

    ]



    product_table = Table(

        product_data

    )



    product_table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),0.5,None)

        ])

    )


    content.append(

        product_table

    )



    doc.build(

        content

    )


    return file_name
# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.markdown(

"""
# 🏢 Enterprise ERP

**Business Management System**

---

""",

unsafe_allow_html=True

)

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

st.markdown(

f"""
# 🏢 Enterprise ERP

## {menu}

""",

unsafe_allow_html=True

)

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

    tab1, tab2, tab3 = st.tabs([
        "➕ Add Customer",
        "📋 View Customers",
        "✏️ Edit Customer"
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


            filtered = customers


            if keyword:

                filtered = customers[
                    customers.astype(str)
                    .apply(
                        lambda x:
                        x.str.contains(
                            keyword,
                            case=False,
                            na=False
                        )
                    )
                    .any(axis=1)
                ]


            st.dataframe(
                filtered,
                use_container_width=True
            )


            st.divider()


            st.subheader(
                "👁 Customer Details"
            )


            customer_id = st.selectbox(

                "Select Customer",

                filtered["id"]

            )


            customer = filtered[
                filtered["id"] == customer_id
            ].iloc[0]


            c1, c2 = st.columns(2)


            with c1:

                st.write(
                    f"**Name:** {customer['customer_name']}"
                )

                st.write(
                    f"**Phone:** {customer['phone']}"
                )

                st.write(
                    f"**Email:** {customer['email']}"
                )


            with c2:

                st.write(
                    f"**Address:** {customer['address']}"
                )

                st.write(
                    f"**Notes:** {customer['notes']}"
                )


            st.divider()


            if st.button(
                "❌ Delete Customer"
            ):


                delete_customer(
                    customer_id
                )


                st.success(
                    "Customer deleted successfully."
                )


                st.rerun()



    # ======================================
    # EDIT CUSTOMER
    # ======================================

    with tab3:


        customers = get_customers()


        if customers.empty:

            st.info(
                "No customers available."
            )


        else:


            selected_id = st.selectbox(

                "Select Customer To Edit",

                customers["id"],

                key="edit_customer"

            )


            customer = customers[
                customers["id"] == selected_id
            ].iloc[0]



            with st.form(
                "edit_customer_form"
            ):


                name = st.text_input(

                    "Customer Name",

                    value=customer["customer_name"]

                )


                phone = st.text_input(

                    "Phone",

                    value=customer["phone"]

                )


                email = st.text_input(

                    "Email",

                    value=customer["email"]

                )


                address = st.text_area(

                    "Address",

                    value=customer["address"]

                )


                notes = st.text_area(

                    "Notes",

                    value=customer["notes"]

                )



                update = st.form_submit_button(

                    "Update Customer"

                )



                if update:


                    update_customer(

                        selected_id,

                        name,

                        phone,

                        email,

                        address,

                        notes

                    )


                    st.success(

                        "Customer updated successfully."

                    )


                    st.rerun()

# ==========================================
# SUPPLIERS
# ==========================================

elif menu == "🚚 Suppliers":

    st.header("🚚 Supplier Management")


    tab1, tab2, tab3 = st.tabs([
        "➕ Add Supplier",
        "📋 View Suppliers",
        "✏️ Edit Supplier"
    ])



    # ======================================
    # ADD SUPPLIER
    # ======================================

    with tab1:


        with st.form(
            "supplier_form"
        ):


            supplier_name = st.text_input(
                "Supplier Name"
            )


            phone = st.text_input(
                "Phone"
            )


            email = st.text_input(
                "Email"
            )


            company = st.text_input(
                "Company Name"
            )


            address = st.text_area(
                "Address"
            )


            notes = st.text_area(
                "Notes"
            )


            submitted = st.form_submit_button(
                "Save Supplier"
            )


            if submitted:


                if supplier_name.strip() == "":


                    st.error(
                        "Supplier name is required."
                    )


                else:


                    add_supplier(

                        supplier_name,

                        phone,

                        email,

                        company,

                        address,

                        notes

                    )


                    st.success(
                        "Supplier added successfully."
                    )


                    st.rerun()



    # ======================================
    # VIEW SUPPLIERS
    # ======================================

    with tab2:


        suppliers = get_suppliers()



        if suppliers.empty:


            st.info(
                "No suppliers found."
            )



        else:



            keyword = st.text_input(
                "🔍 Search Supplier"
            )



            filtered = suppliers



            if keyword:


                filtered = suppliers[

                    suppliers.astype(str)

                    .apply(

                        lambda x:

                        x.str.contains(

                            keyword,

                            case=False,

                            na=False

                        )

                    )

                    .any(axis=1)

                ]



            st.dataframe(

                filtered,

                use_container_width=True

            )



            st.divider()



            st.subheader(
                "👁 Supplier Details"
            )



            supplier_id = st.selectbox(

                "Select Supplier",

                filtered["id"]

            )



            supplier = filtered[

                filtered["id"] == supplier_id

            ].iloc[0]



            c1, c2 = st.columns(2)



            with c1:


                st.write(
                    f"**Name:** {supplier['supplier_name']}"
                )


                st.write(
                    f"**Phone:** {supplier['phone']}"
                )


                st.write(
                    f"**Email:** {supplier['email']}"
                )



            with c2:


                st.write(
                    f"**Company:** {supplier['company']}"
                )


                st.write(
                    f"**Address:** {supplier['address']}"
                )


                st.write(
                    f"**Notes:** {supplier['notes']}"
                )



            st.divider()



            if st.button(
                "❌ Delete Supplier"
            ):



                delete_supplier(

                    supplier_id

                )


                st.success(
                    "Supplier deleted successfully."
                )


                st.rerun()



    # ======================================
    # EDIT SUPPLIER
    # ======================================

    with tab3:



        suppliers = get_suppliers()



        if suppliers.empty:


            st.info(
                "No suppliers available."
            )



        else:



            selected_id = st.selectbox(

                "Select Supplier To Edit",

                suppliers["id"],

                key="edit_supplier"

            )



            supplier = suppliers[

                suppliers["id"] == selected_id

            ].iloc[0]



            with st.form(
                "edit_supplier_form"
            ):



                name = st.text_input(

                    "Supplier Name",

                    value=supplier["supplier_name"]

                )


                phone = st.text_input(

                    "Phone",

                    value=supplier["phone"]

                )


                email = st.text_input(

                    "Email",

                    value=supplier["email"]

                )


                company = st.text_input(

                    "Company",

                    value=supplier["company"]

                )


                address = st.text_area(

                    "Address",

                    value=supplier["address"]

                )


                notes = st.text_area(

                    "Notes",

                    value=supplier["notes"]

                )



                update = st.form_submit_button(

                    "Update Supplier"

                )



                if update:



                    update_supplier(

                        selected_id,

                        name,

                        phone,

                        email,

                        company,

                        address,

                        notes

                    )



                    st.success(

                        "Supplier updated successfully."

                    )



                    st.rerun()

# ==========================================
# INVENTORY
# ==========================================

elif menu == "📦 Inventory":

    st.header("📦 Inventory Management")


    tab1, tab2, tab3 = st.tabs([
        "➕ Add Product",
        "📋 View Inventory",
        "✏️ Edit Product"
    ])



    # ======================================
    # ADD PRODUCT
    # ======================================

    with tab1:


        with st.form(
            "product_form"
        ):


            product_name = st.text_input(
                "Product Name"
            )


            category = st.text_input(
                "Category"
            )


            sku = st.text_input(
                "SKU Code"
            )


            quantity = st.number_input(

                "Quantity",

                min_value=0,

                step=1

            )


            purchase_price = st.number_input(

                "Purchase Price",

                min_value=0.0

            )


            sale_price = st.number_input(

                "Sale Price",

                min_value=0.0

            )


            supplier = st.text_input(
                "Supplier"
            )


            low_stock_limit = st.number_input(

                "Low Stock Alert Limit",

                min_value=0,

                value=5

            )


            notes = st.text_area(
                "Notes"
            )



            submitted = st.form_submit_button(
                "Save Product"
            )



            if submitted:



                if product_name.strip() == "":


                    st.error(
                        "Product name is required."
                    )


                else:


                    add_product(

                        product_name,

                        category,

                        sku,

                        quantity,

                        purchase_price,

                        sale_price,

                        supplier,

                        low_stock_limit,

                        notes

                    )


                    st.success(

                        "Product added successfully."

                    )


                    st.rerun()



    # ======================================
    # VIEW INVENTORY
    # ======================================

    with tab2:



        products = get_products()



        if products.empty:


            st.info(
                "No products found."
            )



        else:



            keyword = st.text_input(
                "🔍 Search Product"
            )



            filtered = products



            if keyword:



                filtered = products[

                    products.astype(str)

                    .apply(

                        lambda x:

                        x.str.contains(

                            keyword,

                            case=False,

                            na=False

                        )

                    )

                    .any(axis=1)

                ]



            st.dataframe(

                filtered,

                use_container_width=True

            )



            st.divider()



            st.subheader(
                "📊 Inventory Status"
            )



            for index, row in filtered.iterrows():


                if row["quantity"] <= row["low_stock_limit"]:


                    st.warning(

                        f"⚠️ {row['product_name']} - Low Stock ({row['quantity']})"

                    )



                else:


                    st.success(

                        f"✅ {row['product_name']} - Stock Available ({row['quantity']})"

                    )



            st.divider()



            st.subheader(
                "👁 Product Details"
            )



            product_id = st.selectbox(

                "Select Product",

                filtered["id"]

            )



            product = filtered[

                filtered["id"] == product_id

            ].iloc[0]



            c1, c2 = st.columns(2)



            with c1:


                st.write(
                    f"**Product:** {product['product_name']}"
                )


                st.write(
                    f"**Category:** {product['category']}"
                )


                st.write(
                    f"**SKU:** {product['sku']}"
                )


                st.write(
                    f"**Quantity:** {product['quantity']}"
                )



            with c2:


                st.write(

                    f"**Purchase Price:** Rs {product['purchase_price']}"

                )


                st.write(

                    f"**Sale Price:** Rs {product['sale_price']}"

                )


                st.write(

                    f"**Supplier:** {product['supplier']}"

                )


                st.write(

                    f"**Notes:** {product['notes']}"

                )



            st.divider()



            if st.button(

                "❌ Delete Product"

            ):



                delete_product(

                    product_id

                )



                st.success(

                    "Product deleted successfully."

                )



                st.rerun()



    # ======================================
    # EDIT PRODUCT
    # ======================================

    with tab3:



        products = get_products()



        if products.empty:


            st.info(
                "No products available."
            )



        else:



            selected_id = st.selectbox(

                "Select Product To Edit",

                products["id"],

                key="edit_product"

            )



            product = products[

                products["id"] == selected_id

            ].iloc[0]



            with st.form(

                "edit_product_form"

            ):



                name = st.text_input(

                    "Product Name",

                    value=product["product_name"]

                )


                category = st.text_input(

                    "Category",

                    value=product["category"]

                )


                sku = st.text_input(

                    "SKU",

                    value=product["sku"]

                )


                quantity = st.number_input(

                    "Quantity",

                    value=int(product["quantity"])

                )


                purchase_price = st.number_input(

                    "Purchase Price",

                    value=float(product["purchase_price"])

                )


                sale_price = st.number_input(

                    "Sale Price",

                    value=float(product["sale_price"])

                )


                supplier = st.text_input(

                    "Supplier",

                    value=product["supplier"]

                )


                low_stock_limit = st.number_input(

                    "Low Stock Limit",

                    value=int(product["low_stock_limit"])

                )


                notes = st.text_area(

                    "Notes",

                    value=product["notes"]

                )



                update = st.form_submit_button(

                    "Update Product"

                )



                if update:



                    update_product(

                        selected_id,

                        name,

                        category,

                        sku,

                        quantity,

                        purchase_price,

                        sale_price,

                        supplier,

                        low_stock_limit,

                        notes

                    )



                    st.success(

                        "Product updated successfully."

                    )



                    st.rerun()


# ==========================================
# PURCHASES
# ==========================================

elif menu == "🛒 Purchases":

    st.header("🛒 Purchase Management")


    tab1, tab2 = st.tabs([
        "➕ Create Purchase",
        "📋 Purchase History"
    ])



    # ======================================
    # CREATE PURCHASE
    # ======================================

    with tab1:


        suppliers = get_suppliers()

        products = get_products()



        if suppliers.empty or products.empty:

            st.warning(
                "Supplier and Product data required first."
            )

        else:


            supplier_list = suppliers["supplier_name"].tolist()


            selected_supplier = st.selectbox(

                "Select Supplier",

                supplier_list

            )


            product_list = products["product_name"].tolist()


            selected_product = st.selectbox(

                "Select Product",

                product_list

            )


            product = products[

                products["product_name"] == selected_product

            ].iloc[0]



            quantity = st.number_input(

                "Quantity",

                min_value=1,

                step=1

            )


            purchase_price = st.number_input(

                "Purchase Price",

                value=float(product["purchase_price"])

            )



            total = quantity * purchase_price



            st.metric(

                "Total Amount",

                f"Rs. {total:,.2f}"

            )



            payment_status = st.selectbox(

                "Payment Status",

                [

                    "Paid",

                    "Partial",

                    "Pending"

                ]

            )



            paid_amount = st.number_input(

                "Paid Amount",

                min_value=0.0,

                value=0.0

            )



            notes = st.text_area(

                "Notes"

            )



            if st.button(

                "Save Purchase"

            ):



                add_purchase(

                    selected_supplier,

                    selected_product,

                    quantity,

                    purchase_price,

                    total,

                    payment_status,

                    paid_amount,

                    notes

                )


                update_stock(

                    selected_product,

                    quantity

                )


                st.success(

                    "Purchase created successfully."

                )


                st.rerun()



    # ======================================
    # PURCHASE HISTORY
    # ======================================

    with tab2:



        purchases = get_purchases()



        if purchases.empty:


            st.info(

                "No purchase records found."

            )



        else:



            st.dataframe(

                purchases,

                use_container_width=True

            )



            st.divider()



            st.subheader(

                "Purchase Summary"

            )



            total_purchase = purchases["total"].sum()



            paid = purchases["paid_amount"].sum()



            remaining = total_purchase - paid



            c1, c2, c3 = st.columns(3)



            with c1:


                st.metric(

                    "Total Purchases",

                    f"Rs. {total_purchase:,.0f}"

                )



            with c2:


                st.metric(

                    "Paid",

                    f"Rs. {paid:,.0f}"

                )



            with c3:


                st.metric(

                    "Outstanding",

                    f"Rs. {remaining:,.0f}"

                )

# ==========================================
# SALES
# ==========================================

elif menu == "💰 Sales":

    st.header("💰 Sales Management")


    tab1, tab2 = st.tabs([
        "➕ Create Sale",
        "📋 Sales History"
    ])



    # ======================================
    # CREATE SALE
    # ======================================

    with tab1:


        customers = get_customers()

        products = get_products()



        if customers.empty or products.empty:


            st.warning(

                "Customer and Product data required first."

            )


        else:



            customer_list = customers[
                "customer_name"
            ].tolist()



            selected_customer = st.selectbox(

                "Select Customer",

                customer_list

            )



            product_list = products[
                "product_name"
            ].tolist()



            selected_product = st.selectbox(

                "Select Product",

                product_list

            )



            product = products[

                products["product_name"] == selected_product

            ].iloc[0]



            available_stock = product["quantity"]



            st.info(

                f"Available Stock: {available_stock}"

            )



            quantity = st.number_input(

                "Quantity",

                min_value=1,

                max_value=int(available_stock),

                step=1

            )



            sale_price = st.number_input(

                "Sale Price",

                value=float(product["sale_price"])

            )



            total = quantity * sale_price



            cost = quantity * float(
                product["purchase_price"]
            )



            profit = total - cost



            c1, c2 = st.columns(2)



            with c1:


                st.metric(

                    "Sale Amount",

                    f"Rs. {total:,.2f}"

                )



            with c2:


                st.metric(

                    "Expected Profit",

                    f"Rs. {profit:,.2f}"

                )



            payment_status = st.selectbox(

                "Payment Status",

                [

                    "Paid",

                    "Partial",

                    "Pending"

                ]

            )



            received_amount = st.number_input(

                "Received Amount",

                min_value=0.0,

                value=0.0

            )



            notes = st.text_area(

                "Notes"

            )



            if st.button(

                "Save Sale"

            ):



                add_sale(

                    selected_customer,

                    selected_product,

                    quantity,

                    sale_price,

                    total,

                    profit,

                    payment_status,

                    received_amount,

                    notes

                )


                reduce_stock(

                    selected_product,

                    quantity

                )



                st.success(

                    "Sale created successfully."

                )


                st.rerun()



    # ======================================
    # SALES HISTORY
    # ======================================

    with tab2:



        sales = get_sales()



        if sales.empty:


            st.info(

                "No sales records found."

            )



        else:



            st.dataframe(

                sales,

                use_container_width=True

            )



            st.divider()



            st.subheader(

                "Sales Summary"

            )



            total_sales = sales[
                "total"
            ].sum()



            total_profit = sales[
                "profit"
            ].sum()



            received = sales[
                "received_amount"
            ].sum()



            remaining = total_sales - received



            c1, c2, c3, c4 = st.columns(4)



            with c1:


                st.metric(

                    "Revenue",

                    f"Rs. {total_sales:,.0f}"

                )



            with c2:


                st.metric(

                    "Profit",

                    f"Rs. {total_profit:,.0f}"

                )



            with c3:


                st.metric(

                    "Received",

                    f"Rs. {received:,.0f}"

                )



            with c4:


                st.metric(

                    "Outstanding",

                    f"Rs. {remaining:,.0f}"

                )

# ==========================================
# INVOICE
# ==========================================

elif menu == "📄 Invoice":

    st.header("📄 Invoice Management")


    tab1, tab2 = st.tabs([
        "➕ Create Invoice",
        "📋 Invoice History"
    ])



    # ======================================
    # CREATE INVOICE
    # ======================================

    with tab1:


        customers = get_customers()

        products = get_products()



        if customers.empty or products.empty:


            st.warning(

                "Customer and Product data required first."

            )


        else:



            customer_list = customers[
                "customer_name"
            ].tolist()



            selected_customer = st.selectbox(

                "Select Customer",

                customer_list

            )



            product_list = products[
                "product_name"
            ].tolist()



            selected_product = st.selectbox(

                "Select Product",

                product_list

            )



            product = products[

                products["product_name"] == selected_product

            ].iloc[0]



            quantity = st.number_input(

                "Quantity",

                min_value=1,

                step=1

            )



            price = st.number_input(

                "Price",

                value=float(product["sale_price"])

            )



            subtotal = quantity * price



            tax_rate = st.number_input(

                "Tax %",

                min_value=0.0,

                value=0.0

            )



            tax_amount = subtotal * tax_rate / 100



            total = subtotal + tax_amount



            st.divider()



            c1, c2, c3 = st.columns(3)



            with c1:

                st.metric(

                    "Subtotal",

                    f"Rs. {subtotal:,.0f}"

                )


            with c2:

                st.metric(

                    "Tax",

                    f"Rs. {tax_amount:,.0f}"

                )


            with c3:

                st.metric(

                    "Total",

                    f"Rs. {total:,.0f}"

                )



            notes = st.text_area(

                "Invoice Notes"

            )



            if st.button(

                "Generate Invoice"

            ):



                create_invoice(

                    selected_customer,

                    selected_product,

                    quantity,

                    price,

                    subtotal,

                    tax_amount,

                    total,

                    notes

                )


                st.success(

                    "Invoice created successfully."

                )


                st.rerun()



    # ======================================
    # INVOICE HISTORY
    # ======================================

    with tab2:

        invoices = get_invoices()

        if invoices.empty:

            st.info("No invoices found.")

        else:

            st.dataframe(
                invoices,
                use_container_width=True
            )

            st.divider()

            invoice_id = st.selectbox(
                "Select Invoice",
                invoices["id"]
            )

            invoice = invoices[
                invoices["id"] == invoice_id
            ].iloc[0]

            if st.button("📄 Generate PDF Invoice"):

                pdf = generate_invoice_pdf(invoice)

                with open(pdf, "rb") as file:

                    st.download_button(
                        "⬇️ Download PDF",
                        file,
                        file_name=pdf,
                        mime="application/pdf"
                    )

            st.subheader("Invoice Details")

            st.write(f"Customer: {invoice['customer_name']}")
            st.write(f"Total Amount: Rs. {invoice['total']}")
            st.write(f"Date: {invoice['date']}")

            export = invoices[
                invoices["id"] == invoice_id
            ]

            st.download_button(
                "⬇️ Export Invoice CSV",
                export.to_csv(index=False).encode("utf-8"),
                file_name=f"invoice_{invoice_id}.csv",
                mime="text/csv",
                use_container_width=True
            )
elif menu == "💼 Business Deals":

    if not has_role("Admin", "Manager"):

        st.error("Access denied.")
        st.stop()

    st.header("💼 Business Deals Management")

    tab1, tab2, tab3 = st.tabs([
        "💼 Business Deals",
        "📊 Dashboard",
        "💳 Payment History"
    ])

    # ==========================
    # BUSINESS DEALS
    # ==========================
    with tab1:
        business_tab()

    # ==========================
    # DASHBOARD
    # ==========================
    with tab2:

        deals = get_deals()

        if deals.empty:
            st.info("No business deals available.")

        else:
            stats = get_dashboard_stats()

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Revenue",
                    f"Rs. {stats['Revenue']:,.0f}"
    )

            with c2:
                st.metric(
                    "Profit",
                    f"Rs. {stats['Profit']:,.0f}"
    )

            with c3:
                st.metric(
                    "Received",
                    f"Rs. {stats['Received']:,.0f}"
    )

            with c4:
                st.metric(
                    "Remaining",
                    f"Rs. {stats['Remaining']:,.0f}"
    )

            st.divider()

            business_analytics()

    # ==========================
    # PAYMENT HISTORY
    # ==========================
    with tab3:
        payment_history_tab()
# ==========================================
# QUOTATION
# ==========================================

elif menu == "📝 Quotation":

    st.header("📝 Quotation Management")


    tab1, tab2 = st.tabs([
        "➕ Create Quotation",
        "📋 Quotation History"
    ])



    # ======================================
    # CREATE QUOTATION
    # ======================================

    with tab1:


        customers = get_customers()

        products = get_products()



        if customers.empty or products.empty:


            st.warning(

                "Customer and Product data required first."

            )


        else:



            customer_list = customers[

                "customer_name"

            ].tolist()



            selected_customer = st.selectbox(

                "Select Customer",

                customer_list

            )



            product_list = products[

                "product_name"

            ].tolist()



            selected_product = st.selectbox(

                "Select Product",

                product_list

            )



            product = products[

                products["product_name"] == selected_product

            ].iloc[0]



            quantity = st.number_input(

                "Quantity",

                min_value=1,

                step=1

            )



            price = st.number_input(

                "Unit Price",

                value=float(product["sale_price"])

            )



            discount = st.number_input(

                "Discount %",

                min_value=0.0,

                max_value=100.0,

                value=0.0

            )



            validity = st.date_input(

                "Valid Until"

            )



            subtotal = quantity * price



            discount_amount = (

                subtotal * discount / 100

            )



            total = subtotal - discount_amount



            st.divider()



            c1, c2, c3 = st.columns(3)



            with c1:


                st.metric(

                    "Subtotal",

                    f"Rs. {subtotal:,.0f}"

                )



            with c2:


                st.metric(

                    "Discount",

                    f"Rs. {discount_amount:,.0f}"

                )



            with c3:


                st.metric(

                    "Final Amount",

                    f"Rs. {total:,.0f}"

                )



            notes = st.text_area(

                "Notes"

            )



            if st.button(

                "Save Quotation"

            ):



                add_quotation(

                    selected_customer,

                    selected_product,

                    quantity,

                    price,

                    discount,

                    total,

                    validity,

                    notes

                )


                st.success(

                    "Quotation created successfully."

                )


                st.rerun()



    # ======================================
    # QUOTATION HISTORY
    # ======================================

    with tab2:



        quotations = get_quotations()



        if quotations.empty:


            st.info(

                "No quotations found."

            )



        else:



            st.dataframe(

                quotations,

                use_container_width=True

            )



            st.divider()



            quotation_id = st.selectbox(

                "Select Quotation",

                quotations["id"]

            )



            quotation = quotations[

                quotations["id"] == quotation_id

            ].iloc[0]



            st.subheader(

                "Quotation Details"

            )



            st.write(

                f"Customer: {quotation['customer_name']}"

            )



            st.write(

                f"Amount: Rs. {quotation['total']}"

            )



            st.write(

                f"Valid Until: {quotation['validity']}"

            )



            if st.button(

                "Convert To Invoice"

            ):



                convert_quotation_to_invoice(

                    quotation_id

                )


                st.success(

                    "Quotation converted into invoice."

                )


                st.rerun()

# ==========================================
# DELIVERY CHALLAN
# ==========================================

elif menu == "🚛 Delivery Challan":

    st.header("🚛 Delivery Challan Management")


    tab1, tab2 = st.tabs([
        "➕ Create Challan",
        "📋 Challan History"
    ])



    # ======================================
    # CREATE CHALLAN
    # ======================================

    with tab1:


        customers = get_customers()

        products = get_products()



        if customers.empty or products.empty:


            st.warning(

                "Customer and Product data required first."

            )


        else:



            customer_list = customers[

                "customer_name"

            ].tolist()



            selected_customer = st.selectbox(

                "Select Customer",

                customer_list

            )



            product_list = products[

                "product_name"

            ].tolist()



            selected_product = st.selectbox(

                "Select Product",

                product_list

            )



            product = products[

                products["product_name"] == selected_product

            ].iloc[0]



            available_stock = product["quantity"]



            st.info(

                f"Available Stock: {available_stock}"

            )



            quantity = st.number_input(

                "Delivery Quantity",

                min_value=1,

                max_value=int(available_stock),

                step=1

            )



            delivery_date = st.date_input(

                "Delivery Date"

            )



            status = st.selectbox(

                "Delivery Status",

                [

                    "Pending",

                    "Dispatched",

                    "Delivered"

                ]

            )



            notes = st.text_area(

                "Notes"

            )



            if st.button(

                "Create Challan"

            ):



                add_delivery_challan(

                    selected_customer,

                    selected_product,

                    quantity,

                    delivery_date,

                    status,

                    notes

                )


                st.success(

                    "Delivery Challan created successfully."

                )


                st.rerun()



    # ======================================
    # CHALLAN HISTORY
    # ======================================

    with tab2:



        challans = get_delivery_challans()



        if challans.empty:


            st.info(

                "No delivery challans found."

            )



        else:



            st.dataframe(

                challans,

                use_container_width=True

            )



            st.divider()



            st.subheader(

                "🚚 Delivery Status"

            )



            pending = challans[

                challans["status"] == "Pending"

            ]



            dispatched = challans[

                challans["status"] == "Dispatched"

            ]



            delivered = challans[

                challans["status"] == "Delivered"

            ]



            c1, c2, c3 = st.columns(3)



            with c1:


                st.metric(

                    "Pending",

                    len(pending)

                )



            with c2:


                st.metric(

                    "Dispatched",

                    len(dispatched)

                )



            with c3:


                st.metric(

                    "Delivered",

                    len(delivered)

                )



            st.divider()



            challan_id = st.selectbox(

                "Select Challan",

                challans["id"]

            )



            selected = challans[

                challans["id"] == challan_id

            ].iloc[0]



            st.write(

                f"Customer: {selected['customer_name']}"

            )


            st.write(

                f"Product: {selected['product_name']}"

            )


            st.write(

                f"Quantity: {selected['quantity']}"

            )


            st.write(

                f"Status: {selected['status']}"

            )

# ==========================================
# ANALYTICS
# ==========================================

elif menu == "📈 Analytics":

    st.header("📈 Business Analytics")


    sales = get_sales()

    purchases = get_purchases()

    customers = get_customers()

    products = get_products()



    if sales.empty and purchases.empty:

        st.info(
            "Not enough data for analytics."
        )


    else:


        # ==================================
        # KPI CARDS
        # ==================================

        total_revenue = 0

        total_profit = 0

        total_purchase = 0



        if not sales.empty:

            total_revenue = sales["total"].sum()

            total_profit = sales["profit"].sum()



        if not purchases.empty:

            total_purchase = purchases["total"].sum()



        c1, c2, c3 = st.columns(3)



        with c1:

            st.metric(

                "💰 Revenue",

                f"Rs. {total_revenue:,.0f}"

            )


        with c2:

            st.metric(

                "📈 Profit",

                f"Rs. {total_profit:,.0f}"

            )


        with c3:

            st.metric(

                "🛒 Purchases",

                f"Rs. {total_purchase:,.0f}"

            )



        st.divider()



        # ==================================
        # SALES TREND
        # ==================================

        st.subheader(

            "📊 Sales Trend"

        )



        if not sales.empty:



            sales_chart = sales.copy()



            sales_chart["date"] = (

                pd.to_datetime(

                    sales_chart["date"]

                )

            )



            sales_chart = (

                sales_chart

                .groupby(

                    sales_chart["date"]

                    .dt

                    .to_period("M")

                    .astype(str)

                )

                ["total"]

                .sum()

            )



            st.line_chart(

                sales_chart

            )


        else:


            st.info(

                "No sales data."

            )



        st.divider()



        # ==================================
        # PROFIT CHART
        # ==================================

        st.subheader(

            "📈 Profit Trend"

        )



        if not sales.empty:


            profit_chart = sales.copy()



            profit_chart["date"] = (

                pd.to_datetime(

                    profit_chart["date"]

                )

            )



            profit_chart = (

                profit_chart

                .groupby(

                    profit_chart["date"]

                    .dt

                    .to_period("M")

                    .astype(str)

                )

                ["profit"]

                .sum()

            )



            st.bar_chart(

                profit_chart

            )



        st.divider()



        # ==================================
        # TOP CUSTOMERS
        # ==================================

        st.subheader(

            "🏆 Top Customers"

        )



        if not sales.empty:


            top_customers = (

                sales

                .groupby(

                    "customer_name"

                )

                ["total"]

                .sum()

                .sort_values(

                    ascending=False

                )

                .head(10)

            )


            st.dataframe(

                top_customers,

                use_container_width=True

            )



        else:


            st.info(

                "No customer sales data."

            )



        st.divider()



        # ==================================
        # TOP PRODUCTS
        # ==================================

        st.subheader(

            "🔥 Top Selling Products"

        )



        if not sales.empty:


            top_products = (

                sales

                .groupby(

                    "product_name"

                )

                ["quantity"]

                .sum()

                .sort_values(

                    ascending=False

                )

                .head(10)

            )


            st.dataframe(

                top_products,

                use_container_width=True

            )


        else:


            st.info(

                "No product sales data."

            )


    st.divider()

    st.subheader("Quick Report")

    report = pd.DataFrame({

    "Metric":[
        "Revenue",
        "Profit",
        "Purchases",
        "Customers",
        "Products"
    ],

    "Value":[
        total_revenue,
        total_profit,
        total_purchase,
        len(customers),
        len(products)
    ]

})

    st.dataframe(
    report,
    use_container_width=True,
    hide_index=True
)

    st.download_button(
    "⬇️ Export Report",
    report.to_csv(index=False).encode(),
    "analytics_report.csv",
    "text/csv"
)


# ==========================================
# BACKUP
# ==========================================

elif menu == "💾 Backup":

    if not is_admin():

        st.error("Only Admin can access Backup.")

        st.stop()

    st.header("💾 Database Backup")


    st.info(
        "Create and download your ERP database backup."
    )



    if st.button(

        "Create Backup"

    ):



        backup_file = create_backup()



        st.success(

            "Backup created successfully."

        )



        with open(

            backup_file,

            "rb"

        ) as file:



            st.download_button(

                "⬇️ Download Backup",

                file,

                file_name=backup_file,

                mime="application/octet-stream",

                use_container_width=True

            )



    st.divider()



    st.subheader(

        "Restore Database"

    )



    uploaded_backup = st.file_uploader(

        "Upload Backup File",

        type=["db"]

    )



    if uploaded_backup:



        if st.button(

            "Restore Backup"

        ):



            restore_backup(

                uploaded_backup

            )


            st.success(

                "Database restored successfully."

            )



            st.rerun()





# ==========================================
# USERS
# ==========================================
elif menu == "👤 Users":

    if not is_admin():

        st.error("Only Admin can access User Management.")

        st.stop()

    st.header("👤 User Management")



    tab1, tab2 = st.tabs([

        "➕ Add User",

        "📋 User List"

    ])



    # ======================================
    # ADD USER
    # ======================================

    with tab1:



        with st.form(

            "user_form"

        ):



            username = st.text_input(

                "Username"

            )



            password = st.text_input(

                "Password",

                type="password"

            )



            role = st.selectbox(

                "Role",

                [

                    "Admin",

                    "Manager",

                    "Employee"

                ]

            )



            submit = st.form_submit_button(

                "Create User"

            )



            if submit:



                add_user(

                    username,

                    password,

                    role

                )



                st.success(

                    "User created successfully."

                )



                st.rerun()




    # ======================================
    # USER LIST
    # ======================================

    with tab2:



        users = get_users()



        if users.empty:


            st.info(

                "No users found."

            )



        else:



            st.dataframe(

                users,

                use_container_width=True

            )



            st.divider()



            user_id = st.selectbox(

                "Select User",

                users["id"]

            )



            if st.button(

                "Delete User"

            ):



                delete_user(

                    user_id

                )


                st.success(

                    "User deleted successfully."

                )


                st.rerun()

