import hashlib
import streamlit as st
import pandas as pd

from database import get_connection


# ==========================================
# PASSWORD HASHING
# ==========================================

def hash_password(password):
    """
    Hash password using SHA256.
    """

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def verify_password(password, hashed_password):
    """
    Verify password.
    """

    return hash_password(password) == hashed_password


# ==========================================
# USER FUNCTIONS
# ==========================================

def create_user(
    username,
    password,
    full_name,
    role="Staff"
):
    """
    Create new user.
    """

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    cur.execute("""
        INSERT INTO users(
            username,
            password,
            full_name,
            role
        )
        VALUES(?,?,?,?)
    """, (
        username,
        hashed,
        full_name,
        role
    ))

    conn.commit()
    conn.close()


def username_exists(username):
    """
    Check if username already exists.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT id
        FROM users
        WHERE username=?
    """, conn, params=(username,))

    conn.close()

    return not df.empty

# ==========================================
# LOGIN / LOGOUT
# ==========================================

def login(username, password):
    """
    Login user.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM users
        WHERE username=?
    """, conn, params=(username,))

    conn.close()

    if df.empty:
        return False

    user = df.iloc[0]

    if not verify_password(
        password,
        user["password"]
    ):
        return False

    st.session_state["logged_in"] = True

    st.session_state["user_id"] = int(user["id"])

    st.session_state["username"] = user["username"]

    st.session_state["full_name"] = user["full_name"]

    st.session_state["role"] = user["role"]

    return True


def logout():
    """
    Logout current user.
    """

    keys = [
        "logged_in",
        "user_id",
        "username",
        "full_name",
        "role"
    ]

    for key in keys:

        if key in st.session_state:

            del st.session_state[key]


# ==========================================
# SESSION HELPERS
# ==========================================

def is_logged_in():
    """
    Check login status.
    """

    return st.session_state.get(
        "logged_in",
        False
    )


def current_user():
    """
    Return current user info.
    """

    if not is_logged_in():

        return None

    return {

        "id": st.session_state.get(
            "user_id"
        ),

        "username": st.session_state.get(
            "username"
        ),

        "full_name": st.session_state.get(
            "full_name"
        ),

        "role": st.session_state.get(
            "role"
        )

    }


def require_login():
    """
    Stop execution if user is not logged in.
    """

    if not is_logged_in():

        st.error(
            "Please login first."
        )

        st.stop()

# ==========================================
# USER MANAGEMENT
# ==========================================

def change_password(user_id, new_password):
    """
    Change user's password.
    """

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(new_password)

    cur.execute("""
        UPDATE users
        SET password=?
        WHERE id=?
    """, (
        hashed,
        user_id
    ))

    conn.commit()
    conn.close()


def update_user(
    user_id,
    full_name,
    role
):
    """
    Update user information.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET
            full_name=?,
            role=?
        WHERE id=?
    """, (
        full_name,
        role,
        user_id
    ))

    conn.commit()
    conn.close()


def get_user(user_id):
    """
    Return a single user.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            username,
            full_name,
            role
        FROM users
        WHERE id=?
    """, conn, params=(user_id,))

    conn.close()

    if df.empty:
        return None

    return df.iloc[0]


def get_all_users():
    """
    Return all users.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            username,
            full_name,
            role
        FROM users
        ORDER BY username
    """, conn)

    conn.close()

    return df


def delete_user(user_id):
    """
    Delete a user.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM users
        WHERE id=?
    """, (user_id,))

    conn.commit()
    conn.close()

# ==========================================
# ROLE & PERMISSION HELPERS
# ==========================================

def get_user_role():
    """
    Return current user's role.
    """

    if not is_logged_in():
        return None

    return st.session_state.get("role")


def is_admin():
    """
    Check if current user is Admin.
    """

    return get_user_role() == "Admin"


def is_manager():
    """
    Check if current user is Manager.
    """

    return get_user_role() == "Manager"


def is_staff():
    """
    Check if current user is Staff.
    """

    return get_user_role() == "Staff"


def has_role(*roles):
    """
    Check whether current user's role is in the allowed roles.

    Example:
        has_role("Admin", "Manager")
    """

    return get_user_role() in roles


# ==========================================
# ACCESS CONTROL
# ==========================================

def require_admin():
    """
    Allow Admin only.
    """

    require_login()

    if not is_admin():

        st.error(
            "Access denied. Admin privileges required."
        )

        st.stop()


def require_manager():
    """
    Allow Admin or Manager.
    """

    require_login()

    if not has_role("Admin", "Manager"):

        st.error(
            "Access denied."
        )

        st.stop()


def require_staff():
    """
    Any logged-in user.
    """

    require_login()


# ==========================================
# USER DISPLAY
# ==========================================

def current_user_name():
    """
    Return current user's full name.
    """

    if not is_logged_in():
        return ""

    return st.session_state.get("full_name", "")


def current_username():
    """
    Return current username.
    """

    if not is_logged_in():
        return ""

    return st.session_state.get("username", "")

# ==========================================
# INITIALIZATION
# ==========================================

def initialize_auth():
    """
    Create default admin if no users exist.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT COUNT(*) AS total
        FROM users
    """, conn)

    conn.close()

    if df.iloc[0]["total"] == 0:

        create_user(
            username="admin",
            password="admin123",
            full_name="System Administrator",
            role="Admin"
        )


# ==========================================
# STREAMLIT LOGIN FORM
# ==========================================

def login_form():
    """
    Display login form.
    """

    st.title("ERP Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if login(username, password):

            st.success("Login successful.")

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )


# ==========================================
# LOGOUT BUTTON
# ==========================================

def logout_button():
    """
    Display logout button.
    """

    if st.sidebar.button("Logout"):

        logout()

        st.rerun()


# ==========================================
# USER INFO
# ==========================================

def show_user_info():
    """
    Display logged-in user information.
    """

    if not is_logged_in():
        return

    st.sidebar.markdown("### Logged In User")

    st.sidebar.write(
        f"**Name:** {current_user_name()}"
    )

    st.sidebar.write(
        f"**Username:** {current_username()}"
    )

    st.sidebar.write(
        f"**Role:** {get_user_role()}"
    )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    initialize_auth()

    print("Authentication module loaded successfully.")