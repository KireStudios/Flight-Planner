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
        self.popup_win = None

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

    def PopupSelect(self,x,y,button,event):
        self.popup_win = tk.Toplevel()
        self.popup_win.geometry(f"+{int(x)}+{int(y)}")#cambiar alto y ancho
        self.popup_win.wm_overrideredirect(True)
        if button == 1:
            neighbors = tk.Button(self.popup_win, text="Neighbors", command=lambda:[self.NodeNeighbors_(event),self.popup_win.destroy()])
            neighbors.grid(row=0, column=0,sticky="nsew")
            node = tk.Button(self.popup_win, text="Node", command=lambda:[self.AddNode_(event),self.popup_win.destroy()])
            node.grid(row=1, column=0, sticky="nsew")
            segment = tk.Button(self.popup_win, text="Segment", command=lambda:[self.AddSegment_(),self.popup_win.destroy()])
            segment.grid(row=0, column=1,sticky="nsew")
            segment = tk.Button(self.popup_win, text="Exit", command=lambda:self.popup_win.destroy())
            segment.grid(row=1, column=1,sticky="nsew")
        elif button == 3:
            node = tk.Button(self.popup_win, text="Node", command=lambda:[self.DeleteNode_(event),self.popup_win.destroy()])
            node.grid(row=0, column=0, sticky="nsew")
            segment = tk.Button(self.popup_win, text="Segment", command=lambda:[self.DeleteSegment_(event),self.popup_win.destroy()])
            segment.grid(row=0, column=1,sticky="nsew")
            segment = tk.Button(self.popup_win, text="Exit", command=lambda:self.popup_win.destroy())
            segment.grid(row=1, column=0,sticky="nsew")

    def NodeNeighbors_(self,event):
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
    def AddNode_(self,event):
        try:
            name = simpledialog.askstring("Input", "Enter origin node name:")
        except ValueError:
            messagebox.showerror("Error", "Invalid nodes.")
            return
        self.clear_graph()
        AddNode(self.graph,Node(str(name),event.xdata,event.ydata))
        SaveGraph(self.graph, self.file_path)
        Plot(self.graph, self.ax1)
        self.canvas.draw()
    def AddSegment_(self):
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
    def DeleteNode_(self,event):
        if event.inaxes != self.ax1:
            return
        min_dist = float('inf')
        selected_node = None
        for node in self.graph.nodes:
            dist = ((event.xdata - node.coords_x) ** 2 + (event.ydata - node.coords_y) ** 2) ** 0.5
            threshold=(((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/100
            if dist < min_dist and dist < threshold:
                min_dist = dist
                selected_node = node
        if selected_node:
            DeleteNode(self.graph, selected_node)
            SaveGraph(self.graph, self.file_path)
            self.clear_graph()
            Plot(self.graph, self.ax1)
            self.canvas.draw()
    def DeleteSegment_(self,event):
        for s in self.graph.segments:
                    dist=abs((s.des.coords_x-s.org.coords_x)*(s.org.coords_y-event.ydata)-(s.org.coords_x-event.xdata)*(s.des.coords_y-s.org.coords_y))/((s.des.coords_x-s.org.coords_x)**2+(s.des.coords_y-s.org.coords_y)**2)**0.5
                    threshold=(((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/100
                    if dist<threshold:
                        DeleteSegment(self.graph,s.org.name,s.des.name)
                        SaveGraph(self.graph, self.file_path)
                        self.clear_graph()
                        Plot(self.graph, self.ax1)
                        self.canvas.draw()
                        return
        pass
    
    def on_click(self,event):
        if self.popup_win != None:
            self.popup_win.destroy()
        if event.xdata != None or event.ydata != None:
            x = self.canvas.get_tk_widget().winfo_rootx()+event.x
            y = self.canvas.get_tk_widget().winfo_rooty()+self.canvas.get_tk_widget().winfo_height()-event.y
        self.PopupSelect(x,y,event.button,event)

root = tk.Tk()
app = GraphVisualizer(root)
root.mainloop()