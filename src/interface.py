import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from airSpace import *
from navPoint import *
from navSegment import *
from navAirport import *
import os

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
        self.graph = AirSpace()
        self.cid = None
        self.nav_points_file = ''
        self.nav_segments_file = ''
        self.nav_airports_file = ''
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
            tk.Button(self.left_frame, text="Reachability", command=self.PlotReachability_).pack(pady=5)
            tk.Button(self.left_frame, text="Shortest Path", command=self.PlotShortestPath_).pack(pady=5)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
            self.text_label.destroy()
    
    # Métodos para las acciones
    def GraphLoad(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta con los archivos .txt")
        if not carpeta:
            print("No se ha seleccionado ninguna carpeta.")
        self.nav_points_file = None
        self.nav_segments_file = None
        self.nav_airports_file = None    
        for archivo in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, archivo)
            if "nav" in archivo and archivo.endswith(".txt"):
                self.nav_points_file = ruta_completa 
            elif "seg" in archivo and archivo.endswith(".txt"):
                self.nav_segments_file = ruta_completa
            elif "aer" in archivo and archivo.endswith(".txt"):
                self.nav_airports_file = ruta_completa
        # self.nav_points_file = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.nav_points_file:
            print("No se ha seleccionado ningún archivo de puntos.")
            return
        # self.nav_segments_file = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.nav_segments_file:
            print("No se ha seleccionado ningún archivo de segmentos.")
            return #tenkiu
        # self.nav_airports_file = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.nav_airports_file:
            print("No se ha seleccionado ningún archivo de aeropuertos.")
            return 
        self.main_widgets() 
        self.load = True
        self.clear_graph()
        self.graph.read_airspace(self.nav_points_file, self.nav_segments_file, self.nav_airports_file)
        self.clear_graph()
        self.graph.Plot(self.ax1)
        self.canvas.draw()
    def GraphCreate(self):
        folder_selected = filedialog.askdirectory(title="Select Folder to Save Graph")
        if not folder_selected:
            messagebox.showerror("Error", "No folder selectsed.")
            return
        file_name = simpledialog.askstring("Input", "Enter file name (without extension):")
        if not file_name:
            messagebox.showerror("Error", "No file name entered.")
            return
        self.nav_points_file = folder_selected + "/" + file_name + "_nav.txt"
        self.nav_segments_file = folder_selected + "/" + file_name + "_seg.txt"
        self.nav_airports_file = folder_selected + "/" + file_name + "_aer.txt"
        self.main_widgets()
        self.load = True
        try:
            with open(self.nav_airports_file, "w") as file:
                file.write("")
            with open(self.nav_points_file, "w") as file:
                file.write("")
            with open(self.nav_segments_file, "w") as file:
                file.write("")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create file: {e}")
            return
        messagebox.showinfo("Success", f"Graph file created at")
        self.graph.read_airspace(self.nav_points_file, self.nav_segments_file, self.nav_airports_file)
        self.clear_graph()
        self.graph.Plot(self.ax1)
        self.canvas.draw()
    def GraphSave(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta con los archivos .txt")
        if not carpeta:
            print("No se ha seleccionado ninguna carpeta.")
        self.nav_points_file = None
        self.nav_segments_file = None
        self.nav_airports_file = None    
        for archivo in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, archivo)
            if "nav" in archivo and archivo.endswith(".txt"):
                self.nav_points_file = ruta_completa 
            elif "seg" in archivo and archivo.endswith(".txt"):
                self.nav_segments_file = ruta_completa
            elif "aer" in archivo and archivo.endswith(".txt"):
                self.nav_airports_file = ruta_completa
        if not self.nav_points_file:
            self.nav_points_file = os.join(carpeta, "nav.txt")
        if not self.nav_segments_file:
            self.nav_segments_file = os.join(carpeta, "seg.txt")
        if not self.nav_airports_file:
            self.nav_airports_file = os.join(carpeta, "aer.txt")
        self.graph.save_graph([self.nav_points_file,self.nav_segments_file,self.nav_airports_file])

    def PopupSelect(self,x,y,button,event):
        self.popup_win = tk.Toplevel()
        self.popup_win.geometry(f"+{int(x)}+{int(y)}")#cambiar alto y ancho
        self.popup_win.wm_overrideredirect(True)
        if button == 1:
            neighbors = tk.Button(self.popup_win, text="Neighbors", command=lambda:[self.NodeNeighbors_(event),self.popup_win.destroy()])
            neighbors.grid(row=0, column=0,sticky="nsew")
            node = tk.Button(self.popup_win, text="Node", command=lambda:[self.AddNavPoint_(event),self.popup_win.destroy()])
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

    def NodeNeighbors_(self,event): #FUNCIONA
        if event.inaxes != self.ax1:
            return
        min_dist = float('inf')
        selected_point = None
        for point in self.graph.pts:
            dist = ((event.xdata - point.lon) ** 2 + (event.ydata - point.lat) ** 2) ** 0.5
            if dist < min_dist and dist < 1:
                min_dist = dist
                selected_point = point
        print(selected_point)
        if selected_point:
            self.clear_graph()
            self.graph.PlotNeighbors(self.ax1,selected_point.number)
            self.canvas.draw()
    def AddNavPoint_(self,event): #FUNCIONA
        try:
            code = simpledialog.askinteger("Input", "Enter point code:")
            name = simpledialog.askstring("Input", "Enter point name:")
        except ValueError:
            messagebox.showerror("Error", "Invalid entry.")
            return
        if name is None or code is None: return
        print(event.xdata,event.ydata)
        self.clear_graph()
        self.graph.AddNavPoint(NavPoint(code,str(name),event.ydata,event.xdata))
        self.graph.Plot(self.ax1)
        # self.graph.save_graph([self.nav_points_file,self.nav_segments_file,self.nav_airports_file]) #Para guardado automatico
        self.canvas.draw()
    def AddSegment_(self): #FUNCIONA
        try:
            c1 = simpledialog.askinteger("Input", "Enter origin point code:")
            if c1 is None:
                messagebox.showerror("Error", "Point must be registered or check the name.")
                return
            c2 = simpledialog.askinteger("Input", "Enter destination point code:")
            if c2 is None:
                messagebox.showerror("Error", "Nodes must be registered or check the name.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid nodes.")
            return
        if c1 == None or c2 == None: return
        self.clear_graph()
        self.graph.AddNavSegment(c1, c2)
        self.graph.Plot(self.ax1)
        self.canvas.draw()
    def DeleteNode_(self,event): #FUNCIONA
        min_dist = (((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/self.tquocient
        selected_point = None
        for point in self.graph.pts:
            dist = ((event.xdata - point.lon) ** 2 + (event.ydata - point.lat) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                selected_point = point
        if selected_point:
            self.graph.DeleteNavPoint(selected_point)

            self.clear_graph()
            self.graph.Plot(self.ax1)
            self.canvas.draw()
    def DeleteSegment_(self,event):#HAY QUE CAMBIARLO HAY VARIOS SEGMENTOS CON LA MISMA DIRECCION Y PUNTO DE INICIO
        min_dist = (((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/self.tquocient
        segment = []
        for s in self.graph.seg:
            for p in self.graph.pts:
                if p.number == s.org:
                    org = p
                elif p.number == s.des:
                    des = p
            dist=abs((des.lat - org.lat) * (event.xdata - org.lon) - (des.lon - org.lon) * (event.ydata - org.lat)) / ((des.lat - org.lat)**2 + (des.lon - org.lon)**2)**0.5
            if dist<min_dist:
                min_dist=dist
                segment.append(s)
        print(segment)
        if segment[0]:
                self.clear_graph()
                self.graph.seg.remove(segment[0])
                print(self.graph.seg)
                if segment[1].org == segment[0].des and segment[1].des == segment[0].org:
                    self.graph.seg.remove(segment[1])
                # self.DeleteSegmentByName(segment.org,segment.des)
                self.graph.Plot(self.ax1)
                self.canvas.draw()
 
    def on_click(self,event):
        if self.popup_win != None:
            self.popup_win.destroy()
        if event.xdata != None or event.ydata != None:
            x = self.canvas.get_tk_widget().winfo_rootx()+event.x
            y = self.canvas.get_tk_widget().winfo_rooty()+self.canvas.get_tk_widget().winfo_height()-event.y
        self.PopupSelect(x,y,event.button,event)

    def PlotReachability_(self): #FUNCIONA
        try:
            point = simpledialog.askstring("Input", "Enter origin name:")
            if point is None:
                messagebox.showerror("Error", "Point must be registered or check the code.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid point.")
            return
        self.clear_graph()
        self.graph.PlotReachability(self.ax1, point)
        self.canvas.draw()

    def PlotShortestPath_(self): #FUNCIONA
        try:
            origin = simpledialog.askstring("Input", "Enter origin name:")
            if origin is None:
                messagebox.showerror("Error", "Point must be registered or check the code.")
                return
            destination = simpledialog.askstring("Input", "Enter destination name:")
            if destination is None:
                messagebox.showerror("Error", "Point must be registered or check the code.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid points.")
            return
        self.clear_graph()
        path=self.graph.FindShortestPath(origin, destination)
        self.graph.PlotPath(self.ax1, path)
        self.canvas.draw()

    #Version 4 ideas: Añadir 3 stage switch con el que se muestre el code, name o code y name, encima de cada punto

root = tk.Tk()
app = GraphVisualizer(root)
root.mainloop()