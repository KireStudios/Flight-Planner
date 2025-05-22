from src.airSpace import *
import matplotlib.pyplot as plt

nav_points=AirSpace.load_nav_points('docs/Cat_nav.txt')
print(nav_points)
nav_segments=AirSpace.load_nav_segments('docs/Cat_seg.txt')
print(nav_points)
air_space=AirSpace()
air_space.pts=nav_points
air_space.seg=nav_segments
fig, ax = plt.subplots()
air_space.Plot(ax)
print(air_space)