import sqlite3
import pandas as pd
import streamlit as st
import requests
import base64
import os
import shutil
from contextlib import contextmanager
from datetime import datetime

LOCAL_DATABASE = "enterprise.db"

# =====================================================
# TURSO CURSOR
# =====================================================

class TursoCursor:

    def __init__(self, connection):
        self.connection = connection
        self.rows = []
        self.description = None
        self.lastrowid = None
        self.rowcount = 0

    def execute(self, sql, params=None):

        result = self.connection.execute_sql(
            sql,
            params or ()
        )

        self.rows = result["rows"]
        self.description = result["description"]
        self.lastrowid = result["lastrowid"]
        self.rowcount = result["rowcount"]

        return self

    def fetchone(self):

        if self.rows:
            return self.rows[0]

        return None

    def fetchall(self):
        return self.rows

    def close(self):
        pass


# =====================================================
# TURSO CONNECTION
# =====================================================

class TursoConnection:

    def __init__(self, url, token):

        self.url = url.replace(
            "libsql://",
            "https://"
        ).rstrip("/")

        self.url += "/v2/pipeline"

        self.token = token

        self.session = requests.Session()

    # ---------------------------------------------

    def _argument(self, value):

        if value is None:
            return {"type": "null"}

        if isinstance(value, bool):
            return {
                "type": "integer",
                "value": str(int(value))
            }

        if isinstance(value, int):
            return {
                "type": "integer",
                "value": str(value)
            }

        if isinstance(value, float):
            return {
                "type": "float",
                "value": value
            }

        if isinstance(value, (bytes, bytearray)):
            return {
                "type": "blob",
                "base64": base64.b64encode(value).decode()
            }

        return {
            "type": "text",
            "value": str(value)
        }

    # ---------------------------------------------

    def _python_value(self, cell):

        if cell is None:
            return None

        cell_type = cell.get("type")

        if cell_type == "null":
            return None

        if cell_type == "integer":
            return int(cell["value"])

        if cell_type == "float":
            return float(cell["value"])

        if cell_type == "text":
            return cell["value"]

        if cell_type == "blob":
            return base64.b64decode(cell["base64"])

        return cell.get("value")

    # ---------------------------------------------

    def execute_sql(self, sql, params):

        payload = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": sql,
                        "args": [
                            self._argument(x)
                            for x in params
                        ]
                    }
                },
                {
                    "type": "close"
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = self.session.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        result = data["results"][0]["response"]["result"]

        columns = [
            col["name"]
            for col in result.get("cols", [])
        ]

        rows = []

        for row in result.get("rows", []):

            rows.append(
                tuple(
                    self._python_value(cell)
                    for cell in row
                )
            )

        lastrow = result.get("last_insert_rowid")

        if lastrow:
            lastrow = int(lastrow)

        return {

            "rows": rows,

            "description": [

                (
                    col,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                )

                for col in columns

            ],

            "lastrowid": lastrow,

            "rowcount": result.get(
                "affected_row_count",
                0
            )
        }

    # ---------------------------------------------

    def cursor(self):
        return TursoCursor(self)

    def execute(self, sql, params=None):
        cursor = self.cursor()
        cursor.execute(sql, params)
        return cursor

    def commit(self):
        pass

    def close(self):
        pass


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    try:
        url = st.secrets.get("TURSO_DATABASE_URL")
        token = st.secrets.get("TURSO_AUTH_TOKEN")
    except Exception:
        url = None
        token = None

    if url and token:
        return TursoConnection(url, token)

    return sqlite3.connect(LOCAL_DATABASE)


# =====================================================
# READ SQL
# =====================================================

def read_sql(query, params=None):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        query,
        params or ()
    )

    columns = [
        col[0]
        for col in cursor.description
    ]

    rows = cursor.fetchall()

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    conn.close()

    return df

# =====================================================
# GENERIC QUERY FUNCTIONS
# =====================================================

def execute_query(query, params=None):
    """
    Execute INSERT, UPDATE, DELETE queries
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        query,
        params or ()
    )

    conn.commit()
    conn.close()


def fetch_dataframe(query, params=None):
    """
    Execute SELECT queries and return pandas DataFrame
    """

    return read_sql(
        query,
        params
    )
# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def initialize_database():

    conn = get_connection()
    c = conn.cursor()

    print("DATABASE INITIALIZATION STARTED")
    # -----------------------------
    # CLIENTS
    # -----------------------------

    c.execute("""
    CREATE TABLE IF NOT EXISTS clients (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        client_name TEXT NOT NULL,

        email TEXT,

        phone TEXT,

        company TEXT,

        address TEXT,

        notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # -----------------------------
    # DEALS
    # -----------------------------

    c.execute("""
    CREATE TABLE IF NOT EXISTS deals (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        client_name TEXT NOT NULL,

        service TEXT,

        deal_value REAL DEFAULT 0,

        cost REAL DEFAULT 0,

        sent_payment REAL DEFAULT 0,

        remaining REAL DEFAULT 0,

        payment_method TEXT,

        status TEXT,

        due_date TEXT,

        notes TEXT,

        profit REAL DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # -----------------------------
    # EXPENSES
    # -----------------------------

    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        expense_date TEXT,

        category TEXT,

        description TEXT,

        amount REAL,

        payment_method TEXT,

        notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # -----------------------------
    # INVOICES
    # -----------------------------

    c.execute("""
    CREATE TABLE IF NOT EXISTS invoices (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        invoice_no TEXT UNIQUE,

        client_name TEXT,

        issue_date TEXT,

        due_date TEXT,

        amount REAL,

        status TEXT,

        notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # -----------------------------
    # SETTINGS
    # -----------------------------

    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        setting_key TEXT UNIQUE,

        setting_value TEXT

    )
    """)

    # -----------------------------
    # USERS
    # -----------------------------

    c.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    full_name TEXT,

    role TEXT DEFAULT 'Staff',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

    try:
        conn.commit()
    except Exception:
        pass

    conn.close()

# =====================================================
# CLIENTS
# =====================================================

def add_client(
    client_name,
    email="",
    phone="",
    company="",
    address="",
    notes=""
):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO clients(
            client_name,
            email,
            phone,
            company,
            address,
            notes
        )
        VALUES(?,?,?,?,?,?)
    """, (
        client_name,
        email,
        phone,
        company,
        address,
        notes
    ))

    conn.commit()
    conn.close()


def get_clients():

    return read_sql("""

        SELECT *

        FROM clients

        ORDER BY client_name

    """)


def get_client(client_id):

    df = read_sql(

        "SELECT * FROM clients WHERE id=?",

        (client_id,)

    )

    if df.empty:
        return None

    return df.iloc[0]


def update_client(
    client_id,
    client_name,
    email,
    phone,
    company,
    address,
    notes
):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""

        UPDATE clients

        SET

            client_name=?,
            email=?,
            phone=?,
            company=?,
            address=?,
            notes=?

        WHERE id=?

    """, (

        client_name,
        email,
        phone,
        company,
        address,
        notes,
        client_id

    ))

    conn.commit()
    conn.close()


def delete_client(client_id):

    conn = get_connection()
    c = conn.cursor()

    c.execute(

        "DELETE FROM clients WHERE id=?",

        (client_id,)

    )

    conn.commit()
    conn.close()

# =====================================================
# DEALS
# =====================================================

def add_deal(
    client_name,
    service,
    deal_value,
    cost,
    sent_payment,
    payment_method,
    due_date,
    notes=""
):

    conn = get_connection()
    c = conn.cursor()

    deal_value = float(deal_value)
    cost = float(cost)
    sent_payment = float(sent_payment)

    remaining = deal_value - sent_payment
    profit = deal_value - cost

    if remaining <= 0:
        status = "Paid"
    elif sent_payment > 0:
        status = "Partial"
    else:
        status = "Pending"

    c.execute("""
        INSERT INTO deals(

            client_name,
            service,
            deal_value,
            cost,
            sent_payment,
            remaining,
            payment_method,
            status,
            due_date,
            notes,
            profit

        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """, (

        client_name,
        service,
        deal_value,
        cost,
        sent_payment,
        remaining,
        payment_method,
        status,
        due_date,
        notes,
        profit

    ))

    conn.commit()
    conn.close()


def get_deals():

    return read_sql("""

        SELECT *

        FROM deals

        ORDER BY id DESC

    """)


def get_deal(deal_id):

    df = read_sql(

        "SELECT * FROM deals WHERE id=?",

        (deal_id,)

    )

    if df.empty:
        return None

    return df.iloc[0]


def update_deal(

    deal_id,
    client_name,
    service,
    deal_value,
    cost,
    sent_payment,
    payment_method,
    due_date,
    notes

):

    conn = get_connection()
    c = conn.cursor()

    deal_value = float(deal_value)
    cost = float(cost)
    sent_payment = float(sent_payment)

    remaining = deal_value - sent_payment
    profit = deal_value - cost

    if remaining <= 0:
        status = "Paid"
    elif sent_payment > 0:
        status = "Partial"
    else:
        status = "Pending"

    c.execute("""

        UPDATE deals

        SET

            client_name=?,
            service=?,
            deal_value=?,
            cost=?,
            sent_payment=?,
            remaining=?,
            payment_method=?,
            status=?,
            due_date=?,
            notes=?,
            profit=?

        WHERE id=?

    """, (

        client_name,
        service,
        deal_value,
        cost,
        sent_payment,
        remaining,
        payment_method,
        status,
        due_date,
        notes,
        profit,
        deal_id

    ))

    conn.commit()
    conn.close()


def delete_deal(deal_id):

    conn = get_connection()
    c = conn.cursor()

    c.execute(

        "DELETE FROM deals WHERE id=?",

        (deal_id,)

    )

    conn.commit()
    conn.close()


def update_payment(deal_id, payment):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""

        SELECT
            deal_value,
            sent_payment

        FROM deals

        WHERE id=?

    """, (deal_id,))

    row = c.fetchone()

    if row is None:
        conn.close()
        return

    deal_value = float(row[0])
    current_payment = float(row[1])

    new_payment = current_payment + float(payment)

    remaining = deal_value - new_payment

    if remaining <= 0:
        remaining = 0
        status = "Paid"
    else:
        status = "Partial"

    c.execute("""

        UPDATE deals

        SET

            sent_payment=?,
            remaining=?,
            status=?

        WHERE id=?

    """, (

        new_payment,
        remaining,
        status,
        deal_id

    ))

    conn.commit()
    conn.close()

# =====================================================
# INVOICES
# =====================================================

def add_invoice(
    invoice_no,
    client_name,
    issue_date,
    due_date,
    amount,
    status,
    notes=""
):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""

        INSERT INTO invoices(

            invoice_no,
            client_name,
            issue_date,
            due_date,
            amount,
            status,
            notes

        )

        VALUES(?,?,?,?,?,?,?)

    """, (

        invoice_no,
        client_name,
        issue_date,
        due_date,
        amount,
        status,
        notes

    ))

    conn.commit()
    conn.close()


def get_invoices():

    return read_sql("""

        SELECT *

        FROM invoices

        ORDER BY id DESC

    """)


def get_invoice(invoice_id):

    df = read_sql(

        "SELECT * FROM invoices WHERE id=?",

        (invoice_id,)

    )

    if df.empty:
        return None

    return df.iloc[0]


def update_invoice(

    invoice_id,
    invoice_no,
    client_name,
    issue_date,
    due_date,
    amount,
    status,
    notes=""

):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""

        UPDATE invoices

        SET

            invoice_no=?,
            client_name=?,
            issue_date=?,
            due_date=?,
            amount=?,
            status=?,
            notes=?

        WHERE id=?

    """, (

        invoice_no,
        client_name,
        issue_date,
        due_date,
        amount,
        status,
        notes,
        invoice_id

    ))

    conn.commit()
    conn.close()


def delete_invoice(invoice_id):

    conn = get_connection()
    c = conn.cursor()

    c.execute(

        "DELETE FROM invoices WHERE id=?",

        (invoice_id,)

    )

    conn.commit()
    conn.close()


def get_pending_invoices():

    return read_sql("""

        SELECT *

        FROM invoices

        WHERE status!='Paid'

        ORDER BY due_date

    """)


def get_overdue_invoices():

    today = datetime.now().strftime("%Y-%m-%d")

    return read_sql("""

        SELECT *

        FROM invoices

        WHERE due_date < ?

        AND status!='Paid'

        ORDER BY due_date

    """, (today,))


def generate_invoice_number():

    conn = get_connection()
    c = conn.cursor()

    c.execute("""

        SELECT MAX(id)

        FROM invoices

    """)

    row = c.fetchone()

    conn.close()

    if row[0] is None:
        return "INV-0001"

    return f"INV-{row[0]+1:04d}"

# =====================================================
# EXPENSES
# =====================================================

def add_expense(
    expense_date,
    category,
    description,
    amount,
    payment_method,
    notes=""
):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO expenses(
            expense_date,
            category,
            description,
            amount,
            payment_method,
            notes
        )
        VALUES(?,?,?,?,?,?)
    """, (

        expense_date,
        category,
        description,
        amount,
        payment_method,
        notes

    ))

    conn.commit()
    conn.close()


def get_expenses():

    return read_sql("""

        SELECT *

        FROM expenses

        ORDER BY expense_date DESC,id DESC

    """)


def get_expense(expense_id):

    df = read_sql(

        "SELECT * FROM expenses WHERE id=?",

        (expense_id,)

    )

    if df.empty:
        return None

    return df.iloc[0]


def update_expense(

    expense_id,
    expense_date,
    category,
    description,
    amount,
    payment_method,
    notes=""

):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""

        UPDATE expenses

        SET

            expense_date=?,
            category=?,
            description=?,
            amount=?,
            payment_method=?,
            notes=?

        WHERE id=?

    """, (

        expense_date,
        category,
        description,
        amount,
        payment_method,
        notes,
        expense_id

    ))

    conn.commit()
    conn.close()


def delete_expense(expense_id):

    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "DELETE FROM expenses WHERE id=?",
        (expense_id,)
    )

    conn.commit()
    conn.close()


# =====================================================
# DASHBOARD
# =====================================================

def get_dashboard_stats():

    stats = {}

    deals = get_deals()
    expenses = get_expenses()

    if deals.empty:

        stats["Revenue"] = 0
        stats["Cost"] = 0
        stats["Profit"] = 0
        stats["Received"] = 0
        stats["Remaining"] = 0
        stats["Deals"] = 0
        stats["Clients"] = 0

    else:

        stats["Revenue"] = deals["deal_value"].sum()
        stats["Cost"] = deals["cost"].sum()
        stats["Profit"] = deals["profit"].sum()
        stats["Received"] = deals["sent_payment"].sum()
        stats["Remaining"] = deals["remaining"].sum()
        stats["Deals"] = len(deals)
        stats["Clients"] = deals["client_name"].nunique()

    if expenses.empty:

        stats["Expenses"] = 0

    else:

        stats["Expenses"] = expenses["amount"].sum()

    stats["Net Profit"] = (

        stats["Profit"] -
        stats["Expenses"]

    )

    return stats


def get_monthly_revenue():

    return read_sql("""

        SELECT

            substr(created_at,1,7) AS Month,

            SUM(deal_value) AS Revenue

        FROM deals

        GROUP BY Month

        ORDER BY Month

    """)


def get_monthly_profit():

    return read_sql("""

        SELECT

            substr(created_at,1,7) AS Month,

            SUM(profit) AS Profit

        FROM deals

        GROUP BY Month

        ORDER BY Month

    """)


def get_expense_breakdown():

    return read_sql("""

        SELECT

            category,

            SUM(amount) AS Total

        FROM expenses

        GROUP BY category

        ORDER BY Total DESC

    """)


def get_client_summary():

    return read_sql("""

        SELECT

            client_name,

            COUNT(*) AS Deals,

            SUM(deal_value) AS Revenue,

            SUM(sent_payment) AS Received,

            SUM(remaining) AS Remaining,

            SUM(profit) AS Profit

        FROM deals

        GROUP BY client_name

        ORDER BY Revenue DESC

    """)

# ==========================================================
# UTILITIES
# ==========================================================

def backup_database():
    import shutil
    import os

    if not os.path.exists("backups"):
        os.makedirs("backups")

    filename = datetime.now().strftime(
        "backups/enterprise_%Y%m%d_%H%M%S.db"
    )

    shutil.copy(
        LOCAL_DATABASE,
        filename
    )

    return filename


def database_health():

    health = {}

    for table in [
        "clients",
        "deals",
        "expenses",
        "invoices"
    ]:

        try:

            df = read_sql(
                f"SELECT COUNT(*) AS total FROM {table}"
            )

            health[table] = int(df.iloc[0]["total"])

        except:

            health[table] = 0

    return health


# ==========================================================
# INITIALIZE
# ==========================================================

initialize_database()
