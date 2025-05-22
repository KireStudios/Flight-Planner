from src.airSpace import *
import matplotlib.pyplot as plt

air_space=AirSpace()
air_space.read_airspace('docs/Cat_nav.txt', 'docs/Cat_seg.txt', 'docs/Cat_aer.txt')

fig, ax = plt.subplots(2, 3, figsize=(12, 6))
air_space.PlotNeighbors(ax[0][0],10673)

air_space.PlotReachability(ax[0][1], 313)

path = air_space.FindShortestPath(1663, 14920)
air_space.PlotPath(ax[0][2], path)

air_space.Plot(ax[1][0])


# print(air_space)
plt.show()