"""
Hotel Management System - Tkinter + SQLite
Save as: hotel_management_tkinter.py
Run: python hotel_management_tkinter.py

Features:
- Add / Update / Delete bookings
- Search bookings (by guest or room)
- Export bookings to CSV
- Simple, attractive UI using ttk
- SQLite for persistent storage (hotel.db)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

DB_FILE = "hotel.db"

# ---------------- Database helper ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            phone TEXT,
            room_no TEXT NOT NULL,
            room_type TEXT,
            price REAL,
            checkin TEXT,
            checkout TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_booking(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO bookings (guest_name, phone, room_no, room_type, price, checkin, checkout, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def update_booking(bid, data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        UPDATE bookings
        SET guest_name=?, phone=?, room_no=?, room_type=?, price=?, checkin=?, checkout=?, status=?
        WHERE id=?
    ''', data + (bid,))
    conn.commit()
    conn.close()

def delete_booking(bid):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('DELETE FROM bookings WHERE id=?', (bid,))
    conn.commit()
    conn.close()

def fetch_all_bookings():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, guest_name, phone, room_no, room_type, price, checkin, checkout, status, created_at FROM bookings ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def search_bookings(term):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    q = f"%{term}%"
    cur.execute('''
        SELECT id, guest_name, phone, room_no, room_type, price, checkin, checkout, status, created_at
        FROM bookings
        WHERE guest_name LIKE ? OR room_no LIKE ? OR phone LIKE ?
        ORDER BY id DESC
    ''', (q, q, q))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- UI / App ----------------
class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.geometry("1000x640")
        self.root.minsize(900, 600)
        self.setup_style()

        # Top frame (header)
        header = tk.Frame(root, bg="#0b3d91", height=72)
        header.pack(side="top", fill="x")
        title = tk.Label(header, text="Hotel Management System", bg="#0b3d91", fg="white",
                         font=("Helvetica", 18, "bold"))
        title.pack(side="left", padx=20, pady=14)
        subtitle = tk.Label(header, text="Simple desktop app with Tkinter + SQLite", bg="#0b3d91", fg="#dbe9ff",
                            font=("Helvetica", 10))
        subtitle.pack(side="left", pady=20)

        # Main frame
        main = tk.Frame(root, bg="#f4f7fb")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        # Left panel: form
        form_panel = tk.Frame(main, bg="#f4f7fb", bd=1, relief="groove")
        form_panel.place(relx=0.02, rely=0.02, relwidth=0.34, relheight=0.96)

        f_title = tk.Label(form_panel, text="Booking Details", bg="#f4f7fb", fg="#0b3d91",
                           font=("Helvetica", 14, "bold"))
        f_title.pack(anchor="nw", padx=12, pady=(12, 8))

        self.build_form(form_panel)

        # Right panel: bookings table + controls
        right_panel = tk.Frame(main, bg="#f4f7fb")
        right_panel.place(relx=0.38, rely=0.02, relwidth=0.6, relheight=0.96)

        self.build_table(right_panel)

        # Load data
        self.selected_booking_id = None
        self.refresh_table()

    def setup_style(self):
        style = ttk.Style()
        # Use default theme but customize
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#0b3d91", foreground="white")
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", background="#0b3d91", foreground="white")
        style.map("Accent.TButton",
                  background=[('active', '#092b63')])

    def build_form(self, parent):
        padx = 12
        pady = 6
        lbl_opts = {"bg": "#f4f7fb", "fg": "#0b3d91", "anchor": "w", "font": ("Helvetica", 10)}

        # Guest name
        tk.Label(parent, text="Guest Name:", **lbl_opts).pack(fill="x", padx=padx, pady=(8,0))
        self.entry_name = ttk.Entry(parent)
        self.entry_name.pack(fill="x", padx=padx, pady=(0,pady))

        # Phone
        tk.Label(parent, text="Phone:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_phone = ttk.Entry(parent)
        self.entry_phone.pack(fill="x", padx=padx, pady=(0,pady))

        # Room number
        tk.Label(parent, text="Room No:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_room = ttk.Entry(parent)
        self.entry_room.pack(fill="x", padx=padx, pady=(0,pady))

        # Room type
        tk.Label(parent, text="Room Type:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.combo_type = ttk.Combobox(parent, values=["Single", "Double", "Deluxe", "Suite"], state="readonly")
        self.combo_type.pack(fill="x", padx=padx, pady=(0,pady))
        self.combo_type.current(0)

        # Price
        tk.Label(parent, text="Price (per night):", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_price = ttk.Entry(parent)
        self.entry_price.pack(fill="x", padx=padx, pady=(0,pady))

        # Check-in / Check-out
        tk.Label(parent, text="Check-in (YYYY-MM-DD):", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_checkin = ttk.Entry(parent)
        self.entry_checkin.pack(fill="x", padx=padx, pady=(0,pady))

        tk.Label(parent, text="Check-out (YYYY-MM-DD):", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.entry_checkout = ttk.Entry(parent)
        self.entry_checkout.pack(fill="x", padx=padx, pady=(0,pady))

        # Status
        tk.Label(parent, text="Status:", **lbl_opts).pack(fill="x", padx=padx, pady=(0,0))
        self.combo_status = ttk.Combobox(parent, values=["Booked", "Checked-in", "Checked-out", "Cancelled"], state="readonly")
        self.combo_status.pack(fill="x", padx=padx, pady=(0,pady))
        self.combo_status.current(0)

        # Buttons
        btn_frame = tk.Frame(parent, bg="#f4f7fb")
        btn_frame.pack(fill="x", pady=12, padx=padx)

        btn_add = ttk.Button(btn_frame, text="Add Booking", command=self.add_booking, style="Accent.TButton")
        btn_add.pack(side="left", expand=True, fill="x", padx=(0,6))

        btn_update = ttk.Button(btn_frame, text="Update Booking", command=self.update_booking)
        btn_update.pack(side="left", expand=True, fill="x", padx=(6,0))

        btn_clear = ttk.Button(parent, text="Clear Form", command=self.clear_form)
        btn_clear.pack(fill="x", padx=padx, pady=(0,8))

    def build_table(self, parent):
        # Controls: search, export, delete
        ctrl_frame = tk.Frame(parent, bg="#f4f7fb")
        ctrl_frame.pack(fill="x", padx=6, pady=(6,4))

        tk.Label(ctrl_frame, text="Search:", bg="#f4f7fb", fg="#0b3d91").pack(side="left", padx=(6,6))
        self.entry_search = ttk.Entry(ctrl_frame)
        self.entry_search.pack(side="left", padx=(0,6), fill="x", expand=True)
        self.entry_search.bind("<Return>", lambda e: self.search_records())

        btn_search = ttk.Button(ctrl_frame, text="Search", command=self.search_records)
        btn_search.pack(side="left", padx=6)

        btn_show_all = ttk.Button(ctrl_frame, text="Show All", command=self.refresh_table)
        btn_show_all.pack(side="left", padx=6)

        btn_export = ttk.Button(ctrl_frame, text="Export CSV", command=self.export_csv)
        btn_export.pack(side="left", padx=6)

        btn_delete = ttk.Button(ctrl_frame, text="Delete Selected", command=self.delete_selected)
        btn_delete.pack(side="left", padx=6)

        # Treeview
        cols = ("id", "guest", "phone", "room", "type", "price", "checkin", "checkout", "status", "created")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        headings = {
            "id":"ID", "guest":"Guest Name", "phone":"Phone", "room":"Room No",
            "type":"Room Type", "price":"Price", "checkin":"Check-in", "checkout":"Check-out",
            "status":"Status", "created":"Created At"
        }
        for c in cols:
            self.tree.heading(c, text=headings[c])
            # Widths: id small, others variable
            w = 50 if c=="id" else 110
            if c in ("guest", "created"):
                w = 160
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Footer label
        self.footer_label = tk.Label(parent, text="0 bookings", bg="#f4f7fb", fg="#444")
        self.footer_label.pack(anchor="w", padx=8, pady=(0,8))

    # ---------------- CRUD operations ----------------
    def add_booking(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        room = self.entry_room.get().strip()
        rtype = self.combo_type.get().strip()
        price = self.entry_price.get().strip()
        checkin = self.entry_checkin.get().strip()
        checkout = self.entry_checkout.get().strip()
        status = self.combo_status.get().strip()

        if not name or not room:
            messagebox.showwarning("Validation", "Guest name and Room number are required.")
            return
        # Try to convert price
        try:
            price_val = float(price) if price else 0.0
        except ValueError:
            messagebox.showwarning("Validation", "Price must be a number.")
            return

        # Basic date validation (not strict)
        if checkin and not self.valid_date(checkin):
            messagebox.showwarning("Validation", "Check-in date must be YYYY-MM-DD.")
            return
        if checkout and not self.valid_date(checkout):
            messagebox.showwarning("Validation", "Check-out date must be YYYY-MM-DD.")
            return

        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = (name, phone, room, rtype, price_val, checkin, checkout, status, created)
        insert_booking(data)
        messagebox.showinfo("Success", f"Booking added for {name} (Room {room}).")
        self.clear_form()
        self.refresh_table()

    def update_booking(self):
        if not self.selected_booking_id:
            messagebox.showinfo("Select", "Please select a booking to update from the table.")
            return
        bid = self.selected_booking_id
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        room = self.entry_room.get().strip()
        rtype = self.combo_type.get().strip()
        price = self.entry_price.get().strip()
        checkin = self.entry_checkin.get().strip()
        checkout = self.entry_checkout.get().strip()
        status = self.combo_status.get().strip()

        if not name or not room:
            messagebox.showwarning("Validation", "Guest name and Room number are required.")
            return
        try:
            price_val = float(price) if price else 0.0
        except ValueError:
            messagebox.showwarning("Validation", "Price must be a number.")
            return
        if checkin and not self.valid_date(checkin):
            messagebox.showwarning("Validation", "Check-in date must be YYYY-MM-DD.")
            return
        if checkout and not self.valid_date(checkout):
            messagebox.showwarning("Validation", "Check-out date must be YYYY-MM-DD.")
            return

        update_booking(bid, (name, phone, room, rtype, price_val, checkin, checkout, status))
        messagebox.showinfo("Updated", f"Booking #{bid} updated.")
        self.refresh_table()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a booking to delete.")
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        bid = int(vals[0])
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete booking #{bid}?")
        if not confirm:
            return
        delete_booking(bid)
        messagebox.showinfo("Deleted", f"Booking #{bid} deleted.")
        self.clear_form()
        self.refresh_table()

    def search_records(self):
        term = self.entry_search.get().strip()
        if not term:
            self.refresh_table()
            return
        rows = search_bookings(term)
        self.populate_table(rows)

    def export_csv(self):
        rows = fetch_all_bookings()
        if not rows:
            messagebox.showinfo("No Data", "No bookings to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Guest", "Phone", "Room", "Type", "Price", "Check-in", "Check-out", "Status", "Created At"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("Exported", f"Bookings exported to {path}")

    # ---------------- Table handling ----------------
    def refresh_table(self):
        rows = fetch_all_bookings()
        self.populate_table(rows)

    def populate_table(self, rows):
        # clear
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=r)
        self.footer_label.config(text=f"{len(rows)} bookings")

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        # vals: (id, guest_name, phone, room_no, room_type, price, checkin, checkout, status, created_at)
        self.selected_booking_id = int(vals[0])
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, vals[1])
        self.entry_phone.delete(0, "end"); self.entry_phone.insert(0, vals[2])
        self.entry_room.delete(0, "end"); self.entry_room.insert(0, vals[3])
        # set comboboxes
        try:
            self.combo_type.set(vals[4])
        except:
            pass
        self.entry_price.delete(0, "end"); self.entry_price.insert(0, vals[5])
        self.entry_checkin.delete(0, "end"); self.entry_checkin.insert(0, vals[6])
        self.entry_checkout.delete(0, "end"); self.entry_checkout.insert(0, vals[7])
        try:
            self.combo_status.set(vals[8])
        except:
            pass

    def clear_form(self):
        self.selected_booking_id = None
        self.entry_name.delete(0, "end")
        self.entry_phone.delete(0, "end")
        self.entry_room.delete(0, "end")
        self.combo_type.current(0)
        self.entry_price.delete(0, "end")
        self.entry_checkin.delete(0, "end")
        self.entry_checkout.delete(0, "end")
        self.combo_status.current(0)

    # ---------------- Utilities ----------------
    @staticmethod
    def valid_date(s):
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except:
            return False

# ---------------- Run ----------------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()
