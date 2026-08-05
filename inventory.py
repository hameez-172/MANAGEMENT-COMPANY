import streamlit as st
import pandas as pd

from database import (
    execute_query,
    fetch_dataframe,
)

class InventoryService:

    @staticmethod
    def get_all():

        query = """
        SELECT *
        FROM inventory
        ORDER BY id DESC
        """

        return fetch_dataframe(query)


    @staticmethod
    def get(product_id):

        query = """
        SELECT *
        FROM inventory
        WHERE id = ?
        """

        df = fetch_dataframe(
            query,
            (product_id,)
        )

        if df.empty:
            return None

        return df.iloc[0]


    @staticmethod
    def total_products():

        query = """
        SELECT COUNT(*) AS total
        FROM inventory
        """

        df = fetch_dataframe(query)

        return int(df.iloc[0]["total"])


    @staticmethod
    def sku_exists(sku):

        query = """
        SELECT id
        FROM inventory
        WHERE sku = ?
        """

        df = fetch_dataframe(
            query,
            (sku,)
        )

        return not df.empty


    @staticmethod
    def product_exists(product_name):

        query = """
        SELECT id
        FROM inventory
        WHERE product_name = ?
        """

        df = fetch_dataframe(
            query,
            (product_name,)
        )

        return not df.empty

# ==========================================
# INVENTORY CRUD FUNCTIONS
# ==========================================

from database import get_connection


def add_product(
    product_name,
    sku,
    category,
    purchase_price,
    selling_price,
    quantity,
    minimum_stock,
    supplier,
    location,
    notes
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO inventory(
            product_name,
            sku,
            category,
            purchase_price,
            selling_price,
            quantity,
            minimum_stock,
            supplier,
            location,
            notes
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        product_name,
        sku,
        category,
        purchase_price,
        selling_price,
        quantity,
        minimum_stock,
        supplier,
        location,
        notes
    ))

    conn.commit()
    conn.close()


def update_product(
    product_id,
    product_name,
    sku,
    category,
    purchase_price,
    selling_price,
    quantity,
    minimum_stock,
    supplier,
    location,
    notes
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE inventory
        SET
            product_name=?,
            sku=?,
            category=?,
            purchase_price=?,
            selling_price=?,
            quantity=?,
            minimum_stock=?,
            supplier=?,
            location=?,
            notes=?
        WHERE id=?
    """, (
        product_name,
        sku,
        category,
        purchase_price,
        selling_price,
        quantity,
        minimum_stock,
        supplier,
        location,
        notes,
        product_id
    ))

    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM inventory WHERE id=?",
        (product_id,)
    )

    conn.commit()
    conn.close()


def get_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM inventory WHERE id=?",
        (product_id,)
    )

    row = cur.fetchone()

    conn.close()

    return row

# ==========================================
# INVENTORY FETCH FUNCTIONS
# ==========================================

import pandas as pd
from database import get_connection


def get_all_products():
    """
    Return all inventory products.
    """
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM inventory
        ORDER BY product_name
    """, conn)

    conn.close()

    return df


def search_products(keyword):
    """
    Search products by name, SKU or category.
    """
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM inventory
        WHERE
            product_name LIKE ?
            OR sku LIKE ?
            OR category LIKE ?
        ORDER BY product_name
    """, conn, params=(
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    conn.close()

    return df


def get_low_stock_products():
    """
    Products where quantity is less than or equal to minimum stock.
    """
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM inventory
        WHERE quantity <= minimum_stock
        ORDER BY quantity ASC
    """, conn)

    conn.close()

    return df


def get_out_of_stock_products():
    """
    Products with zero quantity.
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


def get_inventory_summary():
    """
    Inventory summary statistics.
    """
    conn = get_connection()

    total_products = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    total_quantity = pd.read_sql_query("""
        SELECT COALESCE(SUM(quantity),0) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    purchase_value = pd.read_sql_query("""
        SELECT COALESCE(
            SUM(quantity * purchase_price),0
        ) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    selling_value = pd.read_sql_query("""
        SELECT COALESCE(
            SUM(quantity * selling_price),0
        ) AS total
        FROM inventory
    """, conn).iloc[0]["total"]

    low_stock = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM inventory
        WHERE quantity <= minimum_stock
    """, conn).iloc[0]["total"]

    out_of_stock = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM inventory
        WHERE quantity = 0
    """, conn).iloc[0]["total"]

    conn.close()

    return {
        "Total Products": total_products,
        "Total Quantity": total_quantity,
        "Purchase Value": purchase_value,
        "Selling Value": selling_value,
        "Expected Profit": selling_value - purchase_value,
        "Low Stock": low_stock,
        "Out of Stock": out_of_stock
    }

# ==========================================
# STOCK MANAGEMENT
# ==========================================

from database import get_connection


def increase_stock(product_id, quantity):
    """
    Increase stock after a purchase.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE inventory
        SET quantity = quantity + ?
        WHERE id = ?
    """, (
        quantity,
        product_id
    ))

    conn.commit()
    conn.close()


def decrease_stock(product_id, quantity):
    """
    Decrease stock after a sale.

    Returns:
        True  -> Success
        False -> Not enough stock
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT quantity
        FROM inventory
        WHERE id=?
    """, (product_id,))

    row = cur.fetchone()

    if row is None:
        conn.close()
        return False

    current_stock = row[0]

    if current_stock < quantity:
        conn.close()
        return False

    cur.execute("""
        UPDATE inventory
        SET quantity = quantity - ?
        WHERE id=?
    """, (
        quantity,
        product_id
    ))

    conn.commit()
    conn.close()

    return True


def adjust_stock(product_id, new_quantity):
    """
    Manually set stock quantity.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE inventory
        SET quantity=?
        WHERE id=?
    """, (
        new_quantity,
        product_id
    ))

    conn.commit()
    conn.close()


def get_current_stock(product_id):
    """
    Return current stock quantity.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT quantity
        FROM inventory
        WHERE id=?
    """, (product_id,))

    row = cur.fetchone()

    conn.close()

    if row:
        return row[0]

    return 0


def stock_available(product_id, required_quantity):
    """
    Check if requested quantity is available.
    """

    current = get_current_stock(product_id)

    return current >= required_quantity

# ==========================================
# INVENTORY ANALYTICS & EXPORT
# ==========================================

import pandas as pd
from database import get_connection


def get_inventory_value():
    """
    Return purchase value, selling value and expected profit.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            SUM(quantity * purchase_price) AS purchase_value,
            SUM(quantity * selling_price) AS selling_value
        FROM inventory
    """, conn)

    conn.close()

    purchase = df.iloc[0]["purchase_value"] or 0
    selling = df.iloc[0]["selling_value"] or 0

    return {
        "purchase_value": purchase,
        "selling_value": selling,
        "expected_profit": selling - purchase
    }


def get_category_summary():
    """
    Category-wise inventory summary.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            category,
            COUNT(*) AS total_products,
            SUM(quantity) AS total_quantity,
            SUM(quantity * purchase_price) AS purchase_value,
            SUM(quantity * selling_price) AS selling_value
        FROM inventory
        GROUP BY category
        ORDER BY category
    """, conn)

    conn.close()

    return df


def get_top_valuable_products(limit=10):
    """
    Products having highest inventory value.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            product_name,
            category,
            quantity,
            purchase_price,
            selling_price,
            quantity * purchase_price AS purchase_value,
            quantity * selling_price AS selling_value
        FROM inventory
        ORDER BY selling_value DESC
        LIMIT ?
    """, conn, params=(limit,))

    conn.close()

    return df


def export_inventory_csv(file_name="inventory_export.csv"):
    """
    Export inventory to CSV.
    """

    df = get_all_products()

    df.to_csv(
        file_name,
        index=False
    )

    return file_name


def inventory_dashboard():
    """
    Complete inventory dashboard data.
    """

    return {
        "summary": get_inventory_summary(),
        "inventory_value": get_inventory_value(),
        "low_stock": get_low_stock_products(),
        "out_of_stock": get_out_of_stock_products(),
        "categories": get_category_summary(),
        "top_products": get_top_valuable_products()
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print(get_inventory_summary())

    print(get_inventory_value())

    print(get_category_summary())