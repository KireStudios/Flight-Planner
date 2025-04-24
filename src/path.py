from graph import Graph

class Path:
    def __init__(self, path):
        self.path = path
        self.cost = 0.0

    def AddNodeToPath (Path, Node):
        # Adds the Node to the Path. Returns True if successful and False otherwise.
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

    #def PlotPath (Graph, Path):
        # Plots the Path in the Graph. Returns True if successful and False otherwise.
        