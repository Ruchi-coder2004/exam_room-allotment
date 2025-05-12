from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="Ruchi@2004", 
    database="exceldb"  
)
cursor = db.cursor(dictionary=True)

# Route for HTML page to input USN and find the room
@app.route('/', methods=['GET', 'POST'])
def find_room():
    if request.method == 'POST':
        usn = request.form.get('usn')

        cursor.execute("SELECT room FROM room_allotment WHERE usn = %s", (usn,))
        student = cursor.fetchall()  

        std = []
        for i in student:
            std.append(i['room'])
  

        if std:
            return render_template('frontpagee.html', usn=usn, room_no=std)
        else:
            return render_template('frontpagee.html', error="Student not found!")

    return render_template('frontpagee.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
