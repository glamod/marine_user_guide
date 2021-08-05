#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:43:22 2018

@author: iregon
"""
import os
import json
import sys
import logging
from copy import deepcopy
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import matplotlib as mpl
import numpy as np

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import xarray as xr
import cartopy.crs as ccrs

from figures import map_properties

logging.getLogger('plt').setLevel(logging.INFO)
logging.getLogger('mpl').setLevel(logging.INFO)

# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':map_properties.font_size_legend})        # controls default text sizes
plt.rc('axes', titlesize=map_properties.axis_label_size)     # fontsize of the axes title
plt.rc('axes', labelsize=map_properties.axis_label_size)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=map_properties.tick_label_size)    # fontsize of the tick labels
plt.rc('ytick', labelsize=map_properties.tick_label_size)    # fontsize of the tick labels
plt.rc('figure', titlesize=map_properties.title_label_size)  # fontsize of the figure title
# END PARAMS ------------------------------------------------------------------

def read_dataset(file_path,var_properties):
    dataset = xr.open_dataset(file_path,autoclose=True)
        
    if isinstance(var_properties.get('scale'),dict):
        for var in var_properties['scale'].keys():
            scale = var_properties['scale'].get(var,1)
            offset = var_properties['offset'].get(var,0)
            print('{0}. Applying scale {1}, offset {2}'.format(var,str(scale),str(offset)))
            dataset[var] = offset + scale*dataset[var]
    else:
        var = var_properties.get('vars')
        scale = var_properties.get('scale',1)
        offset = var_properties.get('offset',0)
        print('{0}. Applying scale {1}, offset {2}'.format(var,str(scale),str(offset)))
        dataset[var] = offset + scale*dataset[var]    
    return dataset

def map_on_subplot(f,subplot_ax,z,lons,lats,colorpalette = 'jet',colorbar_show = True,
                   colorbar_title = '', colorbar_title_size = 9, 
                   colorbar_label_size = 7, colorbar_orien = 'v', 
                   colorbar_w = 4, cmin_value = None, cmax_value = None, 
                   normalization = 'linear', grid_width = 0.7,
                   grid_label_size = 12, coastline_width = 0.7):
    
    """Plots a map on subplot cartopy axis.
 
    Arguments
    ---------
    f : matplotlib.figure
        Figure to map to
    ax : matplotlib.axis
        Axis to map to
    z : ?
        Values to map
    lons : ? 
        Grid longitudes
    lats : ?
        Grid latitudes
    
    Keyword arguments
    -----------------
     
    colorpalette : str
        The name of the matplolib color palette to use. Defaults to jet
    colorbar_show : bool
        Whether colorbar is plotted (True/False)
    colorbar_title : str
        The colorbar title
    colorbar_title_size : int
        The colorbar title font size
    colorbar_label_size : int
        The colorbar labels' font size
    colorbar_orien : str
        The colorbar orientation (h/v)
    colorbar_w : integer
        Width of the colorbar. Defaults to 4
    cmin_value : numeric, optional
        Min value to use in colorbar normalization. Defaults to xarray min
    cmax_value : numeric, optional
        Max value to use in colorbar normalization. Defaults to xarray max 
    normalization : str
        Normalization to apply to colorbar (linear/log). Defaults to linear 
    grid_width : numeric
        Width of the lat/lon grid line
    grid_label_size : integer
        Font size of the grid labels
    coastline_width : numeric
        Width of the coastline
    
    """
    # Plots a map on subplot cartopy axis
    # The axis is divided (an map re-scaled accordingly) to accomodate a colorbar. Colorbar is only drawn if show_colorbar = True.
    # Otherwise, added axis is made transparent. This axis is always added to keep same scaling between maps in subplots.
    # This colorbar approach so that the colorbar height matches the height of cartopy's axes...!!!!!
    # colorbar_w = percent of axis width: have to declare equal to other subplots in figure so that re-scaling is the same
    #
    # To be used locally: all variables/params to be set in script before invocation (but subplot_axis)
    #
    # Could potentially, more or less easily, choose to have an horiontal colorbar...just a couple of parameters more....
    
    # Make sure we know what z is. Now we control this from the caller
    #cmin_value = np.nanmin(z) if cmin_value is None else cmin_value
    #cmax_value = np.nanmax(z) if cmax_value is None else cmax_value

    if normalization== 'log':
        normalization_f = LogNorm(vmin = cmin_value,vmax = cmax_value)
    else:
        normalization_f = mpl.colors.Normalize(vmin = cmin_value,
                                             vmax = cmax_value)
        
    cmap = plt.get_cmap(colorpalette)    
    subplot_ax.pcolormesh(lons,lats,z,transform = ccrs.PlateCarree(),
                          cmap = cmap, norm = normalization_f, vmin = cmin_value, 
                          vmax = cmax_value)
    
    gl = subplot_ax.gridlines(crs=ccrs.PlateCarree(),color = 'k',
                              linestyle = ':', linewidth = grid_width, 
                              alpha=0.3, draw_labels=True)
    
    subplot_ax.coastlines(linewidth = coastline_width)
    
    gl.xlabels_bottom = False
    gl.ylabels_right = False
    gl.xlabel_style = {'size': grid_label_size}
    gl.ylabel_style = {'size': grid_label_size}
    
    # following https://matplotlib.org/2.0.2/mpl_toolkits/axes_grid/users/overview.html#colorbar-whose-height-or-width-in-sync-with-the-master-axes
    # we need to set axes_class=plt.Axes, else it attempts to create
    # a GeoAxes as colorbar
    divider = make_axes_locatable(subplot_ax)
    new_axis_w = str(colorbar_w) + '%'
    if colorbar_orien == 'v':
        cax = divider.new_horizontal(size = new_axis_w, pad = 0.08,
                                     axes_class=plt.Axes)
        orientation = 'vertical'
    else:
        cax = divider.new_vertical(size = new_axis_w, pad = 0.08, 
                                   axes_class=plt.Axes,pack_start=True)
        orientation = 'horizontal'
        
    f.add_axes(cax)
    
    if colorbar_show:
        #cb_v = plt.colorbar(t1, cax=cax) could do it this way and would work: would just have to add label and tick as 2 last lines below. But would have to do arrangements anyway if we wanted it to be horizontal. So we keep as it is...
        cb = mpl.colorbar.ColorbarBase(cax, cmap = cmap,norm = normalization_f, 
                                       orientation = orientation, extend='both')
        cb.set_label(colorbar_title, size = colorbar_title_size)
        cb.ax.tick_params(labelsize = colorbar_label_size)
    else:
        cax.axis('off')

def map_single(dataset,variable,out_file,**kwargs):
    """Plot xarray on to a map.
 
    Arguments
    ---------
    dataset : xarray.dataset
       xarray dataset with data to map
    variables : list
        List of dataset variables to map, in order.
    out_file : str
        Path to the output file
    
    Keyword arguments
    -----------------
    colorpalette : dict
        The names of the matplolib color pallette to use for each variable        
    colorbar_title : dictionary
        The colorbar titles
    colorbar_orien : str
        h|v 
    cmin_value : dict (numeric), optional
        Min value to use in colorbar normalization for each variable.
        Defaults to variable min.
    cmax_value : dict (numeric), optional
        Max value to use in colorbar normalization for each variable.
        Defaults to variable max.
    normalization : dict
        Normalization for colormap. Defaults to linear
    projection : str
        Projection name to use in map. See map_properties.projections for options.
        Defaults to PlateCarree

    """
    # HOW ARE WE PLOTTING:
    # We plot using matplotlib (not xarray direct plotting) on a cartopy axis
    # Have to do some adjustments to matplotlib because of cartopy.
    # Why cartopy, and not basemap?:   https://github.com/SciTools/cartopy/issues/920
    # But we might face the need of a projection not yet in cartopy......


    # Complete the kwargs
    # The actual projection is set here in the subplots declaration!!!!
    proj = map_properties.projections.get(kwargs['projection']) if kwargs.get('projection') else map_properties.projections.get('PlateCarree')

    kwargs['colorbar_show'] = True
    kwargs['colorbar_w'] = map_properties.single_map['colorbar_width']
    kwargs['grid_label_size'] = map_properties.single_map.get('grid_label_size')
    kwargs['grid_width'] = map_properties.single_map.get('grid_width')
    kwargs['colorbar_label_size'] = map_properties.single_map.get('colorbar_label_size')
    kwargs['colorbar_title_size'] = map_properties.single_map.get('colorbar_title_size')
    kwargs['coastline_width'] = map_properties.single_map.get('coastline_width')
    
    f, ax = plt.subplots(1, 1, subplot_kw=dict(projection=proj),figsize=(14,7))#,dpi = 180)

    print('Mapping {}'.format(variable))  
    var_kwargs = deepcopy(kwargs)
    var_kwargs['colorpalette'] = kwargs.get('colorpalette','jet')
    var_kwargs['colorbar_title'] = kwargs.get('colorbar_title',' ')
    var_kwargs['colorbar_orien'] = kwargs.get('colorbar_orien','h')
    var_kwargs['cmin_value'] = kwargs.get('cmin_value')
    var_kwargs['cmax_value'] = kwargs.get('cmax_value')
    var_kwargs['normalization'] = kwargs.get('normalization','linear')

    z = dataset[variable].values
    lons = dataset[variable]['longitude']
    lats = dataset[variable]['latitude']

    if not kwargs.get('cmin_value'):
        kwargs['cmin_value'] = np.nanmin(z)
    if not kwargs.get('cmax_value'):
        kwargs['cmax_value'] = np.nanmax(z)
    if kwargs['cmin_value'] == kwargs['cmax_value']: # see if we get these from a common var_properties
        kwargs['cmin_value'] = 0
        kwargs['cmax_value'] = 1
    map_on_subplot(f,ax,z,lons,lats,**var_kwargs)
    dpi = 200
    plt.savefig(out_file,bbox_inches='tight',dpi = dpi)
    plt.close()
    print('Done')

    return 0


def map_mosaic(dataset,variables,out_file,**kwargs):
    """Plot xarray on to a map.
 
    Arguments
    ---------
    dataset : xarray.dataset
       xarray dataset with data to map
    variables : list
        List of dataset variables to map, in order.
    out_file : str
        Path to the output file
    
    Keyword arguments
    -----------------
    colorpalette : dict
        The names of the matplolib color pallette to use for each variable        
    colorbar_title : dictionary
        The colorbar titles
    colorbar_orien : str
        h|v 
    cmin_value : dict (numeric), optional
        Min value to use in colorbar normalization for each variable.
        Defaults to variable min.
    cmax_value : dict (numeric), optional
        Max value to use in colorbar normalization for each variable.
        Defaults to variable max.
    normalization : dict
        Normalization for colormap. Defaults to linear
    projection : str
        Projection name to use in map. See map_properties.projections for options.
        Defaults to PlateCarree

    """
    # HOW ARE WE PLOTTING:
    # We plot using matplotlib (not xarray direct plotting) on a cartopy axis
    # Have to do some adjustments to matplotlib because of cartopy.
    # Why cartopy, and not basemap?:   https://github.com/SciTools/cartopy/issues/920
    # But we might face the need of a projection not yet in cartopy......


    # Complete the kwargs
    # The actual projection is set here in the subplots declaration!!!!
    proj = map_properties.projections.get(kwargs['projection']) if kwargs.get('projection') else map_properties.projections.get('PlateCarree')

    kwargs['colorbar_show'] = True
    kwargs['colorbar_w'] = map_properties.mosaic_map['colorbar_width']
    kwargs['grid_label_size'] = map_properties.mosaic_map.get('grid_label_size')
    kwargs['grid_width'] = map_properties.mosaic_map.get('grid_width')
    kwargs['colorbar_label_size'] = map_properties.mosaic_map.get('colorbar_label_size')
    kwargs['colorbar_title_size'] = map_properties.mosaic_map.get('colorbar_title_size')
    kwargs['coastline_width'] = map_properties.mosaic_map.get('coastline_width')
    
    f, ax = plt.subplots(1, len(variables), subplot_kw=dict(projection=proj),figsize=(14,7))#,dpi = 180)
    c = 0
    for var in variables: 
        print('Mapping {}'.format(var))  
        var_kwargs = deepcopy(kwargs)
        var_kwargs['colorpalette'] = kwargs.get('colorpalette',{}).get(var,'jet')
        var_kwargs['colorbar_title'] = kwargs.get('colorbar_title',{}).get(var,' ')
        var_kwargs['colorbar_orien'] = kwargs.get('colorbar_orien','h')
        var_kwargs['cmin_value'] = kwargs.get('cmin_value').get(var)
        var_kwargs['cmax_value'] = kwargs.get('cmax_value').get(var)
        var_kwargs['normalization'] = kwargs.get('normalization').get(var,'linear')

        z = dataset[var].values
        lons = dataset[var]['longitude']
        lats = dataset[var]['latitude']

        if not kwargs.get('cmin_value'):
            kwargs['cmin_value'] = np.nanmin(z)
        if not kwargs.get('cmax_value'):
            kwargs['cmax_value'] = np.nanmax(z)
        if kwargs['cmin_value'] == kwargs['cmax_value']: # see if we get these from a common var_properties
            kwargs['cmin_value'] = 0
            kwargs['cmax_value'] = 1
        map_on_subplot(f,ax[c],z,lons,lats,**var_kwargs)
        c += 1
    print('Done')
    wspace = 0.08# if qc_mode else 0.05
    dpi = 200 #if qc_mode else 300
    plt.subplots_adjust(wspace=wspace,hspace=0.05)#  Force small separation (default is .2, to keep in mind "transparent" colorbar between subplots....THIS WILL DEPEND ON THE FIGURE WIDTH
    print('Saving')
    plt.savefig(out_file,bbox_inches='tight',dpi = dpi)# 'tight' here, not in plt.tight_layout: here it realizes the new size because of add_axes, but not in plt.tight_layout..
    print('Done')
    plt.close()
    return 0


if __name__ == "__main__":

    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    dir_data = sys.argv[1]
    dir_out = sys.argv[2]
    config_file = sys.argv[3]
    
    with open(config_file) as cf:
        kwargs = json.load(cf)
     
    figures = list(kwargs.get('figures').keys())
    no_figures = len(figures)
    non_avail_figures = 0
   
    for figurei in figures:
        logging.info('Figure: {}'.format(figurei))
        
        figure_kwargs = kwargs['figures'].get(figurei)
        dataset_path = os.path.join(dir_data,figure_kwargs.get('nc_file'))
        out_file = os.path.join(dir_out,figure_kwargs.get('out_file'))
        variables = figure_kwargs.get('vars')
        layout = 'mosaic' if isinstance(variables,list) else 'single'
       
        if not os.path.isfile(dataset_path):
            non_avail_figures += 1
            logging.warning('No nc file for figure {0}: {1}'.format(figurei,dataset_path))
            continue
 
        dataset = read_dataset(dataset_path,figure_kwargs)
        
        figure_kwargs.pop('nc_file')
        figure_kwargs.pop('out_file')
        figure_kwargs.pop('vars')
        figure_kwargs.pop('scale',None)
        figure_kwargs.pop('offset',None)
        
        if layout == 'mosaic':
            status = map_mosaic(dataset,variables,out_file, **figure_kwargs)
            if status != 0:
                logging.error('On map {}'.format(figurei))
                sys.exit(1)
        else:
            status = map_single(dataset,variables,out_file, **figure_kwargs)
            if status != 0:
                logging.error('On map {}'.format(figurei))
                sys.exit(1)

    if non_avail_figures == no_figures:
        logging.error('No nc files found for figures: {}'.format(','.join(figures)))
        sys.exit(1)
    else:
        sys.exit(0)
