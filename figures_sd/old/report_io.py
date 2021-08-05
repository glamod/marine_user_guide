#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:18:42 2019


@author: iregon
"""

# HAVE TO EVAL FAILED NOT ONLY AS LOC FAILED + ALL OBS_FAILED
# SOMETIMES THERE ARE REPORTS WITH NO OBS VALUES!!! THESE
# ARE SET TO REPORT_QUALITY == 1 BY LEVEL1E! BUT LOC_FAILED CAN
# BE PASSED AND THERE ARE NO OBS VALUES QUALITY FLAGS TO EVALUATE>
# THIS IS THE REASON OF THE APPEARANCE OF SOME REPORT_QUALITY PLOTS (009-116)

import cdm
import glob
import datetime
import pandas as pd
import itertools
import os
import json
import numpy as np
import logging
import sys
import matplotlib.pyplot as plt
#plt.switch_backend('agg')


script_path = os.path.dirname(os.path.realpath(__file__))

# PARAMS ----------------------------------------------------------------------

with open(os.path.join(script_path,'var_properties.json'),'r') as f:
    properties_var = json.load(f)
    
params = ['at','sst','dpt','wbt','slp','ws','wd']
kdims = ['latitude', 'longitude']
cdm_columns = {'header':['report_id','duplicate_status','report_quality','location_quality']}
for param in params:
    cdm_columns['observations-' + param] = ['report_id','quality_flag']
               

df_list = ['report_no_all','report_no_best','duplicate_status','report_quality','location_quality','io_history']
status_list = ['duplicate_status','report_quality','location_quality']
status_plot = ['duplicate_status','report_quality']
# state this as in order we want to plot
df_columns = {'report_no_all': ['header'] + [ 'observations-' + i for i in params ],
              'report_no_best': ['header'] + [ 'observations-' + i for i in params ],
              'duplicate_status': ['total'] + [ str(i) for i in range(0,5) ],
              'report_quality': ['total','10','11'] + [ str(i) for i in range(0,4) ],
              'location_quality': ['total'] + [ str(i) for i in range(0,4) ],
              'io_history': ['ICOADS','PT selection','l1c-invalid','md-invalid','dt-invalid','id-invalid','invalid','valid','C3S']} # TBD 

labels = {'duplicate_status':{'0':'unique', '1':'best','2':'dup','3':'worst','4':'unchecked'},
          'report_quality':{'0':'pass', '10':'loc-fail','11':'par-fail','2':'unchecked','3':'missing'}}

colors = {'duplicate_status':{'0':'green', '1':'Chartreuse','2':'OrangeRed','3':'Indigo','4':'Yellow'},
          'report_quality':{'0':'Chartreuse', '10':'OrangeRed','11':'Indigo','2':'Yellow','3':'Yellow'}}

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
## END PARAMS ------------------------------------------------------------------



# FUNCTIONS  ------------------------------------------------------------------

def flip(items, ncol):
    return itertools.chain(*[items[i::ncol] for i in range(ncol)])

def plot_io(data,x0,x1,title,out_file):
    io_df = data.dropna(how='all',axis=1)
    line_colsi = ['ICOADS','PT selection','C3S']
    line_cols = [ x for x in line_colsi if x in io_df ]
    line_colors_dict = {'ICOADS':'black','PT selection':'LightGray','C3S':'DarkRed'}
    line_colors = [ line_colors_dict.get(x) for x in line_cols ]
    stack_colsi = ['md-invalid','dt-invalid','id-invalid']
    stack_cols = [ x for x in stack_colsi if x in io_df ]
    stack_colors_dict = {'md-invalid':'DarkRed','dt-invalid':'DarkOrange','id-invalid':'yellow'}
#    stack_colors = [ stack_colors_dict.get(x) for x in stack_cols ]
    
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

def plot_no_reports(data,x0,x1,title,out_file):
    #3.- No.reports plot    
    no_df = data.dropna(how='all',axis=1)
    plot_tables = [ x for x in no_df if x != 'header' ] 
    param_colors = [ properties_var.get('color').get(x.split('-')[1]) for x in plot_tables  ]
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize, dpi=150) 
    # Do it in separate axis to be able to control labeling in legend.....should be able to
    # to in a different way...
    if no_df['header'].sum()>0:
        #ax.fill_between(no_df.loc[no_df['header']>0].index,0,no_df['header'].loc[no_df['header']>0].astype('float'), facecolor='LightGray',alpha=0.25,interpolate=False,label='total reports',zorder=0) 
        ax.fill_between(no_df.index,0,no_df['header'].astype('float'), facecolor='Linen',alpha=0.8,interpolate=False,label='total reports',zorder=0)
    
    ax2 = ax.twinx()
    for i,table in enumerate(plot_tables): 
        ax2.plot(no_df.index,no_df[table],marker='o',markersize= 12 - 2*i,color = param_colors[i], linewidth=1,zorder = i + 1 )
    # Set limits and scale and hide the right one
    minrep = no_df.min().min()
    maxrep = no_df['header'].max()
    miny = int(np.max([1,-0.05*minrep + minrep]))
    maxy = int(maxrep + 0.5*maxrep )
    ax.set_xlim(x0,x1)
    ax.set_ylim(miny,maxy )
    ax.set_yscale("log")
    ax2.set_ylim(miny, maxy )
    ax2.set_yscale("log")
    ax2.get_yaxis().set_visible(False)
    
    # Now decorate....
    ax.set_ylabel('no.reports', color='k')
    ax.grid(linestyle=':',which='both',color='grey')
    axlines, axlabels = ax.get_legend_handles_labels()    
    ax2lines, ax2labels = ax2.get_legend_handles_labels()
    ax.legend(axlines + ax2lines,axlabels + ax2labels,loc='center', bbox_to_anchor=(0.5, -0.15),ncol=4)
    plt.title(title)  
    plt.tight_layout();
    # And save plot and data
    plt.savefig(out_file,bbox_inches='tight',dpi = 300)

    return

#------------------------------------------------------------------------------

def main():   
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    try:
        config_file = sys.argv[1]
#        data_path = sys.argv[1]
#        release = sys.argv[2]
#        update = sys.argv[3]
#        source = sys.argv[4]
#        level = sys.argv[5]
#        sid_dck = sys.argv[6] 
#        sid_periods_file = sys.argv[7] # either release initial or level2 config file
#        out_path = sys.argv[8]
    except Exception as e:
        logging.error(e, exc_info=True)
        return
    
    with open(config_file,'r') as fO:
        config = json.load(fO)  
        
    paths = {}
    paths['data'] = os.path.join(config['dir_data'],config['sid_dck'])
    paths['reports'] = os.path.join(config['dir_out'],config['sid_dck'])
    paths['level1a_ql'] = os.path.join(config['dir_level1a_ql'],config['sid_dck'])
    paths['level1c_ql'] = os.path.join(config['dir_level1a_ql'],config['sid_dck'])
    # Get periods for sid-dck (year_init, year_end)    
    yr_ini = config['start'] 
    yr_end = config['stop'] 
    sid_dck = config['sid_dck']
    
    # Initialize the structure where the TSs is stored
    index = pd.date_range(start=datetime.datetime(int(yr_ini),1,1),end=datetime.datetime(int(yr_end),12,1),freq='MS')
    df_dict = { df:pd.DataFrame(index=index,columns = df_columns.get(df)) for df in df_list }
         
    # Loop through time range:
    level_data = False
    for date in index:
        
        yr = date.year
        mm = date.month
        yr_mo = date.strftime('%Y-%m') 
        # First final product we are looking at (inarg level)
        hdr_path = os.path.join(paths['data'],'-'.join(['header',str(yr),str(mm).zfill(2)]) + '-*.psv')
        hdr_files = glob.glob(hdr_path)
        if len(hdr_files) > 1:
            logging.error('Multiple files found for {0}-{1}'.format(str(yr),str(mm).zfill(2))) 
            logging.error('{}'.format(','.join(hdr_files)))
            sys.exit(1)
        if len(hdr_files) == 1:
            hdr_file = hdr_files[0]
            level_data = True
            mon_table = cdm.table_reader.table_reader.read_tables(hdr_file,col_subset=cdm_columns)
               
            for status in status_list:
                counts = mon_table['header'][status].value_counts()
                df_dict[status].loc[date,counts.index.values] = counts
                df_dict[status].loc[date,'total'] = mon_table['header']['report_id'].count()
            
            df_dict['report_no_all'].loc[date,'header'] = df_dict[status].loc[date,'total']
            loc_qcr_ok = mon_table.loc[mon_table['header']['report_quality'] == '0'].index
            df_dict['report_no_best'].loc[date,'header'] = len(loc_qcr_ok)
            for param in params:
                table = 'observations-' + param
                if table in mon_table.columns.levels[0]:
                    df_dict['report_no_all'].loc[date,table] = mon_table[table]['report_id'].count()
                    loc_ok = mon_table.loc[(mon_table['header']['report_quality'] == '0') & (mon_table[table]['quality_flag'] == '0')].index
                    df_dict['report_no_best'].loc[date,table] = len(loc_ok)
        else:
            logging.warning('No level data found for {0}-{1}'.format(str(yr),str(mm).zfill(2)))    
        # Now io history
        # 1. Source data, what we selected from there and waht was invalid at source: level1a
        file = glob.glob(os.path.join(paths['level1a_ql'],'-'.join([str(yr),str(mm).zfill(2)]) + '-*.json'))
        if len(file) == 1:
            with open(file[0]) as fileObj:
                level_dict = json.load(fileObj)  
            level_dict = level_dict.get(yr_mo)
            df_dict['io_history'].loc[date,'ICOADS'] = level_dict.get('read',{}).get('total')
            df_dict['io_history'].loc[date,'PT selection'] = level_dict.get('pre_selected',{}).get('total')
            df_dict['io_history'].loc[date,'md-invalid'] = level_dict.get('invalid',{}).get('total')
        # 2. Now data that was dropped because it was invalid: level1c
        file = glob.glob(os.path.join(paths.get('level1c_ql'),'-'.join([str(yr),str(mm).zfill(2)]) + '-*.json'))
        if len(file) > 0:
            with open(file[0]) as fileObj:
                level_dict = json.load(fileObj)
            level_dict = level_dict.get(yr_mo)
            df_dict['io_history'].loc[date,'dt-invalid'] = level_dict.get('invalid',{}).get('report_timestamp')
            df_dict['io_history'].loc[date,'id-invalid'] = level_dict.get('invalid',{}).get('primary_station_id')
            df_dict['io_history'].loc[date,'l1c-invalid'] = level_dict.get('invalid',{}).get('total')
        
        df_dict['io_history'].loc[date,'invalid'] = df_dict['report_no_all'].loc[date,'header']    
        df_dict['io_history'].loc[date,'C3S'] = df_dict['report_no_all'].loc[date,'header']    
    
    # merge all invalids in io_history
    df_dict['io_history'].loc[:,'invalid'] = df_dict['io_history'][['md-invalid','l1c-invalid']].sum(axis=1)
#    df_dict['io_history'].loc[:,'invalid'] = df_dict['io_history'][['md-invalid','dt-invalid','id-invalid']].sum(axis=1)
    df_dict['io_history'].loc[:,'valid'] = df_dict['io_history']['PT selection'] - df_dict['io_history']['invalid']
    # merge position fails with report_quality fails
    df_dict['report_quality'].loc[:,'10'] = df_dict['location_quality'].loc[:,'2']
    df_dict['report_quality'].loc[:,'11'] = df_dict['report_quality'].loc[:,'1'] - df_dict['report_quality'].loc[:,'10'] 
    
    
    #1.- Status plots: send to function!
    if level_data:
        for i,status in enumerate(status_plot):
            status_df = df_dict[status].dropna(how='all',axis=1)
            
            if len(status_df) == 0:
                continue
            
            plt_cols = [ x for x in labels.get(status).keys() if x in status_df ]
            plt_labels = [ labels.get(status).get(x) for x in plt_cols ]
            plt_colors = [ colors.get(status).get(x) for x in plt_cols ]
            
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize, dpi=150) 
            for line in plt_cols:
    #            ax.plot(status_df.loc[status_df[line]>0].index,status_df[line].loc[status_df[line]>0],color= colors.get(status).get(line), linewidth = 1, markersize = 1,alpha=0.8,marker = '.',zorder = 1,label = labels.get(status).get(line) )
                ax.plot(status_df.index,status_df[line],color= colors.get(status).get(line), linewidth = 1, markersize = 2,alpha=1,marker = '.',zorder = 1,label = labels.get(status).get(line) )
            ax.set_xlim(index[0], index[-1])
            ax.set_yscale('log')
            ax.set_ylabel('no.reports', color='k')
            ax.legend(loc='center', bbox_to_anchor=(0.5, -0.15),ncol=5)
            
            ax2 = ax.twinx()
            ax2.stackplot(df_dict[status].index,100*status_df[plt_cols].div(status_df['total'],axis=0).fillna(0).astype(float).T,labels = plt_labels, colors = plt_colors,alpha=0.1,zorder = 2) # if no fillna., behaves strange    
            ax2.set_xlim(index[0], index[-1])
            ax2.set_ylim(0,100)
            ax2.set_ylabel('percent', color='k')
          
            plt.title(sid_dck + ' ' + status)
            plt.tight_layout();
            out_file = os.path.join(paths.get('reports'), '-'.join([status,'ts.png']))
            plt.savefig(out_file,bbox_inches='tight',dpi = 300)
            out_file = os.path.join(paths.get('reports'), '-'.join([status,'ts.psv']))
            status_df.to_csv(out_file,sep='|',index_label='yr-mo')
    
    
    #2.- io history plots 
    title = sid_dck + ' main IO flow'
    out_file = os.path.join(paths.get('reports'), '-'.join(['io_history','ts.png']))
    plot_io(df_dict['io_history'],index[0],index[-1],title,out_file)
    out_file = os.path.join(paths.get('reports'), '-'.join(['io_history','ts.psv']))
    df_dict['io_history'].dropna(how='all',axis=1).to_csv(out_file,sep='|',index_label='yr-mo')    
    
    #3.- No.reports plot
    if level_data:
        out_file = os.path.join(paths.get('reports'), '-'.join(['no_reports','all-ts.png']))
        title = sid_dck + ' C3S data (all qualities)'
        plot_no_reports(df_dict['report_no_all'],index[0], index[-1],title,out_file)
        out_file = os.path.join(paths.get('reports'), '-'.join(['no_reports','all-ts.psv']))
        df_dict['report_no_all'].dropna(how='all',axis=1).to_csv(out_file,sep='|',index_label='yr-mo')

        out_file = os.path.join(paths.get('reports'), '-'.join(['no_reports','optimal-ts.png']))
        title = sid_dck + ' C3S data (recommended quality)'
        plot_no_reports(df_dict['report_no_best'],index[0], index[-1],title,out_file)
        out_file = os.path.join(paths.get('reports'), '-'.join(['no_reports','optimal-ts.psv']))
        df_dict['report_no_best'].dropna(how='all',axis=1).to_csv(out_file,sep='|',index_label='yr-mo')

if __name__ == '__main__':
    main()
