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
def get_db_cursor(commit=False):
    """
    Context manager for database cursor
    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            connection.commit()
    except Error as e:
        connection.rollback()
        raise
    finally:
        cursor.close()
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
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor.rowcount

