from segment import *
from node import *
n1 = Node ('aaa', 0, 0) 
n2 = Node ('bbb', 3, 4)
n3 = Node ('ccc', -3, -4)
s1 = Segment ('ab',n1,n2)
s2 = Segment ('bc',n2,n3)
print(s1.__dict__)
print(s2.__dict__)