class NavPoint:
    def __init__(self, number, name, lat, lon):
        self.number = number
        self.name = name
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return f"NavPoints({self.number}, {self.name}, {self.lat}, {self.lon})"
    
def Distance(org, des):
    return round(((org.lon - des.lon) * 2 + (org.lat - des.lat) * 2) * 0.5, 2)

def Cost(org, des):
    return Distance(org, des)