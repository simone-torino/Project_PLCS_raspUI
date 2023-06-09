from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql
from mfrc522 import SimpleMFRC522
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL configuration
mysql_host = '192.168.80.16'
mysql_user = 'pi'
mysql_password = '123'
mysql_db = 'dac'

# Establish MySQL connection
def get_db():
    return pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_db)

reader = SimpleMFRC522()

# Generic functions for RFID read and write
def rfid_read():
    id, text = reader.read()
    print("ID letto: ", id)
    print("Testo:", text)
    return text

def rfid_write(code):
    reader.write(code)
    print("Written", code)
    return True

# Route for home page
@app.route('/', methods=["GET", "POST"])
def read():
    if request.method == "POST":
        # Check if the RFID code is empty
        rfid_code = "00"
        empty = str("00")
        print(empty)
        rfid_code = str(rfid_code)
        print(rfid_code)

        # Empty RFID code, display numeric keypad for authentication
        if rfid_code == empty:
            print("Returning keypad")
            return redirect(url_for('keypad'))

        # Non-empty RFID code, check if it exists in the database
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM people WHERE badge_id = %s', (str(rfid_code)))
        row_badge = cursor.fetchone()

        if row_badge is None:
            # The RFID code was not found in the database
            response = {'success': False}
            print("RFID not found")
            return jsonify(response)
        else:
            # The RFID code was found
            print("RFID found")
            response = {'success': True, 'name': row_badge[3], 'surname' : row_badge[4]}
            return jsonify(response)

    # GET request, render the page
    return render_template('Readbadge.html')

# Route for keypad page
@app.route('/keypad', methods=["GET", "POST"])
def keypad():
    if request.method == 'POST':
        inserted_code = request.form.get('code-input')
        result = check_otp(inserted_code)

        if result == 'OTP - CORRECT':
            #response = {'success': True}
            return redirect(url_for('write'))
        else:
            response = {'success': False}
            return jsonify(response)

    # GET request, render the page
    return render_template('keypad.html')

# Route for write page
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        badge = get_badge()
        rfid_write(badge)
        print("Badge written:")
        print(badge)

    # GET request, render the page    
    return render_template('Writebadge.html')



def check_otp(inserted_otp):
    conn = get_db()
    cursor = conn.cursor()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT otp_code, otp_expiration FROM invitations')
    conn.commit()
    rows = cursor.fetchall()
    cursor.close()

    flag = 0

    for row in rows:
        if inserted_otp == row[0] and datetime.now() < row[1]:
            flag = 1

    if flag == 0:
         # The entered OTP code is incorrect or expired
        return "OTP - ERROR"
    else:
        return 'OTP - CORRECT'

def get_badge():
    inserted_otp = "some_otp"
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id_invitation FROM invitations WHERE otp_code = %s', (str(inserted_otp)))
    idInv = cursor.fetchone()
    if idInv is None:
        return 'ERROR: wrong otp'
    else:
        cursor.execute('SELECT email FROM invitations WHERE otp_code = %s', (str(inserted_otp)))
        row_email = cursor.fetchone()
        email = row_email[0]

        cursor.execute('SELECT badge_id FROM people WHERE email = %s', (str(email)))
        badge = cursor.fetchone()
        badge = badge[0]

        cursor.close()

        return badge

if __name__ == '__main__':
    app.run()