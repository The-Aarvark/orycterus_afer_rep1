import sqlite3
import json

def create_connection(db_path='links_database.db'):
    """Create a database connection to the SQLite database specified by db_path."""
    conn = sqlite3.connect(db_path)
    return conn

def read_all_data(db_path='links_database.db'):
    conn = create_connection(db_path)
    cursor = conn.cursor()

    # Read data from urls table
    cursor.execute("SELECT * FROM urls")
    urls = cursor.fetchall()

    # Read data from url_names table
    cursor.execute("SELECT * FROM url_names")
    url_names = cursor.fetchall()

    conn.close()

    return urls, url_names

def display_data(urls, url_names):
    print("URLs Table:")
    for url in urls:
        print(f"ID: {url[0]}, URL: {url[1]}, Found On: {json.loads(url[2]) if url[2] else '[]'}, Links To: {json.loads(url[3]) if url[3] else '[]'}")

    print("\nURL Names Table:")
    for name in url_names:
        print(f"ID: {name[0]}, URL ID: {name[1]}, Name: {name[2]}")

if __name__ == "__main__":
    urls, url_names = read_all_data()
    display_data(urls, url_names)
