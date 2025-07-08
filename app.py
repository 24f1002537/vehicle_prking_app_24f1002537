from flask import Flask, request
from flask_restful import Resource, Api
import sqlite3, os, hashlib
from flask_cors import CORS


DB = 'user.db'

# ---------- database bootstrap ----------
def init_db():
    if os.path.exists(DB):
        return
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE users(
                          id       INTEGER PRIMARY KEY AUTOINCREMENT,
                          email    TEXT    UNIQUE NOT NULL,
                          password TEXT    NOT NULL,
                          address  TEXT,
                          pincode  TEXT)''')
        conn.commit()

def hash_pw(pw):              # simple SHA-256 helper
    return hashlib.sha256(pw.encode()).hexdigest()

# ---------- Flask app ----------
app = Flask(__name__)
CORS(app)
api = Api(app)
init_db()

class Register(Resource):
    def post(self):
        data = request.get_json()
        email, pw = data.get('email'), data.get('password')
        addr, pin = data.get('address'), data.get('pincode')
        if not email or not pw:
            return {'error': 'email and password required'}, 400
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users(email,password,address,pincode) VALUES(?,?,?,?)',
                            (email, hash_pw(pw), addr, pin))
                conn.commit()
            return {'message': 'registered'}, 201
        except sqlite3.IntegrityError:
            return {'error': 'user already exists'}, 409

class Login(Resource):
    def post(self):
        data = request.get_json()
        email, pw = data.get('email'), data.get('password')
        if not email or not pw:
            return {'error': 'email and password required'}, 400
        if email == 'admin@gmail.com' and pw == '1234':
            return {'message': 'admin'}, 201
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute('SELECT 1 FROM users WHERE email=? AND password=?',
                        (email, hash_pw(pw)))
            if cur.fetchone():
                return {'message': 'user'}, 200
        return {'error': 'invalid credentials'}, 401

api.add_resource(Register, '/api/register')
api.add_resource(Login,    '/api/login')

if __name__ == '__main__':
    app.run(debug=True)
