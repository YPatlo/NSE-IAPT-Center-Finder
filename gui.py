import tkinter as tk
from tkinter import ttk, messagebox
import json
from api import fetch_centres
from utils import (
    simplify_address,
    load_geocode_cache,
    save_geocode_cache,
    normalize,
    geocode_with_cache,
    find_nearest_centres,
)

class CentreFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IAPT Centre Finder")
        self.geometry("800x600")
        self.resizable(False, False)

        # Load locations
        with open("locations.json", "r", encoding="utf-8") as f:
            self.states = json.load(f)

        self.geocode_cache = load_geocode_cache()
        self.centres = []
        self.state_id = None
        self.district = None
        self.city = None

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # State selection
        tk.Label(self, text="Select State:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.state_var = tk.StringVar()
        self.state_combo = ttk.Combobox(self, textvariable=self.state_var, state="readonly")
        self.state_combo['values'] = [f"{sid}: {s['state_name']}" for sid, s in self.states.items()]
        self.state_combo.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.state_combo.bind("<<ComboboxSelected>>", self.on_state_selected)

        # District selection
        tk.Label(self, text="Select District:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.district_var = tk.StringVar()
        self.district_combo = ttk.Combobox(self, textvariable=self.district_var, state="readonly")
        self.district_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.district_combo.bind("<<ComboboxSelected>>", self.on_district_selected)

        # City selection
        tk.Label(self, text="Select City:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(self, textvariable=self.city_var, state="readonly")
        self.city_combo.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Fetch Centres Button
        self.fetch_btn = tk.Button(self, text="Fetch Centres", command=self.fetch_centres_gui)
        self.fetch_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # User address entry
        tk.Label(self, text="Your Address:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.user_addr_entry = tk.Entry(self, width=60)
        self.user_addr_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

        # Find Nearest Button
        self.find_btn = tk.Button(self, text="Find Nearest Centres", command=self.find_nearest_gui)
        self.find_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Results
        self.results_text = tk.Text(self, height=20, width=95, state="disabled")
        self.results_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def on_state_selected(self, event=None):
        state_sel = self.state_combo.get()
        if not state_sel:
            return
        sid = state_sel.split(":")[0].strip()
        self.state_id = sid
        state = self.states[sid]
        districts = state.get("districts", [])
        self.district_combo['values'] = [f"{d['DistrictId']}: {d['DistrictName']}" for d in districts]
        self.district_combo.set("")
        self.city_combo.set("")
        self.city_combo['values'] = []
        self.district = None
        self.city = None

    def on_district_selected(self, event=None):
        district_sel = self.district_combo.get()
        if not district_sel or not self.state_id:
            return
        did = district_sel.split(":")[0].strip()
        state = self.states[self.state_id]
        districts = state.get("districts", [])
        for d in districts:
            if d["DistrictId"] == did:
                self.district = d
                break
        cities = self.district.get("cities", [])
        self.city_combo['values'] = cities
        self.city_combo.set("")
        self.city = None

    def fetch_centres_gui(self):
        if not self.state_id or not self.district_combo.get() or not self.city_combo.get():
            messagebox.showerror("Error", "Please select state, district, and city.")
            return
        city = self.city_combo.get()
        self.city = city
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Fetching centres for {self.states[self.state_id]['state_name']} / {self.district['DistrictName']} / {city} ...\n")
        self.results_text.update()
        centres = fetch_centres(self.state_id, self.district["DistrictId"], city, length=100)
        if not centres:
            self.results_text.insert(tk.END, "No centres found.\n")
            self.results_text.config(state="disabled")
            return
        self.centres = centres
        self.results_text.insert(tk.END, f"Total centres fetched: {len(centres)}\n")
        self.results_text.config(state="disabled")

    def find_nearest_gui(self):
        if not self.centres:
            messagebox.showerror("Error", "No centres loaded. Please fetch centres first.")
            return
        user_addr = self.user_addr_entry.get().strip()
        if not user_addr:
            messagebox.showerror("Error", "Please enter your address.")
            return
        # Geocode all centres if not already done
        state_name = self.states[self.state_id]["state_name"]
        district_name = self.district["DistrictName"]
        city = self.city
        valid_count = 0
        for c in self.centres:
            addr = getattr(c, "address", None)
            if not addr or not addr.strip():
                c.coords = None
                continue
            clean = simplify_address(addr)
            full_addr = f"{clean}, {city}, {district_name}, {state_name}, India"
            coords = geocode_with_cache(full_addr, self.geocode_cache)
            if coords:
                valid_count += 1
            c.coords = coords
        save_geocode_cache(self.geocode_cache)
        # Geocode user address
        user_coords = geocode_with_cache(user_addr, self.geocode_cache)
        if not user_coords:
            messagebox.showerror("Error", "Could not geocode your location.")
            return
        save_geocode_cache(self.geocode_cache)
        nearest = find_nearest_centres(user_coords, self.centres, top_k=3)
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        if not nearest:
            self.results_text.insert(tk.END, "No centres with valid coordinates.\n")
        else:
            self.results_text.insert(tk.END, "Nearest IAPT Centre(s):\n")
            for idx, (c, dist) in enumerate(nearest, start=1):
                self.results_text.insert(tk.END, f"\n#{idx}\n")
                self.results_text.insert(tk.END, f"  Code: {getattr(c, 'code', 'N/A')}\n")
                self.results_text.insert(tk.END, f"  Name: {getattr(c, 'name', 'N/A')}\n")
                self.results_text.insert(tk.END, f"  Address: {getattr(c, 'address', 'N/A')}\n")
                self.results_text.insert(tk.END, f"  Coordinator: {getattr(c, 'coordinator_name', 'N/A')}\n")
                self.results_text.insert(tk.END, f"  Subject: {getattr(c, 'subject', 'N/A')}\n")
                self.results_text.insert(tk.END, f"  Distance: {dist:.2f} km\n")
        self.results_text.config(state="disabled")

if __name__ == "__main__":
    app = CentreFinderApp()
    app.mainloop()