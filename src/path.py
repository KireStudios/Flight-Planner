from graph import *
from node import Cost

class Path:
    def __init__(self, path, origin=None):
        self.path = path
        self.origin = origin if origin else path[0] if path else None
        self.cost = 0.0

def AddNodeToPath (Path, Node):
    # Adds the Node to the Path. Returns True if successful and False otherwise.
    if Path.origin is None:
        Path.origin = Node
        Path.path.append(Node)
        return True
    if Node not in Path.path:
        Path.path.append(Node)
        return True
    return False

def ContainsNode (Path, Node):
    # Returns True if the Node is in the Path and False otherwise.
    return Node in Path.path

def CostToNode (Path, Node):
    # Returns the total cost from the origin of the Path to the 
    # Node. Returns -1 if the Node is not in the Path.
    Cost = 0
    if Node in Path.path:
        for i in range(0, len(Path.path)):
            Cost += Cost(Path.path[i], Path.path[i + 1])
            if Path.path[i+1] == Node:
                break
    return -1

def PlotPath(g, Path, ax):
    # Plots the Path in the Graph. Returns True if successful and False otherwise.
    #Plot origen
    ax.plot(Path.origin.coords_x,Path.origin.coords_y,'bo')
    ax.text(Path.origin.coords_x, Path.origin.coords_y + 0.1, Path.origin.name, ha='center', va='bottom')
    #buscar entre todos los nodos del gráfico
    for n in Path.path:
        #Plot de los puntos vecinos y la línea que los une
        for N in n.neighbors:
            if N in Path.path:
                ax.plot([n.coords_x,N.coords_x],[n.coords_y,N.coords_y],'r-')
                ax.text((n.coords_x+N.coords_x)/2, (n.coords_y+N.coords_y)/2, Cost(n, N), ha='center', va='bottom')
        if n != Path.origin:#No utilizar el origen aquí
            ax.plot(n.coords_x,n.coords_y,'go')
            ax.text(n.coords_x, n.coords_y + 0.1, n.name, ha='center', va='bottom')
    #Plot de los no vecinos
    for n in g.nodes:
        if n not in Path.path:
            ax.plot(n.coords_x,n.coords_y,'o',color='gray')
            ax.text(n.coords_x, n.coords_y + 0.1, n.name, ha='center', va='bottom')
    ax.grid(True)
    ax.autoscale(enable=True, axis='both', tight=False)
    return True