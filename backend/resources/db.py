import sqlite3
def get_users_by_pincode(pincode):
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT full_name, username, address FROM users WHERE pincode = ?', (pincode,))
    users = [{'name': name, 'email': email, 'address': address} for name, email, address in cursor.fetchall()]
    conn.close()
    return users

