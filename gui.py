import tkinter as tk
from tkinter import ttk, messagebox
import threading
from cli import main as cli_main  # assuming cli.py has your logic in a callable main()
from cli import geocode_with_cache, haversine, normalize  # or import specific functions
from geocode import geocode_address

# Create a simple GUI wrapper
class TravelGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Travel Time & Distance Calculator")
        self.geometry("600x400")
        self.resizable(False, False)

        # Variables
        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="Driving")
        self.output_text = tk.StringVar(value="")

        # --- Title ---
        tk.Label(self, text="Travel Time & Distance Tool", font=("Segoe UI", 18, "bold")).pack(pady=10)

        # --- Source ---
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)
        tk.Label(form_frame, text="Source Address:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(form_frame, width=50, textvariable=self.source_var).grid(row=0, column=1, padx=5, pady=5)

        # --- Destination ---
        tk.Label(form_frame, text="Destination Address:", font=("Segoe UI", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(form_frame, width=50, textvariable=self.dest_var).grid(row=1, column=1, padx=5, pady=5)

        # --- Mode Dropdown ---
        tk.Label(form_frame, text="Mode:", font=("Segoe UI", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Combobox(form_frame, textvariable=self.mode_var, values=["Driving", "Walking", "Cycling"], state="readonly").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # --- Button ---
        tk.Button(self, text="Calculate", command=self.calculate_threaded, bg="#0078D7", fg="white", font=("Segoe UI", 11, "bold"), width=15).pack(pady=10)

        # --- Output ---
        tk.Label(self, text="Output:", font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self.output_box = tk.Text(self, width=70, height=8, wrap="word", font=("Segoe UI", 10))
        self.output_box.pack(pady=5)

    def calculate_threaded(self):
        # Run in background thread to avoid freezing GUI
        threading.Thread(target=self.calculate, daemon=True).start()

    def calculate(self):
        src = self.source_var.get().strip()
        dest = self.dest_var.get().strip()

        if not src or not dest:
            messagebox.showwarning("Missing Info", "Please enter both source and destination addresses.")
            return

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Geocoding addresses...\n")

        src_coords = geocode_with_cache(src)
        dest_coords = geocode_with_cache(dest)

        if not src_coords or not dest_coords:
            self.output_box.insert(tk.END, "Failed to get coordinates for one or both addresses.\n")
            return

        distance = haversine(src_coords, dest_coords)
        mode = self.mode_var.get()

        self.output_box.insert(tk.END, f"Mode: {mode}\n")
        self.output_box.insert(tk.END, f"From: {src}\nTo: {dest}\n")
        self.output_box.insert(tk.END, f"\nDistance: {distance:.2f} km\n")

        # (Optional) Add travel time estimate
        avg_speed = {"Driving": 50, "Walking": 5, "Cycling": 15}
        travel_time = distance / avg_speed[mode] * 60  # in minutes
        self.output_box.insert(tk.END, f"Estimated Travel Time: {travel_time:.1f} minutes\n")

        self.output_box.insert(tk.END, "\nDone ✅")

# Run the GUI
if __name__ == "__main__":
    app = TravelGUI()
    app.mainloop()
