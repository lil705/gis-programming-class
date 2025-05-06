from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
)

pr = QgsProject.instance()
layer = pr.mapLayersByName("stations")[0]
districts = pr.mapLayersByName("districts")[0]

layer.setSubsetString("\"colour\" = 'purple'")

buffer_layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "station_buffers", "memory")
prov = buffer_layer.dataProvider()
prov.addAttributes(layer.fields())
buffer_layer.updateFields()

for station in layer.getFeatures():
    radius = (int(station["random_1"]) + 5) * 25
    buffer_geom = station.geometry().buffer(radius, 8)
    
    feat = QgsFeature()
    feat.setGeometry(buffer_geom)
    feat.setAttributes(station.attributes())
    prov.addFeature(feat)

pr.addMapLayer(buffer_layer)
buffer_layer.updateExtents()


# Выделяем объекты, которые пересекаются с буферами
intersecting_ids = set()

for poly in districts.getFeatures():
    poly_geom = poly.geometry()
    for buffer in buffer_layer.getFeatures():
        if buffer.geometry().intersects(poly_geom):
            intersecting_ids.add(poly.id())
            break  

districts.selectByIds(list(intersecting_ids))