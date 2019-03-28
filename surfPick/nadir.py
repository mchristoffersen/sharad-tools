from osgeo import gdal, osr
from gdalconst import *
import numpy as np
import sys

class Dem:
  # Holds an array of DEM data and relevant metadata
  def __init__(self,dem_path):
    src_dem = gdal.Open(dem_path,GA_ReadOnly)
    self.csys = src_dem.GetProjection()
    self.gt = src_dem.GetGeoTransform()
    self.nd = src_dem.GetRasterBand(1).GetNoDataValue()
    if(self.nd == None):
      self.nd = -np.finfo('d').max
    self.data = np.array(src_dem.GetRasterBand(1).ReadAsArray())
    src_dem = None

class Loc:
  # A location in 3D space, either in cartesian or geodetic coordinates
  # The two are switched between often in this program so they are just
  # combined. X is the same field as longitude, Y is the same field as
  # latitude, Z is the same field as the radius.
  def __init__(self,x,y,z):
    self.x = x
    self.y = y
    self.z = z
    self.ol = False
    self.nd = False
    
  def __eq__(self, other):
    if(other is None):
      return False
    else:
      return(self.x == other.x and self.y == other.y and self.z == other.z)
    
  def __ne__(self, other):
    return(not self.__eq__(other))
   
  def __str__(self):
    return('(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')')
    
  def __add__(self,vec):
    # Only allowed to add vectors to points
    return Loc(self.x + vec.i, self.y + vec.j, self.z + vec.k)
    
  def __radd__(self,vec):
    return self.__add__(vec)
    
  def __sub__(self,vec):
    # Only allowed to subtract vectors from points
    return Loc(self.x - vec.i, self.y - vec.j, self.z - vec.k)
    
  def __rsub__(self,vec):
    return self.__add__(vec)
    
  def copy(self):
    return Loc(self.x, self.y, self.z)
    
  def topix(self,dem):
    # This transforms a point to an (x,y) pixel location on a DEM using the input geotransform
    # IF YOU USE THIS ON ITS OWN WITHOUT THE toground() FUNCTION
    # FOR A Path MAKE SURE THAT THE POINT COORDINATES ARE IN THE
    # SAME COORDINATE SYSTEM AS THE GEOTRANSFORM
      
    gt = dem.gt
      
    x = int((gt[0] - self.x)/-gt[1])
    y = int((gt[3] - self.y)/-gt[5])
    
    ## Out of bounds stuff
    #if(x >= dem.data.shape[1]):
    #  x = dem.data.shape[1] - 1
      
    #if(y >= dem.data.shape[0]):
    #  y = dem.data.shape[0] - 1
    
    #if(x < 0):
    #  x = 0
    
    #if(y < 0):
    #  y = 0
    
    ## Other option for out of bounds stuff  
    if(x<0 or y <0 or x >= dem.data.shape[1] or y >= dem.data.shape[0]):
      #print('Requested data off DEM warning',[x,y],[self.x,self.y,self.z])
      #print(x,dem.data.shape[1],y,dem.data.shape[0])
      return Loc(-1,-1,0)
  
    out = Loc(x,y,0)
    
    # SPECIFIC FOR MOLA  
    #if(y < 116 or y > 22412):
    #  out.ol = True

    return out
 
  def equals(self, other):
    # Checks equality of two points
    if(self.x == other.x and self.y == other.y and self.z == other.z):
      return True
      
    return False
    
    
class Path:
  # A list of loc objects, representing a path. Along with some useful
  # metadata
  def __init__(self, csys = None, pts = []):
    self.pts = pts
    self.csys = csys
        
  def __setitem__(self,i,item):
    self.pts[i] = item
    
  def __getitem__(self,i):
    return self.pts[i]

  def __len__(self):
    return len(self.pts)
  
  def append(self,Loc):
    self.pts.append(Loc)
  
  def copy(self):
    # Returns a copy of the Pointlist
    return Path(self.csys,self.pts[:])
    
    
  def transform(self,targ):
    #print(self)
    # Transforms a Pointlist to another coordinate system, can read Proj4 format
    # and WKT
    
    pts = self.copy()
    
    source = osr.SpatialReference()  
    target = osr.SpatialReference()  

    # Deciding whether the coordinate systems are Proj4 or WKT
    sc0 = pts.csys[0]
    if(sc0 == 'G' or sc0 == 'P'):
      source.ImportFromWkt(pts.csys)
    else:
      source.ImportFromProj4(pts.csys)

    tc0 = targ[0]
    if(tc0 == 'G' or tc0 == 'P'):
      target.ImportFromWkt(targ)
    elif(tc0 == '+'):
      target.ImportFromProj4(targ)
    else:
      print("Unrecognized target coordinate system:")
      print(targ)
      sys.exit()

    # The actual transformation
    transform = osr.CoordinateTransformation(source, target)
    xform = transform.TransformPoint
    #print(pts[1].z)
    for i in range(len(pts)):
      #print(pts[1].z)
      #print(type(pts[i].x),type(pts[i].y),type(pts[i].z))
      #print('orig',str(pts[i]))
      npt = list(xform(pts[i].x,pts[i].y,pts[i].z))
      pts[i] = Loc(npt[0],npt[1],npt[2])
      #print('xform',str(pts[i]))

    pts.csys = targ
    return pts
  
  def toground(self, dem, outsys = None):
    # Function will get the points on the ground directly below a list of points,
    # this is not destructive and returns a new list 
    grd = self.copy() # copy to store on-ground points
    origsys = grd.csys

    # Transforming to the DEM coordinate system so the geotransform math works
    grd = grd.transform(dem.csys)

    # Iterate through the points and get the points below them
    for i in range(len(grd)):
      zpix = grd[i].topix(dem)
      if(zpix.x == -1 and zpix.y == -1):
        grd[i].z = dem.nd
      else:
        grd[i].z = float(dem.data[zpix.y][zpix.x])

    # Set coordinate systems for the new lists
    if(not(outsys is None)):
      grd = grd.transform(outsys)
    else:
      grd = grd.transform(origsys)

    return grd
    
#### NAV IMPORT ####


def GetNav_geom(navfile):
  f = open(navfile,'r')
  navdat_raw = f.read()
  f.close()
  navdat_raw = navdat_raw.split('\n')
  navdat_raw = filter(None,navdat_raw)
  navdat = Path()
  for i in navdat_raw:
    if(len(i) > 0):
      i = i.split(',')
      navdat.append(Loc(float(i[2])*1000,float(i[3])*1000,float(i[4])*1000))    # x,y,z position vectors (converted to meters)
  
  # testing
  print('x_vec:  \t' + str(navdat[0].x))
  print('y_vec:  \t' + str(navdat[0].y))
  print('z_vec:  \t' + str(navdat[0].z))
  

  # Transform x,y,z position vectors from 3D cartesian to geographic coords
  geocsys = '+proj=longlat +a=3396190 +b=3376200 +no_defs'
  navdat.csys = '+proj=geocent +a=3396190 +b=3376200 +no_defs'
  navdat = navdat.transform(geocsys)
  
  # Adjust with areoid ... this relies on specific directory structure
  aer = Dem('/mnt/d/MARS/code/modl/MRO/simc/test/temp/dem/mega_16.tif')

  aer_nadir = navdat.toground(aer)

  for i in range(len(navdat)):
    if(aer_nadir[i].z == aer.nd):
      aer_nadir[i].z = aer_nadir[i-1].z

    ## TESTING - NEED TO TRANSFORM TO CARTESIAN
    print('transform navdat...')
    print('long:   \t' + str(navdat[0].x))
    print('lat:    \t' + str(navdat[0].y))
    print('rad [m]:\t' + str(navdat[0].z))
    ##
    ellip_spher_diff = ((3396190 - 3376200)*abs(np.cos((navdat[i].y)*(np.pi/180)))) + 190
    ellip_aer_diff = ellip_spher_diff - aer_nadir[i].z
    newr = navdat[i].z + ellip_aer_diff
    navdat[i].z = newr
    print('corrected radius...')
    print('rad [m]:\t' + str(navdat[0].z))
    sys.exit()


  return navdat


####    ####    ####    ####



'''
need to get proj data for EDRs
need to get reference datum for EDRs
need to add z(radius) to EDR nav data
'''