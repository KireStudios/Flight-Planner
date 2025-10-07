import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from airSpace import *
from navPoint import *
from navSegment import *
from navAirport import *
import os
import webbrowser
import pygame
import random

def pulsate_warning(widget, iterations=4, pulse_speed=25):
    style = widget.cget('style') or 'Header.TLabel'
    temp_style = style + ".Warning"
    s = ttk.Style()
    original_fg = s.lookup(style, 'foreground') or "#000000"
    # Ensure the temp style has the same layout as the base style
    try:
        s.layout(temp_style)
    except tk.TclError:
        s.layout(temp_style, s.layout(style))
        s.configure(temp_style, **s.configure(style))
    step = [0]
    count = [0]

    def pulse_step():
        intensity = ((step[0] % 100) / 100)
        # Red color with varying intensity
        red = 255
        green = max(0, min(255, int(255 * (1 - intensity * 0.8))))
        blue = max(0, min(255, int(255 * (1 - intensity * 0.8))))
        color = f"#{red:02x}{green:02x}{blue:02x}"
        s.configure(temp_style, foreground=color)
        widget.configure(style=temp_style)
        if step[0] % 100 == 0:
            count[0] += 1
        if count[0] >= iterations:
            s.configure(temp_style, foreground=original_fg)
            widget.configure(style=style)
        else:
            step[0] += 5
            widget.after(pulse_speed, pulse_step)
    pulse_step()

def show_animated_intro(root):
        splash = tk.Toplevel()
        splash.overrideredirect(True)
        splash.wm_attributes("-topmost", True)
        w, h = 400, 400
        sw = splash.winfo_screenwidth()
        sh = splash.winfo_screenheight()
        x = (sw // 2)
        y = (sh // 2)
        splash.geometry(f"{w}x{h}+{x}+{y}")
        splash.configure(bg="#3A506B")

        canvas = tk.Canvas(splash, width=200, height=200, bg="#3A506B", highlightthickness=0)
        canvas.place(relx=0.5, rely=0.5, anchor="center")

        # Draw a spinning airplane emoji
        airplane = canvas.create_text(100, 100, text="✈️", font=("Segoe UI Emoji", 64), fill="#F6EAC2", tags="plane")

        # Title
        label = tk.Label(splash, text="Flight Planner", font=("Segoe UI", 20, "bold"), fg="#F6EAC2", bg="#3A506B")
        label.place(relx=0.5, rely=0.15, anchor="center")

        # Simple animation: rotate emoji
        angle = [0]
        def animate():
            angle[0] = (angle[0] + 15) % 360
            canvas.delete("plane")
            offset_x = 40 * (1 if (angle[0] // 90) % 2 == 0 else -1)
            offset_y = 40 * (1 if (angle[0] // 180) == 0 else -1)
            canvas.create_text(100 + offset_x, 100 + offset_y, text="✈️", font=("Segoe UI Emoji", 64), fill="#F6EAC2", tags="plane")
            splash.after(10, animate)

        root.withdraw()
        splash.after(100, animate)
        # Auto-close after 4 seconds in case animation is interrupted
        splash.after(4000, lambda: (splash.destroy(), root.deiconify()))

class GraphVisualizer:
    def __init__(self, root):
        show_animated_intro(root)

        self.root = root
        self.root.title("Flight Planner")
        self.root.geometry("1280x720")
        self.graph = AirSpace()
        self.cid = None
        self.nav_points_file = ''
        self.nav_segments_file = ''
        self.nav_airports_file = ''
        self.popup_win = None
        self.tquocient = 100
        self.load = False
        self.graph_title = "Graph Visualization"
        self.cycle_count = 0
        self.selected_point = None
        self.info_widgets = {}
        self.route_origin = None
        self.route_selecting = False
        self.current_route_path = None

        # Set ttk theme and theme palette
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.theme_palette = {
            "default": "#DDDDDD",
            "light": "#F8F8F8",
            "dark": "#222831",
            "sunny day": "#F6EAC2",
            "marine blue": "#3A506B",
            "rose mist": "#D7A7C1",
            "mint green": "#A7C7A3",
            "sunset orange": "#E6B07A",
            "lemon cream": "#F3E9B0",
            "purple dream": "#B07AD7"
        }
        self.theme_names = [ "Default", "Light", "Dark", "Sunny Day", "Marine Blue", "Rose Mist", "Mint Green", "Sunset Orange", "Lemon Cream", "Purple Dream" ]
        self.selected_theme = tk.StringVar(value=self.theme_names[0])

        # Configure styles for all widgets
        self.style.configure('TButton', font=('Segoe UI', 11), padding=8)
        self.style.configure('TLabel', font=('Segoe UI', 12))
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
        self.style.configure('Custom.TFrame', background="#DDDDDD")
        self.style.configure('Custom.TLabel', background="#DDDDDD")

        # --- Music tracks ---
        self.music_tracks = [
            ("White Palace", "resources/White_Palace.mp3"),
            ("Sweden - C418", "resources/Sweden_C418.mp3"),
            ("The Night King", "resources/The_Night_King.mp3"),
        ]
        random_track = random.choice(self.music_tracks)
        self.selected_music = tk.StringVar(value=random_track[0])
        pygame.mixer.init()
        pygame.mixer.music.load(random_track[1])
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        self.create_layout()
        # --- Apply default theme at startup ---
        self.apply_theme("Default")

        # --- Autoload CAT airspace at startup ---
        self.quick_load_airspace("CAT")

    def create_layout(self):
        """ Create the main interface structure with modern look """
        # Top header
        self.header_frame = ttk.Frame(self.root, padding=(10, 10), style="Custom.TFrame")
        self.header_frame.pack(side="top", fill="x")
        ttk.Label(self.header_frame, text="Flight Planner", style='Header.TLabel').pack(side="left")

        # Main content frames
        self.left_frame = ttk.Frame(self.root, padding=(10, 10), style="Custom.TFrame")
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = ttk.Frame(self.root, padding=(10, 10), style="Custom.TFrame")
        self.right_frame.pack(side="right", fill="y")

        # Center panel: use a Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side="left", expand=True, fill="both")

        self.center_frame = ttk.Frame(self.notebook, padding=(10, 10), style="Custom.TFrame")
        self.notebook.add(self.center_frame, text="Graph")

        # Route planner tab (created when needed)
        self.route_frame = None

        # Settings tab (created when needed)
        self.settings_frame = None

        self.initial_widgets()

    def initial_widgets(self):
        """ Add buttons and graph area with modern style """

        # Left panel buttons
        ttk.Button(self.left_frame, text="File...", command=self.PopupFile).pack(pady=10, fill="x")

        # --- Airspace Data Quick Load Button ---
        ttk.Button(self.left_frame, text="Airspace Data...", command=self.PopupAirspaceData).pack(pady=2, fill="x")

        self.save_btn = ttk.Button(self.left_frame, text="Save Graph", command=self.GraphSaveDirect)
        self.export_btn = ttk.Button(self.left_frame, text="Export to Google Earth", command=self.export_to_google_earth)
        
        # Add About button at the bottom left
        ttk.Button(self.left_frame, text="About", command=self.open_about).pack(side="bottom", pady=10, fill="x")

        # Do not pack save_btn, export_btn, or reset_btn yet

        # Right panel buttons
        ttk.Button(self.right_frame, text="Exit", command=self.root.quit).pack(pady=10, fill="x")
        self.reset_btn = ttk.Button(self.right_frame, text="Reset Graph", command=self.reset_graph)
        ttk.Button(self.right_frame, text="Settings", command = self.open_settings).pack(pady=10, fill="x")
        # Info panel: create but do not pack yet
        self.info_panel = ttk.Frame(self.right_frame, padding=(10, 10), relief="groove", borderwidth=2)
        self.selector_frame = ttk.Frame(self.info_panel)
        ttk.Label(self.selector_frame, text="🔍 Search or select node:", font=('Segoe UI', 11, 'bold')).pack(anchor="w", padx=2)
        self.node_selector_var = tk.StringVar()
        self.node_selector = ttk.Combobox(
            self.selector_frame,
            textvariable=self.node_selector_var,
            state="normal",
            postcommand=self.update_node_selector_values
        )
        self.node_selector.pack(fill="x", padx=2, pady=(2, 0))
        self.node_selector.bind("<<ComboboxSelected>>", self.on_node_selector_change)
        self.node_selector.bind("<Return>", self.on_node_selector_change)
        self.node_selector.bind('<KeyRelease>', self.on_node_selector_keyrelease)
        self.node_selector.bind('<FocusIn>', lambda e: self.update_node_selector_values())
        # Do not pack selector_frame or info_panel yet

        # Center panel: Matplotlib graph and label
        self.fig, self.ax1 = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.center_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        self.text_label = ttk.Label(self.center_frame, text="Create or Load a Graph", style='Header.TLabel', anchor="center")
        self.text_label.pack(expand=True, fill="both", padx=10, pady=10)
        self.cycle_count = 0
        self.cid_start = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.graph_loaded = False
    
    def main_widgets(self):
        # Hide buttons first to avoid duplicates
        self.save_btn.pack_forget()
        self.export_btn.pack_forget()
        self.reset_btn.pack_forget()
        self.info_panel.pack_forget()
        self.selector_frame.pack_forget()

        # Always destroy the text label if it exists
        if hasattr(self, "text_label") and self.text_label.winfo_exists():
            self.text_label.destroy()

        if not self.load:
            self.canvas.mpl_disconnect(self.cid_start)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        # Show Save, Export, and Reset buttons and info panel
        self.save_btn.pack(pady=10, fill="x")
        self.export_btn.pack(pady=10, fill="x")
        self.reset_btn.pack(pady=10, fill="x")
        self.info_panel.pack(fill="both", expand=True, pady=(10, 0))
        self.selector_frame.pack(fill="x", pady=(0, 10))
        self.graph_loaded = True

    def PopupFile(self):
        file_win = tk.Toplevel()
        file_win.geometry(f"+{self.left_frame.winfo_rootx()+80}+{self.left_frame.winfo_rooty()+80}")
        file_win.wm_overrideredirect(True)
        file_win.configure(bg=self.theme_palette.get(self.selected_theme.get().lower(), "#DDDDDD"))
        ttk.Label(file_win, text="File:").grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 5))
        ttk.Button(file_win, text="Load Graph", command=lambda: [self.GraphLoad(), file_win.destroy()]).grid(row=1, column=0, sticky="nsew")
        ttk.Button(file_win, text="Create Graph", command=lambda: [self.GraphCreate(), file_win.destroy()]).grid(row=1, column=1, sticky="nsew")
        save_as_btn = ttk.Button(file_win, text="Save Graph As...", command=lambda: [self.GraphSaveAs(), file_win.destroy()])
        save_as_btn.grid(row=2, column=0, columnspan=2, sticky="nsew")
        if not self.graph_loaded:
            save_as_btn.state(['disabled'])
        ttk.Button(file_win, text="Cancel", command=file_win.destroy).grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(5, 0))

    def clear_graph(self):
        self.ax1.clear()
        self.ax1.set_title(self.graph_title)
        self.ax1.grid(True)
        # Clear any special plot tracking so export only exports what is currently shown
        self.last_special_plot = None
        print(self.last_special_plot)

    def PopupSelect(self, x, y, button, event):
        self.popup_win = tk.Toplevel()
        self.popup_win.geometry(f"+{int(x)}+{int(y)}")
        self.popup_win.wm_overrideredirect(True)
        if button == 1:
            # First row: Select and Start Route
            ttk.Button(self.popup_win, text="Select", command=lambda: [self.SelectNode_(event), self.popup_win.destroy()]).grid(row=0, column=0, sticky="nsew")
            ttk.Button(self.popup_win, text="Start Route from Point", command=lambda: [self.StartRouteFromPoint(event), self.popup_win.destroy()]).grid(row=0, column=1, sticky="nsew")
            # Second row: Neighbors and Reachability
            ttk.Button(self.popup_win, text="Neighbors", command=lambda: [self.NodeNeighbors_(event), self.popup_win.destroy()]).grid(row=1, column=0, sticky="nsew")
            ttk.Button(self.popup_win, text="Reachability", command=lambda: [self.PlotReachabilityNode_(event), self.popup_win.destroy()]).grid(row=1, column=1, sticky="nsew")
            # Third row: Add and Delete
            ttk.Button(self.popup_win, text="Add...", command=lambda: [self.popup_win.destroy(), self.PopupAdd(x, y, event)]).grid(row=2, column=0, sticky="nsew")
            ttk.Button(self.popup_win, text="Delete...", command=lambda: [self.popup_win.destroy(), self.PopupDelete(x, y, event)]).grid(row=2, column=1, sticky="nsew")
            # Cancel button
            ttk.Button(self.popup_win, text="Cancel", command=self.popup_win.destroy).grid(row=3, column=0, columnspan=2, sticky="nsew")
        elif button == 3:
            ttk.Button(self.popup_win, text="Cancel", command=self.popup_win.destroy).grid(row=0, column=0, columnspan=2, sticky="nsew")

    def PopupAdd(self, x, y, event):
        add_win = tk.Toplevel()
        add_win.geometry(f"+{int(x)+40}+{int(y)+40}")
        add_win.wm_overrideredirect(True)
        add_win.configure(bg=self.theme_palette.get(self.selected_theme.get().lower(), "#DDDDDD"))
        ttk.Label(add_win, text="Add:").grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 5))
        ttk.Button(add_win, text="NavPoint (Node)", command=lambda: [self.AddNavPoint_(event), add_win.destroy()]).grid(row=1, column=0, sticky="nsew")
        ttk.Button(add_win, text="NavSegment", command=lambda: [self.AddSegment_(), add_win.destroy()]).grid(row=1, column=1, sticky="nsew")
        ttk.Button(add_win, text="Cancel", command=add_win.destroy).grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(5, 0))

    def PopupAirspaceData(self):
        airspace_win = tk.Toplevel()
        airspace_win.configure(bg=self.theme_palette.get(self.selected_theme.get().lower(), "#DDDDDD"))
        airspace_win.geometry(f"+{self.left_frame.winfo_rootx()+80}+{self.left_frame.winfo_rooty()+140}")
        airspace_win.wm_overrideredirect(True)
        ttk.Label(airspace_win, text="Quick Load Airspace:").grid(row=0, column=0, columnspan=3, sticky="nsew", pady=(0, 5))
        ttk.Button(airspace_win, text="CAT", command=lambda: [self.quick_load_airspace("CAT"), airspace_win.destroy()]).grid(row=1, column=0, sticky="nsew", padx=2)
        ttk.Button(airspace_win, text="SPAIN", command=lambda: [self.quick_load_airspace("SPAIN"), airspace_win.destroy()]).grid(row=1, column=1, sticky="nsew", padx=2)
        ttk.Button(airspace_win, text="ECAC", command=lambda: [self.quick_load_airspace("ECAC"), airspace_win.destroy()]).grid(row=1, column=2, sticky="nsew", padx=2)
        ttk.Button(airspace_win, text="Cancel", command=airspace_win.destroy).grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(5, 0))

    def loading(self, message="Loading...", parent=None):
        """Show a spinning progress bar and a random fun fact. Returns the window to be destroyed after loading."""
        facts = [
          "✈️ The Wright brothers invented and flew the first airplane in 1903.",
          "🛫 The busiest airport in the world is Hartsfield–Jackson Atlanta International Airport.",
          "🌍 There are over 40,000 airports in the world.",
          "🛰️ The first commercial jet was the de Havilland Comet.",
          "🚁 Helicopters can take off and land vertically!",
          "🛩️ The longest non-stop commercial flight is over 18 hours.",
          "🌦️ Pilots use the NATO phonetic alphabet for clear communication.",
          "🦅 Birds inspired the design of early airplanes.",
          "🌙 Some airports have runways lit up like a rainbow at night.",
          "🧭 The autopilot was invented in 1912!",
          "✈️ The Concorde could fly from New York to London in under 3 hours. Speedy... and loud.",
          "🛫 The average commercial airplane takes off at around 180 mph—because crawling into the sky wouldn’t be dramatic enough.",
          "🌍 At any given moment, there are about 9,700 planes in the sky. Think of it as sky traffic—without the horns.",
          "🛰️ GPS signals used in aviation come from satellites 12,550 miles away. And you still miss the turn.",
          "🚁 Helicopters don’t actually fly—they just beat the air into submission.",
          "🛩️ The Boeing 747 has over 6 million parts. No pressure.",
          "🌦️ Pilots train for lightning strikes. Planes can survive them. Your Wi-Fi, however, cannot.",
          "🦅 Birds inspired airplanes, but ironically, bird strikes are now a thing. Thanks, nature.",
          "🌙 Some airport runways use color-coded lights to prevent collisions. Like a disco—if the disco could kill you.",
          "🧭 Autopilot: invented in 1912 so pilots could stop pretending to enjoy flying straight for 6 hours.",
          "✈️ The wings of a Boeing 777 flex up to 26 feet during flight. Just like your sanity on long-haul trips.",
          "🛫 Air traffic controllers guide over 100,000 flights per day. Yes, your delay was still 'unexpected.'",
          "🌍 The shortest commercial flight is 1.7 miles long. It takes longer to fasten your seatbelt.",
          "🛰️ Inmarsat satellites help planes stay connected mid-flight. For when you simply *must* send that meme at 38,000 feet.",
          "🚁 The word 'helicopter' comes from Greek: 'helix' (spiral) and 'pteron' (wing). Nothing says 'safe' like ancient etymology.",
          "🛩️ Pilots have to sleep too. That’s why long flights have 'resting' pilots and 'pretending to rest' copilots.",
          "🌦️ Wind shear is a sudden change in wind speed or direction. Mother Nature’s way of keeping pilots humble.",
          "🦅 The FAA requires reporting bird strikes. Somewhere, there’s paperwork filed on a seagull named Kevin.",
          "🌙 Some runways use embedded LEDs for low-visibility landings. Like landing on a very expensive Lite-Brite.",
          "🧭 Some planes have backup magnetic compasses... just in case all the 21st-century tech decides to quit.",
          "✈️ Commercial jets cruise at around 35,000 feet—because flying any higher might bruise the egos of astronauts.",
          "🛫 The word 'Mayday' comes from the French 'm'aidez'—meaning 'help me.' Aviation: multilingual panic since 1910.",
          "🌍 The ICAO airport code for Reykjavik is BIRK. Ironically, it's rarely sunny enough for actual birds.",
          "🛰️ ADS-B allows planes to constantly broadcast their position. Like a flying stalker with a radio.",
          "🚁 Tiltrotor aircraft combine the features of helicopters and airplanes. Because one kind of danger wasn’t enough.",
          "🛩️ Some planes land with reverse thrust and spoilers—aviation’s version of slamming the brakes and opening the car doors.",
          "🌦️ Clouds have classifications. Stratus, cumulus, and the one that ruined your vacation.",
          "🦅 A flock of geese once forced a jet to land in the Hudson River. Goose 1, Jet 0.",
          "🌙 The longest paved runway is over 18,000 feet. Yes, it’s for planes. No, you can't drag race on it.",
          "🧭 In the cockpit, clocks are set to UTC—so pilots can argue about time zones in a globally consistent way."
        ]

        fact = random.choice(facts)
        win = tk.Toplevel(parent or self.root)
        win.title("Loading...")

        # --- Center the window on the screen ---
        w, h = 360, 140
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw // 2)
        y = (sh // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.resizable(False, False)
        win.grab_set()

        # --- Use theme color ---
        color = self.theme_palette.get(self.selected_theme.get().lower(), "#DDDDDD")
        fg = "#222" if self.selected_theme.get().lower() in ["default", "light", "sunny day", "lemon cream", "rose mist"] else "#fff"
        style = ttk.Style(win)
        style.configure("Loading.TFrame", background=color)
        style.configure("Loading.TLabel", background=color, foreground=fg, font=('Segoe UI', 12, 'bold'))
        style.configure("Loading.Fact.TLabel", background=color, foreground=fg, font=('Segoe UI', 10, 'italic'))
        style.configure("Loading.TProgressbar", background="#4A90E2", troughcolor=color)

        frame = ttk.Frame(win, style="Loading.TFrame", padding=(10, 10))
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text=message, style="Loading.TLabel", anchor="center").pack(pady=(4, 2), fill="x")
        ttk.Label(frame, text=fact, style="Loading.Fact.TLabel", wraplength=320, anchor="center", justify="center").pack(pady=(0, 8), fill="x")

        win.update()
        return win

    def quick_load_airspace(self, airspace_name):
        progress_win = self.loading(f"Loading {airspace_name} airspace...")
        self.graph_title = airspace_name + " Airspace"
        # Define the file paths for each airspace set
        base_dir = os.path.join("data", "AirSpaces")
        paths = {
            "CAT": {
                "nav": os.path.join(base_dir, "Catalonia_data/CAT_nav.txt"),
                "seg": os.path.join(base_dir, "Catalonia_data/CAT_seg.txt"),
                "aer": os.path.join(base_dir, "Catalonia_data/CAT_aer.txt"),
            },
            "SPAIN": {
                "nav": os.path.join(base_dir, "Spain_data/SPAIN_nav.txt"),
                "seg": os.path.join(base_dir, "Spain_data/SPAIN_seg.txt"),
                "aer": os.path.join(base_dir, "Spain_data/SPAIN_aer.txt"),
            },
            "ECAC": {
                "nav": os.path.join(base_dir, "ECAC_data/ECAC_nav.txt"),
                "seg": os.path.join(base_dir, "ECAC_data/ECAC_seg.txt"),
                "aer": os.path.join(base_dir, "ECAC_data/ECAC_aer.txt"),
            }
        }
        files = paths.get(airspace_name)
        if not files or not all(os.path.exists(f) for f in files.values()):
            messagebox.showerror("Error", f"Files for {airspace_name} not found in {base_dir}.")
            progress_win.destroy()
            return
        self.nav_points_file = files["nav"]
        self.nav_segments_file = files["seg"]
        self.nav_airports_file = files["aer"]
        self.main_widgets()
        self.load = True
        self.clear_graph()
        self.graph.read_airspace(self.nav_points_file, self.nav_segments_file, self.nav_airports_file)
        self.clear_graph()
        self.graph.Plot(self.ax1)
        self.canvas.draw()
        progress_win.destroy()
        
    # Métodos para las acciones
    def GraphLoad(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta con los archivos .txt", initialdir="data/AirSpaces")
        if not carpeta:
            print("No se ha seleccionado ninguna carpeta.")
            return
        progress_win = self.loading("Loading graph data...")
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
        self.graph_title = os.path.basename(self.nav_points_file).split("_")[0] + " Airspace"
        # self.nav_points_file = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.nav_points_file:
            print("No se ha seleccionado ningún archivo de puntos.")
            progress_win.destroy()
            return
        # self.nav_segments_file = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.nav_segments_file:
            print("No se ha seleccionado ningún archivo de segmentos.")
            progress_win.destroy()
            return #tenkiu
        # self.nav_airports_file = filedialog.askopenfilename(title="Select Graph Data File", filetypes=[("Text Files", "*.txt")])
        if not self.nav_airports_file:
            print("No se ha seleccionado ningún archivo de aeropuertos.")
            progress_win.destroy()
            return 
        self.main_widgets() 
        self.load = True
        self.clear_graph()
        try:
            self.graph.read_airspace(self.nav_points_file, self.nav_segments_file, self.nav_airports_file)
        except ValueError as e:
            messagebox.showerror("Error", f"{e}")
            progress_win.destroy()
            return
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"{e}")
        self.clear_graph()
        self.graph.Plot(self.ax1)
        self.canvas.draw()
        progress_win.destroy()

    def GraphCreate(self):
        folder_selected = filedialog.askdirectory(title="Select Folder to Save Graph")
        if not folder_selected:
            messagebox.showerror("Error", "No folder selected.")
            return
        file_name = simpledialog.askstring("Input", "Enter file name (without extension):")
        if not file_name:
            messagebox.showerror("Error", "No file name entered.")
            return
        progress_win = self.loading("Creating new graph...")
        self.nav_points_file = os.path.join(folder_selected, file_name + "_nav.txt")
        self.nav_segments_file = os.path.join(folder_selected, file_name + "_seg.txt")
        self.nav_airports_file = os.path.join(folder_selected, file_name + "_aer.txt")
        try:
            with open(self.nav_airports_file, "w") as file:
                file.write("")
            with open(self.nav_points_file, "w") as file:
                file.write("")
            with open(self.nav_segments_file, "w") as file:
                file.write("")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create file: {e}")
            progress_win.destroy()
            return
        self.graph_title = os.path.basename(self.nav_points_file).split("_")[0] + " Airspace"
        self.graph = AirSpace()  # Reset to a new, empty graph
        # --- Insta-save the empty graph ---
        self.graph.save_graph([self.nav_points_file, self.nav_segments_file, self.nav_airports_file])
        self.graph_loaded = True
        self.load = True
        self.main_widgets()
        self.clear_graph()
        self.graph.read_airspace(self.nav_points_file, self.nav_segments_file, self.nav_airports_file)
        self.graph.Plot(self.ax1)
        self.canvas.draw()
        progress_win.destroy()

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
            # Only outgoing neighbors (as displayed)
            neighbors = [p for p in self.graph.pts if any(
                s.org == selected_point.number and s.des == p.number
                for s in self.graph.seg
            )]
            self.last_special_plot = {
                'type': 'neighbors',
                'points': [selected_point] + neighbors,
                'segments': [(selected_point, n) for n in neighbors]
            }

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
            c1 = simpledialog.askstring("Input", "Enter origin point name:")
            if c1 is None:
                messagebox.showerror("Error", "Point must be registered or check the name.")
                return
            c2 = simpledialog.askstring("Input", "Enter destination point name:")
            if c2 is None:
                messagebox.showerror("Error", "Point must be registered or check the name.")
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
    def DeleteSegment_(self,event):#Ya esta canviado: HAY QUE CAMBIARLO HAY VARIOS SEGMENTOS CON LA MISMA DIRECCION Y PUNTO DE INICIO
        min_dist = float('inf')#(((self.ax1.get_xlim()[1]-self.ax1.get_xlim()[0])**2+(self.ax1.get_ylim()[1]-self.ax1.get_ylim()[0])**2)**0.5)/self.tquocient
        segment = []
        for s in self.graph.seg:
            for p in self.graph.pts:
                if p.number == s.org:
                    org = p
                elif p.number == s.des:
                    des = p
            # miramos distancia al punto de inicio y final ya que si no es la prolongacion de la linea y no funciona
            dist= ((event.xdata - org.lon) ** 2 + (event.ydata - org.lat) ** 2) ** 0.5 + ((event.xdata - des.lon) ** 2 + (event.ydata - des.lat) ** 2) ** 0.5
            # abs((des.lat - org.lat) * (event.xdata - org.lon) - (des.lon - org.lon) * (event.ydata - org.lat)) / ((des.lat - org.lat)**2 + (des.lon - org.lon)**2)**0.5
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

    def start_route_from_info(self, point):
        self.open_route_planner(point)

    def StartRouteFromPoint(self, event):
        # Find nearest node as origin
        min_dist = float('inf')
        origin = None
        for point in self.graph.pts:
            dist = ((event.xdata - point.lon) ** 2 + (event.ydata - point.lat) ** 2) ** 0.5
            if dist < min_dist and dist < 1:
                min_dist = dist
                origin = point
        if origin:
            self.open_route_planner(origin)
        else:
            messagebox.showerror("Error", "No node found at click location.")
 
    def on_click(self,event):
        if not getattr(self, 'graph_loaded', False):
            pulsate_warning(self.text_label)
            self.PopupFile()
            return
        if self.popup_win is not None:
            self.popup_win.destroy()
        if self.route_selecting:
            # User is selecting destination for route
            min_dist = float('inf')
            dest = None
            for point in self.graph.pts:
                dist = ((event.xdata - point.lon) ** 2 + (event.ydata - point.lat) ** 2) ** 0.5
                if dist < min_dist and dist < 1:
                    min_dist = dist
                    dest = point
            if dest and self.route_origin:
                self.clear_graph()
                path = self.graph.FindShortestPath(self.route_origin.name, dest.name)
                self.graph.PlotPath(self.ax1, path)
                self.canvas.draw()
                messagebox.showinfo("Route", f"Route from '{self.route_origin.name}' to '{dest.name}' shown.")
                self.route_origin = None
                self.route_selecting = False
            else:
                messagebox.showerror("Error", "No node found at click location.")
                self.route_origin = None
                self.route_selecting = False
            return
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

    def PlotReachabilityNode_(self, event):
        # Find nearest node to the click
        min_dist = float('inf')
        selected_point = None
        for point in self.graph.pts:
            dist = ((event.xdata - point.lon) ** 2 + (event.ydata - point.lat) ** 2) ** 0.5
            if dist < min_dist and dist < 1:
                min_dist = dist
                selected_point = point
        if selected_point:
            self.clear_graph()
            self.graph.PlotReachability(self.ax1, selected_point.name)
            self.canvas.draw()
            # Track for export: points and segments between reachable nodes
            reachable = self.graph.Reachability(selected_point.name)
            all_points = [selected_point] + reachable
            point_numbers = set(p.number for p in all_points)
            segments = [
                (org, des)
                for s in self.graph.seg
                for org in all_points
                for des in all_points
                if s.org == org.number and s.des == des.number
            ]
            self.last_special_plot = {
                'type': 'reachability',
                'points': all_points,
                'segments': segments
            }
        else:
            messagebox.showerror("Error", "No node found at click location.")

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
        path = self.graph.FindShortestPath(origin, destination)
        self.graph.PlotPath(self.ax1, path)
        self.canvas.draw()
        self.current_route_path = path  # <-- Store the route path

    def GraphSaveDirect(self):
        # Save directly to the currently loaded/created files
        if self.nav_points_file and self.nav_segments_file and self.nav_airports_file:
            self.graph.save_graph([self.nav_points_file, self.nav_segments_file, self.nav_airports_file])
            messagebox.showinfo("Saved", "Graph saved successfully.")
        else:
            messagebox.showerror("Error", "No graph file loaded or created.")

    def GraphSaveAs(self):
        # Ask for new folder and base name, then save as new files
        folder_selected = filedialog.askdirectory(title="Select Folder to Save Graph As")
        if not folder_selected:
            return
        file_name = simpledialog.askstring("Input", "Enter new file name (without extension):")
        if not file_name:
            return
        nav_points_file = os.path.join(folder_selected, file_name + "_nav.txt")
        nav_segments_file = os.path.join(folder_selected, file_name + "_seg.txt")
        nav_airports_file = os.path.join(folder_selected, file_name + "_aer.txt")
        self.graph.save_graph([nav_points_file, nav_segments_file, nav_airports_file])
        messagebox.showinfo("Saved", f"Graph saved as {file_name} in {folder_selected}")

    def SelectNode_(self, event):
        # Find nearest node
        min_dist = float('inf')
        selected_point = None
        for point in self.graph.pts:
            dist = ((event.xdata - point.lon) ** 2 + (event.ydata - point.lat) ** 2) ** 0.5
            if dist < min_dist and dist < 1:
                min_dist = dist
                selected_point = point
        if selected_point:
            self.selected_point = selected_point
            # Set the selector to the selected node and update info panel
            node_str = f"{selected_point.name} (#{selected_point.number})"
            self.node_selector_var.set(node_str)
            self.update_info_panel(selected_point)

    def on_node_selector_change(self, event=None):
        selected = self.node_selector_var.get()
        self.show_node_info_from_selector(selected)

    def on_node_selector_keyrelease(self, event):
        typed = self.node_selector_var.get().lower()
        all_values = [f"{p.name} (#{p.number})" for p in self.graph.pts]
        all_values += [f"{a.name} [AP]" for a in self.graph.aip]
        filtered = [v for v in all_values if typed in v.lower()]
        self.node_selector['values'] = filtered

        if event.keysym in ("Down", "Up"):
            # Force dropdown to close and reopen to refresh the list
            if self.node_selector.winfo_ismapped():
                self.node_selector.event_generate('<Escape>')  # Close dropdown if open
                self.node_selector.after(1, lambda: self.node_selector.event_generate('<Button-1>'))  # Reopen
        elif event.keysym == "Return":
            if len(filtered) == 1:
                self.node_selector_var.set(filtered[0])
                self.show_node_info_from_selector(filtered[0])
            elif len(filtered) > 1:
                # Force dropdown to close and reopen to refresh the list
                if self.node_selector.winfo_ismapped():
                    self.node_selector.event_generate('<Escape>')  # Close dropdown if open
                    self.node_selector.after(1, lambda: self.node_selector.event_generate('<Button-1>'))  # Reopen

    def update_node_selector_values(self):
        # Include both points and airports in the selector
        typed = self.node_selector_var.get().strip().lower()
        values = [f"{p.name} (#{p.number})" for p in self.graph.pts]
        values += [f"{a.name} [AP]" for a in self.graph.aip]
        if not typed:
            self.node_selector['values'] = values
        else:
            filtered = [v for v in values if typed in v.lower()]
            self.node_selector['values'] = filtered

    def show_node_info_from_selector(self, selected):
        # Check if it's an airport
        if "[AP]" in selected:
            name = selected.split(" [AP]")[0]
            for a in self.graph.aip:
                if a.name == name:
                    self.selected_point = a
                    self.update_info_panel(a)
                    break
        elif "(" in selected and "#" in selected:
            try:
                code = int(selected.split("#")[-1].split(")")[0])
                for point in self.graph.pts:
                    if point.number == code:
                        self.selected_point = point
                        self.update_info_panel(point)
                        break
            except Exception:
                pass

    def update_info_panel(self, point):
        # Remove previous info_frame if it exists
        if hasattr(self, 'info_frame') and self.info_frame.winfo_exists():
            self.info_frame.destroy()
        # Node info section
        self.info_frame = ttk.Frame(self.info_panel)
        self.info_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(self.info_frame, text="Node Details", style='Header.TLabel').pack(pady=(0, 10))
        ttk.Label(self.info_frame, text="Name:").pack(anchor="w")
        name_var = tk.StringVar(value=point.name)
        name_entry = ttk.Entry(self.info_frame, textvariable=name_var)
        name_entry.pack(fill="x")

        # Only show lat/lon for NavPoint, not for Airport
        if hasattr(point, "lat") and hasattr(point, "lon"):
            ttk.Label(self.info_frame, text="Latitude:").pack(anchor="w")
            lat_var = tk.DoubleVar(value=point.lat)
            lat_entry = ttk.Entry(self.info_frame, textvariable=lat_var)
            lat_entry.pack(fill="x")
            ttk.Label(self.info_frame, text="Longitude:").pack(anchor="w")
            lon_var = tk.DoubleVar(value=point.lon)
            lon_entry = ttk.Entry(self.info_frame, textvariable=lon_var)
            lon_entry.pack(fill="x")
        else:
            lat_var = None
            lon_var = None

        def save_changes():
            point.name = name_var.get()
            if lat_var is not None and lon_var is not None:
                try:
                    point.lat = float(lat_var.get())
                    point.lon = float(lon_var.get())
                except ValueError:
                    messagebox.showerror("Error", "Latitude and Longitude must be numbers.")
                    return
            self.clear_graph()
            self.graph.Plot(self.ax1)
            self.canvas.draw()
            messagebox.showinfo("Saved", "Node info updated.")
            self.update_node_selector_values()  # Only here, after save
            self.node_selector_var.set(f"{point.name} (#{point.number})" if hasattr(point, "number") else f"{point.name} [AP]")

        ttk.Button(self.info_frame, text="Save Changes", command=save_changes).pack(pady=10)

        # --- Add action buttons below ---
        action_frame1 = ttk.Frame(self.info_frame)
        action_frame1.pack(fill="x", pady=(5, 0))
        action_frame2 = ttk.Frame(self.info_frame)
        action_frame2.pack(fill="x", pady=(0, 5))

        ttk.Button(action_frame1, text="Neighbors", command=lambda: self.show_neighbors(point)).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(action_frame1, text="Reachability", command=lambda: self.show_reachability(point)).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(action_frame2, text="Start Route", command=lambda: self.start_route_from_info(point)).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(action_frame2, text="Delete Node", command=lambda: self.delete_node_from_info(point)).pack(side="left", expand=True, fill="x", padx=2)

    # Helper methods for the info panel actions:
    def show_neighbors(self, point):
        if hasattr(point, 'SIDs'): point = point.SIDs[0]
        self.clear_graph()
        self.graph.PlotNeighbors(self.ax1, point.number)
        self.canvas.draw()
        # Only outgoing neighbors (as displayed)
        neighbors = [p for p in self.graph.pts if any(
            s.org == point.number and s.des == p.number
            for s in self.graph.seg
        )]
        self.last_special_plot = {
            'type': 'neighbors',
            'points': [point] + neighbors,
            'segments': [(point, n) for n in neighbors]
        }

    def show_reachability(self, point):
        if hasattr(point, 'SIDs'): point = point.SIDs[0]
        self.clear_graph()
        self.graph.PlotReachability(self.ax1, point.name)
        self.canvas.draw()
        # Track for export: points and segments between reachable nodes
        reachable = self.graph.Reachability(point.name)
        all_points = [point] + reachable
        point_numbers = set(p.number for p in all_points)
        segments = [
            (org, des)
            for s in self.graph.seg
            for org in all_points
            for des in all_points
            if s.org == org.number and s.des == des.number
        ]
        self.last_special_plot = {
            'type': 'reachability',
            'points': all_points,
            'segments': segments
        }

    def delete_node_from_info(self, point):
        self.graph.DeleteNavPoint(point)
        self.clear_graph()
        self.graph.Plot(self.ax1)
        self.canvas.draw()
        self.node_selector_var.set("")
        self.update_node_selector_values()
        self.info_frame.destroy()

    def reset_graph(self):
        if self.nav_points_file and self.nav_segments_file and self.nav_airports_file:
            self.clear_graph()
            self.graph.read_airspace(self.nav_points_file, self.nav_segments_file, self.nav_airports_file)
            self.graph.Plot(self.ax1)
            self.canvas.draw()

    def export_to_google_earth(self):
        print("Exporting to Google Earth KML...")
        from tkinter import filedialog

        # Fast export without asking with later option to save it
        kml_path = "data/KMLs/fast_export/flight_planner_export.kml"

        def kml_coords(lat, lon):
            # KML uses lon,lat[,alt]
            return f"{lon},{lat},0"

        kml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<kml xmlns="http://www.opengis.net/kml/2.2">',
            '<Document>',
            '<name>Flight Planner Export</name>',
            # Styles
            '<Style id="nodeStyle"><IconStyle><color>ff0000ff</color><scale>1.1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>',
            '<Style id="deactivatedNodeStyle"><IconStyle><color>ddddddaa</color><scale>1.1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>',
            '<Style id="segmentStyle"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle></Style>',
            '<Style id="airportStyle"><IconStyle><color>ff00ff00</color><scale>1.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle></Style>',
        ]

        drawn_pts = []
        # --- Only export the current route if it exists ---
        if self.current_route_path and len(self.current_route_path) > 1:
            # Export only the route nodes
            if self.graph.show_pts_var.get():
                for p in self.current_route_path:
                    drawn_pts.append(p)
                    kml.append(f'''
<Placemark>
    <name>{p.name} (#{p.number})</name>
    <styleUrl>#nodeStyle</styleUrl>
    <Point>
        <coordinates>{kml_coords(p.lat, p.lon)}</coordinates>
    </Point>
</Placemark>
''')
            # Export only the route segments
            if self.graph.show_seg_var.get():
                for i in range(len(self.current_route_path) - 1):
                    org = self.current_route_path[i]
                    des = self.current_route_path[i+1]
                    kml.append(f'''
<Placemark>
    <name>{org.name} → {des.name}</name>
    <styleUrl>#segmentStyle</styleUrl>
    <LineString>
        <coordinates>
            {kml_coords(org.lat, org.lon)}
            {kml_coords(des.lat, des.lon)}
        </coordinates>
    </LineString>
</Placemark>
''')
        # --- Export only what is shown for Neighbors or Reachability ---
        elif hasattr(self, "last_special_plot") and self.last_special_plot:
            # last_special_plot: dict with keys 'type' and 'points' and optionally 'segments'
            special = self.last_special_plot
            if self.graph.show_pts_var.get():
                for p in special.get('points', []):
                    drawn_pts.append(p)
                    kml.append(f'''
<Placemark>
    <name>{p.name} (#{p.number})</name>
    <styleUrl>#nodeStyle</styleUrl>
    <Point>
        <coordinates>{kml_coords(p.lat, p.lon)}</coordinates>
    </Point>
</Placemark>
''')
            if self.graph.show_seg_var.get() and 'segments' in special:
                for org, des in special['segments']:
                    kml.append(f'''
<Placemark>
    <name>{org.name} → {des.name}</name>
    <styleUrl>#segmentStyle</styleUrl>
    <LineString>
        <coordinates>
            {kml_coords(org.lat, org.lon)}
            {kml_coords(des.lat, des.lon)}
        </coordinates>
    </LineString>
</Placemark>
''')
        # --- Fallback: export the whole graph as before ---
        else:
            # Export Segments (edges)
            if self.graph.show_seg_var.get():
                for s in self.graph.seg:
                    # Find origin and destination points
                    org = next((p for p in self.graph.pts if p.number == s.org), None)
                    des = next((p for p in self.graph.pts if p.number == s.des), None)
                    if org and des:
                        kml.append(f'''
<Placemark>
    <name>{org.name} → {des.name}</name>
    <styleUrl>#segmentStyle</styleUrl>
    <LineString>
        <coordinates>
            {kml_coords(org.lat, org.lon)}
            {kml_coords(des.lat, des.lon)}
        </coordinates>
    </LineString>
</Placemark>
''')

            if self.graph.show_pts_var.get():
                for p in self.graph.pts:
                        kml.append(f'''
<Placemark>
    <name>{p.name} (#{p.number})</name>
    <styleUrl>#nodeStyle</styleUrl>
    <Point>
        <coordinates>{kml_coords(p.lat, p.lon)}</coordinates>
    </Point>
</Placemark>
''')

        # Always export Airports
        # Export Airports
        if self.graph.show_airports_var.get():
            for a in self.graph.aip:
                # Airports are treated as special NavPoints, and as not knowing their position we use the one of their first SID
                b = a.SIDs[0]
                kml.append(f'''
<Placemark>
    <name>{a.name} [Airport]</name>
    <styleUrl>#airportStyle</styleUrl>
    <Point>
        <coordinates>{kml_coords(b.lat, b.lon)}</coordinates>
    </Point>
</Placemark>
''')
        # gray out all points not in the route if deactivated is enabled
        if self.graph.show_pts_var.get() and self.graph.show_deactivated_var.get():
                for p in self.graph.pts:
                    if p not in drawn_pts:
                        kml.append(f'''
<Placemark>
    <name>{p.name} (#{p.number})</name>
    <styleUrl>#deactivatedNodeStyle</styleUrl>
    <Point>
        <coordinates>{kml_coords(p.lat, p.lon)}</coordinates>
    </Point>
</Placemark>
''')

        kml.append('</Document></kml>')

        try:
            with open(kml_path, "w", encoding="utf-8") as f:
                f.write('\n'.join(kml))
            webbrowser.open(f'file://{os.path.abspath(kml_path)}')

            # message box with button to save the KML file
            kml_path = None
            save_kml = messagebox.askyesno("Exported", "Graph exported to Google Earth.\nDo you want to save the KML file?")
            if save_kml:
                # Ask user where to save the KML file in KMLs by default
                kml_path = filedialog.asksaveasfilename(
                    title="Save KML File",
                    defaultextension=".kml",
                    filetypes=[("KML Files", "*.kml")],
                    initialdir="data/KMLs/",
                ) 
            if not kml_path:
                #delete the fast export file if it exists
                if os.path.exists("data/KMLs/fast_export/flight_planner_export.kml"):
                    os.remove("data/KMLs/fast_export/flight_planner_export.kml")
            else:
                with open(kml_path, "w", encoding="utf-8") as f:
                        f.write('\n'.join(kml))    
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export KML:\n{e}")

    def open_route_planner(self, origin_point):
        # Helper to close the route planner tab and clear reference
        def close_route_tab():
            if self.route_frame and self.route_frame.winfo_exists():
                self.notebook.forget(self.route_frame)
            self.route_frame = None

        # If already open, close it before opening a new one
        close_route_tab()

        self.route_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(self.route_frame, text="Route Planner")
        self.notebook.select(self.route_frame)

        if hasattr(origin_point, 'SIDs'): origin_point = origin_point.SIDs[0] 
        ttk.Label(self.route_frame, text=f"Origin: {origin_point.name} (#{origin_point.number})", font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=(0, 10))

        # Get all reachable nodes from the origin (excluding the origin itself)
        reachable_points = self.graph.Reachability(origin_point.name)
        reachable_points = [p for p in reachable_points if p.number != getattr(origin_point, "number", None)]
        # Add airports as possible destinations
        all_dest_values = [f"{p.name} (#{p.number})" for p in reachable_points]
        all_dest_values += [f"{a.name} [AP]" for a in self.graph.aip if (a.name != origin_point.name and any(pt in reachable_points for pt in a.STARs))]

        # Destination selector
        ttk.Label(self.route_frame, text="Destination:").pack(anchor="w")
        dest_var = tk.StringVar()
        dest_combo = ttk.Combobox(self.route_frame, textvariable=dest_var, values=all_dest_values, state="normal")
        dest_combo.pack(fill="x", pady=(0, 10))

        def update_dest_combo_values():
            typed = dest_var.get().lower()
            filtered = [v for v in all_dest_values if typed in v.lower()]
            dest_combo['values'] = filtered

        def on_dest_combo_keyrelease(event):
            update_dest_combo_values()
            if event.keysym in ("Down", "Up"):
                if dest_combo.winfo_ismapped():
                    dest_combo.event_generate('<Escape>')
                    dest_combo.after(1, lambda: dest_combo.event_generate('<Button-1>'))
            elif event.keysym == "Return":
                filtered = dest_combo['values']
                if isinstance(filtered, str):  # Defensive: can be a string in some Tk versions
                    filtered = dest_combo['values'] = list(all_dest_values)
                if len(filtered) == 1:
                    dest_var.set(filtered[0])
                elif len(filtered) > 1:
                    if dest_combo.winfo_ismapped():
                        dest_combo.event_generate('<Escape>')
                        dest_combo.after(1, lambda: dest_combo.event_generate('<Button-1>'))

        dest_combo.bind('<KeyRelease>', on_dest_combo_keyrelease)
        dest_combo.bind('<FocusIn>', lambda e: dest_combo.configure(values=all_dest_values))

        # --- Helper to get NavPoint from string ---
        def get_point_from_str(s):
            if "[AP]" in s:
                name = s.split(" [AP]")[0]
                return next((a for a in self.graph.aip if a.name == name), None)
            code = int(s.split("#")[-1].split(")")[0])
            return next((p for p in self.graph.pts if p.number == code), None)

        # Waypoints (dual-listbox for order control)
        ttk.Label(self.route_frame, text="Waypoints (optional, in order):").pack(anchor="w")
        waypoint_frame = ttk.Frame(self.route_frame)
        waypoint_frame.pack(fill="x", pady=(0, 10))
        
        available_listbox = tk.Listbox(waypoint_frame, selectmode="extended", exportselection=False, height=6)
        waypoint_listbox = tk.Listbox(waypoint_frame, selectmode="extended", exportselection=False, height=6)
        available_listbox.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(0, 5))
        waypoint_listbox.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=(5, 0))
        waypoint_frame.columnconfigure(0, weight=1)
        waypoint_frame.columnconfigure(2, weight=1)

        # --- Dynamic available waypoints update ---
        def update_available_waypoints():
            # Start from origin or last waypoint
            if waypoint_listbox.size() > 0:
                last_str = waypoint_listbox.get(waypoint_listbox.size()-1)
                last_point = get_point_from_str(last_str)
            else:
                last_point = origin_point
            # Exclude already used waypoints and origin
            used_codes = {origin_point.number}
            for i in range(waypoint_listbox.size()):
                used_codes.add(get_point_from_str(waypoint_listbox.get(i)).number)
            # Only show reachable and not already used, and can reach destination
            dest_str = dest_var.get()
            dest_point = get_point_from_str(dest_str) if dest_str else None
            reachable = self.graph.Reachability(last_point.name)
            filtered = []
            for p in reachable:
                if p.number not in used_codes and dest_point and self.graph.FindShortestPath(p.name, dest_point.name):
                    filtered.append(p)
                elif p.number not in used_codes and not dest_point:
                    filtered.append(p)
            available_listbox.delete(0, "end")
            for p in filtered:
                available_listbox.insert("end", f"{p.name} (#{p.number})")

        # --- Control buttons ---
        def add_waypoints():
            selected = list(available_listbox.curselection())
            for idx in selected:
                value = available_listbox.get(idx)
                if value not in waypoint_listbox.get(0, "end"):
                    waypoint_listbox.insert("end", value)
            update_available_waypoints()
            update_path_preview()

        def remove_waypoints():
            selected = list(waypoint_listbox.curselection())
            for idx in reversed(selected):
                waypoint_listbox.delete(idx)
            update_available_waypoints()
            update_path_preview()

        def move_up():
            selected = list(waypoint_listbox.curselection())
            for idx in selected:
                if idx == 0:
                    continue
                value = waypoint_listbox.get(idx)
                waypoint_listbox.delete(idx)
                waypoint_listbox.insert(idx-1, value)
                waypoint_listbox.selection_set(idx-1)
            update_available_waypoints()
            update_path_preview()

        def move_down():
            selected = list(waypoint_listbox.curselection())
            for idx in reversed(selected):
                if idx == waypoint_listbox.size() - 1:
                    continue
                value = waypoint_listbox.get(idx)
                waypoint_listbox.delete(idx)
                waypoint_listbox.insert(idx+1, value)
                waypoint_listbox.selection_set(idx+1)
            update_available_waypoints()
            update_path_preview()

        btn_frame = ttk.Frame(waypoint_frame)
        btn_frame.grid(row=0, column=1, rowspan=4, sticky="ns")
        ttk.Button(btn_frame, text="Add →", command=add_waypoints).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="← Remove", command=remove_waypoints).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Up", command=move_up).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Down", command=move_down).pack(fill="x", pady=2)

        # --- Initial population ---
        update_available_waypoints()

        # --- In calculate_route, validate each segment ---
        def calculate_route():
            dest = dest_var.get()
            if not dest:
                messagebox.showerror("Error", "Please select a destination.")
                return
            dest_point = get_point_from_str(dest)
            if not dest_point:
                messagebox.showerror("Error", "Destination not found.")
                return

            # Get waypoints in order
            selected_waypoints = [waypoint_listbox.get(i) for i in range(waypoint_listbox.size())]
            waypoints = []
            for wp_str in selected_waypoints:
                wp_point = get_point_from_str(wp_str)
                if wp_point and wp_point != origin_point and wp_point != dest_point:
                    waypoints.append(wp_point)

            # --- SID/STAR logic ---
            route_points = [origin_point] + waypoints + [dest_point]
            full_path = []

            # Main route segments
            for i in range(len(route_points) - 1):
                segment = self.graph.FindShortestPath(route_points[i].name, route_points[i+1].name)
                if not segment:
                    messagebox.showerror("Error", f"No path between {route_points[i].name} and {route_points[i+1].name}.")
                    return
                if i > 0 or full_path:  # Avoid duplicate nodes
                    segment = segment[1:]
                full_path.extend(segment)

            # Plot the route on the main graph tab
            self.notebook.select(self.center_frame)
            self.clear_graph()
            self.graph.PlotPath(self.ax1, full_path)
            self.canvas.draw()
            self.current_route_path = full_path  # <-- Store the route path

        ttk.Button(self.route_frame, text="Calculate Route", command=calculate_route).pack(pady=10)
        ttk.Button(self.route_frame, text="Close", command=close_route_tab).pack()

        # --- Path preview label and cost ---
        path_preview_frame = ttk.Frame(self.route_frame)
        path_preview_frame.pack(fill="x", pady=(10, 0))
        path_preview_label = ttk.Label(path_preview_frame, text="Current Path Preview:", font=('Segoe UI', 11, 'italic'))
        path_preview_label.pack(side="left")
        cost_var = tk.StringVar()
        cost_label = ttk.Label(path_preview_frame, textvariable=cost_var, font=('Segoe UI', 11, 'italic'))
        cost_label.pack(side="right")

        path_preview_text = tk.Text(self.route_frame, height=2, font=('Segoe UI', 11), relief="flat")
        path_preview_text.pack(fill="x", pady=(0, 10))
        path_preview_text.tag_configure("bold", font=('Segoe UI', 11, 'bold'))
        path_preview_text.config(state="disabled")

        def update_path_preview():
            dest_str = dest_var.get()
            if not dest_str:
                names = [origin_point.name]
                bold_indices = {0}
                total_cost = 0
            else:
                dest_point = get_point_from_str(dest_str)
                # Get user waypoints
                user_waypoints = []
                for i in range(waypoint_listbox.size()):
                    wp_str = waypoint_listbox.get(i)
                    wp_point = get_point_from_str(wp_str)
                    if wp_point:
                        user_waypoints.append(wp_point)
                # Build full route: origin -> waypoints... -> destination
                route_points = [origin_point] + user_waypoints + [dest_point]
                full_path = [origin_point.name]
                bold_indices = set()
                total_cost = 0
                path_index = 0
                # For bold: always mark 0 (origin), user waypoints at their segment start, and last (destination)
                for i in range(len(route_points) - 1):
                    segment = self.graph.FindShortestPath(route_points[i].name, route_points[i+1].name)
                    if not segment:
                        full_path = [p.name for p in route_points[:i+1]]
                        break
                    # For cost: sum the cost of each segment in the path
                    for i in range(len(segment)-1):
                        seg = next((s for s in self.graph.seg if (s.org == segment[i].number and s.des == segment[i+1].number)), None)
                        total_cost += seg.dis
                    # For path, skip first node except for the first segment
                    if i > 0:
                        segment = segment[1:]
                        # For bold: mark the first node of each segment
                        bold_indices.add(path_index)
                    for j, p in enumerate(segment):
                        full_path.append(p.name)                            
                        path_index += 1
                names = full_path
                # Always mark first and last node (destination) in bold
                if names:
                    bold_indices.add(0)
                    bold_indices.add(len(names)-1)
            # Update the cost label
            cost_var.set(f"Total cost: {total_cost}")
            # Update the Text widget
            path_preview_text.config(state="normal")
            path_preview_text.delete("1.0", "end")
            for i, name in enumerate(names):
                if i > 0:
                    path_preview_text.insert("end", "  →  ")
                if i in bold_indices:
                    path_preview_text.insert("end", name, "bold")
                else:
                    path_preview_text.insert("end", name)
            path_preview_text.config(state="disabled")

        # Bind updates to changes in waypoints and destination
        waypoint_listbox.bind('<<ListboxSelect>>', lambda e: update_path_preview())
        waypoint_listbox.bind('<KeyRelease>', lambda e: update_path_preview())
        waypoint_listbox.bind('<ButtonRelease-1>', lambda e: update_path_preview())
        available_listbox.bind('<ButtonRelease-1>', lambda e: update_path_preview())
        dest_var.trace_add('write', lambda *a: update_path_preview())

        # Also call after any add/remove/move operation
        def add_waypoints():
            selected = list(available_listbox.curselection())
            for idx in selected:
                value = available_listbox.get(idx)
                if value not in waypoint_listbox.get(0, "end"):
                    waypoint_listbox.insert("end", value)
            update_available_waypoints()
            update_path_preview()

        def remove_waypoints():
            selected = list(waypoint_listbox.curselection())
            for idx in reversed(selected):
                waypoint_listbox.delete(idx)
            update_available_waypoints()
            update_path_preview()

        def move_up():
            selected = list(waypoint_listbox.curselection())
            for idx in selected:
                if idx == 0:
                    continue
                value = waypoint_listbox.get(idx)
                waypoint_listbox.delete(idx)
                waypoint_listbox.insert(idx-1, value)
                waypoint_listbox.selection_set(idx-1)
            update_available_waypoints()
            update_path_preview()

        def move_down():
            selected = list(waypoint_listbox.curselection())
            for idx in reversed(selected):
                if idx == waypoint_listbox.size() - 1:
                    continue
                value = waypoint_listbox.get(idx)
                waypoint_listbox.delete(idx)
                waypoint_listbox.insert(idx+1, value)
                waypoint_listbox.selection_set(idx+1)
            update_available_waypoints()
            update_path_preview()

        # Initial preview
        update_path_preview()

    def PopupDelete(self, x, y, event):
        del_win = tk.Toplevel()
        del_win.geometry(f"+{int(x)+40}+{int(y)+40}")
        del_win.wm_overrideredirect(True)
        del_win.configure(bg=self.theme_palette.get(self.selected_theme.get().lower(), "#DDDDDD"))
        ttk.Label(del_win, text="Delete:").grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 5))
        ttk.Button(del_win, text="Delete Node", command=lambda: [self.DeleteNode_(event), del_win.destroy()]).grid(row=1, column=0, sticky="nsew")
        ttk.Button(del_win, text="Delete Segment", command=lambda: [self.DeleteSegment_(event), del_win.destroy()]).grid(row=1, column=1, sticky="nsew")
        ttk.Button(del_win, text="Cancel", command=del_win.destroy).grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(5, 0))

    def open_settings(self):
        def close_settings_tab():
            if self.settings_frame and self.settings_frame.winfo_exists():
                self.notebook.forget(self.settings_frame)
            self.settings_frame = None

        close_settings_tab()
        
        self.settings_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.select(self.settings_frame)

        ttk.Label(self.settings_frame, text="Music", font=('Segoe UI', 12)).pack(anchor="w")
        music_frame = ttk.Frame(self.settings_frame)
        music_frame.pack(fill="x", pady=(0, 10))
        music_inner_frame = ttk.Frame(music_frame)
        music_inner_frame.pack(anchor="center")

        def change_music(event=None):
            track = next((t for t in self.music_tracks if t[0] == self.selected_music.get()), None)
            if track:
                pygame.mixer.music.load(track[1])
                pygame.mixer.music.play(-1)
                self.is_music_paused = False
                pause_btn.config(text="Pause")
        ttk.Label(music_inner_frame, text="Track:").pack(side="left", padx=(0, 5))
        music_combo = ttk.Combobox(
            music_inner_frame,
            textvariable=self.selected_music,
            values=[t[0] for t in self.music_tracks],
            state="readonly",
            width=16
        )
        music_combo.pack(side="left", padx=(0, 10))
        music_combo.bind("<<ComboboxSelected>>", change_music)

        # --- Pause/Unpause toggle ---
        self.is_music_paused = False
        def toggle_pause():
            if self.is_music_paused:
                pygame.mixer.music.unpause()
                pause_btn.config(text="Pause")
                self.is_music_paused = False
            else:
                pygame.mixer.music.pause()
                pause_btn.config(text="Unpause")
                self.is_music_paused = True
        pause_btn = ttk.Button(music_inner_frame, text="Pause", command=toggle_pause)
        pause_btn.pack(side="left", padx=(0, 5))

        # --- Volume slider always visible ---
        def set_volume(val):
            pygame.mixer.music.set_volume(float(val))
        volume_slider_frame = ttk.Frame(music_frame)
        volume_slider_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(volume_slider_frame, text="Volume:").pack(padx=(0, 5))
        volume_slider = ttk.Scale(
            volume_slider_frame,
            from_=0, to=1, orient="horizontal",
            value=pygame.mixer.music.get_volume(),
            command=set_volume,
            length=150,
        )
        volume_slider.pack(padx=(0, 5))

        # Theme selection
        ttk.Label(self.settings_frame, text="Theme", font=('Segoe UI', 12)).pack(anchor="w")
        theme_frame = ttk.Frame(self.settings_frame)
        theme_frame.pack(fill="x", pady=(0, 10))
        theme_inner_frame = ttk.Frame(theme_frame)
        theme_inner_frame.pack(anchor="center")
        self.theme_inner_frame = theme_inner_frame

        # Theme selection combobox (ensure it also gets themed)
        self.theme_combobox = ttk.Combobox(
            theme_inner_frame,
            textvariable=self.selected_theme,
            values=self.theme_names,
            state="readonly",
            width=15
        )
        self.theme_combobox.pack(fill='x', side="left", padx=(0, 5))
        self.theme_combobox.bind("<<ComboboxSelected>>", lambda e: self.apply_theme(self.selected_theme.get()))

        '''ttk.Button(
            theme_inner_frame,
            text="Apply",
            command=lambda: self.apply_theme(self.selected_theme.get())
        ).pack(side="left", padx=(0, 5))'''

        if self.graph_loaded:
            ttk.Label(self.settings_frame, text="Graph Options", font=('Segoe UI', 12)).pack(anchor="w")
            options_frame = ttk.Frame(self.settings_frame)
            options_frame.pack(fill="x", pady=(0, 10))
            options_inner_frame = ttk.Frame(options_frame)
            options_inner_frame.pack(anchor="center")
            self.options_inner_frame = options_inner_frame
            
            ttk.Checkbutton(options_inner_frame, text="Show Nodes", variable=self.graph.show_pts_var, command=lambda: [self.graph.TogglePts(self.ax1, self.graph.show_pts_var.get()), self.reset_graph(), self.canvas.draw()]).pack(side="left", padx=(0, 5))
            ttk.Checkbutton(options_inner_frame, text="Show Segments", variable=self.graph.show_seg_var, command=lambda: [self.graph.ToggleSeg(self.ax1, self.graph.show_seg_var.get()), self.reset_graph(), self.canvas.draw()]).pack(side="left", padx=(0, 5))
            ttk.Checkbutton(options_inner_frame, text="Show Airports", variable=self.graph.show_airports_var, command=lambda: [self.graph.ToggleAirports(self.ax1, self.graph.show_airports_var.get()), self.reset_graph(), self.canvas.draw()]).pack(side="left", padx=(0, 5))
            ttk.Checkbutton(options_inner_frame, text="Show Names", variable=self.graph.show_names_var, command=lambda: [self.graph.ToggleNames(self.ax1, self.graph.show_names_var.get()), self.reset_graph(), self.canvas.draw()]).pack(side="left", padx=(0, 5))
            ttk.Checkbutton(options_inner_frame, text="Show Deactivated", variable=self.graph.show_deactivated_var, command=lambda: [self.graph.ToggleDeactivated(self.ax1, self.graph.show_deactivated_var.get()), self.reset_graph(), self.canvas.draw()]).pack(side="left", padx=(0, 5))

        ttk.Button(self.settings_frame, text="Close", command=close_settings_tab).pack(pady=(0, 10))

    def open_about(self):
        # Close previous About tab if open
        if hasattr(self, 'about_frame') and self.about_frame and self.about_frame.winfo_exists():
            self.notebook.forget(self.about_frame)
        self.about_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(self.about_frame, text="About")
        self.notebook.select(self.about_frame)

        # Project info
        ttk.Label(self.about_frame, text="Flight Planner", style='Header.TLabel').pack(anchor="center", pady=(0, 10))
        ttk.Label(self.about_frame, text="Version 4.0\n\nA modern tool for visualizing and planning flight routes.\n", font=('Segoe UI', 11)).pack(anchor="center")

        # Features
        features = (
            "Extra Features:\n"
            "- Route planner with waypoints and SID/STAR support\n"
            "- Export to Google Earth (KML)\n"
            "- Theme customization\n"
            "- Music playback\n"
            "- Node/segment/airport visibility toggles\n"
            "- Node info editing and search\n"
        )
        ttk.Label(self.about_frame, text=features, font=('Segoe UI', 10)).pack(anchor="w", pady=(10, 0))

        # Usage
        usage = (
            "How to Use:\n"
            "1. Use 'File...' to load or create a graph.\n"
            "2. Click nodes for options (neighbors, reachability, route, etc).\n"
            "3. Use the left/right panels for saving, exporting, and settings.\n"
            "4. Plan routes with the Route Planner tab.\n"
            "5. Export your route or graph to Google Earth.\n"
        )
        ttk.Label(self.about_frame, text=usage, font=('Segoe UI', 10)).pack(anchor="w", pady=(10, 0))

        # Team info
        team = (
            "Team:\n"
            "Èrik Ventura Gili, Adrià Martínez Mirabent and Alex Sanz Rautiainen\n"
        )
        ttk.Label(self.about_frame, text=team, font=('Segoe UI', 10, 'italic')).pack(anchor="w", pady=(10, 0))

        # Photo
        try:
            from PIL import Image, ImageTk
            img = Image.open("resources/team_photo.png")
            img = img.resize((540, 360))
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(self.about_frame, image=photo)
            label.image = photo  # Keep a reference!
            label.pack(pady=(10, 0))
        except Exception as e:
            ttk.Label(self.about_frame, text="[Team photo not found]", font=('Segoe UI', 9, 'italic')).pack(pady=(10, 0))

    def apply_theme(self, theme_name):
        color = self.theme_palette.get(theme_name.lower(), "#DDDDDD")
        theme_key = theme_name.lower().replace(" ", "_")

        # Update ttk styles for all relevant widgets
        self.style.configure('TFrame', background=color)
        self.style.configure('TLabel', background=color)
        self.style.configure('Header.TLabel', background=color)
        self.style.configure('Custom.TFrame', background=color)
        self.style.configure('Custom.TLabel', background=color)
        self.style.configure('TButton', background=color)
        self.style.configure('TCombobox', fieldbackground=color, background=color)
        self.style.configure('TCheckbutton', background=color)
        self.style.map('TButton', background=[('active', color), ('!active', color)])

        self.style.configure('TNotebook', background=color, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=color, lightcolor=color, borderwidth=0)
        self.style.map('TNotebook.Tab', background=[('selected', color), ('!selected', color)])

        self.style.configure('TCombobox', selectbackground=color, selectforeground="#222" if theme_key in ["default", "light", "sunny_day", "lemon_cream", "rose_mist"] else "#fff")

        fg = "#222" if theme_key in ["default", "light", "sunny_day", "lemon_cream", "rose_mist"] else "#fff"
        self.style.configure('TLabel', foreground=fg)
        self.style.configure('Header.TLabel', foreground=fg)
        self.style.configure('TButton', foreground=fg)
        self.style.configure('TCombobox', foreground=fg)
        self.style.configure('TCheckbutton', foreground=fg)
        self.style.configure('TNotebook.Tab', foreground=fg)

        self.root.configure(bg=color)
        self.canvas.figure.set_facecolor(color)
        for ax in self.canvas.figure.axes:
            for line in ax.get_lines():
                line.set_color(fg)
        self.canvas.draw_idle()

    #Función para cerrar todo
    def on_exit(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.root.quit()

#Version 4 ideas: Añadir 3 stage switch con el que se muestre el code, name o code y name, encima de cada punto
#                        Añadir un botón para enseñar o ocultar nodos y segmentos
#                        Posibilidad de hacer zoom en una zona concreta

# At the end, launch the app as before
root = tk.Tk()
root.iconbitmap("resources/icon.ico")
app = GraphVisualizer(root)
root.mainloop()