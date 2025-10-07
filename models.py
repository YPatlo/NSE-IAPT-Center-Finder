# models.py

class Centre:
    def __init__(self, code, name, address, coordinator_name, subject, coords=None):
        self.code = code
        self.name = name
        self.address = address
        self.coordinator_name = coordinator_name
        self.subject = subject
        self.coords = coords  # tuple (lat, lon)

    def __repr__(self):
        return f"Centre(code={self.code}, name={self.name})"

    def __lt__(self, other):
        # For sorting, example by name (can change as needed)
        return self.name < other.name
