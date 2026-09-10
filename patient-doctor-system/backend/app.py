from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = "hospital.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            education TEXT,
            symptoms TEXT,
            queue_number INTEGER NOT NULL,
            status TEXT DEFAULT 'Waiting'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctor (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            room TEXT,
            hospital TEXT,
            qualification TEXT,
            status TEXT DEFAULT 'Available'
        )
    """)

    doctor = conn.execute(
        "SELECT * FROM doctor WHERE id = 1"
    ).fetchone()

    if doctor is None:
        conn.execute("""
            INSERT INTO doctor
            (id, name, age, room, hospital, qualification, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            1,
            "Dr. Aditya Patil",
            45,
            "5",
            "Ram Krishna Hospital",
            "MBBS, MD",
            "Available"
        ))

    conn.commit()
    conn.close()


# Home
@app.route("/")
def home():
    return jsonify({
        "message": "Patient-Doctor Backend is Running!"
    })


# Register patient
@app.route("/patients", methods=["POST"])
def add_patient():

    data = request.get_json()

    name = data.get("name")
    age = data.get("age")
    education = data.get("education")
    symptoms = data.get("symptoms")

    if not name or not age:
        return jsonify({
            "error": "Name and age are required"
        }), 400

    conn = get_db()

    result = conn.execute(
        "SELECT MAX(queue_number) AS max_queue FROM patients"
    ).fetchone()

    queue_number = (
        1 if result["max_queue"] is None
        else result["max_queue"] + 1
    )

    cursor = conn.execute("""
        INSERT INTO patients
        (name, age, education, symptoms, queue_number, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        education,
        symptoms,
        queue_number,
        "Waiting"
    ))

    conn.commit()

    patient_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Patient registered successfully",
        "patient": {
            "id": patient_id,
            "name": name,
            "age": age,
            "education": education,
            "symptoms": symptoms,
            "queue_number": queue_number,
            "status": "Waiting"
        }
    }), 201


# Get all patients
@app.route("/patients", methods=["GET"])
def get_patients():

    conn = get_db()

    patients = conn.execute("""
        SELECT * FROM patients
        ORDER BY queue_number ASC
    """).fetchall()

    conn.close()

    return jsonify([dict(patient) for patient in patients])


# Update patient status
@app.route("/patients/<int:patient_id>/status", methods=["PUT"])
def update_patient_status(patient_id):

    data = request.get_json()
    status = data.get("status")

    if not status:
        return jsonify({
            "error": "Status is required"
        }), 400

    conn = get_db()

    conn.execute("""
        UPDATE patients
        SET status = ?
        WHERE id = ?
    """, (status, patient_id))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Patient status updated"
    })


# Get doctor
@app.route("/doctor", methods=["GET"])
def get_doctor():

    conn = get_db()

    doctor = conn.execute(
        "SELECT * FROM doctor WHERE id = 1"
    ).fetchone()

    conn.close()

    return jsonify(dict(doctor))


# Update doctor status
@app.route("/doctor/status", methods=["PUT"])
def update_doctor_status():

    data = request.get_json()
    status = data.get("status")

    if not status:
        return jsonify({
            "error": "Status is required"
        }), 400

    conn = get_db()

    conn.execute("""
        UPDATE doctor
        SET status = ?
        WHERE id = 1
    """, (status,))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Doctor status updated",
        "status": status
    })


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )