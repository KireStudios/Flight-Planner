class Node:
    def __init__(self, name="", x=.0, y=.0):
        self.name=name
        self.coords_x=x
        self.coords_y=y
        self.neighbors=[]

def AddNeighbor(n1,n2):
    if n2 in n1.neighbors:
        return False
    n1.neighbors.append(n2)
    return True

def Distance(n1,n2):
    return ((n1.coords_x - n2.coords_x)**2 + (n1.coords_y - n2.coords_y)**2)**0.5

def Cost(n1,n2):
    return Distance(n1,n2)