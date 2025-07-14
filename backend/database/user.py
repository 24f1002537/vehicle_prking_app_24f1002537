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
            pincode TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    
    ''')
    #c.execute('''INSERT INTO users(username,password,address,pincode,role) VALUES(?,?,?,?,?)''', ('admin', 'admin123', '123 Admin St', '12345', 'admin'))
    conn.commit()
    conn.close()

