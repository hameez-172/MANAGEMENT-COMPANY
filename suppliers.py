import streamlit as st
import pandas as pd

from database import (
    execute_query,
    fetch_dataframe,
)

class SupplierService:

    @staticmethod
    def get_all():

        query = """
        SELECT *
        FROM suppliers
        ORDER BY id DESC
        """

        return fetch_dataframe(query)


    @staticmethod
    def get(supplier_id):

        query = """
        SELECT *
        FROM suppliers
        WHERE id = ?
        """

        df = fetch_dataframe(
            query,
            (supplier_id,)
        )

        if df.empty:
            return None

        return df.iloc[0]


    @staticmethod
    def exists(email):

        query = """
        SELECT id
        FROM suppliers
        WHERE email = ?
        """

        df = fetch_dataframe(
            query,
            (email,)
        )

        return not df.empty


    @staticmethod
    def total():

        query = """
        SELECT COUNT(*) AS total
        FROM suppliers
        """

        df = fetch_dataframe(query)

        return int(df.iloc[0]["total"])

    @staticmethod
    def add_supplier(
        name,
        company,
        phone,
        email,
        address,
        city,
        country,
        notes
    ):

        query = """
        INSERT INTO suppliers (
            name,
            company,
            phone,
            email,
            address,
            city,
            country,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        execute_query(
            query,
            (
                name,
                company,
                phone,
                email,
                address,
                city,
                country,
                notes
            )
        )

    @staticmethod
    def update_supplier(
        supplier_id,
        name,
        company,
        phone,
        email,
        address,
        city,
        country,
        notes
    ):

        query = """
        UPDATE suppliers
        SET
            name = ?,
            company = ?,
            phone = ?,
            email = ?,
            address = ?,
            city = ?,
            country = ?,
            notes = ?
        WHERE id = ?
        """

        execute_query(
            query,
            (
                name,
                company,
                phone,
                email,
                address,
                city,
                country,
                notes,
                supplier_id
            )
        )

    @staticmethod
    def delete_supplier(supplier_id):

        query = """
        DELETE FROM suppliers
        WHERE id = ?
        """

        execute_query(
            query,
            (supplier_id,)
        )

    @staticmethod
    def search(keyword):

        keyword = f"%{keyword}%"

        query = """
        SELECT *
        FROM suppliers
        WHERE
            name LIKE ?
            OR company LIKE ?
            OR phone LIKE ?
            OR email LIKE ?
            OR city LIKE ?
            OR country LIKE ?
        ORDER BY name
        """

        return fetch_dataframe(
            query,
            (
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword
            )
        )


    @staticmethod
    def search_by_name(name):

        query = """
        SELECT *
        FROM suppliers
        WHERE name LIKE ?
        ORDER BY name
        """

        return fetch_dataframe(
            query,
            (f"%{name}%",)
        )


    @staticmethod
    def search_by_company(company):

        query = """
        SELECT *
        FROM suppliers
        WHERE company LIKE ?
        ORDER BY company
        """

        return fetch_dataframe(
            query,
            (f"%{company}%",)
        )


    @staticmethod
    def search_by_phone(phone):

        query = """
        SELECT *
        FROM suppliers
        WHERE phone LIKE ?
        """

        return fetch_dataframe(
            query,
            (f"%{phone}%",)
        )


    @staticmethod
    def search_by_email(email):

        query = """
        SELECT *
        FROM suppliers
        WHERE email LIKE ?
        """

        return fetch_dataframe(
            query,
            (f"%{email}%",)
        )

    @staticmethod
    def supplier_summary(supplier_id):

        query = """
        SELECT
            s.id,
            s.name,
            s.company,

            COUNT(p.id) AS total_purchases,

            COALESCE(SUM(p.total_amount), 0) AS total_purchase_amount,

            COALESCE(SUM(p.paid_amount), 0) AS total_paid,

            COALESCE(SUM(p.remaining_amount), 0) AS total_remaining

        FROM suppliers s

        LEFT JOIN purchases p
            ON s.name = p.supplier

        WHERE s.id = ?

        GROUP BY s.id
        """

        df = fetch_dataframe(query, (supplier_id,))

        if df.empty:
            return None

        return df.iloc[0]


    @staticmethod
    def supplier_purchases(supplier_id):

        query = """
        SELECT
            p.*
        FROM purchases p

        INNER JOIN suppliers s
            ON s.name = p.supplier

        WHERE s.id = ?

        ORDER BY p.id DESC
        """

        return fetch_dataframe(query, (supplier_id,))


    @staticmethod
    def top_suppliers(limit=10):

        query = """
        SELECT

            supplier,

            COUNT(*) AS total_purchases,

            SUM(total_amount) AS purchase_amount,

            SUM(paid_amount) AS paid,

            SUM(remaining_amount) AS remaining

        FROM purchases

        GROUP BY supplier

        ORDER BY purchase_amount DESC

        LIMIT ?
        """

        return fetch_dataframe(query, (limit,))


    @staticmethod
    def suppliers_with_pending_balance():

        query = """
        SELECT

            supplier,

            SUM(remaining_amount) AS remaining_balance

        FROM purchases

        WHERE remaining_amount > 0

        GROUP BY supplier

        ORDER BY remaining_balance DESC
        """

        return fetch_dataframe(query)


    @staticmethod
    def inactive_suppliers():

        query = """
        SELECT *

        FROM suppliers

        WHERE name NOT IN (

            SELECT DISTINCT supplier

            FROM purchases

        )

        ORDER BY name
        """

        return fetch_dataframe(query)

    @staticmethod
    def recent_suppliers(limit=10):

        query = """
        SELECT *
        FROM suppliers
        ORDER BY id DESC
        LIMIT ?
        """

        return fetch_dataframe(query, (limit,))


    @staticmethod
    def supplier_dropdown():

        query = """
        SELECT
            id,
            name
        FROM suppliers
        ORDER BY name
        """

        return fetch_dataframe(query)


    @staticmethod
    def supplier_names():

        query = """
        SELECT
            name
        FROM suppliers
        ORDER BY name
        """

        df = fetch_dataframe(query)

        return df["name"].tolist()


    @staticmethod
    def supplier_statistics():

        query = """
        SELECT

            COUNT(*) AS total_suppliers,

            COUNT(
                DISTINCT city
            ) AS total_cities,

            COUNT(
                DISTINCT country
            ) AS total_countries

        FROM suppliers
        """

        df = fetch_dataframe(query)

        return df.iloc[0]


    @staticmethod
    def supplier_email_exists(email):

        query = """
        SELECT id
        FROM suppliers
        WHERE email = ?
        """

        df = fetch_dataframe(query, (email,))

        return not df.empty


    @staticmethod
    def supplier_phone_exists(phone):

        query = """
        SELECT id
        FROM suppliers
        WHERE phone = ?
        """

        df = fetch_dataframe(query, (phone,))

        return not df.empty


    @staticmethod
    def suppliers_by_city(city):

        query = """
        SELECT *
        FROM suppliers
        WHERE city = ?
        ORDER BY name
        """

        return fetch_dataframe(query, (city,))


    @staticmethod
    def suppliers_by_country(country):

        query = """
        SELECT *
        FROM suppliers
        WHERE country = ?
        ORDER BY name
        """

        return fetch_dataframe(query, (country,))

