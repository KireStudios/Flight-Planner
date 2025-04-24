import sys
import os

# Añade la ruta a la carpeta 'src' al PATH de Python
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(src_path)
from node import *
n1 = Node ('aaa', 0, 0) 
n2 = Node ('bbb', 3, 4) 
print (Distance(n1,n2)) 
print (AddNeighbor(n1, n2)) 
print (AddNeighbor(n1, n2)) 
print (n1.__dict__) 
for n in n1.neighbors: 
    print ( n.__dict__) 