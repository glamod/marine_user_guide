#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:43:22 2018

@author: iregon
"""
import os
import sys
import logging
import json
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import datetime
import xarray as xr
from matplotlib.colors import LogNorm

from figures import var_properties


# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':8})# controls default text sizes
plt.rc('axes', titlesize=8)      # fontsize of the axes title
plt.rc('axes', labelsize=8)      #fontsize of the x and y labels
plt.rc('xtick', labelsize=6)     # fontsize of the tick labels
plt.rc('ytick', labelsize=6)     # fontsize of the tick labels
plt.rc('figure', titlesize=10)   # fontsize of the figure title
figsize=(6,6)
# END PARAMS ------------------------------------------------------------------

def is_season_center(month,season):
    if season == 'DJF':
        return month == 1   
    elif season == 'MAM':
        return month == 4
    elif season == 'JJA':
        return month == 7
    elif season == 'SON':
        return month == 10

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
#    dir_data = sys.argv[1]
#    dir_out = sys.argv[2]
    config_file = sys.argv[1]
    
    with open(config_file) as cf:
        config = json.load(cf)
    
    dir_data = config['dir_data']
    dir_out = config['dir_out']
    file_in_id = config['file_in_id']
    file_out_id_sea = config['file_out_id_sea']
    file_out_id_mon = config['file_out_id_mon']
    start_int = config['start']
    stop_int = config['stop']
    start = datetime.datetime(start_int,1,1)
    stop = datetime.datetime(stop_int,12,31)
    tables = config['tables']
    colorbar = config.get('colorbar','magma')

    
    for table in tables:
        logging.info('Plotting table {}'.format(table))
        if table == 'header':
            cbar_label = '#reports'   
        else:
            param = table.split('-')[1]
            cbar_label = '#Observations'
        
        file_pattern = table + file_in_id + '.nc'
        dataset = xr.open_dataset(os.path.join(dir_data,file_pattern))
        
        # Do the aggregations for monthly
        dataset['monthly'] = dataset['counts'].sum(dim='longitude')
        # Do the aggregation for seasonal: do a 3 month rolling sum and then 
        # pick just central months
        dataset['3_mon_counts'] = dataset['counts'].rolling(time=3, center=True).sum()
        #try (to resample to yearly): da.resample(time="AS").sum() -> not straighforward to keep x,y dims 
        for season in ['DJF','MAM','JJA','SON']:
            dataset[season] = dataset['3_mon_counts'].sel(time=is_season_center(dataset['time.month'],season)).sum(dim='longitude')
        
        # Normalize colorbar counts for all tables with respect to total number
        # of reports (header reports)
        min_counts = 1
        if table == 'header': # Use same scale for all params
            max_counts_sea = dataset['3_mon_counts'].sum(dim='longitude').max().data.tolist()
            normalization_f_sea = LogNorm(vmin = min_counts,vmax = max_counts_sea)
            max_counts_mon = dataset['monthly'].max().data.tolist()
            normalization_f_mon = LogNorm(vmin = min_counts,vmax = max_counts_mon)
        
        # Do a grid with the seasonal Hovmoller
        f, axes = plt.subplots(nrows=2, ncols=2, figsize=figsize)
        for i, season in enumerate(['DJF','MAM','JJA','SON']):
            c = 0 if i%2 == 0 else 1
            r = int(i/2)
            dataset[season].sel(time=is_season_center(dataset['time.month'],season)).where(dataset[season]>0).plot.pcolormesh(x = 'time', y = 'latitude',vmin=min_counts,
                       vmax=max_counts_sea, cmap=colorbar,norm = normalization_f_sea,add_colorbar=True,
                       extend='both',ax=axes[c,r],cbar_kwargs={'label':cbar_label})
            axes[c,r].set_title(season)
        f.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig_path = os.path.join(dir_out,table + '-' + file_out_id_sea)
        plt.savefig(fig_path,bbox_inches='tight',dpi = 150)
        plt.close(f)
        
        # Do the monthly separatelly
        f, axes = plt.subplots(nrows=1, ncols=1, figsize=(7,2))
        dataset['monthly'].where(dataset['monthly']>0).plot.pcolormesh(x = 'time', y = 'latitude',vmin=min_counts,
             vmax=max_counts_mon, cmap=colorbar,norm = normalization_f_mon,add_colorbar=True,
             extend='both',ax=axes,cbar_kwargs={'label':cbar_label,'pad':0.01})
        if table == 'header':
            axes.set_title('Reports')
        else:
            axes.set_title(var_properties.var_properties['short_name_upper'][param])
        axes.tick_params(axis='x',labelbottom=True,labelrotation=0) 
        f.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig_path = os.path.join(dir_out,table + '-' + file_out_id_mon)
        plt.savefig(fig_path,bbox_inches='tight',dpi = 150)
        plt.close(f)
