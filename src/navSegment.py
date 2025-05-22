class NavSegment:
    def __init__(self, OriginNumber, DestinationNumber, Distance):
        self.org = OriginNumber
        self.des = DestinationNumber
        self.dis = Distance

    def __repr__(self):
        return f"NavSegment({self.org}, {self.des}, {self.dis})"