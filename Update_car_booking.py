"""
Car Booking App - Tkinter
A visually attractive mock car booking desktop UI built with tkinter and ttk.
Features:
- Modern colored layout with header, sidebar, and main area
- Search form for pickup, dropoff, date, time, and car type
- List of available cars with thumbnails (placeholder colored rectangles)
- Book button that saves booking to an in-memory list and shows bookings in a table
- Export bookings to a JSON file
- Responsive-ish layout using grid

Run: save as `car_booking_tkinter.py` and run `python car_booking_tkinter.py` (Python 3)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime

# ----------------- Sample car data -----------------
SAMPLE_CARS = [
    {"id": 1, "name": "City Cruiser", "seats": 4, "price": 25, "color": "#FF6B6B"},
    {"id": 2, "name": "Family Van", "seats": 7, "price": 40, "color": "#4ECDC4"},
    {"id": 3, "name": "Executive", "seats": 4, "price": 60, "color": "#556270"},
    {"id": 4, "name": "Sportster", "seats": 2, "price": 85, "color": "#FFD93D"},
]

# ----------------- App Class -----------------
class CarBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Booking App")
        self.root.geometry("980x600")
        self.root.minsize(900, 540)

        # Use ttk style for nicer widgets
        style = ttk.Style()
        style.theme_use('clam')

        # Colors
        self.bg_primary = '#0f1724'    # deep navy
        self.panel_bg = '#0b1220'      # darker panel
        self.accent = '#5eead4'        # mint
        self.soft = '#e6eef7'          # light
        self.button_bg = '#2563eb'     # vivid blue

        self.root.configure(bg=self.bg_primary)

        # Data
        self.available_cars = SAMPLE_CARS.copy()
        self.bookings = []

        # Layout frames
        self.create_header()
        self.create_sidebar()
        self.create_main()
        self.create_footer()

    def create_header(self):
        header = tk.Frame(self.root, bg=self.panel_bg, height=70)
        header.pack(side='top', fill='x')

        title = tk.Label(header, text="Car Booking", bg=self.panel_bg, fg=self.soft,
                         font=("Helvetica", 18, "bold"))
        title.pack(side='left', padx=20, pady=15)

        subtitle = tk.Label(header, text="Safe • Fast • Comfortable", bg=self.panel_bg, fg='#9aa4b2',
                            font=("Helvetica", 10))
        subtitle.pack(side='left', padx=6, pady=20)

        # Right side quick actions
        actions = tk.Frame(header, bg=self.panel_bg)
        actions.pack(side='right', padx=16)

        btn_export = tk.Button(actions, text="Export Bookings", bg=self.button_bg, fg='white',
                               activebackground=self.button_bg, bd=0, padx=12, pady=6,
                               command=self.export_bookings)
        btn_export.pack(side='right', padx=8, pady=10)

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.panel_bg, width=220)
        sidebar.pack(side='left', fill='y')

        # Profile / logo area
        profile = tk.Frame(sidebar, bg=self.panel_bg)
        profile.pack(fill='x', pady=20)
        logo = tk.Canvas(profile, width=64, height=64, bg=self.accent, highlightthickness=0)
        logo.create_text(32, 32, text="CB", font=("Helvetica", 18, 'bold'), fill=self.bg_primary)
        logo.pack(pady=6)

        lbl = tk.Label(profile, text="Welcome, Driver!", bg=self.panel_bg, fg=self.soft, font=("Helvetica", 11))
        lbl.pack()

        # Menu
        menu = tk.Frame(sidebar, bg=self.panel_bg)
        menu.pack(fill='both', expand=True, pady=10)

        self.make_sidebar_button(menu, "Search Cars", lambda: self.show_frame('search'))
        self.make_sidebar_button(menu, "My Bookings", lambda: self.show_frame('bookings'))
        self.make_sidebar_button(menu, "About", self.show_about)

    def make_sidebar_button(self, parent, text, command):
        b = tk.Button(parent, text=text, bg=self.panel_bg, fg=self.soft, bd=0, anchor='w',
                      padx=20, pady=10, activebackground=self.bg_primary, command=command)
        b.pack(fill='x')

    def create_main(self):
        self.main = tk.Frame(self.root, bg=self.bg_primary)
        self.main.pack(side='left', fill='both', expand=True)

        # Frames for different views
        self.frames = {}
        self.frames['search'] = tk.Frame(self.main, bg=self.bg_primary)
        self.frames['bookings'] = tk.Frame(self.main, bg=self.bg_primary)

        for f in self.frames.values():
            f.place(relwidth=1, relheight=1)

        self.build_search(self.frames['search'])
        self.build_bookings(self.frames['bookings'])

        self.show_frame('search')

    def create_footer(self):
        footer = tk.Frame(self.root, bg=self.panel_bg, height=28)
        footer.pack(side='bottom', fill='x')
        now = datetime.now().strftime('%b %d, %Y %H:%M')
        lbl = tk.Label(footer, text=f"{now}  —  Car Booking App demo", bg=self.panel_bg, fg='#6b7280', font=("Helvetica", 9))
        lbl.pack(side='left', padx=12)

    def show_frame(self, name):
        for k, v in self.frames.items():
            if k == name:
                v.lift()
            else:
                v.lower()

    # ---------------- Search View ----------------
    def build_search(self, parent):
        # Left: search form
        left = tk.Frame(parent, bg=self.bg_primary)
        left.place(relx=0.02, rely=0.04, relwidth=0.34, relheight=0.9)

        l_title = tk.Label(left, text="Find Your Ride", bg=self.bg_primary, fg=self.accent, font=("Helvetica", 16, 'bold'))
        l_title.pack(anchor='nw', pady=(10,6), padx=8)

        # Form fields
        form = tk.Frame(left, bg=self.bg_primary)
        form.pack(fill='both', expand=True, padx=8, pady=8)

        # Pickup
        tk.Label(form, text="Pickup Location:", bg=self.bg_primary, fg=self.soft).grid(row=0, column=0, sticky='w', pady=6)
        self.entry_pickup = ttk.Entry(form)
        self.entry_pickup.grid(row=0, column=1, sticky='ew', padx=8)

        # Dropoff
        tk.Label(form, text="Dropoff Location:", bg=self.bg_primary, fg=self.soft).grid(row=1, column=0, sticky='w', pady=6)
        self.entry_drop = ttk.Entry(form)
        self.entry_drop.grid(row=1, column=1, sticky='ew', padx=8)

        # Date
        tk.Label(form, text="Date (YYYY-MM-DD):", bg=self.bg_primary, fg=self.soft).grid(row=2, column=0, sticky='w', pady=6)
        self.entry_date = ttk.Entry(form)
        self.entry_date.grid(row=2, column=1, sticky='ew', padx=8)

        # Time
        tk.Label(form, text="Time (HH:MM):", bg=self.bg_primary, fg=self.soft).grid(row=3, column=0, sticky='w', pady=6)
        self.entry_time = ttk.Entry(form)
        self.entry_time.grid(row=3, column=1, sticky='ew', padx=8)

        # Car type
        tk.Label(form, text="Car Type:", bg=self.bg_primary, fg=self.soft).grid(row=4, column=0, sticky='w', pady=6)
        self.car_type = ttk.Combobox(form, values=[c['name'] for c in self.available_cars], state='readonly')
        self.car_type.grid(row=4, column=1, sticky='ew', padx=8)
        self.car_type.current(0)

        # Search button
        search_btn = tk.Button(left, text="Search Cars", bg=self.button_bg, fg='white', bd=0, padx=12, pady=8, command=self.search_cars)
        search_btn.pack(pady=12, padx=12, anchor='s')

        # Right: available cars
        right = tk.Frame(parent, bg=self.bg_primary)
        right.place(relx=0.38, rely=0.04, relwidth=0.6, relheight=0.9)

        r_title = tk.Label(right, text="Available Cars", bg=self.bg_primary, fg=self.soft, font=("Helvetica", 14, 'bold'))
        r_title.pack(anchor='nw', pady=(6,8), padx=6)

        # Canvas to show car cards
        self.cars_canvas = tk.Canvas(right, bg=self.bg_primary, highlightthickness=0)
        self.cars_canvas.pack(fill='both', expand=True, padx=8, pady=6)

        # Use an internal frame inside canvas for scrollbar
        self.cards_frame = tk.Frame(self.cars_canvas, bg=self.bg_primary)
        self.cars_canvas.create_window((0,0), window=self.cards_frame, anchor='nw')
        self.cards_frame.bind('<Configure>', lambda e: self.cars_canvas.configure(scrollregion=self.cars_canvas.bbox('all')))

        # Scrollbar
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.cars_canvas.yview)
        self.cars_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Initial populate
        self.populate_car_cards(self.available_cars)

    def populate_car_cards(self, cars):
        # clear
        for w in self.cards_frame.winfo_children():
            w.destroy()

        for i, car in enumerate(cars):
            card = tk.Frame(self.cards_frame, bg='#071427', bd=0, relief='flat')
            card.grid(row=i, column=0, pady=8, padx=10, sticky='ew')

            # Color block as thumbnail
            thumb = tk.Canvas(card, width=120, height=70, bg=car['color'], highlightthickness=0)
            thumb.pack(side='left', padx=8, pady=8)
            thumb.create_text(60, 35, text=car['name'].split()[0], fill='white', font=("Helvetica", 10, 'bold'))

            # Info
            info = tk.Frame(card, bg=self.bg_primary)
            info.pack(side='left', fill='both', expand=True, padx=8)
            tk.Label(info, text=car['name'], bg=self.bg_primary, fg=self.soft, font=("Helvetica", 12, 'bold')).pack(anchor='w')
            tk.Label(info, text=f"Seats: {car['seats']}    Price: ${car['price']}/hr", bg=self.bg_primary, fg='#9aa4b2').pack(anchor='w')

            # Action button
            action = tk.Button(card, text="Book Now", bg=self.accent, fg=self.bg_primary, bd=0, padx=12, pady=6,
                               command=lambda c=car: self.open_booking_dialog(c))
            action.pack(side='right', padx=12, pady=16)

    def open_booking_dialog(self, car):
        # Small top-level dialog to confirm booking
        dlg = tk.Toplevel(self.root)
        dlg.title("Confirm Booking")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=self.panel_bg)
        dlg.geometry('360x220')

        tk.Label(dlg, text=f"Book: {car['name']}", bg=self.panel_bg, fg=self.accent, font=("Helvetica", 14, 'bold')).pack(pady=(12,2))
        tk.Label(dlg, text=f"Seats: {car['seats']}    Price: ${car['price']}/hr", bg=self.panel_bg, fg=self.soft).pack(pady=4)

        tk.Label(dlg, text="Your Name:", bg=self.panel_bg, fg=self.soft).pack(anchor='w', padx=12, pady=(12,0))
        name_entry = ttk.Entry(dlg)
        name_entry.pack(fill='x', padx=12)

        tk.Label(dlg, text="Phone:", bg=self.panel_bg, fg=self.soft).pack(anchor='w', padx=12, pady=(8,0))
        phone_entry = ttk.Entry(dlg)
        phone_entry.pack(fill='x', padx=12)

        def confirm():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            if not name or not phone:
                messagebox.showwarning("Incomplete", "Please enter name and phone number.")
                return
            booking = {
                'id': len(self.bookings) + 1,
                'car_id': car['id'],
                'car_name': car['name'],
                'name': name,
                'phone': phone,
                'pickup': self.entry_pickup.get().strip(),
                'dropoff': self.entry_drop.get().strip(),
                'date': self.entry_date.get().strip(),
                'time': self.entry_time.get().strip(),
                'created_at': datetime.now().isoformat()
            }
            self.bookings.append(booking)
            messagebox.showinfo("Booked", f"Booking confirmed for {car['name']}\nThank you, {name}!")
            dlg.destroy()
            self.refresh_bookings_table()

        btn_frame = tk.Frame(dlg, bg=self.panel_bg)
        btn_frame.pack(fill='x', pady=12)
        ttk.Button(btn_frame, text="Cancel", command=dlg.destroy).pack(side='right', padx=8)
        ttk.Button(btn_frame, text="Confirm", command=confirm).pack(side='right')

    def search_cars(self):
        # Very simple filter by car name contains selected type or always return all
        q = self.car_type.get().lower()
        results = [c for c in self.available_cars if q in c['name'].lower()] if q else self.available_cars
        self.populate_car_cards(results)

    # ---------------- Bookings View ----------------
    def build_bookings(self, parent):
        title = tk.Label(parent, text="My Bookings", bg=self.bg_primary, fg=self.accent, font=("Helvetica", 16, 'bold'))
        title.pack(anchor='nw', pady=(12,8), padx=12)

        cols = ("id", "car", "name", "phone", "pickup", "dropoff", "date", "time")
        self.bookings_tree = ttk.Treeview(parent, columns=cols, show='headings', height=18)
        for c in cols:
            self.bookings_tree.heading(c, text=c.capitalize())
            self.bookings_tree.column(c, width=100, anchor='center')
        self.bookings_tree.pack(fill='both', expand=True, padx=12, pady=8)

        # Action buttons
        btns = tk.Frame(parent, bg=self.bg_primary)
        btns.pack(fill='x', padx=12, pady=6)
        ttk.Button(btns, text="Cancel Booking", command=self.cancel_selected_booking).pack(side='left')
        ttk.Button(btns, text="Export Selected", command=self.export_selected).pack(side='left', padx=8)

    def refresh_bookings_table(self):
        # clear
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        for b in self.bookings:
            self.bookings_tree.insert('', 'end', values=(b['id'], b['car_name'], b['name'], b['phone'], b['pickup'], b['dropoff'], b['date'], b['time']))

    def cancel_selected_booking(self):
        sel = self.bookings_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a booking to cancel.")
            return
        item = sel[0]
        vals = self.bookings_tree.item(item, 'values')
        bid = int(vals[0])
        self.bookings = [b for b in self.bookings if b['id'] != bid]
        self.refresh_bookings_table()
        messagebox.showinfo("Cancelled", f"Booking #{bid} cancelled.")

    def export_bookings(self):
        if not self.bookings:
            messagebox.showinfo("No Data", "There are no bookings to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.bookings, f, indent=2)
        messagebox.showinfo("Exported", f"Bookings exported to {path}")

    def export_selected(self):
        sel = self.bookings_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select one booking to export.")
            return
        item = sel[0]
        vals = self.bookings_tree.item(item, 'values')
        bid = int(vals[0])
        booking = next((b for b in self.bookings if b['id'] == bid), None)
        if not booking:
            messagebox.showerror("Error", "Booking not found.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(booking, f, indent=2)
        messagebox.showinfo("Exported", f"Booking #{bid} exported to {path}")

    def show_about(self):
        messagebox.showinfo("About", "Car Booking App\nDemo UI built with tkinter.\nMade by ChatGPT.")


# ---------------- Run -----------------
if __name__ == '__main__':
    root = tk.Tk()
    app = CarBookingApp(root)
    # Make sure bookings view updates when shown
    root.bind('<Visibility>', lambda e: app.refresh_bookings_table())
    root.mainloop()
