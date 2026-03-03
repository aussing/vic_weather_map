import os
import sys
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cmasher as cmr
from datetime import datetime
import schedule

sys.path.insert(0, './')
from vic_weather_map import observations

def main_loop():

    obs_data = observations.Observations('Vic')
    # print(obs_data.acknowedgment, '\n')

    with open("ID_LIST") as f:
      lines = f.readlines()
      ID_array = np.genfromtxt(lines,dtype=str)

    station_id_list = []
    for station_num in range(len(obs_data.stations())):
        station_id_list.append(obs_data.stations()[station_num]['wmo-id'])
    station_id_list = np.array(station_id_list)

    fig,axs = plt.subplots(figsize=(11,8))
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
        wind_speed      = float(obs_data.wind_speed(station_id))
        
        if wind_speed > 0:
            wind_direction  = float(obs_data.wind_drection_deg(station_id))+90
            dx = np.cos(wind_direction*np.pi/180)  * wind_speed 
            dy = np.sin(wind_direction*np.pi/180)  * wind_speed 
            plt.arrow(x,y, dx=dx,dy=dy, width=4, alpha=0.5)
        
        plt.scatter(x,y, c='k',s=0.01)
        plt.text(x+5,y+5, air_temperature, size='x-large', weight='bold', color=cmap(norm(air_temperature)))

    axs.set_axis_off()
    fig.tight_layout()

    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m_%b")
    day = now.strftime("%d_%a")
    if not os.path.exists(f'./snapshots/{year}/'): 
        os.makedirs(f'./snapshots/{year}')
    if not os.path.exists(f'./snapshots/{year}/{month}/'): 
        os.makedirs(f'./snapshots/{year}/{month}/')
    if not os.path.exists(f'./snapshots/{year}/{month}/{day}/'):    
        os.makedirs(f'./snapshots/{year}/{month}/{day}/')

    formatted_file_name = now.strftime("%H_%M")
    formatted_snapshot_title = now.strftime("%I:%M %p - %d/%B/%Y ")
    plt.text(len_x/2.5, len_y/10, formatted_snapshot_title, size='xx-large',weight='bold')
    
    folder_file_name = './snapshots/' + f'{year}/{month}/{day}/' + formatted_file_name
    fig.savefig(f'{folder_file_name}.png',dpi=250)

    print(f'{folder_file_name}.png saved successfully!')

if __name__ == "__main__":
    
    if not os.path.exists('./snapshots'):
        os.makedirs('./snapshots')

    main_loop()
    schedule.every(10).minutes.do(main_loop)
    while True:
        schedule.run_pending()
    