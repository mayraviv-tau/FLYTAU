"""
Database connection and helper functions
"""
import os
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

def get_db_connection():
    try:
        if os.getenv('PYTHONANYWHERE_DOMAIN'):
            connection = mysql.connector.connect(
                host='AmitHovav.mysql.pythonanywhere-services.com',
                user='AmitHovav',
                password='Group_14',  
                database='AmitHovav$flytau', 
                autocommit=False
            )
        else:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',                
                password='1234', 
                database='flytau',
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
    """
    with db_transaction(commit=commit) as db:
        db.execute(query, params or ())

        if fetch_one:
            return db.fetchone()
        elif fetch_all:
            return db.fetchall()
        else:
            return db.rowcount