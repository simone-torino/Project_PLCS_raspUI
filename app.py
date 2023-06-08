from flask import Flask, render_template, request
import mysql.connector
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

app = Flask(__name__)

# MySQL configuration
mysql_host = '192.168.221.16'
mysql_user = 'root'
mysql_password = '123'
mysql_db = 'dac'

reader = SimpleMFRC522()

# Generic functions for RFID read and write
def rfid_read():
    try:
        id, text = reader.read()
        print("ID letto: ", id)
        print("Testo: ", text)
    finally:
        GPIO.cleanup()
    return text

def rfid_write(code):
    try:
        reader.write(code)
        print("Written")
    finally:
        GPIO.cleanup()
    return True


# Route for user login
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if the RFID code is empty
        rfid_code = rfid_read()
        if not rfid_code:
            # Empty RFID code, display numeric keypad for login
            return keypad()

        # Non-empty RFID code, check if it exists in the database
        cnx = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        cursor = cnx.cursor()

        query = "SELECT * FROM people WHERE badge_id = %s"
        cursor.execute(query, (rfid_code,))
        result = cursor.fetchone()

        if result:
            # Correct RFID code, proceed to the dashboard
            return render_template('access_allowed.html')
        else:
            # Incorrect RFID code, display error message
            error_message = "Invalid RFID code"
            return render_template('access_denied.html')

    # GET request, render the login page
    return render_template('index.html')

def get_otp():
    return 123456


@app.route('/keypad', methods=["GET", "POST"])
def keypad():
    if request.method == 'POST':
        inserted_code = request.form.get('code-input')
        db_code = get_otp()

        if db_code == inserted_code:
            result = "Code is correct!"
            return render_template('access_allowed.html', result=result)
        else:
            result = "Code is incorrect!"
            return render_template('access_denied.html', result=result)

    return render_template('keypad.html')


if __name__ == '__main__':
    app.run()
