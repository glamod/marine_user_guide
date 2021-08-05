#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:43:22 2018

@author: iregon
"""
import os
import sys
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import datetime
import itertools
import xarray as xr
from dateutil.relativedelta import relativedelta


from figures import var_properties

logging.getLogger('plt').setLevel(logging.INFO)
logging.getLogger('mpl').setLevel(logging.INFO)

# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':12})        # controls default text sizes
plt.rc('axes', titlesize=12)     # fontsize of the axes title
plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('figure', titlesize=14)  # fontsize of the figure title
# END PARAMS ------------------------------------------------------------------

def create_index(time):
    start_yr = time.dt.year.values[0]
    start_mo = time.dt.month.values[0]
    stop_yr = time.dt.year.values[-1]
    stop_mo = time.dt.month.values[-1]
    nmonths = ((stop_yr - start_yr) * 12) + stop_mo - start_mo + 1
    
    return [ datetime.datetime(start_yr,start_mo,1) + relativedelta(months=+i) for i in range(0,nmonths) ]   

def flip(items, ncol):
    return itertools.chain(*[items[i::ncol] for i in range(ncol)])

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    sid_dck = sys.argv[1]
    config_file = sys.argv[2]
    
    with open(config_file) as cf:
        config = json.load(cf)
    
    dir_data = os.path.join(config['dir_data'],sid_dck)
    dir_out = os.path.join(config['dir_out'],sid_dck)
    file_in_id = config['file_in_id']
    file_out = config['file_out']
     
    filtered = False
    log_scale_reports = True
    n_reports_color = 'Black'
    bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
        
    observation_tables = ['observations-at','observations-sst','observations-dpt',
                          'observations-slp','observations-ws','observations-wd']   
    table = 'header'
    file_pattern = table + file_in_id + '.nc'
    hdr_dataset = xr.open_dataset(os.path.join(dir_data,file_pattern))
    # Fill gaps in periods with NaN to avoid interpolation in plots
    index = create_index(hdr_dataset.time)
    hdr_dataset = hdr_dataset.reindex(time=index)
    header_n_reports = hdr_dataset['counts'].sum(dim=['longitude','latitude'])
    header_n_reports_max = header_n_reports.max()
    if filtered:
        header_n_reports = header_n_reports.rolling(time=12, center=True,min_periods=1).mean()
        
    header_n_reports_max = header_n_reports.max()    
    
    f, ax = plt.subplots(3, 2, figsize=(14,10),sharex=True,sharey=True)# 
    for i,table in enumerate(observation_tables):
        logging.info('Table: {}'.format(table))
        obs_avail = True
        var = table.split('-')[1]
        title = var_properties.var_properties['long_name_upper'][var]
        c = 0 if i%2 == 0 else 1
        r = int(i/2)
        file_pattern = table + file_in_id + '.nc'
        if not os.path.isfile(os.path.join(dir_data,file_pattern)):
            obs_avail = False
            
        if obs_avail:
            dataset = xr.open_dataset(os.path.join(dir_data,file_pattern))
            # Fill gaps in periods with NaN to avoid interpolation in plots
            index = create_index(dataset.time)
            dataset  = dataset.reindex(time=index)
            n_cells = dataset['counts'].where(dataset['counts'] > 0).count(dim=['longitude','latitude'])
            n_reports = dataset['counts'].sum(dim=['longitude','latitude'])
            if filtered:
                logging.info('...filtering time series')
                n_reports = n_reports.rolling(time=12, center=True,min_periods=1).mean()
           
        logging.info('...plotting time series')
        header_n_reports.plot(ax=ax[r,c],color=n_reports_color,zorder = 1 ,label='#reports',linewidth=3,alpha=0.15)
        #header_n_reports.to_series().plot.bar(ax=ax[r,c],color=n_reports_color,zorder = 1 ,label='#reports',linewidth=0,alpha=0.15)
        if obs_avail:
            n_reports.plot(ax=ax[r,c],color=n_reports_color,zorder = 3 ,label='#obs parameter',linewidth=1)
            #n_reports.to_series().plot.bar(ax=ax[r,c],color=n_reports_color,zorder = 3 ,label='#obs parameter',linewidth=0)
                           
        if not obs_avail:
            ax[r,c].text(0.5, 0.5,'No data',horizontalalignment='center',
                          verticalalignment='center',transform = ax[r,c].transAxes,size=20,bbox=bbox_props)
        
        ax[r,c].set_ylabel('#Observations', color=n_reports_color)
        ax[r,c].tick_params(axis='y', colors=n_reports_color)
        ax[r,c].set_title(title, color='k')
        
        if log_scale_reports:
            ax[r,c].set_yscale('log')

        
        
        ax[r,c].tick_params(axis='x',labelbottom=True,labelrotation=0)
        ax[r,c].tick_params(axis='y',labelleft=True,labelrotation=0)
        
    lines, labels = ax[r,c].get_legend_handles_labels() 
    lines = [lines[1]] + [lines[0]]
    labels = [labels[1]] + [labels[0]]
    f.legend(flip(lines,4),flip(labels,4),loc='lower center', ncol=4)
    f.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    fig_path = os.path.join(dir_out,file_out)
    plt.savefig(fig_path,bbox_inches='tight',dpi = 300)
    plt.close(f)
