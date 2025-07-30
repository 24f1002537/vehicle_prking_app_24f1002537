from unittest import result
from flask import Flask, request,jsonify
from flask_restful import Resource, Api, reqparse
import sqlite3, os, hashlib
from flask_cors import CORS
import sys
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from datetime import timedelta,datetime
from collections import defaultdict
import redis
import json
from resources import PincodeSubmit
from resources import UserCSVReport  # Make sure it's imported
from resources import UserIdLookup

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

# Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_db_connection():
    """Creates a database connection."""
    # This script expects 'user.db' to be in the same directory.
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn

def invalidate_parking_cache(lot_id=None):
    """Invalidates the cache for parking-related data."""
    redis_client.delete('admin_dashboard_data')
    redis_client.delete('user_dashboard_data')
    if lot_id:
        redis_client.delete(f'parking_lot_{lot_id}')

class Register(Resource):
    def post(self):
        data = request.get_json()
        email, pw = data.get('username'), data.get('password')
        addr, pin = data.get('address'), data.get('pincode')
        full_name = data.get('full_name', '')  # Optional full name
        if not email or not pw:
            return {'error': 'email and password required'}, 400
        try:    
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users(username,password,address,pincode,full_name) VALUES(?,?,?,?,?)',
                            (email, pw, addr, pin, full_name))
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
        cached_data = redis_client.get('admin_dashboard_data')
        if cached_data:
            return json.loads(cached_data)
        try:
            result = {}
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT parking_lots.id, parking_lots.number_of_spots, parking_spots.is_occupied, parking_spots.id, parking_lots.address, parking_lots.pincode, parking_lots.price FROM parking_lots INNER JOIN parking_spots ON parking_lots.id = parking_spots.parking_lot_id')
                a = cur.fetchall()
                

                for row in a:
                    lot_id, maxcapacity, occupied, spot_id, address, pincode, price = row
                    if lot_id not in result:
                        result[lot_id] = {
                        'id': lot_id,
                        'maxcapacity': maxcapacity,
                        'spotdetail': [],
                        'occupied': 0,
                        'address': address,
                        'pincode': pincode,
                        'price': price
                    }
                    if occupied:
                        result[lot_id]['occupied'] += 1  
                    result[lot_id]['spotdetail'].append({'id': spot_id, 'occupied': occupied})
            output = list(result.values())
            response = {'message': 'admin dashboard', 'data': output}
            redis_client.setex('admin_dashboard_data', 3600, json.dumps(response)) # Cache for 1 hour
            return response, 200
            
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
            invalidate_parking_cache()
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
            invalidate_parking_cache(lot_id)
            return {'message': 'parking lot deleted'}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500

class edit(Resource):
    @jwt_required()
    def get(self, lot_id):
        cached_lot = redis_client.get(f'parking_lot_{lot_id}')
        if cached_lot:
            return json.loads(cached_lot)
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT * FROM parking_lots WHERE id=?', (lot_id,))
                lot = cur.fetchone()
                print(lot)
                if not lot:
                    return {'error': 'parking lot not found'}, 404
                response = {'id': lot[0], 'prime_location_name': lot[1], 'address': lot[3], 'pincode': lot[4], 'price': lot[2], 'number_of_spots': lot[5]}
                redis_client.setex(f'parking_lot_{lot_id}', 3600, json.dumps(response)) # Cache for 1 hour
                return response, 200
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
            invalidate_parking_cache(lot_id)
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
                    cur.execute('SELECT user_id, vehicle_number,reserved_at,leave_at FROM reserved_parking_spots WHERE parking_spot_id=?', (lot_id,))
                    reserved_info = cur.fetchone()
                    cur.execute('SELECT price FROM parking_lots WHERE id=?', (spots[0][1],))
                    lot = cur.fetchone()
                    if reserved_info and lot:
                        return {
                            'id': lot_id,
                            'status': 'O',
                            'customer_id': reserved_info[0],
                            'vehicle_number': reserved_info[1],
                            'reserved_at': reserved_info[2],
                            'leave_at': reserved_info[3],
                            'cost': lot[0]
                        }, 200
                return {'id': lot_id, 'status': 'A'}, 200
        except sqlite3.Error as e:
            print("Error fetching spot details:", e)
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
            invalidate_parking_cache()
            return {'message': 'Parking spot deleted'}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500   

class OccupiedSpots(Resource):
    @jwt_required()
    def get(self,email):
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                # Get all occupied spots with details
                cur.execute('SELECT id FROM users WHERE username=?', (email,))
                user = cur.fetchone()
                if user:
                    cur.execute('''
                        SELECT ps.id, rps.vehicle_number, rps.reserved_at, rps.leave_at, pl.address, ps.is_occupied
                        FROM reserved_parking_spots AS rps
                        INNER JOIN parking_spots AS ps ON rps.parking_spot_id = ps.id
                        INNER JOIN parking_lots AS pl ON ps.parking_lot_id = pl.id
                        WHERE rps.user_id = ?
                    ''', (user[0],))
                rows = cur.fetchall()
                print(rows)
                spots = []
                for row in rows:
                    spot_id,vehicle_number,occupied_time,release_time,location,is_occupied=row
                    if is_occupied and release_time is None:
                        is_occupied = 'occupied'
                    else:
                        is_occupied = 'Available'
                    spots.append({
                        'spot_id': spot_id,
                        'address': location,
                        'vehicle_number': vehicle_number,
                        'occupied_time': occupied_time,
                        'release_time': release_time,
                        'status': is_occupied
                    })
                print(spots)
                return {'spots': spots}, 200
        except sqlite3.Error as e:
            print("Error fetching occupied spots:", e)
            return {'error': str(e)}, 500
class notoccupied(Resource):
    @jwt_required()
    def get(self):
        cached_data = redis_client.get('user_dashboard_data')
        if cached_data:
            return json.loads(cached_data)
        try:
            result = {}
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT parking_lots.id, parking_lots.number_of_spots, parking_spots.is_occupied, parking_spots.id, parking_lots.address, parking_lots.pincode FROM parking_lots INNER JOIN parking_spots ON parking_lots.id = parking_spots.parking_lot_id')
                a = cur.fetchall()
                

                for row in a:
                    lot_id, maxcapacity, occupied, spot_id, address, pincode = row
                    if lot_id not in result:
                        result[lot_id] = {
                        'id': lot_id,
                        'spotid': 0,
                        'available': maxcapacity,
                        'address': address,
                        'pincode': pincode,
                    }
                    if occupied:
                        result[lot_id]['available'] -= 1
                    else:
                        result[lot_id]['spotid'] = spot_id
            output = list(result.values())
            response = {'message': 'user dashboard', 'data': output}
            redis_client.setex('user_dashboard_data', 3600, json.dumps(response)) # Cache for 1 hour
            return response, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500
    

class userbook(Resource):
    def get(self,email,spotid):
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT id FROM users WHERE username=?',(email,))
                user=cur.fetchone()
                cur.execute('SELECT parking_lot_id FROM parking_spots WHERE id=? ',(spotid,))
                spot=cur.fetchone()
                return {'userid': user[0],'lotid':spot[0],'spotid':spotid}, 200
        except sqlite3.Error as e:
                return {'error': str(e)}, 500
    def put(self):
        data = request.get_json()
        email = data.get('email')
        spotid = data.get('spotid')
        userid = data.get('userid')
        vehicle_number = data.get('vehicle_number')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
          with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO reserved_parking_spots(parking_spot_id, user_id, vehicle_number, reserved_at) VALUES(?,?,?,?)', (spotid, userid, vehicle_number, now))
                cur.execute('UPDATE parking_spots SET is_occupied=1 WHERE id=?', (spotid,))
                conn.commit()
                invalidate_parking_cache()
                return {'message': 'Spot booked successfully', 'email': email}, 200
        except sqlite3.Error as e:
                return {'error': str(e)}, 500  

class release(Resource):
    @jwt_required()
    def get(self,spotid):
        try:
                
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('''SELECT
            r.vehicle_number,
            r.reserved_at,
            r.leave_at,
            pl.price
        FROM reserved_parking_spots     AS r
        JOIN parking_spots     AS ps ON ps.id = r.parking_spot_id
        JOIN parking_lots      AS pl ON pl.id = ps.parking_lot_id WHERE ps.id = ?''', (spotid,))
                a = cur.fetchall()
                cur.execute('SELECT username FROM users WHERE id=(SELECT user_id FROM reserved_parking_spots WHERE parking_spot_id=? AND leave_at IS NULL)', (spotid,))
                username = cur.fetchone()
                for row in a:
                    vehicle_number, occupied_time, release_time, price = row
                    if not release_time:
                        cur.execute('SELECT strftime("%s", "now", "localtime") - strftime("%s", reserved_at) AS seconds_passed FROM reserved_parking_spots WHERE parking_spot_id=?', (spotid,))
                        duration = cur.fetchone()[0]
                        print(duration/3600)
                        cost = (duration/3600)*price
                        return {'vehicle_number': vehicle_number, 'cost': cost,'occupied_time': occupied_time , 'release_time': release_time,'email': username[0]}

        except sqlite3.Error as e:
            print("Error fetching spot details:", e)
            return {'error': str(e)}, 500
    @jwt_required()
    def post(self, spotid):
        data = request.get_json()
        try:
            with sqlite3.connect(DB) as conn:
                cur = conn.cursor()
                cur.execute('SELECT username FROM users WHERE id = (SELECT user_id FROM reserved_parking_spots WHERE parking_spot_id=? AND leave_at IS NULL)', (spotid,))
                username = cur.fetchone()
                cur.execute('UPDATE reserved_parking_spots SET leave_at=strftime("%Y-%m-%d %H:%M:%S", "now", "localtime") WHERE parking_spot_id=?', (spotid,))
                cur.execute('UPDATE parking_spots SET is_occupied=0 WHERE id=?', (spotid,))
                conn.commit()
                invalidate_parking_cache()
                return {'message': 'Parking spot released successfully', 'username': username[0]}, 200
        except sqlite3.Error as e:
            return {'error': str(e)}, 500


class Adsummary(Resource):
    @jwt_required()
    def get(self):
        revenue_data = {
        'user_detail': {},
        'spot_detail': {}}

        try:
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()

        # --- Query 1: Calculate total revenue per user ---
        # This query joins reservations with parking lots to get the price,
        # calculates the duration in hours, computes the revenue for each
        # reservation, and finally sums it up for each user.
        # It only considers reservations that have been completed (leave_at is not NULL).
                query_user_revenue = """
            SELECT
                u.id,
                SUM((strftime('%s', rps.leave_at) - strftime('%s', rps.reserved_at)) / 3600.0 * pl.price) AS total_revenue
            FROM
                users u
            JOIN
                reserved_parking_spots rps ON u.id = rps.user_id
            JOIN
                parking_spots ps ON rps.parking_spot_id = ps.id
            JOIN
                parking_lots pl ON ps.parking_lot_id = pl.id
            WHERE
                rps.leave_at IS NOT NULL
            GROUP BY
                u.id;
        """
                cursor.execute(query_user_revenue)
                user_revenues = cursor.fetchall()

        # --- Populate the user_detail dictionary ---
                for user_id, total_revenue in user_revenues:
            # Format revenue to 2 decimal places
                        revenue_data['user_detail'][user_id] = round(total_revenue, 2)


        # --- Query 2: Calculate total revenue per parking spot ---
        # This query is similar to the first but groups by the parking spot ID
        # to calculate the revenue generated by each individual spot.
                query_spot_revenue = """
            SELECT
                ps.id,
                SUM((strftime('%s', rps.leave_at) - strftime('%s', rps.reserved_at)) / 3600.0 * pl.price) AS total_revenue
            FROM
                parking_spots ps
            JOIN
                reserved_parking_spots rps ON ps.id = rps.parking_spot_id
            JOIN
                parking_lots pl ON ps.parking_lot_id = pl.id
            WHERE
                rps.leave_at IS NOT NULL
            GROUP BY
                ps.id;
        """
                cursor.execute(query_spot_revenue)
                spot_revenues = cursor.fetchall()

        # --- Populate the spot_detail dictionary ---
                for spot_id, total_revenue in spot_revenues:
                    revenue_data['spot_detail'][spot_id] = round(total_revenue, 2)


        except sqlite3.Error as e:
        # --- Handle potential SQL errors ---
            return {"error": f"Database error: {e}"}
        finally:
        # --- Ensure the database connection is closed ---
            if 'conn' in locals() and conn:
                conn.close()
        print(revenue_data)
        return revenue_data

class usersumarry(Resource):
    @jwt_required()
    def get(self,email):
        user_revenue_data = defaultdict(lambda: defaultdict(dict))
        try:
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()

        # --- Step 1: Find the user_id from the email ---
        # The 'username' column stores the email address.
            cursor.execute("SELECT id FROM users WHERE username = ?", (email,))
            user_record = cursor.fetchone()

            if not user_record:
                return {"error": f"User with email '{email}' not found."},400
        
            user_id = user_record[0]

        # --- Step 2: Get all completed reservations and calculate revenue for the user ---
        # This query calculates the revenue for each individual reservation and extracts
        # the year, month, and day from the 'reserved_at' timestamp.
            query = """
            SELECT
                strftime('%Y', rps.reserved_at) as year,
                strftime('%m', rps.reserved_at) as month,
                strftime('%d', rps.reserved_at) as day,
                (strftime('%s', rps.leave_at) - strftime('%s', rps.reserved_at)) / 3600.0 * pl.price AS revenue
            FROM
                reserved_parking_spots rps
            JOIN
                parking_spots ps ON rps.parking_spot_id = ps.id
            JOIN
                parking_lots pl ON ps.parking_lot_id = pl.id
            WHERE
                rps.user_id = ? AND rps.leave_at IS NOT NULL;
        """
            cursor.execute(query, (user_id,))
            daily_revenues = cursor.fetchall()

        # --- Step 3: Aggregate the revenues by day, month, and year ---
            for year, month, day, revenue in daily_revenues:
                # Convert keys to integers for proper sorting and access
                year_key = int(year)
                month_key = int(month)
                day_key = int(day)

            # Add the revenue of the current reservation to the total for that day
                current_day_revenue = user_revenue_data[year_key][month_key].get(day_key, 0)
                user_revenue_data[year_key][month_key][day_key] = current_day_revenue + revenue

        except sqlite3.Error as e:
            print(e)
            return {"error": f"Database error: {e}"},500
        finally:
        # --- Ensure the database connection is closed ---
            if 'conn' in locals() and conn:
                conn.close()

    # --- Convert defaultdict back to a regular dict for the final output ---
        return {year: {month: dict(days) for month, days in months.items()} for year, months in user_revenue_data.items()}

class aduser(Resource):
    @jwt_required()
    def get(self):
        try:
            conn = get_db_connection()
        # Fetch all columns needed for the frontend display, excluding users with the 'admin' role.
            users = conn.execute("SELECT id, username as email, full_name, address, pincode FROM users WHERE role != 'admin'").fetchall()
            conn.close()

        # Convert the database rows into a list of dictionaries to be sent as JSON.
            user_list = [dict(user) for user in users]
            return jsonify(user_list)
        except Exception as e:
            print(f"An error occurred while fetching users: {e}")
            return jsonify({"error": "An internal server error occurred."}), 500


class GetUserByEmail(Resource):
    @jwt_required()
    def get(self, email):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT username, full_name, address, pincode FROM users WHERE username = ?", (email,))
            user = cur.fetchone()
            conn.close()
            if user:
                return dict(zip(["username", "full_name", "address", "pincode"], user)), 200
            print(dict(zip(["username", "full_name", "address", "pincode"], user)))
            return {"error": "User not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 500
        
class UpdateUser(Resource):
    @jwt_required()
    def put(self, email):
        data = request.get_json()
        full_name = data.get('full_name')
        address = data.get('address')
        pincode = data.get('pincode')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET full_name = ?, address = ?, pincode = ? WHERE username = ?",
                        (full_name, address, pincode, email))
            conn.commit()
            conn.close()
            return {"message": "User updated successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500


# Add this resource to your API
api.add_resource(OccupiedSpots, '/api/user/Coccupied-spots/<string:email>')
api.add_resource(notoccupied, '/api/user/occupied-spots')
api.add_resource(release, '/api/user/occupied-spots/<int:spotid>')
api.add_resource(userbook, '/api/user/book/<string:email>/<int:spotid>', '/api/user/book')
api.add_resource(Register, '/api/register')
api.add_resource(Login,    '/api/login')
api.add_resource(create,   '/create')
api.add_resource(admin,    '/admin')
api.add_resource(delete,   '/delete/lot/<int:lot_id>')
api.add_resource(edit,     '/api/parking-lots/<int:lot_id>')
api.add_resource(Adsummary, '/api/admin/summary')
api.add_resource(spotdetail, '/admin/spot/<int:lot_id>')
api.add_resource(usersumarry, '/api/user/summary/<string:email>')
api.add_resource(aduser, '/api/admin/users')
api.add_resource(PincodeSubmit, '/submit-pincode')
api.add_resource(UserCSVReport, '/api/user/report/<string:email>/<int:user_id>')
api.add_resource(UserIdLookup, '/api/user/lookup/<string:email>')
api.add_resource(GetUserByEmail, '/api/user/profile/<string:email>')
api.add_resource(UpdateUser, '/api/user/update/<string:email>')


if __name__ == '__main__':
    app.run(debug=True)