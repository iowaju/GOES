from awips.dataaccess import DataAccessLayer
import cartopy.crs as ccrs, numpy as np, datetime
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER 
from dynamicserialize.dstypes.com.raytheon.uf.common.time import TimeRange
from datetime import datetime, timedelta

# Create an EDEX data request
DataAccessLayer.changeEDEXHost("edex-cloud.unidata.ucar.edu")
request = DataAccessLayer.newDataRequest()
request.setDatatype("satellite")

# Show available creatingEntities
identifier = "creatingEntity"
creatingEntities = DataAccessLayer.getIdentifierValues(request, identifier)

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
    request.setLocationNames(sector)
    request.setParameters(parameter)
    
    #adjusting the time stamps
    times = DataAccessLayer.getAvailableTimes(request)
    beginRange = datetime.strptime( str(times[-2]).split(".")[0], "%Y-%m-%d %H:%M:%S")
    endRange = datetime.strptime( str(times[-1]).split(".")[0], "%Y-%m-%d %H:%M:%S")
    timerange = TimeRange(beginRange, endRange)
    #print "timerange: " + str(timerange)
    
    #requesting the data
    response = DataAccessLayer.getGridData(request, timerange)
    
    #organizing the gridded data
    grid = response[0]
    data = grid.getRawData()
    
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
    cbar.set_label(str(sector) + " " + str(grid.getParameter()) + " " + str(grid.getDataTime().getRefTime()))
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
        sec = sector.decode('utf-8')
        request.setLocationNames(sec)
        availableProducts = DataAccessLayer.getAvailableParameters(request)
        availableProducts.sort()
        
        #loop thru all the variables within each sector:
        for product in availableProducts: 
            prod = product.decode('utf-8')
            try:    
                Calling the function
                plotting(sec, prod)
                print("Printing " + sec + " " + prod)
            except:
                print(sec + " - " + prod + " not worked")    
                continue

