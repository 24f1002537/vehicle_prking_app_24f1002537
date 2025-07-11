import sqlite3

def init_db():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            address TEXT,
            pincode TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
