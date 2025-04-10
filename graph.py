from segment import *
from node import *
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

def AddSegment (g, nameOriginNode, nameDestinationNode):
    #Buscar si los nombres estan en los nodos del gráfico
    find=False
    for n in g.nodes:
        if n.name == nameOriginNode:find=True;org=n;break
    if not find:return False #innecesarias solo para no hacer for
    find=False
    for n in g.nodes:
        if n.name == nameDestinationNode:find=True;des=n;break
    if not find:return False
    #Añadirlos como vecinos
    AddNeighbor(org,des)
    #Añadir el segmento
    g.segments.append(Segment(org.name+des.name,org,des))
    return True

def GetClosest(g,x,y):
    n_aux = Node('aux',x,y)
    dist = {}
    for n in g.nodes:
        dist[n]=(Distance(n_aux,n))
    #Mide distancia entre todos y coge del diccionario la key del valor minimo
    return min(dist, key=dist.get)

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
    ax.text(n.coords_x, n.coords_y + 0.1, org.name, ha='center', va='bottom')
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
    for s in g.segments:
        if s.org == nd:s.des.neighbors.remove(nd);g.segments.remove(s)
        if s.des == nd:s.org.neighbors.remove(nd);g.segments.remove(s)
    #Remove de la lista de nodos nd
    g.nodes.remove(nd)
    return

def DeleteSegment(g,nameOrg,nameDes):
    find=False
    for n in g.nodes:
        if n.name == nameOrg:find=True;org=n;break
    if not find:return False #innecesarias solo para no hacer for
    find=False
    for n in g.nodes:
        if n.name == nameDes:find=True;des=n;break
    if not find:return False
    for s in g.segments:
        if s.org == org or s.des == org and s.org == des or s.des == des:g.segments.remove(s);org.neighbors.remove(des);des.neighbors.remove(org);return True
    return False