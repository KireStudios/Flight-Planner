# Airspace Route Explorer - Version 3

## Project Overview
This project is a Python application developed for Informàtica 1 (2024-25 Q2) that allows users to explore routes in airspace by manipulating and visualizing graph structures. The tool enables operations such as finding optimal routes between waypoints, with this third version adding new functionalities like importing and using real airspaces.

## Version Information
- **Version 3 generated by**: Èrik Ventura Gili
- **Version 3 verified by**: Adrià Martínez Mirabent
- **Version 3 communicated by**: Alex Sanz Rautiainen
- **URL del video**: [\[v3.0 video\]](https://drive.google.com/file/d/17wS0_ATEhulf9PddLA4oYBvcFqGBnOxn/view?usp=sharing)

## Features
- Graph representation with waypoints and segments (paths between waypoints)
- NavPoint class implementation with coordinates
- NavSegment class implementation with cost calculation
- NavAirport class implementation with cost calculation
- AirSpace operations including:
  - Adding/removing waypoints and segments
  - Visualizing graphs with different display options
  - Showing the reachable waypoints from another one
  - Finding the shortest path between two waypoints
- Graphical user interface (Tkinter) for user-friendly interaction

## Installation
1. Clone this repository
2. Ensure Python 3.x is installed
3. Install required dependencies: ``` pip install matplotlib tkinter ```

## Usage
Run the main interface:
    ```
    python interface.py
    ```

The GUI allows you to:
- Load and display example graphs
- Create custom graphs
- Save and load graphs from files
- Visualize node neighborhoods
- Interactively add/remove waypoints and segments
- Reachability analisis from a node
- Shortest path finding using A* algorithm

## Next Steps
Future versions will implement:
- Google Earth visualization capabilities
- Our own added implementations