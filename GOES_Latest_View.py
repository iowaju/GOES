# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 15:07:41 2018

@author: juliano
"""

from awips.dataaccess import DataAccessLayer
import cartopy.crs as ccrs, numpy as np, datetime
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER 
from dynamicserialize.dstypes.com.raytheon.uf.common.time import TimeRange
from datetime import datetime, timedelta

# Create an EDEX data request
DataAccessLayer.changeEDEXHost("edex-cloud.unidata.ucar.edu")

#function to create the map
def make_map(bbox, projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize = (16,9), subplot_kw = dict(projection = projection))
    if bbox[0] is not np.nan:
        ax.set_extent(bbox)
    ax.coastlines(resolution = '50m')
    gl = ax.gridlines(draw_labels = True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

def plotting(sector, parameter):
    
    #setting locations
    fig = plt.figure(figsize = (16, 7 * len(sector)))
    
    #connecting to the server and retrieving the variables
    request = DataAccessLayer.newDataRequest()
    request.setDatatype("satellite")
    #request.setLocationNames("ECONUS")
    #request.setParameters("CH-13-10.35um")
    request.setLocationNames(sector)
    request.setParameters(parameter)
    
    #adjusting the time stamps
    times = DataAccessLayer.getAvailableTimes(request)
    #print "times: " + str(times[-1])
    beginRange = datetime.strptime( str(times[-2]).split(".")[0], "%Y-%m-%d %H:%M:%S")
    endRange = datetime.strptime( str(times[-1]).split(".")[0], "%Y-%m-%d %H:%M:%S")
    timerange = TimeRange(beginRange, endRange)
    #print "timerange: " + str(timerange)
    
    #requesting the data
    response = DataAccessLayer.getGridData(request, timerange)
    #print "Response: " + str(response)
    
    #organizing the gridded data
    grid = response[0]
    #print "Grid " + str(grid)
    
    data = grid.getRawData()
    #print "data: " + str(data)
    
    #getting latlong from the file to build the image
    lons,lats = grid.getLatLonCoords()
    lats = np.nan_to_num(lats)
    lons = np.nan_to_num(lons)
    
    #Here you choose the Quadrants of the Area of Interest: XMin, Xmax, YMin, YMax)_________________________
    bbox = [-100.0, -67.0, 25.0, 49.0]

    #creating the map
    fig, ax = make_map(bbox = bbox)
    ax.set_extent(bbox)
    
    #Adjust colour scheme
    cs = ax.pcolormesh(lons, lats, data, cmap = 'rainbow')
    
    #adjusting the legend bar
    cbar = fig.colorbar(cs, shrink = 0.6, orientation='horizontal')
    cbar.set_label(str(sector) + " " + grid.getParameter() + " " + str(grid.getDataTime().getRefTime()))
    plt.savefig('C:/GOES/' + sector + "_" + parameter + '.png')
    plt.clf()

#loop Thru all entities
for entity in creatingEntities:
    request = DataAccessLayer.newDataRequest("satellite")
    request.addIdentifier("creatingEntity", entity)
    availableSectors = DataAccessLayer.getAvailableLocationNames(request)
    availableSectors.sort()
    
    #loop thru all the Sectors within each entity:
    for sector in availableSectors:
        request.setLocationNames(sector)
        availableProducts = DataAccessLayer.getAvailableParameters(request)
        availableProducts.sort()
        
        #loop thru all the variables within each sector:
        for product in availableProducts: 
            try:    
                #Calling the function
                plotting(sector, product)
                print "Printing " + sector + " " + product
            except:
                print(sector + " - " + product + " not worked")  
                continue