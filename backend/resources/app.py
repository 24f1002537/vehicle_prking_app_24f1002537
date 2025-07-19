from unittest import result
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

class admin(Resource):
    def get(self):
            try:
                result = {}
                with sqlite3.connect(DB) as conn:
                    cur = conn.cursor()
                    cur.execute('SELECT parking_lots.id, parking_lots.number_of_spots, parking_spots.is_occupied, parking_spots.id FROM parking_lots INNER JOIN parking_spots ON parking_lots.id = parking_spots.parking_lot_id')
                    a = cur.fetchall()
                    

                    for row in a:
                        lot_id, maxcapacity, occupied, spot_id = row
                        if lot_id not in result:
                            result[lot_id] = {
                            'id': lot_id,
                            'maxcapacity': maxcapacity,
                            'spotdetail': [],
                            'occupied': 0
                        }
                        if occupied:
                            result[lot_id]['occupied'] += 1  
                        result[lot_id]['spotdetail'].append({'id': spot_id, 'occupied': occupied})
                output = list(result.values())
                return {'message': 'admin dashboard', 'data': output}, 200
                
            except sqlite3.Error as e:
                return {'error': str(e)}, 500
                

class create(Resource):
    def get(self):
        return {'message': 'create parking lot page'}
    def post(self):
        data = request.get_json()
        lot_address, lot_location , pincode,price,maxspots = data.get('address'), data.get('locationName'), data.get('pinCode'), data.get('price'), data.get('maxSpots')
        if not lot_address or not lot_location:
            return {'error': 'lot address and location required'}, 400
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO parking_lots(prime_location_name,address,pincode,price,number_of_spots) VALUES(?,?,?,?,?)',
                            (lot_location, lot_address, pincode, price, maxspots))
                conn.commit()
                cur.execute('SELECT id FROM parking_lots WHERE prime_location_name=? AND address=?', (lot_location, lot_address))
                a = cur.fetchone()
                for i in range(maxspots):
                    cur.execute('INSERT INTO parking_spots(parking_lot_id) VALUES(?)', (a[0],))
                conn.commit()
            return {'message': 'parking lot created'}, 201
        except sqlite3.Error as e:
            return {'error': str(e)}, 500
    
api.add_resource(Register, '/api/register')
api.add_resource(Login,    '/api/login')
api.add_resource(create,   '/create')
api.add_resource(admin,    '/admin')

if __name__ == '__main__':
    app.run(debug=True)
