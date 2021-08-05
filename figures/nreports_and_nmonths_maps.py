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

logging.getLogger('plt').setLevel(logging.INFO)
logging.getLogger('mpl').setLevel(logging.INFO)

# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':11})        # controls default text sizes
plt.rc('axes', titlesize=11)     # fontsize of the axes title
plt.rc('axes', labelsize=11)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=9)    # fontsize of the tick labels
plt.rc('ytick', labelsize=9)    # fontsize of the tick labels
plt.rc('figure', titlesize=14)  # fontsize of the figure title

map_properties = {}
map_properties['figsize'] = (4,4)
map_properties['colorbar_show'] = True
map_properties['colorbar_w'] = 5
map_properties['grid_label_size'] = 7
map_properties['grid_width'] = 0.6
map_properties['colorbar_label_size'] = 9
map_properties['colorbar_title_size'] = 8
map_properties['coastline_width'] = 0.5

projections = {}
projections['PlateCarree'] = ccrs.PlateCarree()
projections['Robinson'] = ccrs.Robinson()
projections['Mollweide'] = ccrs.Mollweide()
# END PARAMS ------------------------------------------------------------------

def map_on_subplot(f,subplot_ax,z,lons,lats,colorpalette = 'jet',
                   colorbar_title = '', colorbar_orien = 'v', 
                   cmin_value = None, cmax_value = None, 
                   normalization = 'linear'):
    
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
    colorbar_title : str
        The colorbar title
    colorbar_orien : str
        The colorbar orientation (h/v)
    cmin_value : numeric, optional
        Min value to use in colorbar normalization. Defaults to xarray min
    cmax_value : numeric, optional
        Max value to use in colorbar normalization. Defaults to xarray max 
    normalization : str
        Normalization to apply to colorbar (linear/log). Defaults to linear 
    
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
    
    try:
        gl = subplot_ax.gridlines(crs=ccrs.PlateCarree(),color = 'k',
                               linestyle = ':', linewidth = map_properties['grid_width'], 
                               alpha=0.3, draw_labels=True)
    
    except:
        gl = subplot_ax.gridlines(crs=ccrs.PlateCarree(),color = 'k',
                              linestyle = ':', linewidth = map_properties['grid_width'],
                              alpha=0.3, draw_labels=False)
    
    subplot_ax.coastlines(linewidth = map_properties['coastline_width'])
    
    gl.xlabels_bottom = False
    gl.ylabels_right = False
    gl.xlabel_style = {'size': map_properties['grid_label_size']}
    gl.ylabel_style = {'size': map_properties['grid_label_size']}
    
    # following https://matplotlib.org/2.0.2/mpl_toolkits/axes_grid/users/overview.html#colorbar-whose-height-or-width-in-sync-with-the-master-axes
    # we need to set axes_class=plt.Axes, else it attempts to create
    # a GeoAxes as colorbar
    divider = make_axes_locatable(subplot_ax)
    new_axis_w = str(map_properties['colorbar_w']) + '%'
    if colorbar_orien == 'v':
        cax = divider.new_horizontal(size = new_axis_w, pad = 0.08,
                                     axes_class=plt.Axes)
        orientation = 'vertical'
    else:
        cax = divider.new_vertical(size = new_axis_w, pad = 0.08, 
                                   axes_class=plt.Axes,pack_start=True)
        orientation = 'horizontal'
        
    f.add_axes(cax)
    
    if map_properties['colorbar_show']:
        #cb_v = plt.colorbar(t1, cax=cax) could do it this way and would work: would just have to add label and tick as 2 last lines below. But would have to do arrangements anyway if we wanted it to be horizontal. So we keep as it is...
        cb = mpl.colorbar.ColorbarBase(cax, cmap = cmap,norm = normalization_f, 
                                       orientation = orientation, extend='both')
        cb.set_label(colorbar_title, size = map_properties['colorbar_title_size'])
        cb.ax.tick_params(labelsize = map_properties['colorbar_label_size'])
    else:
        cax.axis('off')

def map_single(dataarray,out_file,**kwargs):
    """Plot xarray on to a map.
 
    Arguments
    ---------
    dataarray : xarray.DataArray
       xarray dataarray with data to map
    out_file : str
        Path to the output file
    
    Keyword arguments
    -----------------
    colorpalette : dict
        The name of the matplolib color pallette to use      
    colorbar_title : dictionary
        The colorbar title
    colorbar_orien : str
        h|v 
    cmin_value : numeric, optional
        Min value to use in colorbar normalization for each variable.
        Defaults to dataarray min
    cmax_value : numeric, optional
        Max value to use in colorbar normalization for each variable.
        Defaults to dataarray max
    normalization : str
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
    proj = projections.get(kwargs['projection']) if kwargs.get('projection') else projections.get('PlateCarree')
    kwargs.pop('projection',None)
    
    f, ax = plt.subplots(1, 1, subplot_kw=dict(projection=proj),figsize=map_properties['figsize'])#,dpi = 180)
 
    var_kwargs = deepcopy(kwargs)
    var_kwargs['colorpalette'] = kwargs.get('colorpalette','jet')
    var_kwargs['colorbar_title'] = kwargs.get('colorbar_title',' ')
    var_kwargs['colorbar_orien'] = kwargs.get('colorbar_orien','h')
    var_kwargs['cmin_value'] = kwargs.get('cmin_value')
    var_kwargs['cmax_value'] = kwargs.get('cmax_value')
    var_kwargs['normalization'] = kwargs.get('normalization','linear')

    z = dataarray.values
    lons = dataarray['longitude']
    lats = dataarray['latitude']

    if not var_kwargs.get('cmin_value'):
        var_kwargs['cmin_value'] = np.nanmin(z)
    if not var_kwargs.get('cmax_value'):
        var_kwargs['cmax_value'] = np.nanmax(z)
    if var_kwargs['cmin_value'] == var_kwargs['cmax_value']: # see if we get these from a common var_properties
        var_kwargs['cmin_value'] = 0
        var_kwargs['cmax_value'] = 1
    map_on_subplot(f,ax,z,lons,lats,**var_kwargs)
    dpi = 200
    plt.savefig(out_file,bbox_inches='tight',dpi = dpi)
    plt.close()
    print('Done')

    return 0


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    config_file = sys.argv[1]
    
    with open(config_file) as cf:
        config = json.load(cf)
    
    dir_data = config['dir_data']
    dir_out = config['dir_out']
    min_obs = config.get('min_obs',1)
    
    tables = list(config.get('tables').keys())
   
    for tablei in tables:
        logging.info('Figure: {}'.format(tablei))
        dataset_path = os.path.join(dir_data,config['tables'][tablei]['nc_file'])
        
        dataset = xr.open_dataset(dataset_path,autoclose=True)
               
        logging.info('Aggregating over time dim...')
        global_nobs = dataset['counts'].sum(dim='time')
        global_nmonths = (dataset['counts']>=min_obs).sum(dim = 'time')

        kwargs = {}
        kwargs['projection'] = config['projection']
        kwargs['colorbar_orien'] = config['colorbar_orien']
        kwargs['normalization'] = 'linear'
        
        if tablei == 'header':
            config['cmin_value_nobs'] = 1
            config['cmax_value_nobs'] = global_nobs.max()
            config['cmin_value_nmonths'] = 1
            config['cmax_value_nmonths'] = global_nmonths.max()

        logging.info('Plotting')
        out_file = os.path.join(dir_out,config['tables'][tablei]['out_file_nobs'])
        kwargs['colorpalette'] = config['colorpalette_nobs']
        kwargs['colorbar_title'] = config['colorbar_title_nobs']
        kwargs['cmin_value'] = config['cmin_value_nobs']
        kwargs['cmax_value'] = config['cmax_value_nobs']
        kwargs['normalization'] = config['normalization_nobs']
        status = map_single(global_nobs,out_file , **kwargs)
        
        out_file = os.path.join(dir_out,config['tables'][tablei]['out_file_nmonths'])
        kwargs['colorpalette'] = config['colorpalette_nmonths']
        kwargs['colorbar_title'] = config['colorbar_title_nmonths']
        kwargs['cmin_value'] = config['cmin_value_nmonths']
        kwargs['cmax_value'] = config['cmax_value_nmonths']
        kwargs['normalization'] = config['normalization_nmonths']
        status = map_single(global_nmonths,out_file, **kwargs)



