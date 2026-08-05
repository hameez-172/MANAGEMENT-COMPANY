import streamlit as st
import pandas as pd

from database import (
    execute_query,
    fetch_dataframe,
)

class CustomerService:

    @staticmethod
    def get_all():
        query = """
        SELECT *
        FROM customers
        ORDER BY id DESC
        """
        return fetch_dataframe(query)

    @staticmethod
    def get(customer_id):
        query = """
        SELECT *
        FROM customers
        WHERE id = ?
        """
        df = fetch_dataframe(query, (customer_id,))
        return df.iloc[0] if not df.empty else None

    @staticmethod
    def exists(email):

        query = """
        SELECT id
        FROM customers
        WHERE email = ?
        """

        df = fetch_dataframe(query, (email,))

        return not df.empty

    @staticmethod
    def total():

        query = """
        SELECT COUNT(*) AS total
        FROM customers
        """

        df = fetch_dataframe(query)

        return int(df.iloc[0]["total"])

    @staticmethod
    def add_customer(
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
        INSERT INTO customers (
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
    def update_customer(
        customer_id,
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
        UPDATE customers
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
                customer_id
            )
        )

    @staticmethod
    def delete_customer(customer_id):

        query = """
        DELETE FROM customers
        WHERE id = ?
        """

        execute_query(query, (customer_id,))

    @staticmethod
    def search(keyword):

        keyword = f"%{keyword}%"

        query = """
        SELECT *
        FROM customers
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
        FROM customers
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
        FROM customers
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
        FROM customers
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
        FROM customers
        WHERE email LIKE ?
        """

        return fetch_dataframe(
            query,
            (f"%{email}%",)
        )

    @staticmethod
    def customer_summary(customer_id):

        query = """
        SELECT
            c.id,
            c.name,
            c.company,

            COUNT(d.id) AS total_deals,

            COALESCE(SUM(d.deal_value),0) AS total_revenue,

            COALESCE(SUM(d.sent_payment),0) AS total_received,

            COALESCE(SUM(d.remaining),0) AS total_remaining,

            COALESCE(SUM(d.profit),0) AS total_profit

        FROM customers c

        LEFT JOIN deals d
            ON c.name = d.client_name

        WHERE c.id = ?

        GROUP BY c.id
        """

        df = fetch_dataframe(query, (customer_id,))

        if df.empty:
            return None

        return df.iloc[0]


    @staticmethod
    def customer_deals(customer_id):

        query = """
        SELECT
            d.*
        FROM deals d

        INNER JOIN customers c
            ON c.name = d.client_name

        WHERE c.id = ?

        ORDER BY d.id DESC
        """

        return fetch_dataframe(query, (customer_id,))


    @staticmethod
    def top_customers(limit=10):

        query = """
        SELECT

            client_name,

            COUNT(*) AS total_deals,

            SUM(deal_value) AS revenue,

            SUM(sent_payment) AS received,

            SUM(remaining) AS remaining,

            SUM(profit) AS profit

        FROM deals

        GROUP BY client_name

        ORDER BY revenue DESC

        LIMIT ?
        """

        return fetch_dataframe(query, (limit,))


    @staticmethod
    def customers_with_pending_balance():

        query = """
        SELECT

            client_name,

            SUM(remaining) AS remaining_balance

        FROM deals

        WHERE remaining > 0

        GROUP BY client_name

        ORDER BY remaining_balance DESC
        """

        return fetch_dataframe(query)


    @staticmethod
    def inactive_customers():

        query = """
        SELECT *

        FROM customers

        WHERE name NOT IN (

            SELECT DISTINCT client_name

            FROM deals

        )

        ORDER BY name
        """

        return fetch_dataframe(query)

    @staticmethod
    def recent_customers(limit=10):

        query = """
        SELECT *
        FROM customers
        ORDER BY id DESC
        LIMIT ?
        """

        return fetch_dataframe(query, (limit,))


    @staticmethod
    def customer_dropdown():

        query = """
        SELECT
            id,
            name
        FROM customers
        ORDER BY name
        """

        return fetch_dataframe(query)


    @staticmethod
    def customer_names():

        query = """
        SELECT
            name
        FROM customers
        ORDER BY name
        """

        df = fetch_dataframe(query)

        return df["name"].tolist()


    @staticmethod
    def customer_statistics():

        query = """
        SELECT

            COUNT(*) AS total_customers,

            COUNT(
                DISTINCT city
            ) AS total_cities,

            COUNT(
                DISTINCT country
            ) AS total_countries

        FROM customers
        """

        df = fetch_dataframe(query)

        return df.iloc[0]


    @staticmethod
    def customer_email_exists(email):

        query = """
        SELECT id
        FROM customers
        WHERE email = ?
        """

        df = fetch_dataframe(query, (email,))

        return not df.empty


    @staticmethod
    def customer_phone_exists(phone):

        query = """
        SELECT id
        FROM customers
        WHERE phone = ?
        """

        df = fetch_dataframe(query, (phone,))

        return not df.empty


    @staticmethod
    def customers_by_city(city):

        query = """
        SELECT *
        FROM customers
        WHERE city = ?
        ORDER BY name
        """

        return fetch_dataframe(query, (city,))


    @staticmethod
    def customers_by_country(country):

        query = """
        SELECT *
        FROM customers
        WHERE country = ?
        ORDER BY name
        """

        return fetch_dataframe(query, (country,))


