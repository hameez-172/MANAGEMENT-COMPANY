import pandas as pd
from datetime import datetime

from database import get_connection
from inventory import increase_stock


# ==========================================
# PURCHASE FUNCTIONS
# ==========================================

def create_purchase(
    supplier_name,
    invoice_no,
    purchase_date,
    payment_method,
    notes=""
):
    """
    Create a purchase header.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO purchases(
            supplier_name,
            invoice_no,
            purchase_date,
            payment_method,
            notes
        )
        VALUES (?,?,?,?,?)
    """, (
        supplier_name,
        invoice_no,
        purchase_date,
        payment_method,
        notes
    ))

    purchase_id = cur.lastrowid

    conn.commit()
    conn.close()

    return purchase_id


# ==========================================
# PURCHASE ITEMS
# ==========================================

def add_purchase_item(
    purchase_id,
    product_id,
    product_name,
    quantity,
    purchase_price
):
    """
    Add an item to a purchase and
    automatically increase inventory.
    """

    conn = get_connection()
    cur = conn.cursor()

    total = quantity * purchase_price

    cur.execute("""
        INSERT INTO purchase_items(
            purchase_id,
            product_id,
            product_name,
            quantity,
            purchase_price,
            total
        )
        VALUES (?,?,?,?,?,?)
    """, (
        purchase_id,
        product_id,
        product_name,
        quantity,
        purchase_price,
        total
    ))

    conn.commit()
    conn.close()

    # Increase inventory automatically
    increase_stock(product_id, quantity)

# ==========================================
# PURCHASE FETCH FUNCTIONS
# ==========================================

import pandas as pd
from database import get_connection


def get_all_purchases():
    """
    Return all purchases.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM purchases
        ORDER BY purchase_date DESC, id DESC
    """, conn)

    conn.close()

    return df


def get_purchase(purchase_id):
    """
    Return a single purchase.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM purchases
        WHERE id=?
    """, conn, params=(purchase_id,))

    conn.close()

    if df.empty:
        return None

    return df.iloc[0]


def get_purchase_items(purchase_id):
    """
    Return all items of a purchase.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM purchase_items
        WHERE purchase_id=?
        ORDER BY id
    """, conn, params=(purchase_id,))

    conn.close()

    return df


def get_purchase_total(purchase_id):
    """
    Return total amount of a purchase.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(total),0) AS total
        FROM purchase_items
        WHERE purchase_id=?
    """, conn, params=(purchase_id,))

    conn.close()

    return df.iloc[0]["total"]

# ==========================================
# UPDATE & DELETE PURCHASES
# ==========================================

from database import get_connection
from inventory import decrease_stock


def update_purchase(
    purchase_id,
    supplier_name,
    invoice_no,
    purchase_date,
    payment_method,
    notes=""
):
    """
    Update purchase header.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE purchases
        SET
            supplier_name=?,
            invoice_no=?,
            purchase_date=?,
            payment_method=?,
            notes=?
        WHERE id=?
    """, (
        supplier_name,
        invoice_no,
        purchase_date,
        payment_method,
        notes,
        purchase_id
    ))

    conn.commit()
    conn.close()


def delete_purchase_item(item_id):
    """
    Delete purchase item and
    reduce inventory automatically.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            product_id,
            quantity
        FROM purchase_items
        WHERE id=?
    """, (item_id,))

    row = cur.fetchone()

    if row is None:
        conn.close()
        return False

    product_id, quantity = row

    # Reduce stock
    decrease_stock(product_id, quantity)

    # Delete item
    cur.execute("""
        DELETE FROM purchase_items
        WHERE id=?
    """, (item_id,))

    conn.commit()
    conn.close()

    return True


def delete_purchase(purchase_id):
    """
    Delete complete purchase and
    restore inventory.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            product_id,
            quantity
        FROM purchase_items
        WHERE purchase_id=?
    """, (purchase_id,))

    items = cur.fetchall()

    for item in items:
        _, product_id, quantity = item
        decrease_stock(product_id, quantity)

    cur.execute("""
        DELETE FROM purchase_items
        WHERE purchase_id=?
    """, (purchase_id,))

    cur.execute("""
        DELETE FROM purchases
        WHERE id=?
    """, (purchase_id,))

    conn.commit()
    conn.close()

    return True

# ==========================================
# PURCHASE ANALYTICS
# ==========================================

import pandas as pd
from database import get_connection


def get_purchase_summary():
    """
    Return purchase summary statistics.
    """

    conn = get_connection()

    total_purchases = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM purchases
    """, conn).iloc[0]["total"]

    total_amount = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(total),0) AS total
        FROM purchase_items
    """, conn).iloc[0]["total"]

    total_items = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(quantity),0) AS total
        FROM purchase_items
    """, conn).iloc[0]["total"]

    total_suppliers = pd.read_sql_query("""
        SELECT
            COUNT(DISTINCT supplier_name) AS total
        FROM purchases
    """, conn).iloc[0]["total"]

    conn.close()

    return {
        "Total Purchases": total_purchases,
        "Total Amount": total_amount,
        "Total Items": total_items,
        "Total Suppliers": total_suppliers
    }


def get_monthly_purchases():
    """
    Monthly purchase report.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            substr(purchase_date,1,7) AS Month,
            SUM(total) AS Amount
        FROM purchase_items
        JOIN purchases
        ON purchases.id = purchase_items.purchase_id
        GROUP BY Month
        ORDER BY Month
    """, conn)

    conn.close()

    return df


def get_supplier_purchase_summary():
    """
    Supplier-wise purchase report.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            supplier_name,
            COUNT(DISTINCT purchases.id) AS Purchases,
            COALESCE(SUM(purchase_items.total),0) AS Amount
        FROM purchases
        LEFT JOIN purchase_items
        ON purchases.id = purchase_items.purchase_id
        GROUP BY supplier_name
        ORDER BY Amount DESC
    """, conn)

    conn.close()

    return df


def get_top_purchased_products(limit=10):
    """
    Most purchased products.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            product_name,
            SUM(quantity) AS Total_Qty,
            SUM(total) AS Total_Amount
        FROM purchase_items
        GROUP BY product_name
        ORDER BY Total_Qty DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def get_recent_purchases(limit=10):
    """
    Latest purchases.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM purchases
        ORDER BY purchase_date DESC, id DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df

# ==========================================
# PURCHASE UTILITIES
# ==========================================

import pandas as pd
from database import get_connection


def search_purchases(keyword):
    """
    Search purchases by supplier or invoice number.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM purchases
        WHERE
            supplier_name LIKE ?
            OR invoice_no LIKE ?
        ORDER BY purchase_date DESC
    """, conn, params=(
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    conn.close()

    return df


def get_purchases_between(start_date, end_date):
    """
    Return purchases between two dates.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM purchases
        WHERE purchase_date
        BETWEEN ? AND ?
        ORDER BY purchase_date DESC
    """, conn, params=(
        start_date,
        end_date
    ))

    conn.close()

    return df


def export_purchases_csv(file_name="purchases_export.csv"):
    """
    Export all purchases to CSV.
    """

    df = get_all_purchases()

    df.to_csv(
        file_name,
        index=False
    )

    return file_name


def purchase_dashboard():
    """
    Complete dashboard data.
    """

    return {
        "summary": get_purchase_summary(),
        "recent": get_recent_purchases(),
        "monthly": get_monthly_purchases(),
        "supplier_summary": get_supplier_purchase_summary(),
        "top_products": get_top_purchased_products()
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print(get_purchase_summary())

    print(get_monthly_purchases())

    print(get_supplier_purchase_summary())

    print(get_recent_purchases())

