from osgeo import gdal
from qgis.core import QgsVectorLayer, QgsProject

path = "C:/Users/elena/Downloads/5.tif"
raster_data = gdal.Open(path)

arrays = []
raster_count = raster_data.RasterCount

for i in range(1, raster_count + 1):
    band = raster_data.GetRasterBand(i)
    band_array = band.ReadAsArray().astype('float32')
    arrays.append(band_array)

#2
driver = gdal.GetDriverByName('GTiff')
output_path = "C:/Users/elena/Downloads/raster_copy.tif"
out_raster = driver.Create(output_path,
                           raster_data.RasterXSize,
                           raster_data.RasterYSize,
                           raster_count,
                           gdal.GDT_Float32)

#3
for i in range(raster_count):
    out_band = out_raster.GetRasterBand(i + 1)
    out_band.WriteArray(arrays[i])

#4
footprint_path = "C:/Users/elena/Downloads/footprint_5.geojson"
footprint_layer = QgsVectorLayer(footprint_path, 'footprint_5', 'ogr')

if not footprint_layer.isValid():
    raise Exception("Footprint layer not loaded correctly")

features = footprint_layer.getFeatures()
feature = next(features)
geometry = feature.geometry().asPolygon()[0]

coords = [(pt.x(), pt.y()) for pt in geometry]

#5
crs = footprint_layer.crs()
out_raster.SetProjection(crs.toWkt())

#6
gcp_list = []
raster_x = raster_data.RasterXSize
raster_y = raster_data.RasterYSize

pixel, line = 0,0
for i in range(4):
    x, y = coords[i]
    z = 0
    if i == 0:
        pixel = 0
        line = 0
    elif i == 1:
        pixel = raster_data.RasterXSize - 1
        line = 0
    elif i == 2:
        pixel = raster_data.RasterXSize - 1
        line = raster_data.RasterYSize - 1
    elif i == 3:
        pixel = 0
        line = raster_data.RasterYSize - 1
    else: continue
    gcp = gdal.GCP(x, y, 0, pixel, line)
    gcp_list.append(gcp)

#7
out_raster.SetGCPs(gcp_list, out_raster.GetProjection())
out_raster.FlushCache()

raster_data = None
out_raster = None
