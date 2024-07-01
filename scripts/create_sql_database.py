import sqlite3

def create_sql_database(db_path='links_database.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create table for URLs
    c.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    found_on TEXT,
                    links_to TEXT
                 )''')
    
    # Create table for URL names
    c.execute('''CREATE TABLE IF NOT EXISTS url_names (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (url_id) REFERENCES urls(id)
                 )''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_sql_database()
