from flask import Flask, request
from flask_restful import Resource, Api
import sqlite3, os, hashlib
from flask_cors import CORS
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from user import init_db

DB = 'user.db'
# ---------- Flask app ----------
app = Flask(__name__)
CORS(app)
api = Api(app)
init_db()

class Register(Resource):
    def post(self):
        data = request.get_json()
        email, pw = data.get('username'), data.get('password')
        addr, pin = data.get('address'), data.get('pincode')
        if not email or not pw:
            return {'error': 'email and password required'}, 400
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users(username,password,address,pincode) VALUES(?,?,?,?)',
                            (email, pw, addr, pin))
                conn.commit()
            return {'message': 'registered'}, 201
        except sqlite3.IntegrityError:
            return {'error': 'user already exists'}, 409

class Login(Resource):
    def post(self):
        data = request.get_json()
        email, pw = data.get('username'), data.get('password')
        print(email, pw)
        if not email or not pw:
            return {'error': 'email and password required'}, 400
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT password FROM users WHERE username=?', (email,))
                stored_pw = cur.fetchone()
                if stored_pw and stored_pw[0] == pw:
                    cur.execute('SELECT role FROM users WHERE username=?', (email,))
                    role = cur.fetchone()
                    if role:
                        return {'message': 'login successful', 'role': role[0]}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500
        return {'error': 'invalid credentials'}, 401

api.add_resource(Register, '/api/register')
api.add_resource(Login,    '/api/login')

if __name__ == '__main__':
    app.run(debug=True)
