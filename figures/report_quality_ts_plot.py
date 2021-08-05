#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:43:22 2018

@author: iregon
"""
import json
import sys
import logging
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import pandas as pd
import datetime


logging.getLogger('plt').setLevel(logging.INFO)
logging.getLogger('mpl').setLevel(logging.INFO)

# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':10})        # controls default text sizes
plt.rc('axes', titlesize=12)     # fontsize of the axes title
plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=9)    # fontsize of the tick labels
plt.rc('ytick', labelsize=9)    # fontsize of the tick labels
plt.rc('figure', titlesize=14)  # fontsize of the figure title

figsize = (7,3)
# END PARAMS ------------------------------------------------------------------


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    config_file = sys.argv[1]
    
    with open(config_file) as cf:
        config = json.load(cf)
    
    file_data = config['file_data']
    file_out = config['file_out']

    data = pd.read_csv(file_data,delimiter='|',header = 0,index_col=[0],parse_dates=[0])
    
    y_med = data['nreports'].max()/2
        
    f, ax = plt.subplots(1, 1,figsize=figsize)
    ax.stackplot(data.index,100*data['0']/data['nreports'],
        100*data['1']/data['nreports'],
        100*data['2']/data['nreports'],
        labels = ['qc passed','qc failed','not checked'], colors=['Grey','Red','SeaShell'],alpha = 0.3,edgecolor=['Grey']*3,linewidth=.3)
    #ax.plot(data['nreports'].rolling(12, center=True).mean(),label='__nolegend__',linewidth = 1,linestyle = ':',color = 'Black',alpha=0.7)
    
    ax.axvline(x=datetime.datetime(1950,1,1),color='Black')
    ax.text(datetime.datetime(1965,1,1),70,'Release 1',fontsize=16,style='italic')
    ax.text(datetime.datetime(1890,1,1),70,'Release 2',fontsize=16,style='italic')
    
    ax.ticklabel_format(axis='y', style='sci',scilimits=(-3,4))
    ax.set_xlim(datetime.datetime(1851,1,1),datetime.datetime(2010,12,31))
    ax.set_ylim(0,100)
    ax.grid(alpha=0.3,color='k',linestyle=':')
    ax.legend(loc='lower left',facecolor = 'white')
    ax.set_ylabel('Percent of reports')
    ax.set_xlabel('Time')
    f.tight_layout()
    plt.savefig(file_out,bbox_inches='tight',dpi = 300)
