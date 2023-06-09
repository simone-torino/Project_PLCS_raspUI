from flask import Flask, render_template, request, jsonify, session
import pymysql
from mfrc522 import SimpleMFRC522
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'melanzana'

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
    # text is always 48 characters long
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
    session.clear()
    if request.method == "POST":
        # Check if the RFID code is empty
        rfid_code = rfid_read()
        rfid_code = str(rfid_code) # Convert to str to validate the comparison with empty
        rfid_code = rfid_code[:20] # Keep only the first 20 char since the read code is 48 long
        empty = str("                    ")
        
        # Empty RFID code, display numeric keypad for authentication
        if rfid_code == empty:
            print("Returning keypad")
            response = {'empty': True}
            # Redirect to /keypad handled in javascript
            return jsonify(response)

        response = {'empty' : False}

        # Non-empty RFID code, check if it exists in the database
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM people WHERE badge_id = %s', rfid_code)
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
    print("Keypad loaded")
    if request.method == 'POST':
        print("keypad POST")
        inserted_code = request.form.get('code')

    
        print("code from html: ", inserted_code)
        result = check_otp(inserted_code)
        print("keypad POST, OTP checked")

        if result == 'OTP - CORRECT':
            response = {'success': True}
            print("Correct OTP")

            # Redirect to /write handled in javascript
            return jsonify(response)
        else:
            response = {'success': False}
            print("wrong OTP")
            return jsonify(response)

    # GET request, render the page
    print("prima della get")
    return render_template('keypad.html')

# Route for write page
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':

        # Get previously inserted OTP from the session
        inserted_otp = session.get('OTP')

        # Retrieve from the database the badge code that corresponds to the OTP 
        badge = get_badge(inserted_otp)

        if(badge == 'ERROR: wrong otp'):
            print("Can't write card")
            response = {'success' : False}
            return jsonify(response)
        else:
            rfid_write(badge)
            ("Badge written:")
            print(badge)

            response = {'success': True}
            return jsonify(response)      
        
    # GET request, render the page    
    return render_template('Writebadge.html')

def check_otp(inserted_otp):
    conn = get_db()
    cursor = conn.cursor()
    conn = get_db()
    cursor = conn.cursor()

    # Fetch all the OTPs present in the database
    cursor.execute('SELECT otp_code, otp_expiration FROM invitations')
    conn.commit()
    rows = cursor.fetchall()
    cursor.close()

    flag = 0

    # Validate the code to be compliant with database types
    inserted_otp = str(inserted_otp)
    inserted_otp = inserted_otp[:6]
    print(inserted_otp)

    # After validation save in session
    session['OTP'] = inserted_otp


    for row in rows:
        print(row[0], " ", row[1])
        if inserted_otp == str(row[0]): 
            if datetime.now() < row[1]:
                # OTP found in the database
                flag = 1
            else:
                print("OTP expired on ", row[1])

    if flag == 0:
         # The entered OTP code is incorrect or expired
        return "OTP - ERROR"
    else:
        return 'OTP - CORRECT'

def get_badge(inserted_otp):
    conn = get_db()
    cursor = conn.cursor()
    print(inserted_otp)

    # CHeck if the inserted otp is present in the invitations table
    cursor.execute('SELECT id_invitation FROM invitations WHERE otp_code = %s', (str(inserted_otp)))
    idInv = cursor.fetchone() #TODO: this is always none
    if idInv is None:
        # If it's not probably something's wrong
        return 'ERROR: wrong otp'
    else:
        # If the OTP is found fetch the correspondent email
        cursor.execute('SELECT email FROM invitations WHERE otp_code = %s', (str(inserted_otp)))
        row_email = cursor.fetchone()
        email = row_email[0]

        # The email is used to retrieve the badge_id assigned at the registration
        cursor.execute('SELECT badge_id FROM people WHERE email = %s', (str(email)))
        badge = cursor.fetchone()
        badge = badge[0]

        cursor.close()

        return badge

if __name__ == '__main__':
    app.run()