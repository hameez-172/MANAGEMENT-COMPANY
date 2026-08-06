import pandas as pd
from datetime import datetime

from database import get_connection
from inventory import decrease_stock


# ==========================================
# SALES FUNCTIONS
# ==========================================

def create_sale(
    customer_name,
    invoice_no,
    sale_date,
    payment_method,
    notes=""
):
    """
    Create a sale header.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sales(
            customer_name,
            invoice_no,
            sale_date,
            payment_method,
            notes
        )
        VALUES (?,?,?,?,?)
    """, (
        customer_name,
        invoice_no,
        sale_date,
        payment_method,
        notes
    ))

    sale_id = cur.lastrowid

    conn.commit()
    conn.close()

    return sale_id


# ==========================================
# SALE ITEMS
# ==========================================

def add_sale_item(
    sale_id,
    product_id,
    product_name,
    quantity,
    selling_price
):
    """
    Add a product to a sale and
    automatically decrease inventory.
    """

    total = quantity * selling_price

    # Reduce inventory first
    success = decrease_stock(product_id, quantity)

    if not success:
        raise ValueError(
            "Insufficient stock available."
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sale_items(
            sale_id,
            product_id,
            product_name,
            quantity,
            selling_price,
            total
        )
        VALUES (?,?,?,?,?,?)
    """, (
        sale_id,
        product_id,
        product_name,
        quantity,
        selling_price,
        total
    ))

    conn.commit()
    conn.close()

# ==========================================
# SALES FETCH FUNCTIONS
# ==========================================

import pandas as pd
from database import get_connection


def get_all_sales():
    """
    Return all sales.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM sales
        ORDER BY sale_date DESC, id DESC
    """, conn)

    conn.close()

    return df


def get_sale(sale_id):
    """
    Return a single sale.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM sales
        WHERE id=?
    """, conn, params=(sale_id,))

    conn.close()

    if df.empty:
        return None

    return df.iloc[0]


def get_sale_items(sale_id):
    """
    Return all items for a sale.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM sale_items
        WHERE sale_id=?
        ORDER BY id
    """, conn, params=(sale_id,))

    conn.close()

    return df


def get_sale_total(sale_id):
    """
    Return total amount of a sale.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(total),0) AS total
        FROM sale_items
        WHERE sale_id=?
    """, conn, params=(sale_id,))

    conn.close()

    return df.iloc[0]["total"]


def get_sale_item_count(sale_id):
    """
    Return total quantity of items sold.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(quantity),0) AS total
        FROM sale_items
        WHERE sale_id=?
    """, conn, params=(sale_id,))

    conn.close()

    return df.iloc[0]["total"]

# ==========================================
# UPDATE & DELETE SALES
# ==========================================

from database import get_connection
from inventory import increase_stock


def update_sale(
    sale_id,
    customer_name,
    invoice_no,
    sale_date,
    payment_method,
    notes=""
):
    """
    Update sale header.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE sales
        SET
            customer_name=?,
            invoice_no=?,
            sale_date=?,
            payment_method=?,
            notes=?
        WHERE id=?
    """, (
        customer_name,
        invoice_no,
        sale_date,
        payment_method,
        notes,
        sale_id
    ))

    conn.commit()
    conn.close()


def delete_sale_item(item_id):
    """
    Delete one sale item and restore stock.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            product_id,
            quantity
        FROM sale_items
        WHERE id=?
    """, (item_id,))

    row = cur.fetchone()

    if row is None:
        conn.close()
        return False

    product_id, quantity = row

    # Restore stock
    increase_stock(product_id, quantity)

    # Delete item
    cur.execute("""
        DELETE FROM sale_items
        WHERE id=?
    """, (item_id,))

    conn.commit()
    conn.close()

    return True


def delete_sale(sale_id):
    """
    Delete complete sale and restore inventory.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            product_id,
            quantity
        FROM sale_items
        WHERE sale_id=?
    """, (sale_id,))

    items = cur.fetchall()

    # Restore stock
    for product_id, quantity in items:
        increase_stock(product_id, quantity)

    # Delete sale items
    cur.execute("""
        DELETE FROM sale_items
        WHERE sale_id=?
    """, (sale_id,))

    # Delete sale
    cur.execute("""
        DELETE FROM sales
        WHERE id=?
    """, (sale_id,))

    conn.commit()
    conn.close()

    return True

# ==========================================
# SALES ANALYTICS
# ==========================================

import pandas as pd
from database import get_connection


def get_sales_summary():
    """
    Return sales summary statistics.
    """

    conn = get_connection()

    total_sales = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM sales
    """, conn).iloc[0]["total"]

    total_amount = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(total),0) AS total
        FROM sale_items
    """, conn).iloc[0]["total"]

    total_items = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(quantity),0) AS total
        FROM sale_items
    """, conn).iloc[0]["total"]

    total_customers = pd.read_sql_query("""
        SELECT
            COUNT(DISTINCT customer_name) AS total
        FROM sales
    """, conn).iloc[0]["total"]

    conn.close()

    return {
        "Total Sales": total_sales,
        "Total Revenue": total_amount,
        "Items Sold": total_items,
        "Customers": total_customers
    }


def get_monthly_sales():
    """
    Monthly sales report.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(sales.sale_date,1,7) AS Month,
            SUM(sale_items.total) AS Revenue
        FROM sale_items
        JOIN sales
        ON sales.id = sale_items.sale_id
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df

def get_customer_sales_summary():
    """
    Customer-wise sales report.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            customer_name,
            COUNT(DISTINCT sales.id) AS Orders,
            COALESCE(SUM(sale_items.total),0) AS Revenue
        FROM sales
        LEFT JOIN sale_items
        ON sales.id = sale_items.sale_id
        GROUP BY customer_name
        ORDER BY Revenue DESC
    """, conn)

    conn.close()

    return df


def get_top_selling_products(limit=10):
    """
    Most sold products.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            product_name,
            SUM(quantity) AS Total_Qty,
            SUM(total) AS Revenue
        FROM sale_items
        GROUP BY product_name
        ORDER BY Total_Qty DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def get_recent_sales(limit=10):
    """
    Latest sales.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM sales
        ORDER BY sale_date DESC, id DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df

# ==========================================
# SALES UTILITIES
# ==========================================

import pandas as pd
from database import get_connection


def search_sales(keyword):
    """
    Search sales by customer or invoice number.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM sales
        WHERE
            customer_name LIKE ?
            OR invoice_no LIKE ?
        ORDER BY sale_date DESC
    """, conn, params=(
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    conn.close()

    return df


def get_sales_between(start_date, end_date):
    """
    Return sales between two dates.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM sales
        WHERE sale_date
        BETWEEN ? AND ?
        ORDER BY sale_date DESC
    """, conn, params=(
        start_date,
        end_date
    ))

    conn.close()

    return df


def export_sales_csv(file_name="sales_export.csv"):
    """
    Export all sales to CSV.
    """

    df = get_all_sales()

    df.to_csv(
        file_name,
        index=False
    )

    return file_name


def sales_dashboard():
    """
    Return complete dashboard data.
    """

    return {
        "summary": get_sales_summary(),
        "recent": get_recent_sales(),
        "monthly": get_monthly_sales(),
        "customer_summary": get_customer_sales_summary(),
        "top_products": get_top_selling_products()
    }


def get_monthly_profit():
    """
    Monthly profit report.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(sales.sale_date,1,7) AS Month,
            SUM(sale_items.total) AS Revenue
        FROM sale_items
        JOIN sales
        ON sales.id = sale_items.sale_id
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df

def get_monthly_profit():
    """
    Monthly profit report.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(sale_date,1,7) AS Month,
            SUM(sale_items.total - (products.cost_price * sale_items.quantity)) AS Profit
        FROM sale_items
        JOIN sales
        ON sales.id = sale_items.sale_id
        JOIN products
        ON products.id = sale_items.product_id
        GROUP BY Month
        ORDER BY Month
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
            COUNT(sales.id) AS Orders,
            SUM(sale_items.total) AS Revenue
        FROM sales
        JOIN sale_items
        ON sales.id = sale_items.sale_id
        GROUP BY customer_name
        ORDER BY Revenue DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df
# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print(get_sales_summary())

    print(get_monthly_sales())

    print(get_customer_sales_summary())

    print(get_top_selling_products())

    print(get_recent_sales())

