import sqlite3
import os

def setup_databases(db_path='web_scraping/database/web_scraping.db'):
    # Ensure the database directory exists
    database_dir = os.path.dirname(db_path)
    if not os.path.exists(database_dir):
        os.makedirs(database_dir)

    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        url TEXT,
        src TEXT,
        url_hash TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY,
        url TEXT,
        action TEXT,
        method TEXT,
        embedding TEXT,
        url_hash TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS form_fields (
        id INTEGER PRIMARY KEY,
        form_id INTEGER,
        name TEXT,
        type TEXT,
        value TEXT,
        FOREIGN KEY(form_id) REFERENCES forms(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soups (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        headers TEXT,
        content TEXT,
        embedding TEXT,
        url_hash TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS links (
        id TEXT PRIMARY KEY,
        url TEXT,
        names TEXT,
        linked_to TEXT,
        linked_from TEXT,
        embedding TEXT,
        url_hash TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY,
        url TEXT,
        table_html TEXT,
        url_hash TEXT
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_databases()
