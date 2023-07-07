# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session
import pymysql
from mfrc522 import SimpleMFRC522
from datetime import datetime

#alla raspberry viene associata una singola area_id
raspberry_area_id = 1

app = Flask(__name__)
app.secret_key = 'secretkey'

# MySQL configuration
mysql_host = '192.168.41.16'
mysql_user = 'pi'
mysql_password = '123'
mysql_db = 'dac'

# Establish MySQL connection
def get_db():
    try:
        return pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_db)
    except pymysql.Error as e:
        print("Error connection to the database:", e)
        return None

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
    if request.method == "POST":
        print("Sto leggendo la carta")
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
        if(conn == None):
            response = {'Err_db' : True}
            return jsonify(response)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM people WHERE badge_id = %s', rfid_code)
        row_badge = cursor.fetchone()

        if row_badge is None:
            # The RFID code was not found in the database
            response = {'dbsuccess': False}
            print("RFID not found")
            return jsonify(response)
        else:
            # The RFID code was found
            print("RFID found")

            #controlli su area
            person_id = row_badge[0] #estraggo l'id della persona
            company_id = row_badge[1] #estraggo l'id della compagnia
            cursor.execute('SELECT area_id FROM person_areas WHERE person_id = %s', [str(person_id)]) #seleziono gli area_id della persona del badge
            badges_area_id = cursor.fetchall()



            #alla persona del badge non è associata alcuna area
            if badges_area_id is None:
                #scrivo nell'access_history che c'è stata una violazione
                violation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO access_history (person_id, company_id, area_id, timestamp_IN, is_violation) VALUES (%s, %s, %s, %s, %s)", [str(person_id), str(company_id), str(raspberry_area_id), str(violation_time), str(1)])
                cursor.commit()
                response = {'dbsuccess': True, 'tssuccess': False, 'name': row_badge[3], 'surname': row_badge[4]} #timestamp success --> significa che c'è stata una violazione
                return jsonify(response)
            
            else:
                badges_area_id = [x[0] for x in badges_area_id] #salvo gli area_id in un vettore
                flag_badge = 0
                #verifico se almeno uno di questi id corrisponde a quello dell'area del raspberry            
                for badge_area_id in badges_area_id:
                    if badge_area_id == raspberry_area_id:
                        flag_badge = 1
                #se esco dal loop senza che la risposta sia stata ritornata allora vuole dire che il badge non ha il permesso e segnalo una violazione
                if flag_badge == 0:    
                    violation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO access_history (person_id, company_id, area_id, timestamp_IN, is_violation) VALUES (%s, %s, %s, %s, %s)", [str(person_id), str(company_id), str(raspberry_area_id), str(violation_time), str(1)])
                    cursor.commit()
                    response = {'dbsuccess': True, 'tssuccess': False, 'name': row_badge[3], 'surname': row_badge[4]}
                    return jsonify(response)

                #log dell'ora di accesso: adesso sappiamo che il permesso c'è quindi scriviamo il log

                #se timestamp_IN non esiste per quell'area allora significa che devo scrivere il log di ingresso
                cursor.execute('SELECT timestamp_IN FROM access_history WHERE person_id = %s AND company_id = %s AND area_id = %s', [str(person_id), str(company_id), str(raspberry_area_id)])
                time_IN = cursor.fetchone()
                
                if time_IN is None: #significa che per quella persona, in quell'azienda per quell'area non c'è stato accesso, pertanto è un ingresso
                    string_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO access_history (person_id, company_id, area_id, timestamp_IN, is_violation) VALUES (%s, %s, %s, %s, %s)", [str(person_id), str(company_id), str(raspberry_area_id), str(string_time), str(0)])
                    cursor.commit()
                    response = {'dbsuccess': True, 'tssuccess': True, 'ts_in' :datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'name': row_badge[3], 'surname': row_badge[4] }
                
                else: #se trovo un timestamp in, devo però verificare che  il timestamp out sia vuoto, in quel caso significa che sto uscendo
                    cursor.execute('SELECT timestamp_OUT FROM access_history WHERE person_id = %s AND company_id = %s AND area_id = %s', [str(person_id), str(company_id), str(raspberry_area_id)])
                    time_OUT = cursor.fetchone()
                    if time_OUT is None:
                        string_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute('UPDATE access_history SET timestamp_OUT = %s',[str(string_time)])
                        response = {'dbsuccess': True, 'tssuccess': True, 'ts_out' :datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'name': row_badge[3], 'surname': row_badge[4] }

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
        print("OTP from session:", inserted_otp)

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

            session.clear()

            response = {'success': True}
            return jsonify(response)      
        
    # GET request, render the page    
    return render_template('Writebadge.html')

def check_otp(inserted_otp):
    conn = get_db()
    if(conn == None):
        response = {'Err_db' : True}
        return jsonify(response)
    cursor = conn.cursor()

    # Fetch all the OTPs present in the database
    cursor.execute('SELECT otp_code, otp_expiration_DAC FROM invitations')
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
    if(conn == None):
        response = {'Err_db' : True}
        return jsonify(response)
    cursor = conn.cursor()
    print(inserted_otp)

    # CHeck if the inserted otp is present in the invitations table
    cursor.execute('SELECT id_invitation FROM invitations WHERE otp_code = %s', (str(inserted_otp)))
    idInv = cursor.fetchone() 
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