import pandas as pd
from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ruchi@2004",
        database="exceldb"
    )

@app.route('/')
def index():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    try:
        df = pd.read_excel(file, header=None)  
        df = df.dropna(how='all') 

        current_rooms = {}

        room_student_pairs = []

        for i, row in df.iterrows():
            for col_idx, cell in enumerate(row):
                cell = str(cell).strip()

                if cell.lower().startswith("room:"):
                    current_rooms[col_idx] = cell.replace("ROOM:", "").strip()
                
                elif cell.startswith("4GW") and col_idx in current_rooms:
                    room_student_pairs.append((cell, current_rooms[col_idx]))

        if not room_student_pairs:
            return "No valid student-room pairs found! Check your file format."

        #Insert data into MySQL
        db = get_db_connection()
        cursor = db.cursor()
        query = "INSERT INTO room_allotment (usn, room) VALUES (%s, %s)"
        cursor.executemany(query, room_student_pairs)
        db.commit()

        cursor.close()
        db.close()

        return "File uploaded, and data stored successfully!"

    except Exception as e:
        return f"Error processing file: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
