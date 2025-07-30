from flask_restful import Resource, reqparse
from db import get_users_by_pincode
from tasks import send_email_to_similar_users
import json
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from tasks import generate_and_send_usage_report
from utils import get_db_connection


class PincodeSubmit(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('pinCode', required=True)
        args = parser.parse_args()

        matched_users = get_users_by_pincode(args['pinCode'])

        if matched_users:
            send_email_to_similar_users.delay(matched_users, args['pinCode'])
            return {"message": f"Emails are being sent to {len(matched_users)} users in pincode {args['pinCode']}."}, 200
        else:
            return {"message": "No users found for that pincode."}, 404
        
class UserCSVReport(Resource):
    @jwt_required()
    def post(self, email, user_id):
        try:
            generate_and_send_usage_report.delay(email, user_id)
            return {"message": f"CSV usage report is being generated and sent to {email}."}, 202
        except Exception as e:
            return {"error": f"Failed to start report generation: {str(e)}"}, 500
        


class UserIdLookup(Resource):
    def get(self, email):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?", (email,))
            user = cur.fetchone()
            conn.close()

            if user:
                return {"user_id": user[0]}, 200
            else:
                return {"error": "User not found"}, 404

        except Exception as e:
            return {"error": str(e)}, 500