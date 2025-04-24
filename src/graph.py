from segment import *
from node import *
from path import *
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.nodes=[]
        self.segments=[]

def AddNode(g,n):
    #Comprobar que no este ya
    if n in g.nodes:
        return False
    #Añadir el nodo
    g.nodes.append(n)
    return True

def AddSegment(g, nameOriginNode, nameDestinationNode):
    #Buscar si los nombres estan en los nodos del gráfico
    org=None
    des=None
    for n in g.nodes:
        if n.name == nameOriginNode:
            org=n
            if des:
                break
        elif n.name == nameDestinationNode:
            des=n
            if org:
                break
    if org and des:
        #mirar que no estigui fet ja
        for s in g.segments:
            if s.org == org and s.des == des:
                return False
        #Añadirlos como vecinos
        AddNeighbor(org,des)
        #Añadir el segmento
        g.segments.append(Segment(org.name+des.name,org,des))
        return True
    return False

def GetClosest(g,x,y):
    n_aux = Node('aux',x,y)
    min_dist = Distance(n_aux,g.nodes[0])
    node = g.nodes[0]
    for n in g.nodes[1:]:
        dist=Distance(n_aux,n)
        if dist < min_dist:
            min_dist = dist
            node = n
    return node

def Plot(g,ax):
    for n in g.nodes:#Plot all nodes
        ax.plot(n.coords_x,n.coords_y,'ro')
        ax.text(n.coords_x, n.coords_y + (((ax.get_xlim()[1]-ax.get_xlim()[0])**2+(ax.get_ylim()[1]-ax.get_ylim()[0])**2)**0.5)/100, n.name, ha='center', va='bottom')
    for s in g.segments:#Print all segments
        ax.plot([s.org.coords_x,s.des.coords_x],[s.org.coords_y,s.des.coords_y],'b-')
        ax.text((s.org.coords_x+s.des.coords_x)/2,(s.org.coords_y+s.des.coords_y)/2, s.cost, ha='center', va='bottom')#Cambiar esto !!!
    ax.grid(True)
    ax.autoscale(enable=True, axis='both', tight=False)

def PlotNode(g,nameOrigin,ax):
    #Buscar si el nombre del nodo origen esta en los nodos del gráfico
    find=False
    for n in g.nodes:
        if n.name == nameOrigin:find=True;org=n;break
    if not find:return False
    #Plot origen
    ax.plot(org.coords_x,org.coords_y,'bo')
    ax.text(org.coords_x, org.coords_y + 0.1, org.name, ha='center', va='bottom')
    #buscar entre todos los nodos del gráfico
    for n in g.nodes:
        if n == org:#No utilizar el origen aquí
            continue
        #Plot de los puntos vecinos y la línea que los une
        if n in org.neighbors:
            ax.plot(n.coords_x,n.coords_y,'go')
            ax.text(n.coords_x, n.coords_y + 0.1, n.name, ha='center', va='bottom')
            AddSegment(g,org,n)
            segmento = next((s for s in g.segments if (s.org == org and s.des == n) or (s.org == n and s.des == org)), None)#Antes utilizaba index, pero index si no existe da error, este no
            ax.plot([segmento.org.coords_x,segmento.des.coords_x],[segmento.org.coords_y,segmento.des.coords_y],'r-')
            ax.text((segmento.org.coords_x+segmento.des.coords_x)/2, (segmento.org.coords_y+segmento.des.coords_y)/2, segmento.cost, ha='center', va='bottom')
        #Plot de los no vecinos
        else:
            ax.plot(n.coords_x,n.coords_y,'o',color='gray')
            ax.text(n.coords_x, n.coords_y + 0.1, n.name, ha='center', va='bottom')
    ax.grid(True)
    ax.autoscale(enable=True, axis='both', tight=False)
    return True

def LoadGraph(g,file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(" ") #Separa cada línea en espacios
            if parts[0] == "Node":
                AddNode(g,Node(parts[1],float(parts[2]),float(parts[3]))) #Si es un nodo carga el nombre y posición
        for line in lines:
            parts = line.strip().split()
            if parts[0] == "Segment":
                AddSegment(g,parts[1],parts[2]) #Si es un segmento carga el nombre del nodo origen y destino
    return

def SaveGraph(self, file_path):
    with open(file_path, 'w') as file:
        for node in self.nodes:
            file.write(f"Node {node.name} {node.coords_x} {node.coords_y}\n") #Para los nodes guarda el nombre, coordsx y coordsy
        for segment in self.segments:
            file.write(f"Segment {segment.org.name} {segment.des.name}\n") #Para los segmentos guarda el nombre del origen y el nombre del destino
    print(f"El grafo se ha guardado correctamente en {file_path}.")
    return

def DeleteNode(g,nd):
    #Buscar segmentos donde esta el nodo y eliminarlos
    segmentsToDelete = []
    for s in g.segments:
        if s.org == nd or s.des == nd:
            segmentsToDelete.append(s)
    for s in segmentsToDelete:
        DeleteSegment(g,s)
    #Remove de la lista de nodos nd
    g.nodes.remove(nd)
    return

def DeleteSegmentByName(g,nameOrg,nameDes):
    org=None
    des=None
    for n in g.nodes:
        if n.name == nameOrg:
            org=n
            if des:
                break
        elif n.name == nameDes:
            des=n
            if org:
                break
    if org and des:
        for s in g.segments:
            if (s.org == org and s.des == des):
                g.segments.remove(s)
                org.neighbors.remove(des)
                return True
    return False

def DeleteSegment(g,s):
    s.org.neighbors.remove(s.des)
    g.segments.remove(s)

def Reachability(g, origin):
    path = Path([])
    # Initialize the queue and the visited nodes
    AddNodeToPath(path, origin)
    queue = [origin]
    visited = set()
    while queue:
        current_node = queue.pop(0)
        visited.add(current_node)
        for neighbor in current_node.neighbors:
            if neighbor not in visited:
                queue.append(neighbor)
                AddNodeToPath(path, neighbor)
    if len(path.path) > 0:
        return path
    return None

def FindShortestPath(g, origin, destination):
    # Initialize the list of paths and the visited nodes
    paths = []
    path = Path([])
    AddNodeToPath(path, origin)
    # Check if the origin and destination are in the graph
    if origin not in g.nodes or destination not in g.nodes:
        return None
    # Check if the origin and destination are the same
    if origin == destination:
        path.AddNodeToPath(destination)
        return path
    # Add the path to the list of paths
    paths.append(path)
    while paths:
        # Get the path with the lowest estimated cost
        min_path = min(paths, key=lambda p: p.cost)
        paths.remove(min_path)
        last_node = min_path.path[-1]
        for neighbor in last_node.neighbors:
            if neighbor == destination:
                AddNodeToPath(min_path, neighbor)
                return min_path
            if neighbor not in min_path.path:
                new_path = Path(min_path.path.copy())
                AddNodeToPath(new_path, neighbor)
                new_path.cost += Cost(last_node, neighbor)
                paths.append(new_path)
            else:
                for p in paths:
                    if neighbor in p.path and p.cost > min_path.cost + Cost(last_node, neighbor):
                        paths.remove(p)
    return None