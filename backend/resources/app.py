from unittest import result
from flask import Flask, request
from flask_restful import Resource, Api
import sqlite3, os, hashlib
from flask_cors import CORS
import sys
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from datetime import timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from user import init_db

DB = 'user.db'
# ---------- Flask app ----------
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'


app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 1 hour, adjust as needed
CORS(app, supports_credentials=True)
api = Api(app)
jwt = JWTManager(app)
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
                        # Create JWT token
                        access_token = create_access_token(identity=email)
                        return {
                            'message': 'login successful',
                            'role': role[0],
                            'access_token': access_token
                        }, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500
        return {'error': 'invalid credentials'}, 401

# Protect endpoints with @jwt_required()
class admin(Resource):
    @jwt_required()
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
    @jwt_required()
    def get(self):
        return {'message': 'create parking lot page'}
    @jwt_required()
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

class delete(Resource):
    @jwt_required()
    def delete(self, lot_id):
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('DELETE FROM parking_spots WHERE parking_lot_id=?', (lot_id,))
                cur.execute('DELETE FROM parking_lots WHERE id=?', (lot_id,))
                conn.commit()
            return {'message': 'parking lot deleted'}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500

class edit(Resource):
    @jwt_required()
    def get(self, lot_id):
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT * FROM parking_lots WHERE id=?', (lot_id,))
                lot = cur.fetchone()
                print(lot)
                if not lot:
                    return {'error': 'parking lot not found'}, 404
                return {'id': lot[0], 'prime_location_name': lot[1], 'address': lot[3], 'pincode': lot[4], 'price': lot[2], 'number_of_spots': lot[5]}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500
    @jwt_required()
    def put(self, lot_id):
        data = request.get_json()
        prime_location_name = data.get('primelocationname')
        address = data.get('address')
        pincode = data.get('pinCode')
        price = float(data.get('price'))
        number_of_spots = int(data.get('maxSpots'))
        print(prime_location_name, address, pincode, price, number_of_spots)

        if not prime_location_name or not address:
            return {'error': 'Required fields missing'}, 400

        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT id FROM parking_spots WHERE parking_lot_id=? AND is_occupied=1', (lot_id,))
                occupied_spots = cur.fetchall()

                if int(number_of_spots) < len(occupied_spots):
                    return {'error': 'Cannot reduce below occupied spots'}, 400

                cur.execute('SELECT number_of_spots FROM parking_lots WHERE id=?', (lot_id,))
                a = cur.fetchone()
                current_spots = a[0]

                if number_of_spots > current_spots:
                    for i in range(number_of_spots - current_spots):
                        cur.execute('INSERT INTO parking_spots(parking_lot_id) VALUES(?)', (lot_id,))
                elif number_of_spots < current_spots:
                    for i in range(current_spots - number_of_spots):
                        cur.execute('''
            DELETE FROM parking_spots
            WHERE id IN (
                SELECT id FROM parking_spots
                WHERE parking_lot_id=? AND is_occupied=0
                LIMIT 1
            )
        ''', (lot_id,))

                cur.execute('''
                    UPDATE parking_lots
                    SET prime_location_name=?, address=?, pincode=?, price=?, number_of_spots=?
                    WHERE id=?''',
                    (prime_location_name, address, pincode, price, number_of_spots, lot_id))
                conn.commit()

            return {'message': 'Parking lot updated'}, 200
        except Exception as e:
            print("Unhandled Error:", e)
            return {'error': str(e)}, 500
        
class spotdetail(Resource):
    @jwt_required()
    def get(self, lot_id):
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT is_occupied,parking_lot_id FROM parking_spots WHERE id=?', (lot_id,))
                spots = cur.fetchall()
                if not spots:
                    return {'error': 'No spots found for this lot'}, 404
                if spots[0][0] == 1:
                    cur.execute('SELECT customer_id, vehicle_number,reserved_at,leave_at FROM parking_spots WHERE id=?', (lot_id,))
                    reserved_info = cur.fetchone()
                    cur.execute('SELECT price FROM parking_lots WHERE id=?', (spots[0][1],))
                    lot = cur.fetchone()
                    if reserved_info and lot:
                        return {
                            'id': lot_id,
                            'status': 'O',
                            'customer_id': reserved_info[0],
                            'vehicle_number': reserved_info[1],
                            'reservedAt': reserved_info[2],
                            'leaveAt': reserved_info[3],
                            'cost': lot[0]
                        }, 200
                return {'id': lot_id, 'status': 'A'}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500
    @jwt_required()
    def delete(self, lot_id):
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                
                cur.execute('SELECT parking_lot_id FROM parking_spots WHERE id=?', (lot_id,))
                lot = cur.fetchone()
                print(lot[0])
                cur.execute('DELETE FROM parking_spots WHERE id=?', (lot_id,))
                cur.execute('SELECT COUNT(*) FROM parking_spots WHERE parking_lot_id=?', (lot[0],))
                count = cur.fetchone()
                cur.execute('UPDATE parking_lots SET number_of_spots=? WHERE id=?', (count[0], lot[0])) 
                conn.commit()
            return {'message': 'Parking spot deleted'}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500   


api.add_resource(Register, '/api/register')
api.add_resource(Login,    '/api/login')
api.add_resource(create,   '/create')
api.add_resource(admin,    '/admin')
api.add_resource(delete,   '/delete/lot/<int:lot_id>')
api.add_resource(edit,     '/api/parking-lots/<int:lot_id>')
api.add_resource(spotdetail, '/admin/spot/<int:lot_id>')


if __name__ == '__main__':
    app.run(debug=True)
