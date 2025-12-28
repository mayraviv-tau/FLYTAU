"""
Database connection management for FLYTAU.
Provides connection pooling and query execution utilities.
"""

import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from flask import current_app


# Global connection pool
_connection_pool = None


def init_db_pool(config):
    """
    Initialize the database connection pool.

    Args:
        config: Flask configuration object with DB settings
    """
    global _connection_pool

    try:
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name=config['DB_POOL_NAME'],
            pool_size=config['DB_POOL_SIZE'],
            host=config['DB_HOST'],
            port=config['DB_PORT'],
            database=config['DB_NAME'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            autocommit=False
        )
        print(f"Database pool initialized: {config['DB_NAME']}@{config['DB_HOST']}")
    except Error as e:
        print(f"Error initializing database pool: {e}")
        raise


def get_connection_pool():
    """Get the global connection pool."""
    if _connection_pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() first.")
    return _connection_pool


@contextmanager
def get_db_connection():
    """
    Get a database connection from the pool (context manager).

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
    """
    connection = None
    try:
        connection = get_connection_pool().get_connection()
        yield connection
    except Error as e:
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a database query with automatic connection management.

    Args:
        query (str): SQL query to execute
        params (tuple/dict): Query parameters
        fetch_one (bool): Return single row
        fetch_all (bool): Return all rows
        commit (bool): Commit transaction after execution

    Returns:
        Query results or None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())

            if commit:
                conn.commit()
                return cursor.lastrowid

            if fetch_one:
                return cursor.fetchone()

            if fetch_all:
                return cursor.fetchall()

            return None
        finally:
            cursor.close()


def execute_transaction(operations):
    """
    Execute multiple database operations in a transaction.

    Args:
        operations (list): List of tuples (query, params)

    Returns:
        List of last row IDs for INSERT operations

    Raises:
        Exception: If any operation fails, rolls back entire transaction

    Usage:
        ops = [
            ("INSERT INTO table1 VALUES (%s, %s)", (val1, val2)),
            ("UPDATE table2 SET col=%s WHERE id=%s", (val, id))
        ]
        execute_transaction(ops)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        results = []

        try:
            for query, params in operations:
                cursor.execute(query, params or ())
                results.append(cursor.lastrowid)

            conn.commit()
            return results
        except Exception as e:
            conn.rollback()
            raise Exception(f"Transaction failed: {str(e)}")
        finally:
            cursor.close()
