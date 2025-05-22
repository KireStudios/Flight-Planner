from src.airSpace import *
import matplotlib.pyplot as plt

nav_points=AirSpace.load_nav_points('docs/Cat_nav.txt')
# print(nav_points)
nav_segments=AirSpace.load_nav_segments('docs/Cat_seg.txt')
# print(nav_points)
nav_airports=AirSpace.load_nav_airports('docs/Cat_aer.txt')
# print(nav_airports)
air_space=AirSpace()
air_space.pts=nav_points
air_space.seg=nav_segments
air_space.aip=nav_airports
print(air_space.aip[0].SIDs)
fig, ax = plt.subplots()
air_space.Plot(ax)
print(air_space)