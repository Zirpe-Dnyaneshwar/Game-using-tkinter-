"""
Hospital Management System - Tkinter + SQLite
Save as: hospital_management_tkinter.py
Run: python hospital_management_tkinter.py

Features:
- Patient registration (Name, Age, Gender, Contact, Disease)
- Doctor assignment and simple doctor list
- Appointment scheduling (patient + doctor + date + time)
- Add / Update / Delete / Search patients & appointments
- SQLite persistence (hospital.db)
- Export patients or appointments to CSV
- Attractive UI using ttk and simple color scheme
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv

DB_FILE = "hospital.db"

# ---------------- Database helpers ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            disease TEXT,
            created_at TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            appt_date TEXT,
            appt_time TEXT,
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
    ''')
    # Insert sample doctors if empty
    cur.execute('SELECT COUNT(*) FROM doctors')
    if cur.fetchone()[0] == 0:
        sample_docs = [
            ("Dr. Asha Patel", "General Physician"),
            ("Dr. Rohit Sharma", "Cardiologist"),
            ("Dr. Meera Singh", "Pediatrician"),
            ("Dr. Vikram Rao", "Orthopedics"),
        ]
        cur.executemany('INSERT INTO doctors (name, specialty) VALUES (?, ?)', sample_docs)
    conn.commit()
    conn.close()

# Patients CRUD
def insert_patient(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO patients (name, age, gender, contact, disease, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def update_patient(pid, data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        UPDATE patients SET name=?, age=?, gender=?, contact=?, disease=? WHERE id=?
    ''', data + (pid,))
    conn.commit()
    conn.close()

def delete_patient(pid):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Also remove appointments for that patient
    cur.execute('DELETE FROM appointments WHERE patient_id=?', (pid,))
    cur.execute('DELETE FROM patients WHERE id=?', (pid,))
    conn.commit()
    conn.close()

def fetch_all_patients():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, name, age, gender, contact, disease, created_at FROM patients ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def search_patients(term):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    q = f"%{term}%"
    cur.execute('''
        SELECT id, name, age, gender, contact, disease, created_at
        FROM patients
        WHERE name LIKE ? OR contact LIKE ? OR disease LIKE ?
        ORDER BY id DESC
    ''', (q, q, q))
    rows = cur.fetchall()
    conn.close()
    return rows

# Doctors
def fetch_doctors():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, name, specialty FROM doctors ORDER BY name')
    rows = cur.fetchall()
    conn.close()
    return rows

# Appointments CRUD
def insert_appointment(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def update_appointment(aid, data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        UPDATE appointments SET patient_id=?, doctor_id=?, appt_date=?, appt_time=?, notes=? WHERE id=?
    ''', data + (aid,))
    conn.commit()
    conn.close()

def delete_appointment(aid):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('DELETE FROM appointments WHERE id=?', (aid,))
    conn.commit()
    conn.close()

def fetch_all_appointments():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        SELECT a.id, p.name, d.name, a.appt_date, a.appt_time, a.notes, a.created_at
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.appt_date DESC, a.appt_time DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows

def search_appointments(term):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    q = f"%{term}%"
    cur.execute('''
        SELECT a.id, p.name, d.name, a.appt_date, a.appt_time, a.notes, a.created_at
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        WHERE p.name LIKE ? OR d.name LIKE ? OR a.appt_date LIKE ?
        ORDER BY a.appt_date DESC, a.appt_time DESC
    ''', (q, q, q))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- UI Application ----------------
class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("1100x660")
        self.root.minsize(1000, 600)
        self.setup_style()

        # Top header
        header = tk.Frame(root, bg="#0b3d91", height=72)
        header.pack(side="top", fill="x")
        tk.Label(header, text="Hospital Management System", bg="#0b3d91", fg="white",
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=20, pady=14)
        tk.Label(header, text="Patient care • Appointments • Doctors", bg="#0b3d91", fg="#dbe9ff",
                 font=("Helvetica", 10)).pack(side="left", pady=20)

        # Main area
        main = tk.Frame(root, bg="#f4f7fb")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        # Left: Patient form & controls
        left = tk.Frame(main, bg="#f4f7fb", bd=1, relief="groove")
        left.place(relx=0.02, rely=0.02, relwidth=0.34, relheight=0.96)

        tk.Label(left, text="Patient Registration", bg="#f4f7fb", fg="#0b3d91", font=("Helvetica", 14, "bold")).pack(anchor="nw", padx=12, pady=(12,6))
        self.build_patient_form(left)

        # Middle-right: Tabs for Patients and Appointments
        right = tk.Frame(main, bg="#f4f7fb")
        right.place(relx=0.38, rely=0.02, relwidth=0.60, relheight=0.96)
        self.build_right_tabs(right)

        # Load initial data
        self.selected_patient_id = None
        self.selected_appointment_id = None
        self.load_doctors()
        self.refresh_patient_table()
        self.refresh_appointment_table()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#0b3d91", foreground="white")
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", background="#0b3d91", foreground="white")
        style.map("Accent.TButton", background=[('active', '#092b63')])

    # ---------------- Patient form ----------------
    def build_patient_form(self, parent):
        padx = 12
        pady = 6
        lbl_opts = {"bg": "#f4f7fb", "fg": "#0b3d91", "anchor": "w", "font": ("Helvetica", 10)}

        tk.Label(parent, text="Full Name:", **lbl_opts).pack(fill="x", padx=padx, pady=(8,0))
        self.entry_p_name = ttk.Entry(parent)
        self.entry_p_name.pack(fill="x", padx=padx, pady=(0,pady))

        tk.Label(parent, text="Age:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_p_age = ttk.Entry(parent)
        self.entry_p_age.pack(fill="x", padx=padx, pady=(0,pady))

        tk.Label(parent, text="Gender:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.combo_p_gender = ttk.Combobox(parent, values=["Male", "Female", "Other"], state="readonly")
        self.combo_p_gender.pack(fill="x", padx=padx, pady=(0,pady))
        self.combo_p_gender.current(0)

        tk.Label(parent, text="Contact:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_p_contact = ttk.Entry(parent)
        self.entry_p_contact.pack(fill="x", padx=padx, pady=(0,pady))

        tk.Label(parent, text="Disease / Notes:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_p_disease = ttk.Entry(parent)
        self.entry_p_disease.pack(fill="x", padx=padx, pady=(0,pady))

        btn_frame = tk.Frame(parent, bg="#f4f7fb")
        btn_frame.pack(fill="x", padx=padx, pady=12)
        ttk.Button(btn_frame, text="Add Patient", command=self.add_patient, style="Accent.TButton").pack(side="left", expand=True, fill="x", padx=(0,6))
        ttk.Button(btn_frame, text="Update Patient", command=self.update_patient).pack(side="left", expand=True, fill="x", padx=(6,0))

        ttk.Button(parent, text="Clear", command=self.clear_patient_form).pack(fill="x", padx=padx, pady=(0,8))

    # ---------------- Right tabs ----------------
    def build_right_tabs(self, parent):
        tabs = ttk.Notebook(parent)
        tabs.pack(fill="both", expand=True)

        # Patients tab
        tab_patients = tk.Frame(tabs, bg="#f4f7fb")
        tabs.add(tab_patients, text="Patients")

        # Controls for patients
        ctrl = tk.Frame(tab_patients, bg="#f4f7fb")
        ctrl.pack(fill="x", padx=6, pady=6)
        tk.Label(ctrl, text="Search:", bg="#f4f7fb", fg="#0b3d91").pack(side="left", padx=(6,6))
        self.entry_search_patient = ttk.Entry(ctrl)
        self.entry_search_patient.pack(side="left", padx=(0,6), fill="x", expand=True)
        self.entry_search_patient.bind("<Return>", lambda e: self.search_patients())
        ttk.Button(ctrl, text="Search", command=self.search_patients).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Show All", command=self.refresh_patient_table).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Export CSV", command=self.export_patients).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Delete Selected", command=self.delete_selected_patient).pack(side="left", padx=6)

        # Patient table
        cols = ("id", "name", "age", "gender", "contact", "disease", "created")
        self.tree_patients = ttk.Treeview(tab_patients, columns=cols, show="headings", height=18)
        headings = {"id":"ID", "name":"Name", "age":"Age", "gender":"Gender", "contact":"Contact", "disease":"Disease", "created":"Created At"}
        for c in cols:
            self.tree_patients.heading(c, text=headings[c])
            w = 50 if c=="id" else 140
            if c=="name":
                w = 180
            self.tree_patients.column(c, width=w, anchor="center")
        self.tree_patients.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree_patients.bind("<<TreeviewSelect>>", self.on_patient_select)

        # Appointments tab
        tab_appt = tk.Frame(tabs, bg="#f4f7fb")
        tabs.add(tab_appt, text="Appointments")

        # Appointment form at top
        ap_top = tk.Frame(tab_appt, bg="#f4f7fb")
        ap_top.pack(fill="x", padx=6, pady=6)

        tk.Label(ap_top, text="Patient:", bg="#f4f7fb", fg="#0b3d91").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.combo_ap_patient = ttk.Combobox(ap_top, state="readonly")
        self.combo_ap_patient.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        tk.Label(ap_top, text="Doctor:", bg="#f4f7fb", fg="#0b3d91").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.combo_ap_doctor = ttk.Combobox(ap_top, state="readonly")
        self.combo_ap_doctor.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        tk.Label(ap_top, text="Date (YYYY-MM-DD):", bg="#f4f7fb", fg="#0b3d91").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.entry_ap_date = ttk.Entry(ap_top)
        self.entry_ap_date.grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        tk.Label(ap_top, text="Time (HH:MM):", bg="#f4f7fb", fg="#0b3d91").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.entry_ap_time = ttk.Entry(ap_top)
        self.entry_ap_time.grid(row=1, column=3, padx=6, pady=6, sticky="ew")

        tk.Label(ap_top, text="Notes:", bg="#f4f7fb", fg="#0b3d91").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        self.entry_ap_notes = ttk.Entry(ap_top)
        self.entry_ap_notes.grid(row=2, column=1, columnspan=3, padx=6, pady=6, sticky="ew")

        ap_btns = tk.Frame(tab_appt, bg="#f4f7fb")
        ap_btns.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(ap_btns, text="Add Appointment", command=self.add_appointment, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(ap_btns, text="Update Appointment", command=self.update_appointment).pack(side="left", padx=6)
        ttk.Button(ap_btns, text="Delete Selected", command=self.delete_selected_appointment).pack(side="left", padx=6)
        ttk.Button(ap_btns, text="Export CSV", command=self.export_appointments).pack(side="left", padx=6)

        # Search appointments
        tk.Label(ap_btns, text="   Search:", bg="#f4f7fb").pack(side="left", padx=(12,6))
        self.entry_search_appt = ttk.Entry(ap_btns)
        self.entry_search_appt.pack(side="left", padx=(0,6), fill="x", expand=True)
        self.entry_search_appt.bind("<Return>", lambda e: self.search_appointments())
        ttk.Button(ap_btns, text="Search", command=self.search_appointments).pack(side="left", padx=6)
        ttk.Button(ap_btns, text="Show All", command=self.refresh_appointment_table).pack(side="left", padx=6)

        # Appointment table
        cols2 = ("id", "patient", "doctor", "date", "time", "notes", "created")
        self.tree_appts = ttk.Treeview(tab_appt, columns=cols2, show="headings", height=14)
        headings2 = {"id":"ID", "patient":"Patient", "doctor":"Doctor", "date":"Date", "time":"Time", "notes":"Notes", "created":"Created At"}
        for c in cols2:
            self.tree_appts.heading(c, text=headings2[c])
            w = 60 if c=="id" else 140
            if c=="patient" or c=="doctor":
                w = 160
            self.tree_appts.column(c, width=w, anchor="center")
        self.tree_appts.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree_appts.bind("<<TreeviewSelect>>", self.on_appt_select)

    # ---------------- Load / refresh helpers ----------------
    def load_doctors(self):
        docs = fetch_doctors()
        self.doctor_map = {f"{d[1]} ({d[2]})": d[0] for d in docs}  # "Name (Spec)" -> id
        vals = list(self.doctor_map.keys())
        self.combo_ap_doctor['values'] = vals
        # Also keep simple list for doctor comboboxes if needed
        # If no doctors found, keep empty

    def refresh_patient_table(self):
        rows = fetch_all_patients()
        # clear and populate
        for item in self.tree_patients.get_children():
            self.tree_patients.delete(item)
        for r in rows:
            self.tree_patients.insert("", "end", values=r)
        # update patient combobox for appointments
        names = [f"{r[1]} (ID:{r[0]})" for r in rows]
        self.combo_ap_patient['values'] = names

    def refresh_appointment_table(self):
        rows = fetch_all_appointments()
        for item in self.tree_appts.get_children():
            self.tree_appts.delete(item)
        for r in rows:
            self.tree_appts.insert("", "end", values=r)

    # ---------------- Patient actions ----------------
    def add_patient(self):
        name = self.entry_p_name.get().strip()
        age = self.entry_p_age.get().strip()
        gender = self.combo_p_gender.get().strip()
        contact = self.entry_p_contact.get().strip()
        disease = self.entry_p_disease.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Patient name is required.")
            return
        try:
            age_val = int(age) if age else None
        except:
            messagebox.showwarning("Validation", "Age must be a number.")
            return
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = (name, age_val, gender, contact, disease, created)
        insert_patient(data)
        messagebox.showinfo("Success", f"Patient '{name}' added.")
        self.clear_patient_form()
        self.refresh_patient_table()

    def update_patient(self):
        if not self.selected_patient_id:
            messagebox.showinfo("Select", "Select a patient to update.")
            return
        pid = self.selected_patient_id
        name = self.entry_p_name.get().strip()
        age = self.entry_p_age.get().strip()
        gender = self.combo_p_gender.get().strip()
        contact = self.entry_p_contact.get().strip()
        disease = self.entry_p_disease.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Patient name is required.")
            return
        try:
            age_val = int(age) if age else None
        except:
            messagebox.showwarning("Validation", "Age must be a number.")
            return
        update_patient(pid, (name, age_val, gender, contact, disease))
        messagebox.showinfo("Updated", f"Patient #{pid} updated.")
        self.clear_patient_form()
        self.refresh_patient_table()

    def delete_selected_patient(self):
        sel = self.tree_patients.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a patient to delete.")
            return
        item = sel[0]
        vals = self.tree_patients.item(item, "values")
        pid = int(vals[0])
        confirm = messagebox.askyesno("Confirm", f"Delete patient #{pid} and their appointments?")
        if not confirm:
            return
        delete_patient(pid)
        messagebox.showinfo("Deleted", f"Patient #{pid} deleted.")
        self.clear_patient_form()
        self.refresh_patient_table()
        self.refresh_appointment_table()

    def on_patient_select(self, event):
        sel = self.tree_patients.selection()
        if not sel:
            return
        vals = self.tree_patients.item(sel[0], "values")
        self.selected_patient_id = int(vals[0])
        # populate form
        self.entry_p_name.delete(0, "end"); self.entry_p_name.insert(0, vals[1])
        self.entry_p_age.delete(0, "end"); self.entry_p_age.insert(0, vals[2] if vals[2] is not None else "")
        try:
            self.combo_p_gender.set(vals[3])
        except:
            pass
        self.entry_p_contact.delete(0, "end"); self.entry_p_contact.insert(0, vals[4])
        self.entry_p_disease.delete(0, "end"); self.entry_p_disease.insert(0, vals[5])

    def clear_patient_form(self):
        self.selected_patient_id = None
        self.entry_p_name.delete(0, "end")
        self.entry_p_age.delete(0, "end")
        self.combo_p_gender.current(0)
        self.entry_p_contact.delete(0, "end")
        self.entry_p_disease.delete(0, "end")

    def search_patients(self):
        term = self.entry_search_patient.get().strip()
        if not term:
            self.refresh_patient_table()
            return
        rows = search_patients(term)
        # populate
        for item in self.tree_patients.get_children():
            self.tree_patients.delete(item)
        for r in rows:
            self.tree_patients.insert("", "end", values=r)

    def export_patients(self):
        rows = fetch_all_patients()
        if not rows:
            messagebox.showinfo("No Data", "No patients to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Name","Age","Gender","Contact","Disease","Created At"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("Exported", f"Patients exported to {path}")

    # ---------------- Appointment actions ----------------
    def add_appointment(self):
        pat_val = self.combo_ap_patient.get().strip()
        doc_val = self.combo_ap_doctor.get().strip()
        date = self.entry_ap_date.get().strip()
        timev = self.entry_ap_time.get().strip()
        notes = self.entry_ap_notes.get().strip()
        if not pat_val or not doc_val or not date or not timev:
            messagebox.showwarning("Validation", "Select patient, doctor, date and time.")
            return
        # parse patient id from "Name (ID:x)"
        try:
            pid = int(pat_val.split("ID:")[1].strip(")"))
        except:
            messagebox.showwarning("Validation", "Select a valid patient from the dropdown.")
            return
        # doctor id from doctor_map keys
        doc_map_key = doc_val
        if doc_map_key not in self.doctor_map:
            messagebox.showwarning("Validation", "Select a valid doctor.")
            return
        did = self.doctor_map[doc_map_key]
        # basic date validation
        if not self.valid_date(date):
            messagebox.showwarning("Validation", "Date must be YYYY-MM-DD")
            return
        if not self.valid_time(timev):
            messagebox.showwarning("Validation", "Time must be HH:MM (24h)")
            return
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = (pid, did, date, timev, notes, created)
        insert_appointment(data)
        messagebox.showinfo("Scheduled", f"Appointment scheduled on {date} at {timev}.")
        self.clear_appt_form()
        self.refresh_appointment_table()

    def update_appointment(self):
        if not self.selected_appointment_id:
            messagebox.showinfo("Select", "Select an appointment to update.")
            return
        aid = self.selected_appointment_id
        pat_val = self.combo_ap_patient.get().strip()
        doc_val = self.combo_ap_doctor.get().strip()
        date = self.entry_ap_date.get().strip()
        timev = self.entry_ap_time.get().strip()
        notes = self.entry_ap_notes.get().strip()
        try:
            pid = int(pat_val.split("ID:")[1].strip(")"))
        except:
            messagebox.showwarning("Validation", "Select a valid patient from the dropdown.")
            return
        if doc_val not in self.doctor_map:
            messagebox.showwarning("Validation", "Select a valid doctor.")
            return
        did = self.doctor_map[doc_val]
        if not self.valid_date(date):
            messagebox.showwarning("Validation", "Date must be YYYY-MM-DD")
            return
        if not self.valid_time(timev):
            messagebox.showwarning("Validation", "Time must be HH:MM (24h)")
            return
        update_appointment(aid, (pid, did, date, timev, notes))
        messagebox.showinfo("Updated", f"Appointment #{aid} updated.")
        self.clear_appt_form()
        self.refresh_appointment_table()

    def delete_selected_appointment(self):
        sel = self.tree_appts.selection()
        if not sel:
            messagebox.showinfo("Select", "Select an appointment to delete.")
            return
        item = sel[0]
        vals = self.tree_appts.item(item, "values")
        aid = int(vals[0])
        confirm = messagebox.askyesno("Confirm", f"Delete appointment #{aid}?")
        if not confirm:
            return
        delete_appointment(aid)
        messagebox.showinfo("Deleted", f"Appointment #{aid} deleted.")
        self.refresh_appointment_table()

    def on_appt_select(self, event):
        sel = self.tree_appts.selection()
        if not sel:
            return
        vals = self.tree_appts.item(sel[0], "values")
        # vals: (id, patient_name, doctor_name, date, time, notes, created)
        self.selected_appointment_id = int(vals[0])
        # set appointment form fields
        # Need patient list values -> find by "Name (ID:x)"
        # We'll set patient combobox to matching "Name (ID:x)"
        pname = vals[1]
        # find patient id by searching tree items (could be optimized)
        pid = None
        for it in self.tree_patients.get_children():
            pvals = self.tree_patients.item(it, "values")
            if pvals[1] == pname:
                pid = pvals[0]
                break
        if pid:
            # find the combo value string
            for v in self.combo_ap_patient['values']:
                if f"(ID:{pid})" in v:
                    self.combo_ap_patient.set(v)
                    break
        # doctor combobox matches doctor_map key format: "Name (Spec)"
        dname = vals[2]
        # find key containing dname
        for key in self.doctor_map.keys():
            if dname in key:
                self.combo_ap_doctor.set(key)
                break
        self.entry_ap_date.delete(0, "end"); self.entry_ap_date.insert(0, vals[3])
        self.entry_ap_time.delete(0, "end"); self.entry_ap_time.insert(0, vals[4])
        self.entry_ap_notes.delete(0, "end"); self.entry_ap_notes.insert(0, vals[5])

    def clear_appt_form(self):
        self.selected_appointment_id = None
        self.combo_ap_patient.set('')
        self.combo_ap_doctor.set('')
        self.entry_ap_date.delete(0, "end")
        self.entry_ap_time.delete(0, "end")
        self.entry_ap_notes.delete(0, "end")

    def search_appointments(self):
        term = self.entry_search_appt.get().strip()
        if not term:
            self.refresh_appointment_table()
            return
        rows = search_appointments(term)
        for item in self.tree_appts.get_children():
            self.tree_appts.delete(item)
        for r in rows:
            self.tree_appts.insert("", "end", values=r)

    def export_appointments(self):
        rows = fetch_all_appointments()
        if not rows:
            messagebox.showinfo("No Data", "No appointments to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Patient","Doctor","Date","Time","Notes","Created At"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("Exported", f"Appointments exported to {path}")

    # ---------------- Utilities ----------------
    @staticmethod
    def valid_date(s):
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except:
            return False

    @staticmethod
    def valid_time(s):
        try:
            datetime.strptime(s, "%H:%M")
            return True
        except:
            return False

# ---------------- Run ----------------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()
