from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL configuration
mysql_host = '192.168.184.16'
mysql_user = 'root'
mysql_password = '123'
mysql_db = 'dac'

#inizializzazione del database MySQL
mysql = MySQL(app)

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

# Route for home page
@app.route('/', methods=["GET", "POST"])
def read_route():
    return read(mysql)

def read(mysql):
    if request.method == "POST":
        # Check if the RFID code is empty
        rfid_code = 1
        if not rfid_code:
            # Empty RFID code, display numeric keypad for login
            return keypad()
        
        #Non-empty RFID code, check if it exists in the database
        conn = mysql.connection
        conn.begin()
        cur = conn.cursor()

        cur.execute('SELECT * FROM people WHERE badge_id = %s', [str(rfid_code)])
        conn.commit()
        row_badge = cur.fetchone()
        
        if row_badge == None:
            error_message = "Invalid RFID code"
        else:
            return render_template('Writebadge.html')

    # GET request, render the page
    return render_template('Readbadge.html')


@app.route('/keypad', methods=["GET", "POST"])
def keypad_route():
    return keypad(mysql)

def keypad(mysql):
    if request.method == 'POST':
        inserted_code = request.form.get('code-input')
        response = get_otp(mysql,inserted_code)

        if response == 'OTP - CORRECT':
            result = "Code is correct!"
            return write(mysql)
        else:
            result = "Code is incorrect!"

    # GET request, render the page
    return render_template('keypad.html')

@app.route('/write', methods = ['GET','POST'])
def write_route():
    return write(mysql)

def write(mysql):
    if request.method == 'POST':
        badge = get_badge();
        
    # GET request, render the page    
    return render_template('Writebadge.html')

if __name__ == '__main__':
    app.run()


def get_otp(mysql,inserted_code):
    conn = mysql.connection
    conn.begin()
    cur = conn.cursor()

    cur.execute('SELECT otp_code, otp_expiration FROM invitations')
    conn.commit()
    rows = cur.fetchall()
    cur.close()

    flag = 0

    for row in rows:
        if inserted_code == row[0] and datetime.now() < row[1]:
            flag = 1

    if flag == 0:
         # L'OTP code inserito è errato o scaduto
        return ("OTP - ERROR")
    else:
        return('OTP - CORRECT')


def get_badge(mysql, inserted_otp):
    conn = mysql.connection
    conn.begin()
    cur = conn.cursor()

    cur.execute('SELECT id_invitation FROM invitations WHERE otp_code = %s', [str(inserted_otp)])
    conn.commit()
    idInv = cur.fetchone()
    if idInv == None:
        return('ERROR: wrong otp')
    else:
        cur.execute('SELECT email FROM invitations WHERE otp_code = %s', [str(inserted_otp)])
        conn.commit()
        row_email = cur.fetchone()
        email = row_email[0]

        cur.execute('SELECT badge_id FROM people WHERE email = %s', [str(email)])
        conn.commit()
        badge = cur.fetchone()
        badge = badge[0]

        cur.close()

        return(badge)