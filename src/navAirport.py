class NavAirport:
    def __init__(self, name, SIDs=[], STARs=[]):
        self.name = name
        self.SIDs = SIDs
        self.STARs = STARs

    def __repr__(self):
        return f"NavAirport({self.name}, {self.SIDs}, {self.STARs})"