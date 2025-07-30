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
    c.execute('''
CREATE TABLE IF NOT EXISTS reserved_parking_spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parking_spot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reserved_at TIMESTAMP ,
    leave_at TIMESTAMP,
    FOREIGN KEY (parking_spot_id) REFERENCES parking_spots (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

    c.execute("PRAGMA table_info(reserved_parking_spots)")
    columns_info = c.fetchall()
    column_names = [col[1] for col in columns_info]
    


# Check if column already exists
    if 'vehicle_number' not in column_names:
        c.execute('ALTER TABLE reserved_parking_spots ADD COLUMN vehicle_number TEXT')
    c.execute("PRAGMA table_info(users)")
    columns_info = c.fetchall()
    column_names = [col[1] for col in columns_info]
    if 'full_name' not in column_names:
        c.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
    conn.commit()
    conn.close()


