import sys
import os

# Añade la ruta a la carpeta 'src' al PATH de Python
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(src_path)
from graph import *
from path import *
import matplotlib.pyplot as plt
path = Path([])
n1 = Node ('aaa', 0, 0)
n2 = Node ('bbb', 3, 4)
n3 = Node ('ccc', 3, -4)
n4 = Node ('ddd', -3, 4)
n5 = Node ('eee', -3, -4)
AddNeighbor(n1, n2)
AddNeighbor(n2, n3)
AddNeighbor(n3, n4)
#Comprobar AddNodeToPath
AddNodeToPath(path, n1)
AddNodeToPath(path, n2)
AddNodeToPath(path, n3)
AddNodeToPath(path, n4)
#Comprobar ContainsNode
print(ContainsNode(path, n1))  # True
print(ContainsNode(path, n5))  # False
#Comprobar CostToNode
# print(CostToNode(path, n4))  # 0.0
#Comprobar PlotPath
g = Graph()
g.nodes = [n1, n2, n3, n4, n5]
g.segments = [Segment('aaa', n1, n2), Segment('bbb', n2, n3), Segment('ccc', n3, n4)]
fig, ax = plt.subplots()
PlotPath(g,path, ax)
plt.show()

print(path.__dict__)
