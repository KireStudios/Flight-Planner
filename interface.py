import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graph import *  # Asegúrate de que graph.py esté correctamente implementado

class GraphVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Visualizer")
        self.root.geometry("1280x720")
        self.graph = Graph()
        self.cid = None
        self.file = ''

        # Crear el layout con frames
        self.create_layout()

    def create_layout(self):
        """ Crea la estructura principal de la interfaz """
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side="left", padx=10, pady=10, fill="y")

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side="right", padx=10, pady=10, fill="y")

        self.center_frame = tk.Frame(self.root)
        self.center_frame.pack(side="left", expand=True, fill="both")

        self.create_widgets()

    def create_widgets(self):
        """ Agrega los botones y la gráfica """

        # Botones en el lado izquierdo
        tk.Button(self.left_frame, text="Load Graph", command=self.GraphLoad).pack(pady=5)
        tk.Button(self.left_frame, text="Create Graph", command=self.GraphCreate).pack(pady=5)
        tk.Button(self.left_frame, text="Create Segment", command=self.SegmentAdd).pack(pady=5)

        # Entrada y botón para enfatizar nodo
        tk.Label(self.left_frame, text="Emphasize Node:").pack(pady=5)
        self.enf_entry = tk.Entry(self.left_frame)
        self.enf_entry.pack(pady=5)
        tk.Button(self.left_frame, text="Show Neighbors", command=self.NodeNeighbors).pack(pady=5)

        # Entrada y botón para eliminar nodo
        tk.Label(self.left_frame, text="Delete Node:").pack(pady=5)
        self.del_entry = tk.Entry(self.left_frame)
        self.del_entry.pack(pady=5)
        tk.Button(self.left_frame, text="Delete", command=self.NodeDelete).pack(pady=5)

        #Eliminar segmento
        tk.Button(self.left_frame, text="Delete Segment", command=self.SegmentDelete).pack(pady=5)

        # Entrada y botón para añadir nodo
        tk.Label(self.left_frame, text="Add Node:").pack(pady=5)
        self.add_entry = tk.Entry(self.left_frame)
        self.add_entry.pack(pady=5)
        tk.Button(self.left_frame, text="Add", command=self.NodeAdd).pack(pady=5)

        # Botones adicionales en el lado derecho (puedes agregar más opciones aquí)
        tk.Button(self.right_frame, text="Exit", command=self.root.quit).pack(pady=5)

        # Crear la figura de matplotlib en el centro
        self.fig, self.ax1 = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.center_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        # Conectar el evento de clic
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def clear_graph(self):
        """ Limpia la gráfica antes de actualizarla """
        self.ax1.clear()
        self.ax1.set_title("Graph Visualization")
        self.ax1.grid(True)

    # Métodos para las acciones
    def GraphLoad(self):
        self.file_path = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.file_path:
            return
        self.graph = Graph()
        LoadGraph(self.graph, self.file_path)
        self.clear_graph()
        Plot(self.graph, self.ax1)
        self.canvas.draw()

    def NodeNeighbors(self):
        node_name = self.enf_entry.get()
        if not node_name:
            messagebox.showerror("Error", "Please enter a node name.")
            return
        for n in self.graph.nodes:
            if n.name == node_name:
                self.clear_graph()
                PlotNode(self.graph, node_name, self.ax1)
                self.canvas.draw()
                return
        messagebox.showerror("Error", f"Node '{node_name}' not found in the graph.")

    def NodeDelete(self):
        node_name = self.del_entry.get()
        if not node_name:
            messagebox.showerror("Error", "Please enter a node name.")
            return
        for n in self.graph.nodes:
            if n.name == node_name:
                DeleteNode(self.graph, n)
                SaveGraph(self.graph, self.file_path)
                self.clear_graph()
                Plot(self.graph, self.ax1)
                self.canvas.draw()
                return
        messagebox.showerror("Error", f"Node '{node_name}' not found in the graph.")

    def on_click(self, event):
        if event.inaxes != self.ax1:
            return
        min_dist = float('inf')
        selected_node = None
        for node in self.graph.nodes:
            dist = ((event.xdata - node.coords_x) ** 2 + (event.ydata - node.coords_y) ** 2) ** 0.5
            if dist < min_dist and dist < 1:
                min_dist = dist
                selected_node = node
        if selected_node:
            self.clear_graph()
            PlotNode(self.graph, selected_node.name, self.ax1)
            self.canvas.draw()

    def NodeAdd(self):
        node_name = self.add_entry.get()
        if not node_name:
            messagebox.showerror("Error", "Please enter a node name.")
            return
        try:
            x = simpledialog.askfloat("Input", "Enter X coordinate:")
            y = simpledialog.askfloat("Input", "Enter Y coordinate:")
            if x is None or y is None:
                messagebox.showerror("Error", "Coordinates must be valid numbers.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates.")
            return
        AddNode(self.graph, Node(node_name, x, y))
        SaveGraph(self.graph, self.file_path)
        self.clear_graph()
        Plot(self.graph, self.ax1)
        self.canvas.draw()

    def GraphCreate(self):
        folder_selected = filedialog.askdirectory(title="Select Folder to Save Graph")
        if not folder_selected:
            messagebox.showerror("Error", "No folder selected.")
            return
        file_name = simpledialog.askstring("Input", "Enter file name (without extension):")
        if not file_name:
            messagebox.showerror("Error", "No file name entered.")
            return
        self.file_path = folder_selected + "/" + file_name + ".txt"
        try:
            with open(self.file_path, "w") as file:
                file.write("")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create file: {e}")
            return
        messagebox.showinfo("Success", f"Graph file created at:\n{self.file_path}")
        self.graph = Graph()
        LoadGraph(self.graph, self.file_path)
        self.clear_graph()
        Plot(self.graph, self.ax1)
        self.canvas.draw()

    def SegmentAdd(self):
        try:
            n1 = simpledialog.askstring("Input", "Enter origin node name:")
            n2 = simpledialog.askstring("Input", "Enter destination node name:")
            if n1 is None or n2 is None:
                messagebox.showerror("Error", "Nodes must be registered or check the name.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid nodes.")
            return
        AddSegment(self.graph, n1, n2)
        SaveGraph(self.graph, self.file_path)
        self.clear_graph()
        Plot(self.graph, self.ax1)
        self.canvas.draw()

    def SegmentDelete(self):
        nameOrg = simpledialog.askstring("Input", "Enter origin node name:")
        nameDes = simpledialog.askstring("Input", "Enter destination node name:")
        DeleteSegment(self.graph,nameOrg,nameDes)
        # except:messagebox.showerror("Error", f"Segment not found in the graph.")
        SaveGraph(self.graph, self.file_path)
        self.clear_graph()
        Plot(self.graph, self.ax1)
        self.canvas.draw()

root = tk.Tk()
app = GraphVisualizer(root)
root.mainloop()