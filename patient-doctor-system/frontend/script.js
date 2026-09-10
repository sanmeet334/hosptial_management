const API_URL = "http://127.0.0.1:5000";


// ===============================
// PATIENT REGISTRATION
// ===============================

async function registerPatient() {

    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const education = document.getElementById("education").value;
    const symptoms = document.getElementById("symptoms").value;

    if (!name || !age) {
        alert("Please enter name and age");
        return;
    }

    try {

        const response = await fetch(`${API_URL}/patients`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                age: age,
                education: education,
                symptoms: symptoms
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error);
            return;
        }

        document.getElementById("result").innerHTML = `
            <p>✅ Registration Successful!</p>
            <p>Your Queue Number: <strong>${data.patient.queue_number}</strong></p>
            <p>Status: ${data.patient.status}</p>
        `;

        loadDoctorStatus();

    } catch (error) {

        console.error(error);

        alert("Unable to connect to the backend.");
    }
}


// ===============================
// LOAD DOCTOR STATUS
// ===============================

async function loadDoctorStatus() {

    const statusElement = document.getElementById("doctorStatus");

    if (!statusElement) {
        return;
    }

    try {

        const response = await fetch(`${API_URL}/doctor`);

        const doctor = await response.json();

        statusElement.innerHTML = `
            <strong>${doctor.name}</strong><br>
            Status: <strong>${doctor.status}</strong>
        `;

    } catch (error) {

        statusElement.innerHTML =
            "Unable to connect to backend.";
    }
}


// ===============================
// DOCTOR: UPDATE STATUS
// ===============================

async function updateDoctorStatus() {

    const status = document.getElementById("status").value;

    try {

        const response = await fetch(`${API_URL}/doctor/status`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                status: status
            })
        });

        const data = await response.json();

        alert(data.message);

        loadPatients();

    } catch (error) {

        alert("Unable to connect to backend.");
    }
}


// ===============================
// DOCTOR: LOAD PATIENTS
// ===============================

async function loadPatients() {

    const patientsElement = document.getElementById("patients");

    if (!patientsElement) {
        return;
    }

    try {

        const response = await fetch(`${API_URL}/patients`);

        const patients = await response.json();

        const waitingPatients =
            patients.filter(patient => patient.status === "Waiting");

        document.getElementById("patientCount").textContent =
            waitingPatients.length;

        if (patients.length === 0) {

            patientsElement.innerHTML =
                "<p>No patients registered.</p>";

            return;
        }

        patientsElement.innerHTML = patients.map(patient => `
            <div class="patient">

                <strong>
                    Queue #${patient.queue_number}
                </strong>

                <p>Name: ${patient.name}</p>

                <p>Age: ${patient.age}</p>

                <p>Education: ${patient.education || "Not provided"}</p>

                <p>Symptoms: ${patient.symptoms || "Not provided"}</p>

                <p>Status: <strong>${patient.status}</strong></p>

                <button onclick="markPatientDone(${patient.id})">
                    Mark Completed
                </button>

            </div>
        `).join("");

    } catch (error) {

        patientsElement.innerHTML =
            "<p>Unable to connect to backend.</p>";
    }
}


// ===============================
// DOCTOR: COMPLETE PATIENT
// ===============================

async function markPatientDone(patientId) {

    try {

        const response = await fetch(
            `${API_URL}/patients/${patientId}/status`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: "Completed"
                })
            }
        );

        if (response.ok) {
            loadPatients();
        }

    } catch (error) {

        alert("Unable to update patient.");
    }
}


// ===============================
// START AUTOMATICALLY
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    loadDoctorStatus();

    loadPatients();

});