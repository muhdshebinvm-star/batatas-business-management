import os
import mysql.connector
import streamlit as st


def get_db_config():
    """Read cloud environment variables first, then local Streamlit secrets."""
    try:
        secrets = st.secrets.get("mysql", {})
    except Exception:
        secrets = {}

    host = os.getenv("DB_HOST") or os.getenv("MYSQLHOST") or secrets.get("host", "localhost")
    port = os.getenv("DB_PORT") or os.getenv("MYSQLPORT") or secrets.get("port", 3306)
    user = os.getenv("DB_USER") or os.getenv("MYSQLUSER") or secrets.get("user", "root")
    password = os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD") or secrets.get("password", "")
    database = os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE") or secrets.get("database", "bataatas_db")

    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": 10,
    }


def get_connection():
    return mysql.connector.connect(**get_db_config())


def query(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def execute(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result
    finally:
        conn.close()
