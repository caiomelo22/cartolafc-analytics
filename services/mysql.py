import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def connect():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
        )
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        raise

def execute_query(query):
    df = None
    db = None
    
    try:
        db = connect()
        cursor = db.cursor()

        cursor.execute(query)
        result = cursor.fetchall()

        # Convert the fetched data to a DataFrame
        column_names = [col[0] for col in cursor.description]
        df = pd.DataFrame(result, columns=column_names)
    finally:
        if db:
            db.close()

    return df

def get_data(table_name, columns=None, where_clause=None, order_by_clause=None):
    try:
        # If columns are not specified, fetch all columns (*)
        columns_str = "*" if columns is None else ", ".join(columns)

        # Build the SQL query with the optional WHERE clause
        query = f"SELECT {columns_str} FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        if order_by_clause:
            query += f" ORDER BY {order_by_clause}"

        df = execute_query(query)

        return df
    except mysql.connector.Error as e:
        print(f"Error fetching data: {e}")
        return None
