#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:18:42 2019


@author: iregon
"""
import pandas as pd
import itertools
import os
import json
import numpy as np
import logging
import sys
import matplotlib.pyplot as plt

# PARAMS ----------------------------------------------------------------------
font_size_legend = 13
axis_label_size = 13
tick_label_size = 11
title_label_size = 16
figsize=(12, 6)

plt.rc('legend',**{'fontsize':font_size_legend})          # controls default text sizes
plt.rc('axes', titlesize=axis_label_size)     # fontsize of the axes title
plt.rc('axes', labelsize=axis_label_size)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=tick_label_size)    # fontsize of the tick labels
plt.rc('ytick', labelsize=tick_label_size)    # fontsize of the tick labels
plt.rc('figure', titlesize=title_label_size)  # fontsize of the figure title


line_colsi = ['ICOADS','PT selection','C3S']
line_colors_dict = {'ICOADS':'black','PT selection':'LightGray',
                    'C3S':'DarkRed'}

stack_colsi = ['imma invalid','DT invalid','ID invalid']
stack_colors_dict = {'imma invalid':'DarkRed','DT invalid':'DarkOrange',
                     'ID invalid':'yellow'}

## END PARAMS ------------------------------------------------------------------



# FUNCTIONS  ------------------------------------------------------------------

def flip(items, ncol):
    return itertools.chain(*[items[i::ncol] for i in range(ncol)])


def plot_io(data,x0,x1,title,out_file):
    io_df = data.dropna(how='all',axis=1)
    line_cols = [ x for x in line_colsi if x in io_df ]
    line_colors = [ line_colors_dict.get(x) for x in line_cols ]
    stack_cols = [ x for x in stack_colsi if x in io_df ]
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize, dpi=150) 
    for i,line in enumerate(line_cols):
        ax.plot(io_df.index,io_df[line],marker='o',color = line_colors[i],markersize= 12 - 4*i,linewidth=1,zorder = i + 10 )
    
    ax2 = ax.twinx()
    # Only calculate fails percent if any data from source has been selected...
    if 'PT selection' in line_cols:
        for i,col in enumerate(stack_cols):
            if io_df[col].sum() > 0:
                io_df[col + 'p'] = 100*io_df[col].div(io_df['PT selection'].where(io_df['PT selection'] != 0, np.nan),axis=0).replace(np.inf,0).fillna(0)
                ax2.fill_between(io_df.index,0,io_df[col + 'p'].astype('float'), facecolor=stack_colors_dict.get(col),alpha=0.15,interpolate=False,label=col,zorder=i + 2)
                ax2.plot(io_df.index,io_df[col + 'p'].replace(0,np.nan),marker='o',color = stack_colors_dict.get(col),markersize= 1,alpha=0.6,linewidth=1,zorder = i + 2,label='_nolegend_' )
#        stack_col_cols = [ col + 'p' for col in stack_cols ]
#        ax2.stackplot(io_df.index,io_df[stack_col_cols].fillna(0).astype(float).T,labels = stack_cols, colors = stack_colors,alpha=0.2,zorder = 1) # if no fillna., behaves strange 
        
    # Set limits and scale and hide the right one
    ax.set_xlim(x0,x1)
    ax.set_yscale("log")
    ax2.set_xlim(x0,x1)
    
    # Now decorate....
    ax.set_ylabel('no.reports', color='k')
    ax2.set_ylabel('percent invalid', color='k')
    ax.grid(linestyle=":",color='grey')
    axlines, axlabels = ax.get_legend_handles_labels()
    ax2lines, ax2labels = ax2.get_legend_handles_labels()
    ax.legend(flip(axlines + ax2lines,3),flip(axlabels + ax2labels,3),loc='center', bbox_to_anchor=(0.5, -0.15),ncol=3)
    ax.set_zorder(ax2.get_zorder()+1) # put ax in front of ax2
    ax.patch.set_visible(False)
    plt.title(title)
    plt.tight_layout();
    # And save plot and data
    plt.savefig(out_file,bbox_inches='tight',dpi = 300)
    return 



#------------------------------------------------------------------------------

def main():   
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    
    
    sid_dck= sys.argv[1]
    config_file = sys.argv[2]

    
    with open(config_file,'r') as fO:
        config = json.load(fO)  
        

    file_data = os.path.join(config.get('dir_data'),sid_dck,'io_history-ts.psv')
    file_out = os.path.join(config.get('dir_out'),sid_dck,'io_history-ts.png')

    data = pd.read_csv(file_data,delimiter='|',header = 0,index_col=[0],parse_dates=[0])

    title = sid_dck + ' main IO flow'
    plot_io(data,data.index[0],data.index[-1],title,file_out)


if __name__ == '__main__':
    main()
