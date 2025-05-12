import os
import pandas as pd
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL connection details
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Ruchi@2004"
MYSQL_DATABASE = "exam_db"

# Upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: Homepage (File Upload + Search)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if file is uploaded
        if "file" not in request.files:
            flash("No file uploaded!", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file!", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = "exam_room_allocation.xlsx"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            flash("File uploaded successfully!", "success")

            # Process the uploaded file
            process_excel(file_path)

            return redirect(url_for("index"))

    return render_template("index.html")

# Function to process Excel file and store today's date sheet in MySQL
def process_excel(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names

        today_sheet = datetime.today().strftime("%m/%d/%Y")  # Sheet name format

        if today_sheet in sheet_names:
            df = pd.read_excel(xls, sheet_name=today_sheet)

            conn = mysql.connector.connect(
                host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
            )
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_allotment (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    Date DATE,
                    USN VARCHAR(20),
                    StudentName VARCHAR(100),
                    RoomNumber VARCHAR(20)
                )
            """)

            insert_query = "INSERT INTO room_allotment (Date, USN, StudentName, RoomNumber) VALUES (%s, %s, %s, %s)"
            for _, row in df.iterrows():
                cursor.execute(insert_query, (datetime.today().strftime("%Y-%m-%d"), row["USN"], row["StudentName"], row["RoomNumber"]))

            conn.commit()
            conn.close()

            flash(f"Room allotment data from {today_sheet} stored successfully!", "success")

        else:
            flash(f"No sheet found for today's date: {today_sheet}", "warning")

    except Exception as e:
        flash(f"Error processing file: {str(e)}", "danger")

# Route: Search for student room
@app.route("/search", methods=["POST"])
def search():
    usn = request.form.get("usn")

    if not usn:
        flash("Please enter a USN!", "danger")
        return redirect(url_for("index"))

    conn = mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
    )
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM room_allotment WHERE USN = %s ORDER BY Date DESC LIMIT 1"
    cursor.execute(query, (usn,))
    record = cursor.fetchone()

    conn.close()

    if record:
        return render_template("index.html", record=record)
    else:
        flash("No record found for this USN!", "danger")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
