import pandas as pd

from database import get_connection


# ==========================================
# DASHBOARD KPIs
# ==========================================

def get_dashboard_summary():
    """
    Returns all dashboard KPIs.
    """

    conn = get_connection()

    revenue = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(total),0) AS total
        FROM sale_items
    """, conn).iloc[0]["total"]

    purchases = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(total),0) AS total
        FROM purchase_items
    """, conn).iloc[0]["total"]

    expenses = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(amount),0) AS total
        FROM expenses
    """, conn).iloc[0]["total"]

    profit = revenue - purchases - expenses

    sales = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM sales
    """, conn).iloc[0]["total"]

    purchase_count = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM purchases
    """, conn).iloc[0]["total"]

    customers = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM customers
    """, conn).iloc[0]["total"]

    suppliers = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM suppliers
    """, conn).iloc[0]["total"]

    products = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    conn.close()

    return {
        "Revenue": revenue,
        "Purchases": purchases,
        "Expenses": expenses,
        "Profit": profit,
        "Sales": sales,
        "Purchase Orders": purchase_count,
        "Customers": customers,
        "Suppliers": suppliers,
        "Products": products
    }


# ==========================================
# QUICK KPIs
# ==========================================

def get_profit():
    """
    Return current profit.
    """

    data = get_dashboard_summary()

    return data["Profit"]


def get_revenue():
    """
    Return total revenue.
    """

    data = get_dashboard_summary()

    return data["Revenue"]


def get_total_expenses():
    """
    Return total expenses.
    """

    data = get_dashboard_summary()

    return data["Expenses"]


# ==========================================
# MONTHLY REPORTS
# ==========================================

import pandas as pd
from database import get_connection


def get_monthly_sales():
    """
    Monthly sales revenue.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(sale_date,1,7) AS Month,
            SUM(total) AS Revenue
        FROM sale_items
        JOIN sales
        ON sales.id = sale_items.sale_id
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df


def get_monthly_purchases():
    """
    Monthly purchase cost.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(purchase_date,1,7) AS Month,
            SUM(total) AS Purchases
        FROM purchase_items
        JOIN purchases
        ON purchases.id = purchase_items.purchase_id
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df


def get_monthly_expenses():
    """
    Monthly expenses.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(expense_date,1,7) AS Month,
            SUM(amount) AS Expenses
        FROM expenses
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df


def get_monthly_profit():
    """
    Monthly profit.
    Profit = Revenue - Purchases
    (Expenses are shown separately.)
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(s.sale_date,1,7) AS Month,
            SUM(si.total) -
            COALESCE((
                SELECT SUM(pi.total)
                FROM purchase_items pi
                JOIN purchases p
                ON p.id = pi.purchase_id
                WHERE substr(p.purchase_date,1,7)=substr(s.sale_date,1,7)
            ),0) AS Profit
        FROM sales s
        JOIN sale_items si
        ON s.id = si.sale_id
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df


def get_monthly_summary():
    """
    Returns all monthly analytics.
    """

    return {
        "sales": get_monthly_sales(),
        "purchases": get_monthly_purchases(),
        "expenses": get_monthly_expenses(),
        "profit": get_monthly_profit()
    }

# ==========================================
# CUSTOMER & SUPPLIER ANALYTICS
# ==========================================

import pandas as pd
from database import get_connection


def get_customer_summary():
    """
    Customer-wise sales summary.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            customer_name,
            COUNT(DISTINCT sales.id) AS Total_Orders,
            COALESCE(SUM(sale_items.total),0) AS Revenue
        FROM sales
        LEFT JOIN sale_items
        ON sales.id = sale_items.sale_id
        GROUP BY customer_name
        ORDER BY Revenue DESC
    """, conn)

    conn.close()

    return df


def get_supplier_summary():
    """
    Supplier-wise purchase summary.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            supplier_name,
            COUNT(DISTINCT purchases.id) AS Total_Purchases,
            COALESCE(SUM(purchase_items.total),0) AS Purchase_Value
        FROM purchases
        LEFT JOIN purchase_items
        ON purchases.id = purchase_items.purchase_id
        GROUP BY supplier_name
        ORDER BY Purchase_Value DESC
    """, conn)

    conn.close()

    return df


def get_top_customers(limit=10):
    """
    Top customers by revenue.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            customer_name,
            COALESCE(SUM(sale_items.total),0) AS Revenue
        FROM sales
        LEFT JOIN sale_items
        ON sales.id = sale_items.sale_id
        GROUP BY customer_name
        ORDER BY Revenue DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def get_top_suppliers(limit=10):
    """
    Top suppliers by purchase value.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            supplier_name,
            COALESCE(SUM(purchase_items.total),0) AS Purchase_Value
        FROM purchases
        LEFT JOIN purchase_items
        ON purchases.id = purchase_items.purchase_id
        GROUP BY supplier_name
        ORDER BY Purchase_Value DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def get_customer_count():
    """
    Total customers.
    """

    conn = get_connection()

    total = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM customers
    """, conn).iloc[0]["total"]

    conn.close()

    return total


def get_supplier_count():
    """
    Total suppliers.
    """

    conn = get_connection()

    total = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM suppliers
    """, conn).iloc[0]["total"]

    conn.close()

    return total

# ==========================================
# INVENTORY ANALYTICS
# ==========================================

import pandas as pd
from database import get_connection


def get_inventory_summary():
    """
    Return inventory summary.
    """

    conn = get_connection()

    total_products = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    total_stock = pd.read_sql_query("""
        SELECT COALESCE(SUM(quantity),0) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    inventory_value = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(quantity * purchase_price),0) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    conn.close()

    return {
        "Products": total_products,
        "Stock": total_stock,
        "Inventory Value": inventory_value
    }


def get_low_stock_products(threshold=10):
    """
    Products with stock less than or equal to threshold.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM inventory
        WHERE quantity <= ?
        ORDER BY quantity ASC
    """, conn, params=(threshold,))

    conn.close()

    return df


def get_out_of_stock_products():
    """
    Products with zero stock.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM inventory
        WHERE quantity = 0
        ORDER BY product_name
    """, conn)

    conn.close()

    return df


def get_top_selling_products(limit=10):
    """
    Top selling products.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            product_name,
            SUM(quantity) AS Quantity_Sold,
            SUM(total) AS Revenue
        FROM sale_items
        GROUP BY product_name
        ORDER BY Quantity_Sold DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def get_top_purchased_products(limit=10):
    """
    Top purchased products.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            product_name,
            SUM(quantity) AS Quantity_Purchased,
            SUM(total) AS Purchase_Value
        FROM purchase_items
        GROUP BY product_name
        ORDER BY Quantity_Purchased DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def get_inventory_value_by_product():
    """
    Inventory value for each product.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            product_name,
            quantity,
            purchase_price,
            (quantity * purchase_price) AS Stock_Value
        FROM inventory
        ORDER BY Stock_Value DESC
    """, conn)

    conn.close()

    return df

# ==========================================
# ANALYTICS UTILITIES
# ==========================================

import pandas as pd
from database import get_connection


def analytics_dashboard():
    """
    Returns all analytics required by the dashboard.
    """

    return {
        "dashboard": get_dashboard_summary(),
        "monthly": get_monthly_summary(),
        "customers": get_customer_summary(),
        "suppliers": get_supplier_summary(),
        "inventory": get_inventory_summary(),
        "top_customers": get_top_customers(),
        "top_suppliers": get_top_suppliers(),
        "top_selling": get_top_selling_products(),
        "top_purchased": get_top_purchased_products(),
        "low_stock": get_low_stock_products(),
        "out_of_stock": get_out_of_stock_products()
    }


def export_dashboard_csv(file_name="analytics_export.csv"):
    """
    Export dashboard KPIs to CSV.
    """

    summary = get_dashboard_summary()

    df = pd.DataFrame(
        list(summary.items()),
        columns=["Metric", "Value"]
    )

    df.to_csv(
        file_name,
        index=False
    )

    return file_name


def get_sales_between_dates(start_date, end_date):
    """
    Sales report between two dates.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            s.invoice_no,
            s.customer_name,
            s.sale_date,
            SUM(si.total) AS Total
        FROM sales s
        JOIN sale_items si
            ON s.id = si.sale_id
        WHERE s.sale_date BETWEEN ? AND ?
        GROUP BY s.id
        ORDER BY s.sale_date
    """, conn, params=(start_date, end_date))

    conn.close()

    return df


def get_purchases_between_dates(start_date, end_date):
    """
    Purchase report between two dates.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            p.invoice_no,
            p.supplier_name,
            p.purchase_date,
            SUM(pi.total) AS Total
        FROM purchases p
        JOIN purchase_items pi
            ON p.id = pi.purchase_id
        WHERE p.purchase_date BETWEEN ? AND ?
        GROUP BY p.id
        ORDER BY p.purchase_date
    """, conn, params=(start_date, end_date))

    conn.close()

    return df


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("Dashboard Summary")
    print(get_dashboard_summary())

    print("\nMonthly Summary")
    print(get_monthly_summary())

    print("\nCustomer Summary")
    print(get_customer_summary())

    print("\nSupplier Summary")
    print(get_supplier_summary())

    print("\nInventory Summary")
    print(get_inventory_summary())


