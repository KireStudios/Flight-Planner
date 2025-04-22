import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graph import *

def pulsate_warning(widget, iterations=4, pulse_speed=25):
    # Save original background color
    original_fg = widget.cget('fg')
    step = [0]  # Using list to make it mutable in nested functions
    count = [0]  # Iteration counter
    
    def pulse_step():
        # Calculate intensity (0.5 to 1.0 range)
        intensity = ((step[0] % 100) / 100)
        
        # Calculate RGB values (red with varying intensity)
        red = 255
        green = max(0, min(255, int(255 * (1 - intensity * 0.8))))
        blue = max(0, min(255, int(255 * (1 - intensity * 0.8))))
        
        # Apply color
        widget.config(fg=f"#{red:02x}{green:02x}{blue:02x}")
        
        # Count complete pulses
        if step[0] % 100 == 0:
            count[0] += 1
            
        # Stop after max iterations or restore original color
        if count[0] >= iterations:
            widget.config(fg=original_fg)
        else:
            step[0] += 5
            widget.after(pulse_speed, pulse_step)
    
    # Start the animation
    pulse_step()

class GraphVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Visualizer")
        self.root.geometry("1280x720")
        self.graph = Graph()
        self.cid = None
        self.file = ''
        self.popup_win = None
        self.tquocient = 100
        self.load = False
        self.cycle_count = 0

        self.create_layout()

    def create_layout(self):
        """ Crea la estructura principal de la interfaz """
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side="left", padx=10, pady=10, fill="y")

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side="right", padx=10, pady=10, fill="y")

        self.center_frame = tk.Frame(self.root)
        self.center_frame.pack(side="left", expand=True, fill="both")

        self.initial_widgets()

    def initial_widgets(self):
        """ Agrega los botones y la gráfica """

        # Botones en el lado izquierdo
        tk.Button(self.left_frame, text="Load Graph", command=self.GraphLoad).pack(pady=5)
        tk.Button(self.left_frame, text="Create Graph", command=self.GraphCreate).pack(pady=5)
        tk.Button(self.right_frame, text="Exit", command=self.root.quit).pack(pady=5)

        self.fig, self.ax1 = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.center_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        self.text_label = tk.Label(self.center_frame, text="Create or Load a Graph", font=("Arial", 14))
        self.text_label.pack(expand=True, fill="both", padx=10, pady=10)
        self.cycle_count = 0
        self.cid_start = self.fig.canvas.mpl_connect('button_press_event', lambda event: pulsate_warning(self.text_label))

    def clear_graph(self):
        """ Limpia la gráfica antes de actualizarla """
        self.ax1.clear()
        self.ax1.set_title("Graph Visualization")
        self.ax1.grid(True)


    def main_widgets(self):
        if not self.load:
            self.canvas.mpl_disconnect(self.cid_start)
            tk.Button(self.left_frame, text="Save Graph", command=self.GraphSave).pack(pady=5)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
            self.text_label.destroy()
    
    # Métodos para las acciones
    def GraphLoad(self):
        self.file_path = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.file_path:
            return
        self.main_widgets()
        self.load = True
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
        self.main_widgets()
        self.load = True
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

    def GraphSave(self):
        try:
            name = simpledialog.askstring("Input", "Enter file name:")
        except:
            messagebox.showerror("Error", "Invalid name.")
            return
        parts=self.file_path.split('/')
        parts[-1] = name
        SaveGraph(self.graph,'/'.join(parts)+'.txt')

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
        Plot(self.graph, self.ax1)
        self.canvas.draw()

    def AddSegment_(self):
        try:
            n1 = simpledialog.askstring("Input", "Enter origin node name:")
            if n1 is None:
                messagebox.showerror("Error", "Nodes must be registered or check the name.")
                return
            n2 = simpledialog.askstring("Input", "Enter destination node name:")
            if n2 is None:
                messagebox.showerror("Error", "Nodes must be registered or check the name.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid nodes.")
            return
        AddSegment(self.graph, n1, n2)
        self.clear_graph()
        Plot(self.graph, self.ax1)
        self.canvas.draw()

    def DeleteNode_(self,event):
        min_dist = (((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/self.tquocient
        selected_node = None
        for node in self.graph.nodes:
            dist = ((event.xdata - node.coords_x) ** 2 + (event.ydata - node.coords_y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                selected_node = node
        if selected_node:
            DeleteNode(self.graph, selected_node)

            self.clear_graph()
            Plot(self.graph, self.ax1)
            self.canvas.draw()

    def DeleteSegment_(self,event):
        min_dist = (((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/self.tquocient
        segment = None
        for s in self.graph.segments:
            dist=abs((s.des.coords_y - s.org.coords_y) * (event.xdata - s.org.coords_x) - (s.des.coords_x - s.org.coords_x) * (event.ydata - s.org.coords_y)) / ((s.des.coords_y - s.org.coords_y)**2 + (s.des.coords_x - s.org.coords_x)**2)**0.5
            if dist<min_dist:
                min_dist=dist
                segment = s
        if segment:
                DeleteSegmentByName(self.graph,segment.org.name,segment.des.name)

                self.clear_graph()
                Plot(self.graph, self.ax1)
                self.canvas.draw()
    
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