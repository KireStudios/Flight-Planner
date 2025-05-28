import matplotlib.pyplot as plt
from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport
import tkinter as tk

class AirSpace:
    def __init__(self, nav_points=None, nav_segments=None, nav_airports=None):
        self.pts = nav_points if nav_points is not None else []  # List of NavPoint objects
        self.seg = nav_segments if nav_segments is not None else []  # List of NavSegment objects
        self.aip = nav_airports if nav_airports is not None else []  # List of NavAirport objects

        self.show_names_var = tk.BooleanVar(value=True)
        self.show_pts_var = tk.BooleanVar(value=True)
        self.show_seg_var = tk.BooleanVar(value=True)
        self.show_airports_var = tk.BooleanVar(value=True)
        self.show_deactivated_var = tk.BooleanVar(value=True)
    
    # Read and fill the airspace with the data from the files
    def read_airspace(self, nav_file, seg_file, airport_file):
        self.read_nav_points(nav_file)
        self.read_nav_segments(seg_file)
        self.read_airports(airport_file)

    # Read the navigation points from the file and fill the nav_points list
    def read_nav_points(self, file_path):
        self.pts.clear()  # Clear existing points
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 4:
                        number = int(parts[0])
                        name = parts[1]
                        lat = float(parts[2])
                        lon = float(parts[3])
                        nav_point = NavPoint(number, name, lat, lon)
                        self.pts.append(nav_point)
        except FileNotFoundError:
            print(f"Error: File '{file}' not found.")
        except ValueError as e:
            print(f"Error processing file '{file}': {e}")

    # Read the navigation segments from the file and fill the nav_segments list
    def read_nav_segments(self, file_path):
        self.seg.clear()
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        origin_number = int(parts[0])
                        destination_number = int(parts[1])
                        distance = float(parts[2])
                        nav_segment = NavSegment(origin_number, destination_number, distance)
                        self.seg.append(nav_segment)
        except FileNotFoundError:
            print(f"Error: File '{file}' not found.")
        except ValueError as e:
            print(f"Error processing file '{file}': {e}")

    # Read the airports from the file and fill the nav_airports list
    def read_airports(self, file_path):
        self.aip.clear()
        try:
            with open(file_path, 'r') as file:
                sids = []
                stars = []
                for line in file:
                    line = line.strip()
                    if "." not in line:
                        if sids and stars:
                            nav_airport = NavAirport(name, sids, stars)
                            self.aip.append(nav_airport)
                        name = line
                        sids = []
                        stars = []
                    else:
                        part = line.split(".")
                        if part[1] == "D":
                            pt = next((pt for pt in self.pts if pt.name == line), None)
                            if pt:
                                sids.append(pt)
                        elif part[1] == "A":
                            pt = next((pt for pt in self.pts if pt.name == line), None)
                            if pt:
                                stars.append(pt)
                if sids and stars:
                    nav_airport = NavAirport(name, sids, stars)
                    self.aip.append(nav_airport)
        except FileNotFoundError:
            print(f"Error: File '{file}' not found.")
        except ValueError as e:
            print(f"Error processing file '{file}': {e}")
                    
    def Plot(self, ax):
        scale_factor = (((ax.get_xlim()[1] - ax.get_xlim()[0])**2 + (ax.get_ylim()[1] - ax.get_ylim()[0])**2)**0.5) / 100
        if self.show_pts_var.get():
            for pt in self.pts:
                ax.plot(pt.lon, pt.lat, 'ob', markersize=scale_factor*200)
                if self.show_names_var.get():
                    ax.text(pt.lon, pt.lat + scale_factor, pt.name, fontsize=scale_factor*400, ha='center', va='bottom')
        if self.show_seg_var.get():
            for seg in self.seg:
                # Buscar los puntos correspondientes a seg.org y seg.des
                pt1 = next((pt for pt in self.pts if pt.number == seg.org), None)
                pt2 = next((pt for pt in self.pts if pt.number == seg.des), None)
                if pt1 and pt2:
                    ax.plot([pt1.lon, pt2.lon], [pt1.lat, pt2.lat], 'r-', linewidth=scale_factor*30)
                    # Agregar una flecha en dirección del punto final
                    ax.annotate('', xy=(pt2.lon, pt2.lat), xytext=(pt1.lon, pt1.lat), arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=scale_factor*30))
        if self.show_airports_var.get():
            for air in self.aip:
                for pts in self.pts:
                    for pt in air.SIDs + air.STARs:
                        if pts.name == pt.name and pt in air.SIDs:
                            if pts.name == air.SIDs[0]:
                                #We plot airport at first SID as we don't know the airport position
                                ax.plot(pts.lon, pts.lat, 'oo', markersize=scale_factor*200)
                                if self.show_names_var.get():
                                    ax.text(pts.lon, pts.lat + scale_factor, air.name, fontsize=scale_factor*400, ha='center', va='bottom')
                            ax.plot(pts.lon, pts.lat, 'og', markersize=scale_factor*200)
                            if self.show_names_var.get():
                                ax.text(pts.lon, pts.lat + scale_factor, air.name, fontsize=scale_factor*400, ha='center', va='bottom')
                        elif pts.name == pt.name and pt in air.STARs:
                            ax.plot(pts.lon, pts.lat, 'or', markersize=scale_factor*200)
                            if self.show_names_var.get():
                                ax.text(pts.lon, pts.lat + scale_factor, air.name, fontsize=scale_factor*400, ha='center', va='bottom')

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

    def PlotNeighbors (self, ax, point_number):
        # Buscar el punto de origen por su número
        origin = next((pt for pt in self.pts if pt.number == point_number), None)

        if not origin:
            print(f"Error: Point with number {point_number} not found.")
            return False

        scale_factor = (((ax.get_xlim()[1] - ax.get_xlim()[0])**2 + (ax.get_ylim()[1] - ax.get_ylim()[0])**2)**0.5) / 100

        # Plotear el punto de origen
        if self.show_pts_var.get():
            ax.plot(origin.lon, origin.lat, 'bo', markersize=scale_factor*200)
            if self.show_names_var.get():
                ax.text(origin.lon, origin.lat + scale_factor, origin.name, fontsize=scale_factor*400, ha='center', va='bottom')

        # Crear un conjunto para almacenar los vecinos
        neighbors = set()

        # Buscar y plotear los puntos vecinos
        if self.show_pts_var.get():
            for seg in self.seg:
                if seg.org == origin.number:
                    neighbor = next((pt for pt in self.pts if pt.number == seg.des), None)
                else:
                    continue

                if neighbor:
                    neighbors.add(neighbor)  # Agregar el vecino al conjunto
                    # Plotear el vecino
                    ax.plot(neighbor.lon, neighbor.lat, 'go', markersize=scale_factor*200)
                    if self.show_names_var.get():
                        ax.text(neighbor.lon, neighbor.lat + scale_factor, neighbor.name, fontsize=scale_factor*400, ha='center', va='bottom')

                    # Dibujar una flecha entre el origen y el vecino
                    ax.annotate('', xy=(neighbor.lon, neighbor.lat), xytext=(origin.lon, origin.lat),
                                arrowprops=dict(facecolor='green', edgecolor='green', arrowstyle='->', lw=scale_factor*30))

        # Plotear los demás puntos en gris
        if self.show_pts_var.get() and self.show_deactivated_var.get():
            if self.show_deactivated_var.get():
                for pt in self.pts:
                    if pt != origin and pt not in neighbors:
                        ax.plot(pt.lon, pt.lat, 'o', color='gray', markersize=scale_factor*200)
                        if self.show_names_var.get():
                            ax.text(pt.lon, pt.lat + scale_factor, pt.name, fontsize=scale_factor*400, ha='center', va='bottom')

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        return True

    def Reachability(self, origin_name):
        # Encuentra todos los puntos alcanzables desde un punto de origen
        origin = next((pt for pt in self.pts if pt.name == origin_name), None)
        
        if not origin:
            # Si no se encuentra, buscar aeropuerto y suar su SID
            for air in self.aip:
                if air.name == origin_name:
                    origin = air.SIDs[0]
        
        if not origin:
            print(f"Error: Point  {origin_name} not found.")
            return None

        reachable = list()
        queue = [origin]
        while queue:
            current = queue.pop(0)
            if current not in reachable:
                reachable.append(current)
                # Agregar vecinos a la cola
                for seg in self.seg:
                    if seg.org == current.number:
                        neighbor = next((pt for pt in self.pts if pt.number == seg.des), None)
                    else:
                        continue
                    if neighbor and neighbor not in reachable:
                        queue.append(neighbor)

        return reachable
    
    def FindShortestPath(self, origin_name, destination_name):
        # Encuentra el camino mas corto entre dos puntos
        origin = next((pt for pt in self.pts if pt.name == origin_name), None)
        destination = next((pt for pt in self.pts if pt.name == destination_name), None)

        if not origin or not destination:
            # Si no se encuentra, buscar aeropuerto y suar su SID/STAR
            for air in self.aip:
                if air.name == origin_name:
                    origin = air.SIDs[0]
                elif air.name == destination_name:
                    destination = air.STARs[0]

        # Si aún no se encuentra, imprimir error
        if not origin or not destination:
            print(f"Error: Origin or destination point not found.")
            return None

        distances = {pt: float('inf') for pt in self.pts}
        previous = {pt: None for pt in self.pts}

        distances[origin] = 0
        queue = [(0, origin)]
        while queue:
            min_dis = float('inf')
            index = 0
            for i in range(len(queue)):
                if queue[i][0] < min_dis:
                    min_dis = queue[i][0]
                    index = i
            current_distance, current_point = queue.pop(index)
            if current_point == destination:
                continue
            for seg in self.seg:
                if seg.org == current_point.number:
                    neighbor = next((pt for pt in self.pts if pt.number == seg.des), None)
                    if neighbor:
                        distance = current_distance + seg.dis
                        if distance < distances[neighbor]:
                            distances[neighbor] = distance
                            previous[neighbor] = current_point
                            queue.append((distance, neighbor))

        # Reconstruir el camino más corto
        path = []
        current = destination
        while current:
            path.insert(0, current)
            current = previous[current]
        print(distances[destination])
        return path if path[0] == origin else None

    def PlotPath(self, ax, points):
        if not points:
            print("Error: No points to plot.")
            return False

        scale_factor = (((ax.get_xlim()[1] - ax.get_xlim()[0])**2 + (ax.get_ylim()[1] - ax.get_ylim()[0])**2)**0.5) / 100

        # Dibujar el camino
        if self.show_seg_var.get():
            for i in range(len(points) - 1):
                pt1 = points[i]
                pt2 = points[i + 1]
                ax.plot([pt1.lon, pt2.lon], [pt1.lat, pt2.lat], 'r-', linewidth=scale_factor*30)
                ax.annotate('', xy=(pt2.lon, pt2.lat), xytext=(pt1.lon, pt1.lat),
                            arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=scale_factor*30))

        # Dibujar los puntos del camino
        if self.show_pts_var.get():
            for pt in points:
                ax.plot(pt.lon, pt.lat, 'go', markersize=scale_factor*200)
                if self.show_names_var.get():
                    ax.text(pt.lon, pt.lat + scale_factor, pt.name, fontsize=scale_factor*400, ha='center', va='bottom')

        # Dibujar los demás puntos en gris
        if self.show_pts_var.get() and self.show_deactivated_var.get():
            if self.show_deactivated_var.get():
                for pt in self.pts:
                    if pt not in points:
                        ax.plot(pt.lon, pt.lat, 'o', color='gray', markersize=scale_factor*200)
                        if self.show_names_var.get():
                            ax.text(pt.lon, pt.lat + scale_factor, pt.name, fontsize=scale_factor*400, ha='center', va='bottom')

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        return True
    
    def PlotReachability(self, ax, origin_name):
        points = self.Reachability(origin_name)
        if not points:
            print("Error: No points to plot.")
            return False

        scale_factor = (((ax.get_xlim()[1] - ax.get_xlim()[0])**2 + (ax.get_ylim()[1] - ax.get_ylim()[0])**2)**0.5) / 100

        # Dibujar el camino
        if self.show_seg_var.get():
            for seg in self.seg:
                pt1 = next((pt for pt in self.pts if pt.number == seg.org), None)
                pt2 = next((pt for pt in self.pts if pt.number == seg.des), None)
                if pt1 in points and pt2 in points:
                    if pt1 and pt2:
                        ax.plot([pt1.lon, pt2.lon], [pt1.lat, pt2.lat], 'r-', linewidth=scale_factor*30)
                        ax.annotate('', xy=(pt2.lon, pt2.lat), xytext=(pt1.lon, pt1.lat), arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=scale_factor*30))

        # Dibujar los puntos del camino
        if self.show_pts_var.get():
            for pt in points:
                ax.plot(pt.lon, pt.lat, 'go', markersize=scale_factor*200)
                if self.show_names_var.get():
                    ax.text(pt.lon, pt.lat + scale_factor, pt.name, fontsize=scale_factor*400, ha='center', va='bottom')

        # Dibujar los demás puntos en gris
        if self.show_pts_var.get() and self.show_deactivated_var.get():
            if self.show_deactivated_var.get():
                for pt in self.pts:
                    if pt not in points:
                        ax.plot(pt.lon, pt.lat, 'o', color='gray', markersize=scale_factor*200)
                        if self.show_names_var.get():
                            ax.text(pt.lon, pt.lat + scale_factor, pt.name, fontsize=scale_factor*400, ha='center', va='bottom')

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        return True
    
    def AddNavPoint(self, point):
        #Comprobar que no este ya
        if point in self.pts:
            return False
        #Añadir el punto
        self.pts.append(point)
        return True
    def AddNavSegment(self, codeOrigin,codeDestinarion):
        if codeOrigin == codeDestinarion:
            return False
        org=None
        des=None
        for pt in self.pts:
            if pt.number == codeOrigin:
                org=pt
                if des:
                    break
            elif pt.number == codeDestinarion:
                des=pt
                if org:
                    break
        if org and des:
            #mirar que no estigui fet ja
            for s in self.seg:
                if s.org == org and s.des == des:
                    return False
            #Distancia
            distance = ((org.lat - des.lat)**2 + (org.lon - des.lon)**2)**0.5
            #Añadir el segmento
            self.seg.append(NavSegment(org.number,des.number,distance))
            print(org.number,des.number,distance)
            return True

    def DeleteNavPoint(self, point):
        segmentsToDelete = []
        for s in self.seg:
            if s.org == point or s.des == point:
                segmentsToDelete.append(s)
        for s in segmentsToDelete:
            self.DeleteNavSegment(s)
        #Remove de la lista de nodos nd
        self.pts.remove(point)
        return True
    def DeleteNavSegment(self, segment):
        self.seg.remove(segment)
    def save_graph(self, filenames):
        with open(filenames[0], 'w') as file:
            for pt in self.pts:
                file.write(f"{pt.number} {pt.name} {pt.lat} {pt.lon}\n")  # Guardar los puntos
        with open(filenames[1], 'w') as file:
            for seg in self.seg:
                file.write(f"{seg.org} {seg.des} {seg.dis}\n")  # Guardar los segmentos
        with open(filenames[2], 'w') as file:
            for air in self.aip:
                file.write(f"{air.name}\n")
                for sid in air.SIDs:
                    file.write(f"{sid}\n")
                for star in air.STARs:
                    file.write(f"{star}\n")
        print(f"El grafo se ha guardado correctamente en {filenames[0]}, {filenames[1]} y {filenames[2]}.")
        return

    def TogglePts(self, ax=None, val=True):
        self.show_pts_var.set(val)
        if ax is not None:
            ax.clear()
        self.Plot(ax)

    def ToggleSeg(self, ax=None, val=True):
        self.show_seg_var.set(val)
        if ax is not None:
            ax.clear()
        self.Plot(ax)

    def ToggleAirports(self, ax=None, val=True):
        self.show_airports_var.set(val)
        if ax is not None:
            ax.clear()
        self.Plot(ax)

    def ToggleNames(self, ax=None, val=True):
        self.show_names_var.set(val)
        if ax is not None:
            ax.clear()
        self.Plot(ax)

    def ToggleDeactivated(self, ax=None, val=True):
        self.show_deactivated_var.set(val)
        if ax is not None:
            ax.clear()
        self.Plot(ax)