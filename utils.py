import os
import shutil
from datetime import datetime
import pandas as pd
import streamlit as st


# ==========================================
# DATE HELPERS
# ==========================================

def today():
    """
    Return today's date.
    """

    return datetime.today().strftime("%Y-%m-%d")


def current_datetime():
    """
    Return current date & time.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==========================================
# CURRENCY
# ==========================================

def currency(amount):
    """
    Format currency.
    """

    try:

        return f"PKR {float(amount):,.2f}"

    except:

        return "PKR 0.00"


# ==========================================
# NUMBER FORMAT
# ==========================================

def number(value):

    try:

        return f"{float(value):,.2f}"

    except:

        return "0.00"


# ==========================================
# TEXT
# ==========================================

def clean_text(text):

    if text is None:

        return ""

    return str(text).strip()

# ==========================================
# DATABASE BACKUP
# ==========================================

import os
import shutil
from datetime import datetime

from database import LOCAL_DATABASE


BACKUP_FOLDER = "backups"


def ensure_backup_folder():
    """
    Create backup folder if it does not exist.
    """

    if not os.path.exists(BACKUP_FOLDER):

        os.makedirs(BACKUP_FOLDER)


def backup_database():
    """
    Create database backup.
    """

    ensure_backup_folder()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = os.path.join(
        BACKUP_FOLDER,
        f"enterprise_backup_{timestamp}.db"
    )

    shutil.copy(
        LOCAL_DATABASE,
        backup_file
    )

    return backup_file


def restore_database(backup_file):
    """
    Restore database from backup.
    """

    if not os.path.exists(backup_file):

        raise FileNotFoundError(
            "Backup file not found."
        )

    shutil.copy(
        backup_file,
        LOCAL_DATABASE
    )


def list_backups():
    """
    Return all available backups.
    """

    ensure_backup_folder()

    backups = []

    for file in os.listdir(BACKUP_FOLDER):

        if file.endswith(".db"):

            backups.append(file)

    backups.sort(reverse=True)

    return backups


def backup_exists():
    """
    Check if any backup exists.
    """

    return len(list_backups()) > 0

# ==========================================
# EXPORT & FILE UTILITIES
# ==========================================

import os
import pandas as pd


def export_csv(dataframe, filename):
    """
    Export DataFrame to CSV.
    """

    dataframe.to_csv(
        filename,
        index=False
    )

    return filename


def export_excel(dataframe, filename):
    """
    Export DataFrame to Excel.
    """

    dataframe.to_excel(
        filename,
        index=False
    )

    return filename


def file_exists(filepath):
    """
    Check whether file exists.
    """

    return os.path.exists(filepath)


def file_size(filepath):
    """
    Return file size in MB.
    """

    if not file_exists(filepath):
        return 0

    size = os.path.getsize(filepath)

    return round(
        size / (1024 * 1024),
        2
    )


def create_folder(folder_name):
    """
    Create folder if it doesn't exist.
    """

    if not os.path.exists(folder_name):

        os.makedirs(folder_name)

    return folder_name


def delete_file(filepath):
    """
    Delete a file.
    """

    if file_exists(filepath):

        os.remove(filepath)

        return True

    return False


def list_files(folder, extension=None):
    """
    Return files inside a folder.

    Example:
        list_files("generated_pdfs")
        list_files("generated_pdfs", ".pdf")
    """

    if not os.path.exists(folder):
        return []

    files = []

    for file in os.listdir(folder):

        if extension:

            if file.lower().endswith(extension.lower()):
                files.append(file)

        else:

            files.append(file)

    files.sort()

    return files

# ==========================================
# STREAMLIT HELPERS
# ==========================================

import streamlit as st


def show_success(message):
    """
    Display success message.
    """

    st.success(message)


def show_error(message):
    """
    Display error message.
    """

    st.error(message)


def show_warning(message):
    """
    Display warning message.
    """

    st.warning(message)


def show_info(message):
    """
    Display information message.
    """

    st.info(message)


# ==========================================
# SESSION HELPERS
# ==========================================

def reset_session():
    """
    Clear Streamlit session state.
    """

    for key in list(st.session_state.keys()):
        del st.session_state[key]


def set_page(title):
    """
    Configure Streamlit page.
    """

    st.set_page_config(
        page_title=title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# ==========================================
# DATAFRAME HELPERS
# ==========================================

def empty_dataframe(df):
    """
    Return True if DataFrame is empty.
    """

    return df is None or df.empty


def safe_float(value):
    """
    Convert value to float safely.
    """

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_int(value):
    """
    Convert value to integer safely.
    """

    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("Today's Date :", today())
    print("Current Time :", current_datetime())
    print("Currency     :", currency(125000.75))
    print("Number       :", number(9876543.21))

    print("\nAvailable Backups:")
    print(list_backups())

    print("\nUtils module loaded successfully.")

