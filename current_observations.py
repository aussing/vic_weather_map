import sys
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cmasher as cmr
from datetime import datetime

sys.path.insert(0, './')
from vic_weather_map import observations

# Read and parse the XML file ftp://ftp.bom.gov.au/anon/gen/fwo/IDV60920.xml
obs_data = observations.Observations('Vic')
# print(obs_data.acknowedgment, '\n')

with open("ID_LIST") as f:
  lines = f.readlines()
  ID_array = np.genfromtxt(lines,dtype=str)

station_id_list = []
for station_num in range(len(obs_data.stations())):
    station_id_list.append(obs_data.stations()[station_num]['wmo-id'])
station_id_list = np.array(station_id_list)


fig,axs = plt.subplots()
img = np.asarray(Image.open('./vic_map.png'))
plt.imshow(img,alpha=0.5)

len_x, len_y = img.shape[1], img.shape[0]
min_lon, max_lon = 140.963583, 149.975605
min_lat, max_lat = -33.980700, -39.136011

cmap = cmr.torch
norm = mpl.colors.Normalize(vmin=5, vmax=40)
for id_num, station_id in enumerate(ID_array):
    # print(station_id, obs_data.station_attribute(station_id, 'description'))
    
    idx = np.where(station_id == station_id_list)[0][0]
    x,y = float(obs_data.stations()[idx]['lon']), float(obs_data.stations()[idx]['lat'])
    x,y = (x-min_lon)/(max_lon-min_lon)*len_x , (y-min_lat)/(max_lat-min_lat)*len_y
    
    air_temperature = float(obs_data.air_temperature(station_id))
    wind_direction  = float(obs_data.wind_drection_deg(station_id))+90
    wind_speed      = float(obs_data.wind_speed(station_id))
    dx = np.cos(wind_direction*np.pi/180)  * 20
    dy = np.sin(wind_direction*np.pi/180)  * 20
    plt.scatter(x,y, c='k',s=0.01)
    plt.text(x+5,y+5, air_temperature, size='large', weight='bold', color=cmap(norm(air_temperature)))
    plt.arrow(x,y, dx=dx,dy=dy, width=4, alpha=0.5)

now = datetime.now()
formatted_string = now.strftime("%Y_%m_%d_%H_%M")

axs.set_axis_off()
fig.tight_layout()
fig.savefig(f'./snapshots/{formatted_string}.png',dpi=250)

