import sys
import os

# Añade la ruta a la carpeta 'src' al PATH de Python
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(src_path)
from node import *
from segment import *
n1 = Node ('aaa', 0, 0) 
n2 = Node ('bbb', 3, 4)
n3 = Node ('ccc', -3, -4)
s1 = Segment ('ab',n1,n2)
s2 = Segment ('bc',n2,n3)
print(s1.__dict__)
print(s2.__dict__)