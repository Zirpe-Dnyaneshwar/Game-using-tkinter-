"""
Car Booking - Tkinter GUI
Features:
- Attractive color scheme and modern-looking ttk widgets
- Enter customer details, car selection, pickup/dropoff info
- Validation and friendly messages
- Save bookings to bookings.csv
- View bookings in a popup table
- Clear form and simple responsive layout
Run: python car_booking_tkinter.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# ----------------- Config / Styling ----------------- #
BG = "#0f1724"           # dark-blue background
PANEL = "#0b1220"        # panel slightly lighter
ACCENT = "#06b6d4"       # cyan accent
BUTTON_BG = "#0ea5a4"    # teal button
TEXT = "#e6eef6"         # light text
WARN = "#f97316"         # warning / accent

CSV_FILE = "bookings.csv"

# Ensure CSV exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Name", "Phone", "Email", "Car Model",
                         "Pickup Date", "Pickup Time", "Dropoff Date", "Dropoff Time", "Notes"])

# ----------------- Helper Functions ----------------- #
def save_booking(row):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def validate_phone(p):
    return p.isdigit() and (7 <= len(p) <= 15)

def validate_email(e):
    return "@" in e and "." in e and len(e) >= 5

# ----------------- Main App ----------------- #
class CarBookingApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        self.parent = parent
        self.parent.title("Car Booking • BookMyRide")
        self.pack(fill="both", expand=True)
        self.create_styles()
        self.build_ui()

    def create_styles(self):
        style = ttk.Style()
        # Use default theme (clam/alt) that supports styling
        try:
            style.theme_use("clam")
        except:
            pass
        # Frame background
        style.configure("TFrame", background=PANEL)
        style.configure("Main.TFrame", background=BG)
        # Labels
        style.configure("TLabel", background=PANEL, foreground=TEXT, font=("Inter", 11))
        style.configure("Title.TLabel", font=("Inter", 18, "bold"), foreground=ACCENT, background=BG)
        # Entry / Combobox
        style.configure("TEntry", fieldbackground="#0b1220", foreground=TEXT, background="#0b1220")
        style.map("TEntry", fieldbackground=[("disabled", "#111827")])
        style.configure("TCombobox", fieldbackground="#0b1220", foreground=TEXT)
        # Buttons
        style.configure("Accent.TButton", background=BUTTON_BG, foreground="#05282d", font=("Inter", 11, "bold"))
        style.map("Accent.TButton",
                  background=[("active", ACCENT), ("!active", BUTTON_BG)],
                  foreground=[("active", "#021014")])
        style.configure("Ghost.TButton", background=PANEL, foreground=TEXT)
        # Treeview
        style.configure("Treeview", background="#061018", foreground=TEXT, fieldbackground="#061018")
        style.map("Treeview", background=[("selected", ACCENT)])

    def build_ui(self):
        # Outer main frame
        main = ttk.Frame(self, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        # Title
        title = ttk.Label(main, text="BookMyRide — Car Booking", style="Title.TLabel")
        title.pack(anchor="w", pady=(6, 12))

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        # Left: Form panel
        form_panel = ttk.Frame(body, padding=12, style="TFrame")
        form_panel.pack(side="left", fill="both", expand=True, padx=(0,10))

        # Right: Summary / actions
        right_panel = ttk.Frame(body, padding=12, style="TFrame")
        right_panel.pack(side="right", fill="y")

        # Form fields
        self._add_label_entry(form_panel, "Full Name:", 0)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_panel, textvariable=self.name_var, width=36)
        self.name_entry.grid(row=0, column=1, pady=6, padx=6)

        self._add_label_entry(form_panel, "Phone:", 1)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(form_panel, textvariable=self.phone_var, width=20)
        self.phone_entry.grid(row=1, column=1, pady=6, padx=6, sticky="w")

        self._add_label_entry(form_panel, "Email:", 2)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(form_panel, textvariable=self.email_var, width=36)
        self.email_entry.grid(row=2, column=1, pady=6, padx=6)

        # Car model combobox
        self._add_label_entry(form_panel, "Car Model:", 3)
        self.car_var = tk.StringVar()
        car_choices = ["Hatchback - Swift", "Sedan - City", "SUV - Creta",
                       "Luxury - C-Class", "SUV - Fortuner", "Electric - Nexon EV"]
        self.car_combo = ttk.Combobox(form_panel, textvariable=self.car_var,
                                      values=car_choices, state="readonly", width=33)
        self.car_combo.grid(row=3, column=1, pady=6, padx=6)
        self.car_combo.current(0)

        # Pickup / Dropoff
        self._add_label_entry(form_panel, "Pickup Date (YYYY-MM-DD):", 4)
        self.pick_date_var = tk.StringVar()
        self.pick_entry = ttk.Entry(form_panel, textvariable=self.pick_date_var, width=20)
        self.pick_entry.grid(row=4, column=1, pady=6, padx=6, sticky="w")

        self._add_label_entry(form_panel, "Pickup Time (HH:MM):", 5)
        self.pick_time_var = tk.StringVar()
        self.pick_time_entry = ttk.Entry(form_panel, textvariable=self.pick_time_var, width=20)
        self.pick_time_entry.grid(row=5, column=1, pady=6, padx=6, sticky="w")

        self._add_label_entry(form_panel, "Dropoff Date (YYYY-MM-DD):", 6)
        self.drop_date_var = tk.StringVar()
        self.drop_entry = ttk.Entry(form_panel, textvariable=self.drop_date_var, width=20)
        self.drop_entry.grid(row=6, column=1, pady=6, padx=6, sticky="w")

        self._add_label_entry(form_panel, "Dropoff Time (HH:MM):", 7)
        self.drop_time_var = tk.StringVar()
        self.drop_time_entry = ttk.Entry(form_panel, textvariable=self.drop_time_var, width=20)
        self.drop_time_entry.grid(row=7, column=1, pady=6, padx=6, sticky="w")

        # Notes
        notes_lbl = ttk.Label(form_panel, text="Notes:", style="TLabel")
        notes_lbl.grid(row=8, column=0, sticky="ne", pady=6)
        self.notes_text = tk.Text(form_panel, height=5, width=36, bg="#071422", fg=TEXT, bd=0, insertbackground=TEXT)
        self.notes_text.grid(row=8, column=1, pady=6, padx=6)

        # Buttons (book / clear)
        btn_frame = ttk.Frame(form_panel, style="TFrame")
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(12,0))

        book_btn = ttk.Button(btn_frame, text="📘 Book Car", style="Accent.TButton", command=self.on_book)
        book_btn.grid(row=0, column=0, padx=(0,8))

        clear_btn = ttk.Button(btn_frame, text="Clear", style="Ghost.TButton", command=self.clear_form)
        clear_btn.grid(row=0, column=1, padx=(8,0))

        # Right panel actions
        info_label = ttk.Label(right_panel, text="Quick Actions", style="TLabel")
        info_label.pack(anchor="nw", pady=(0,8))

        view_btn = ttk.Button(right_panel, text="View Bookings", style="Accent.TButton", command=self.view_bookings)
        view_btn.pack(fill="x", pady=6)

        export_btn = ttk.Button(right_panel, text="Export CSV", style="Ghost.TButton", command=self.export_csv)
        export_btn.pack(fill="x", pady=6)

        quit_btn = ttk.Button(right_panel, text="Quit", style="Ghost.TButton", command=self.parent.quit)
        quit_btn.pack(fill="x", pady=6)

        # Footer / status
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(main, textvariable=self.status_var, style="TLabel")
        status.pack(anchor="w", pady=(12,0))

        # Make grid columns consistent
        for i in range(2):
            form_panel.grid_columnconfigure(i, weight=1)

    def _add_label_entry(self, parent, text, row):
        lbl = ttk.Label(parent, text=text, style="TLabel")
        lbl.grid(row=row, column=0, sticky="w", padx=(0,2))

    def clear_form(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.car_combo.current(0)
        self.pick_date_var.set("")
        self.pick_time_var.set("")
        self.drop_date_var.set("")
        self.drop_time_var.set("")
        self.notes_text.delete("1.0", tk.END)
        self.status_var.set("Form cleared")

    def on_book(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        car = self.car_var.get().strip()
        pdate = self.pick_date_var.get().strip()
        ptime = self.pick_time_var.get().strip()
        ddate = self.drop_date_var.get().strip()
        dtime = self.drop_time_var.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        # Basic validation
        if not name:
            messagebox.showwarning("Validation", "Please enter your full name.")
            return
        if not validate_phone(phone):
            messagebox.showwarning("Validation", "Please enter a valid phone number (digits only).")
            return
        if email and not validate_email(email):
            messagebox.showwarning("Validation", "Please enter a valid email address.")
            return
        # Validate dates/time format simply
        for dt, label in [(pdate, "Pickup Date"), (ddate, "Dropoff Date")]:
            if dt:
                try:
                    datetime.strptime(dt, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Validation", f"{label} should be in YYYY-MM-DD format.")
                    return
        for tm, label in [(ptime, "Pickup Time"), (dtime, "Dropoff Time")]:
            if tm:
                try:
                    datetime.strptime(tm, "%H:%M")
                except ValueError:
                    messagebox.showwarning("Validation", f"{label} should be in HH:MM (24-hour) format.")
                    return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, name, phone, email, car, pdate, ptime, ddate, dtime, notes]
        save_booking(row)
        self.status_var.set(f"Booked {car} for {name} • {timestamp}")
        messagebox.showinfo("Success", f"Booking confirmed for {name}!\nCar: {car}")
        self.clear_form()

    def view_bookings(self):
        # Toplevel window to show CSV rows
        popup = tk.Toplevel(self.parent)
        popup.title("All Bookings")
        popup.geometry("900x400")
        popup.configure(bg=BG)

        header = ttk.Label(popup, text="Bookings", style="Title.TLabel")
        header.pack(anchor="w", padx=12, pady=(12,6))

        cols = ["Timestamp", "Name", "Phone", "Email", "Car Model", "Pickup Date", "Pickup Time", "Dropoff Date", "Dropoff Time", "Notes"]
        tree = ttk.Treeview(popup, columns=cols, show="headings", height=14)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor="w")
        tree.pack(fill="both", expand=True, padx=12, pady=6)

        # Load CSV
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for r in reader:
                # Truncate notes to keep rows tidy
                row = r[:9] + [ (r[9][:60] + "...") if len(r[9])>60 else r[9] ]
                tree.insert("", tk.END, values=row)

        close_btn = ttk.Button(popup, text="Close", command=popup.destroy, style="Ghost.TButton")
        close_btn.pack(pady=8)

    def export_csv(self):
        # In this simple app bookings are already saved to CSV. Inform the user.
        messagebox.showinfo("Export", f"All bookings are saved in the file:\n{os.path.abspath(CSV_FILE)}")

# ----------------- Run ----------------- #
def main():
    root = tk.Tk()
    root.configure(bg=BG)
    # Set minimum window size
    root.minsize(900, 520)
    app = CarBookingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
