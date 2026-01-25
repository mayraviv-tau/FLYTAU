"""
Database connection and helper functions
"""
import mysql.connector
from mysql.connector import Error
from config import Config
from contextlib import contextmanager

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            autocommit=False
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

@contextmanager
def db_transaction(commit=False):
    """
    Context manager for database operations
    Usage:
        with db_transaction(commit=True) as db:
            db.execute(query, params)
    """
    connection = get_db_connection()
    db = connection.cursor(dictionary=True)
    try:
        yield db
        if commit:
            connection.commit()
    except Error as e:
        connection.rollback()
        raise
    finally:
        db.close()
        connection.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a SQL query and return results

    Args:
        query: SQL query string
        params: Parameters for the query (tuple or dict)
        fetch_one: Return single row
        fetch_all: Return all rows
        commit: Commit transaction

    Returns:
        Result based on fetch_one/fetch_all flags
    """
    with db_transaction(commit=commit) as db:
        db.execute(query, params or ())

        if fetch_one:
            return db.fetchone()
        elif fetch_all:
            return db.fetchall()
        else:
            return db.rowcount

