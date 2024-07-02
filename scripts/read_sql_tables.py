import sqlite3
import pandas as pd

def connect_to_db(db_path='web_scraping/database/web_scraping.db'):
    return sqlite3.connect(db_path)

def read_table(conn, table_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    return df

# Connect to the database
db_path = 'web_scraping/database/web_scraping.db'
conn = connect_to_db(db_path)

# Specify the tables you want to read
tables = ['images', 'forms', 'form_fields', 'soups', 'links']

# Read and display the tables
for table in tables:
    df = read_table(conn, table)
    print(f"Table: {table}")
    display(df)

# Close the connection
conn.close()
