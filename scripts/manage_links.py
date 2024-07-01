import sqlite3
import json
import logging

class LinkDatabase:
    def __init__(self, db_path='scripts/links_database.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def add_url(self, url, found_on=None, links_to=None):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO urls (url, found_on, links_to) VALUES (?, ?, ?)", (url, json.dumps(found_on), json.dumps(links_to)))
            self.conn.commit()
            self.cursor.execute("SELECT id FROM urls WHERE url = ?", (url,))
            url_id = self.cursor.fetchone()
            if url_id:
                logging.info(f"Added URL: {url} with ID: {url_id[0]}")
                return url_id[0]
            else:
                logging.error(f"Failed to retrieve ID for URL: {url}")
                return None
        except sqlite3.Error as e:
            logging.error(f"Error adding URL: {url} - {e}")
            return None

    def add_name(self, url_id, name):
        try:
            self.cursor.execute("INSERT INTO url_names (url_id, name) VALUES (?, ?)", (url_id, name))
            self.conn.commit()
            logging.info(f"Added name: {name} for URL ID: {url_id}")
        except sqlite3.Error as e:
            logging.error(f"Error adding name: {name} for URL ID: {url_id} - {e}")

    def update_relationships(self, url, found_on=None, links_to=None):
        url_id = self.get_url_id(url)
        if not url_id:
            url_id = self.add_url(url, found_on, links_to)
        else:
            try:
                self.cursor.execute("SELECT found_on, links_to FROM urls WHERE id = ?", (url_id,))
                row = self.cursor.fetchone()
                current_found_on = json.loads(row[0]) if row[0] else []
                current_links_to = json.loads(row[1]) if row[1] else []

                if found_on:
                    current_found_on.extend([f for f in found_on if f not in current_found_on])
                if links_to:
                    current_links_to.extend([l for l in links_to if l not in current_links_to])

                self.cursor.execute("UPDATE urls SET found_on = ?, links_to = ? WHERE id = ?", (json.dumps(current_found_on), json.dumps(current_links_to), url_id))
                self.conn.commit()
                logging.info(f"Updated URL: {url} with ID: {url_id}")
            except sqlite3.Error as e:
                logging.error(f"Error updating relationships for URL: {url} with ID: {url_id} - {e}")

        return url_id

    def get_url_id(self, url):
        try:
            self.cursor.execute("SELECT id FROM urls WHERE url = ?", (url,))
            result = self.cursor.fetchone()
            if result:
                logging.info(f"Retrieved URL ID: {result[0]} for URL: {url}")
                return result[0]
            else:
                logging.info(f"No URL ID found for URL: {url}")
                return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving URL ID for URL: {url} - {e}")
            return None

    def get_names(self, url_id):
        try:
            self.cursor.execute("SELECT name FROM url_names WHERE url_id = ?", (url_id,))
            names = [row[0] for row in self.cursor.fetchall()]
            logging.info(f"Retrieved names: {names} for URL ID: {url_id}")
            return names
        except sqlite3.Error as e:
            logging.error(f"Error retrieving names for URL ID: {url_id} - {e}")
            return []

    def get_relationships(self, url_id):
        try:
            self.cursor.execute("SELECT found_on, links_to FROM urls WHERE id = ?", (url_id,))
            row = self.cursor.fetchone()
            if row:
                found_on = json.loads(row[0]) if row[0] else []
                links_to = json.loads(row[1]) if row[1] else []
                logging.info(f"Retrieved relationships for URL ID: {url_id} - Found On: {found_on}, Links To: {links_to}")
                return found_on, links_to
            else:
                logging.info(f"No relationships found for URL ID: {url_id}")
                return [], []
        except sqlite3.Error as e:
            logging.error(f"Error retrieving relationships for URL ID: {url_id} - {e}")
            return [], []

    def url_exists(self, url):
        return self.get_url_id(url) is not None

    def add_url_with_relationships(self, url, found_on, links_to):
        url_id = self.update_relationships(url, found_on, links_to)
        if url_id:
            # Add names if they don't exist
            if not self.get_names(url_id):
                self.add_name(url_id, url)
            logging.info(f"Added/updated URL: {url} (ID: {url_id}) with names and relationships")
        else:
            logging.error(f"Failed to add/update URL: {url}")
        return url_id

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    db = LinkDatabase()

    # Example usage
    url = "http://example.com"
    found_on = ["http://another-example.com", "http://yet-another-example.com"]
    links_to = ["http://linked-example.com", "http://another-linked-example.com"]
    
    url_id = db.add_url_with_relationships(url, found_on, links_to)
    
    print(f"URL ID: {url_id}")
    print(f"Names: {db.get_names(url_id)}")
    print(f"Found On: {db.get_relationships(url_id)}")
    
    db.close()
