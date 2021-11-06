import matplotlib  
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import math
import requests
from io import BytesIO
from PIL import Image
import os.path
import errno
from gps import *
from config import get_config

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)
    
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

def cache_tile(filename, file):
    if (get_config('caching') == 'True'):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename,'wb') as f:
            f.write(file.content)
        
        print("Saving file: " + filename)
    else:
        print("Caching is not on")
        return

def tile_calc(zoom,resolution):
    delta_lon = 360.0/(2**zoom)
    delta_lat = 180/(2**zoom)
    xtiles = int(math.ceil(resolution[0]/256.0))
    ytiles = int(math.ceil(resolution[1]/256.0))+1
    long_offset = delta_lon/2 * xtiles
    lat_offset = delta_lat/2 *ytiles
    return lat_offset, long_offset

   
def getImageCluster(lat_deg, lon_deg, zoom, resolution):
    headers = {"User-Agent":"overlanderspi/0.4 linux"}
    smurl = r"http://a.tile.openstreetmap.org/{0}/{1}/{2}.png"
    delta_lat, delta_lon = tile_calc(zoom,resolution)
    xmin, ymax =deg2num(lat_deg-delta_lat, lon_deg - delta_lon, zoom)
    xmax, ymin =deg2num(lat_deg + delta_lat, lon_deg + delta_lon, zoom)
    file = os.path.expanduser('~') + r"/Maps/OSM/{0}/{1}/{2}.png"

    Cluster = Image.new('RGB',((xmax-xmin+1)*256-1,(ymax-ymin+1)*256-1) ) 
    for xtile in range(xmin, xmax+1):
        for ytile in range(ymin,  ymax+1):
            filestr = file.format(zoom, xtile, ytile)
            if (os.path.isfile(filestr)):
                #print("Loading tile: " + filestr + " from cache")
                tile = Image.open(filestr)
                Cluster.paste(tile, box = ((xtile-xmin)*256 ,  (ytile-ymin)*255))
            else:
                #print("Tile not found locally, downloading from server.")
                try:
                    imgurl = smurl.format(zoom, xtile, ytile)
                    #print("Opening: " + imgurl)
                    imgstr = requests.get(imgurl, headers=headers, allow_redirects=True)
                    tile = Image.open(BytesIO(imgstr.content))
                    Cluster.paste(tile, box = ((xtile-xmin)*256 ,  (ytile-ymin)*255))
                    cache_tile(filestr,imgstr)
                except Exception as err: 
                    print("Couldn't download image")
                    tile = None
   
    return Cluster

def get_figure(lat_deg, lon_deg, zoom, resolution):
    a = getImageCluster(lat_deg, lon_deg, zoom, resolution)
    figure = plt.figure()
    figure.figimage(a)
    return figure

#if __name__ == '__main__':
    #a = getImageCluster(28.883, -112.632, 9.0,  9.0, 7)

    #fig1 = plt.figure()
    #fig1.patch.set_facecolor('white')
    #plt.imshow(np.asarray(a))
    #plt.show()