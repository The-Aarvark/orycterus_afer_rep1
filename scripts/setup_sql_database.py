# scripts/setup_sql_database.py

import sqlite3
import os

# Ensure the database directory exists
if not os.path.exists('web_scraping/database'):
    os.makedirs('web_scraping/database')

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('web_scraping/database/web_scraping.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY,
    url TEXT,
    src TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS forms (
    id INTEGER PRIMARY KEY,
    url TEXT,
    action TEXT,
    method TEXT,
    embedding TEXT
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
    content TEXT,
    embedding TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS links (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE,
    names TEXT,
    linked_to TEXT,
    linked_from TEXT,
    embedding TEXT
)
''')

conn.commit()
conn.close()
