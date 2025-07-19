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
    c.execute('''SELECT * FROM users WHERE username='admin' ''')
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password, role,address,pincode) VALUES (?, ?, ?, ?, ?)', ('admin', 'admin', 'admin','admin address','123456 '))
    c.execute('''CREATE TABLE IF NOT EXISTS parking_lots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              prime_location_name TEXT NOT NULL,
              price REAL NOT NULL,
              address TEXT NOT NULL,
              pincode INTEGER NOT NULL,
              number_of_spots INTEGER NOT NULL
              )''')
    c.execute('''CREATE TABLE IF NOT EXISTS parking_spots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              parking_lot_id INTEGER NOT NULL,
              is_occupied BOOLEAN DEFAULT FALSE,
              FOREIGN KEY (parking_lot_id) REFERENCES parking_lots (id)
              )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reserved_parking_spots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              parking_spot_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              leave_at TIMESTAMP,
              FOREIGN KEY (parking_spot_id) REFERENCES parking_spots (id),
              FOREIGN KEY (user_id) REFERENCES users (id)
              )''')
    conn.commit()
    conn.close()

