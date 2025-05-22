from src.airSpace import *
import matplotlib.pyplot as plt

nav_points=AirSpace.load_nav_points('docs/Cat_nav.txt')
print(nav_points)
air_space=AirSpace()
air_space.pts=nav_points
fig, ax = plt.subplots()
air_space.Plot(ax)
print(air_space)