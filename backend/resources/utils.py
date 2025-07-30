

import sqlite3


def get_db_connection():
    """Creates a database connection."""
    # This script expects 'user.db' to be in the same directory.
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn