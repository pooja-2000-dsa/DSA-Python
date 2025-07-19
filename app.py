import streamlit as st
from datetime import datetime

# --------- Data Structures ---------

class MedicalNoteStack:
    def __init__(self):
        self.stack = []

    def add_note(self, note):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stack.append({"note": note, "timestamp": timestamp})

    def view_notes(self):
        return self.stack[::-1]  # latest first

    def undo_last(self):
        if self.stack:
            return self.stack.pop()
        return None


class AppointmentNode:
    def __init__(self, date, doctor):
        self.date = date
        self.doctor = doctor
        self.medical_notes = MedicalNoteStack()
        self.prev = None
        self.next = None


class AppointmentDLL:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_appointment(self, date, doctor):
        new_appt = AppointmentNode(date, doctor)
        if self.head is None:
            self.head = self.tail = new_appt
        else:
            self.tail.next = new_appt
            new_appt.prev = self.tail
            self.tail = new_appt

    def get_all_appointments(self):
        current = self.head
        appts = []
        while current:
            appts.append(current)
            current = current.next
        return appts


class PatientNode:
    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender
        self.appointments = AppointmentDLL()
        self.next = None


class PatientLinkedList:
    def __init__(self):
        self.head = None

    def add_patient(self, name, age, gender):
        new_patient = PatientNode(name, age, gender)
        if self.head is None:
            self.head = new_patient
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_patient

    def get_all_patients(self):
        current = self.head
        patients = []
        while current:
            patients.append(current)
            current = current.next
        return patients

# --------- Streamlit App ---------

st.title("🏥 Patient Appointment & Medical Notes Manager")

# Initialize state
if "patients" not in st.session_state:
    st.session_state.patients = PatientLinkedList()
    st.session_state.selected_patient = None
    st.session_state.selected_appt = None

st.sidebar.header("➕ Add New Patient")
with st.sidebar.form("new_patient"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    if st.form_submit_button("Add Patient"):
        st.session_state.patients.add_patient(name, age, gender)
        st.success(f"Patient {name} added.")

patients = st.session_state.patients.get_all_patients()
if not patients:
    st.info("No patients found. Add a patient from the sidebar.")
    st.stop()

# Select patient
selected_name = st.selectbox("Select a Patient", [p.name for p in patients])
selected_patient = next(p for p in patients if p.name == selected_name)
st.session_state.selected_patient = selected_patient

st.subheader(f"📋 Appointments for {selected_patient.name}")
with st.form("new_appt"):
    appt_date = st.date_input("Date")
    doctor = st.text_input("Doctor")
    if st.form_submit_button("Add Appointment"):
        selected_patient.appointments.add_appointment(str(appt_date), doctor)
        st.success(f"Appointment on {appt_date} with Dr. {doctor} added.")

appts = selected_patient.appointments.get_all_appointments()
if not appts:
    st.warning("No appointments found.")
    st.stop()

# Select appointment
appt_strs = [f"{a.date} - Dr. {a.doctor}" for a in appts]
selected_appt_str = st.selectbox("Select an Appointment", appt_strs)
selected_appt = appts[appt_strs.index(selected_appt_str)]
st.session_state.selected_appt = selected_appt

# Medical Notes Section
st.subheader(f"📝 Medical Notes for {selected_appt.date} - Dr. {selected_appt.doctor}")
with st.form("add_note"):
    new_note = st.text_area("New Note")
    if st.form_submit_button("Add Note"):
        selected_appt.medical_notes.add_note(new_note)
        st.success("Note added.")

if st.button("↩️ Undo Last Note"):
    undone = selected_appt.medical_notes.undo_last()
    if undone:
        st.warning(f"Undid: {undone['note']}")
    else:
        st.info("No notes to undo.")

notes = selected_appt.medical_notes.view_notes()
if notes:
    st.markdown("### 📚 Notes History (Latest First):")
    for i, n in enumerate(notes):
        st.markdown(f"**{i+1}.** {n['note']}  \n🕒 _{n['timestamp']}_")
else:
    st.info("No notes available for this appointment.")
