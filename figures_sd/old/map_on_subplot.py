#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:43:22 2018

@author: iregon
"""
import os
import json
import sys
import glob
import logging
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import matplotlib as mpl
import numpy as np

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import xarray as xr
import cartopy.crs as ccrs

from . import map_properties
from . import var_properties

logging.getLogger('plt').setLevel(logging.INFO)
logging.getLogger('mpl').setLevel(logging.INFO)


script_path = os.path.dirname(os.path.realpath(__file__))
# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':map_properties.font_size_legend})        # controls default text sizes
plt.rc('axes', titlesize=map_properties.axis_label_size)     # fontsize of the axes title
plt.rc('axes', labelsize=map_properties.axis_label_size)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=map_properties.tick_label_size)    # fontsize of the tick labels
plt.rc('ytick', labelsize=map_properties.tick_label_size)    # fontsize of the tick labels
plt.rc('figure', titlesize=map_properties.title_label_size)  # fontsize of the figure title
# END PARAMS ------------------------------------------------------------------

def map_on_subplot(f,subplot_ax,z,lons,lats,colormap = 'jet',colorbar_show = True,
                   colorbar_title = '', colorbar_title_size = 9, 
                   colorbar_label_size = 7, colorbar_orien = 'v', 
                   colorbar_width = 4, cmin_value = None, cmax_value = None, 
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
     
    colormap : str
        The name of the matplolib color pallette to use. Defaults to jet
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
    colorbar_width : integer
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
    
    # Make sure we know what z is
    cmin_value = np.nanmin(z) if cmin_value is None else cmin_value
    cmax_value = np.nanmax(z) if cmax_value is None else cmax_value

    if normalization== 'log':
        normalization_f = LogNorm(vmin = cmin_value,vmax = cmax_value)
    else:
        normalization_f = mpl.colors.Normalize(vmin = cmin_value,
                                             vmax = cmax_value)
        
    cmap = plt.get_cmap(colormap)    
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
    new_axis_w = str(colorbar_width) + '%'
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


def map_individual(dataset,agg,param,out_file,cmax_value = None, cmin_value = None):
    # HOW ARE WE PLOTTING:
    # We plot using matplotlib (not xarray direct plotting) on a cartopy axis
    # Have to do some adjustments to matplotlib because of cartopy.
    # Why cartopy, and not basemap?:   https://github.com/SciTools/cartopy/issues/920
    # But we might face the need of a projection not yet in cartopy......
    
    # The actual projection is set here in the subplots declaration!!!!
    proj = ccrs.PlateCarree()
    proj = ccrs.Robinson()
    
    kwargs = {}
    kwargs['show_colorbar'] = True
    kwargs['colorbar_w'] = map_properties.individual_map['colorbar_width']
    kwargs['grid_label_size'] = map_properties.individual_map.get('grid_label_size')
    kwargs['colorbar_label_size'] = map_properties.individual_map.get('colorbar_label_size')
    kwargs['colorbar_title_size'] = map_properties.individual_map.get('colorbar_title_size')
    kwargs['coastline_width'] = map_properties.individual_map.get('coastline_width')
    

    kwargs['colormap'] = plt.get_cmap()
    kwargs['colorbar_title'] = var_properties['units'].get('counts') if agg == 'counts' else agg + " (" + var_properties['units'].get(param) + ")"
    kwargs['colorbar_orien'] = 'v'
    
    if agg == 'counts':     
        kwargs['cmin_value'] = 1; kwargs['cmax_value'] = dataset['counts'].max()
        z = dataset[agg].where(dataset[agg]> 0).values
        kwargs['normalization'] = LogNorm(vmin=kwargs['cmin_value'], vmax=kwargs['cmax_value'])
    else:
        kwargs['cmin_value'] = np.nanmin(dataset[scalable_vdims].min().to_array()) if cmin_value is None else cmin_value
        kwargs['cmax_value'] = np.nanmax(dataset[scalable_vdims].max().to_array()) if cmax_value is None else cmax_value
        kwargs['normalization'] = mpl.colors.Normalize(vmin=kwargs['cmin_value'], vmax=kwargs['cmax_value'])
        z = dataset[agg].values
    plt.title('-'.join([param]) + ": " + " ".join([agg]) + '\n')# + "-".join([str(y_ini),str(y_end)]) + ' composite')
    f, ax = plt.subplots(1, 1, subplot_kw=dict(projection=proj),figsize=(14,7),dpi = 150)  # It is important to try to estimate dimensions that are more or less proportional to the layout of the mosaic....
    lons = dataset[agg]['longitude']
    lats = dataset[agg]['latitude']
    map_on_subplot(f,ax,z,lons,lats,**kwargs)
    plt.savefig(out_file,bbox_inches='tight')
    plt.close()

def map_mosaic(xarray_grid,out_file,cmax_value = None, cmin_value = None):
    """Plot xarray on to a map.
 
    Arguments
    ---------
    xarray_grid : xarray
        Data to map
    out_file : str
        Path to output the map to
    
    Keyword arguments
    -----------------
    colorpalette : str
        The name of the matplolib color pallette to use
    colorbar_title : str
        The colorbar title
    colorbar_orien : str
        The colorbar orientation (h/v)
    cmin_value : numeric, optional
        Min value to use in colorbar normalization. Defaults to xarray min
    cmax_value : numeric, optional
        Max value to use in colorbar normalization. Defaults to xarray max 
    filter_by_range : dict, optional
        Dictionary with the {(table,element) :[ini, end]} pairs to filter the 
        data with. 
    """
    # HOW ARE WE PLOTTING:
    # We plot using matplotlib (not xarray direct plotting) on a cartopy axis
    # Have to do some adjustments to matplotlib because of cartopy.
    # Why cartopy, and not basemap?:   https://github.com/SciTools/cartopy/issues/920
    # But we might face the need of a projection not yet in cartopy......

    # The actual projection is set here in the subplots declaration!!!!
    proj = ccrs.PlateCarree()
    proj = ccrs.Robinson()
    kwargs = {}
    kwargs['show_colorbar'] = True
    kwargs['colorbar_w'] = map_properties.mosaic_map['colorbar_width']
    kwargs['grid_label_size'] = map_properties.mosaic_map.get('grid_label_size')
    kwargs['colorbar_label_size'] = map_properties.mosaic_map.get('colorbar_label_size')
    kwargs['colorbar_title_size'] = map_properties.mosaic_map.get('colorbar_title_size')
    kwargs['coastline_width'] = map_properties.mosaic_map.get('coastline_width')
    
    f, ax = plt.subplots(1, 3, subplot_kw=dict(projection=proj),figsize=(14,7),dpi = 180)
    c = 0
    for agg in mosaic_vdims:
        kwargs['colormap'] = vars_colormap.get('counts')  if agg == 'counts' else vars_colormap.get(param)
        kwargs['colorbar_title'] = var_properties['units'].get('counts') if agg == 'counts' else agg + " (" + var_properties['units'].get(param) + ")"
        kwargs['colorbar_orien'] = 'h'
        if agg == 'counts':
            kwargs['cmin_value'] = 1; kwargs['cmax_value'] = dataset['counts'].max()
            z = dataset[agg].where(dataset[agg]> 0).values
            kwargs['normalization'] = LogNorm(vmin=kwargs['cmin_value'], vmax=kwargs['cmax_value'])
        else:
            kwargs['cmin_value'] = dataset[scalable_vdims].min().to_array().min() if cmin_value is None else cmin_value
            kwargs['cmax_value'] = dataset[scalable_vdims].max().to_array().max() if cmax_value is None else cmax_value
            kwargs['normalization'] = mpl.colors.Normalize(vmin=kwargs['cmin_value'], vmax=kwargs['cmax_value'])
            z = dataset[agg].values
        lons = dataset[agg]['longitude']
        lats = dataset[agg]['latitude']
        map_on_subplot(f,ax[c],z,lons,lats,**kwargs)
        c += 1

    wspace = 0.08# if qc_mode else 0.05
    dpi = 400 #if qc_mode else 300
    plt.subplots_adjust(wspace=wspace,hspace=0.05)#  Force small separation (default is .2, to keep in mind "transparent" colorbar between subplots....THIS WILL DEPEND ON THE FIGURE WIDTH
    plt.savefig(out_file,bbox_inches='tight',dpi = dpi)# 'tight' here, not in plt.tight_layout: here it realizes the new size because of add_axes, but not in plt.tight_layout..
    plt.close()
           
def read_dataset(file,param):
    if param != 'header':
        param_offset = var_properties['offset'].get(param)
        param_scale = var_properties['scale'].get(param)
        dataset = xr.open_dataset(file,autoclose=True)
        for vdim in scalable_vdims:
            dataset[vdim] = param_offset + param_scale*dataset[vdim]
    else:
        dataset = xr.open_dataset(file,autoclose=True)
        
    return dataset
            
            
def main():   
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    try:
        data_path = sys.argv[1]
        release = sys.argv[2]
        update = sys.argv[3]
        source = sys.argv[4]
        level = sys.argv[5]
        sid_dck = sys.argv[6]
        mode = sys.argv[7]
    except Exception as e:
        logging.error(e, exc_info=True)
        return
    
    
    mode_dataset_dict = {'qcr0-qc0-um':'qcr0-qc0',
                         'all':'',
                         'qcr0-qc0':'qcr0-qc0',
                         'qcr0':'qcr0'}
    
    mode_ext_map = {'qcr0-qc0-um':'qcr0-qc0-um-map.png',
                         'all':'all-map.png',
                         'qcr0-qc0':'qcr0-qc0-map.png',
                         'qcr0':'qcr0-map.png'}
    
    mode_ext_mosaic = {'qcr0-qc0-um':'qcr0-qc0-um-mosaic.png',
                         'all':'all-mosaic.png',
                         'qcr0-qc0':'qcr0-qc0-mosaic.png',
                         'qcr0':'qcr0-mosaic.png'}
    
    mode_dataset_hdr_dict = {'qcr0-qc0-um':'qcr0',
                         'all':'',
                         'qcr0-qc0':'qcr0',
                         'qcr0':'qcr0'}
    
    mode_ext_hdr_map = {'qcr0-qc0-um':'qcr0-um-map.png',
                         'all':'all-map.png',
                         'qcr0-qc0':'qcr0-map.png',
                         'qcr0':'qcr0-map.png'}
    
    mode_ext_hdr_mosaic = {'qcr0-qc0-um':'qcr0-um-mosaic.png',
                         'all':'all-mosaic.png',
                         'qcr0-qc0':'qcr0-mosaic.png',
                         'qcr0':'qcr0-mosaic.png'}
    if mode == 'qcr0-qc0-um':
        for param in vars_colormap.keys():
            if param != 'counts':
                vars_colormap[param].set_over('Pink')
                vars_colormap[param].set_under('DarkMagenta')
    
    params = ['header','at','sst','slp','wbt','dpt','wd','ws']
    reports_path = os.path.join(data_path,release,source,level,'reports',sid_dck)

    ext = mode_dataset_dict.get(mode)
    out_ext_map = mode_ext_map.get(mode)
    out_ext_mosaic = mode_ext_mosaic.get(mode)
    for param in params:
        ext = mode_dataset_hdr_dict.get(mode) if param == 'header' else mode_dataset_dict.get(mode)
        out_ext_map = mode_ext_hdr_map.get(mode) if param == 'header' else mode_ext_map.get(mode)
        out_ext_mosaic = mode_ext_hdr_mosaic.get(mode) if param == 'header' else mode_ext_mosaic.get(mode)
        logging.info('Mapping {}'.format(param))
        prefix = '-'.join(['observations',param]) if param != 'header' else 'header'
        pattern = os.path.join(reports_path,'-'.join(filter(bool,[prefix,release,update,ext])) + '.nc')
        
        logging.info('Searching pattern {}'.format(pattern))
        nc_file = glob.glob(pattern)
    
        if len(nc_file) == 0:
            logging.warning('Map not found')
            logging.warning('Empty map figure will not be produced')
            continue
        else:
            logging.info('Loading nc file {}'.format(nc_file))
            dataset = read_dataset(nc_file[0],param)
            # Have a look at the file, maybe there's nothing there!
            non_nans = np.asscalar(dataset['counts'].max().values)
            if non_nans == 0:
                logging.warning('No data in nc file')
                logging.warning('Empty map figure will not be produced')
                continue    

        if param != 'header':
            cmax_value = var_properties['saturation'].get(param)[1] 
            cmin_value = var_properties['saturation'].get(param)[0]
            
            for agg in vdims:
                logging.info('Mapping {}'.format(agg))
                out_file =os.path.join(reports_path,'-'.join(filter(bool,[prefix,release,update,agg,out_ext_map])))
                if mode == 'qcr0-qc0-um':
                    map_individual(dataset,agg,param,out_file,cmax_value = cmax_value,cmin_value = cmin_value)
                else:
                    map_individual(dataset,agg,param,out_file)

            logging.info('Mapping mosaic') 
            out_file =os.path.join(reports_path,'-'.join(filter(bool,[prefix,release,update,out_ext_mosaic])))
            if mode == 'qcr0-qc0-um':
                map_mosaic(dataset,param,out_file,cmax_value = cmax_value,cmin_value = cmin_value)
            else:
                map_mosaic(dataset,param,out_file)
                
        else:
            
            out_file = os.path.join(reports_path,'-'.join(filter(bool,[prefix,release,update,out_ext_map])))
            map_individual(dataset,'counts',param,out_file)    
    



if __name__ == '__main__':
    main()