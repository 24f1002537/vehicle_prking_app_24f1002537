import os
import smtplib
from email.message import EmailMessage
from celery import Celery
from dotenv import load_dotenv
import sqlite3
import csv
from datetime import datetime
from tempfile import NamedTemporaryFile

# Load .env
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task(name="tasks.send_email_to_similar_users")
def send_email_to_similar_users(users, pincode):
    print("=== EMAIL TASK STARTED ===")

    for user in users:
        recipient = user['email']
        print(f"Sending real email to: {recipient} in pincode {pincode}")

        msg = EmailMessage()
        msg["Subject"] = f"Local Alert for Pincode {pincode}"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg.set_content(f"Hi there!\n\nSomething important is happening in your area (pincode {pincode}). Please check it out.")

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
        except Exception as e:
            print(f"Failed to send to {recipient}: {e}")

@celery.task(name="tasks.generate_and_send_usage_report")
def generate_and_send_usage_report(email, user_id):
    db_path = "user.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch user sessions
        cursor.execute("""
            SELECT 
                r.parking_spot_id,
                r.vehicle_number,
                r.reserved_at,
                r.leave_at,
                p.address,
                l.price
            FROM reserved_parking_spots r
            JOIN parking_spots s ON r.parking_spot_id = s.id
            JOIN parking_lots l ON s.parking_lot_id = l.id
            JOIN parking_lots p ON p.id = s.parking_lot_id
            WHERE r.user_id = ?
        """, (user_id,))
        records = cursor.fetchall()

        # Prepare the CSV
        with NamedTemporaryFile(mode='w', delete=False, newline='', suffix=".csv") as temp_csv:
            writer = csv.writer(temp_csv)
            writer.writerow(["Spot ID", "Vehicle Number", "Reserved At", "Leave At", "Status", "Cost", "Address"])

            total_cost = 0.0

            for spot_id, vehicle_number, reserved_at, leave_at, address, price in records:
                reserved_time = datetime.strptime(reserved_at, '%Y-%m-%d %H:%M:%S')
                if leave_at:
                    leave_time = datetime.strptime(leave_at, '%Y-%m-%d %H:%M:%S')
                    hours = (leave_time - reserved_time).total_seconds() / 3600
                    cost = round(hours * price, 2)
                    status = "Completed"
                else:
                    leave_time = None
                    hours = (datetime.now() - reserved_time).total_seconds() / 3600
                    cost = round(hours * price, 2)
                    status = "Ongoing"

                total_cost += cost

                writer.writerow([
                    spot_id,
                    vehicle_number,
                    reserved_at,
                    leave_at if leave_at else "Ongoing",
                    status,
                    f"{cost:.2f}",
                    address
                ])

            writer.writerow([])
            writer.writerow(["", "", "", "", "TOTAL COST", f"{total_cost:.2f}"])

        # Email the CSV
        msg = EmailMessage()
        msg["Subject"] = "Your Parking Usage Report"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg.set_content("Hi,\n\nAttached is your detailed parking usage report.")

        with open(temp_csv.name, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="usage_report.csv")

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f"CSV report emailed to {email}")

    except Exception as e:
        print(f"Error generating report: {e}")

    finally:
        if conn:
            conn.close()