from node import *
class Segment:
    def __init__(self,name="",n1=None,n2=None):
        self.name=name
        self.org=n1
        self.des=n2
        self.cost=Distance(n1,n2)