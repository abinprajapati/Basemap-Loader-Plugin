import os
import inspect
import requests
from PyQt5.QtWidgets import QAction, QInputDialog
from PyQt5.QtGui import QIcon
from qgis.core import QgsRasterLayer, QgsProject

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

class BasemapLoaderPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        icon = os.path.join(os.path.join(cmd_folder, 'logo.png'))
        self.action = QAction(QIcon(icon), 'Load Basemap', self.iface.mainWindow())
        self.iface.addToolBarIcon(self.action)
        self.action.triggered.connect(self.run)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        # Let user choose which basemap to load
        basemap_choices = ['OpenStreetMap', 'Satellite']
        choice, ok = QInputDialog.getItem(self.iface.mainWindow(), 'Select Basemap', 'Choose a basemap:', basemap_choices, 0, False)

        if ok and choice:
            if choice == 'OpenStreetMap':
                self.load_osm()
            elif choice == 'Satellite':
                self.load_satellite()
    
    def load_osm(self):
        basemap_url = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        zmin = 0
        zmax = 19
        crs = 'EPSG:3857'
        
        uri = f'type=xyz&url={basemap_url}&zmax={zmax}&zmin={zmin}&crs={crs}'
        rlayer = QgsRasterLayer(uri, 'OpenStreetMap', 'wms')
        self.add_basemap_layer(rlayer, 'OpenStreetMap')

    def load_satellite(self):
        # Load TMS layer (Google Satellite)
        service_url = "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" 
        
        zmin = 0
        zmax = 19
        crs = 'EPSG:3857'

        service_uri = "type=xyz&zmin=0&zmax=21&url=https://" + requests.utils.quote(service_url)
        tms_layer = QgsRasterLayer(service_uri, "Satellite Imagery", "wms")
        
        self.add_basemap_layer(tms_layer, 'Satellite Imagery')



    def add_basemap_layer(self, rlayer, name):
        if rlayer.isValid():
            # Add the layer, but not to the legend
            QgsProject.instance().addMapLayer(rlayer, False)
            # Insert layer at the bottom of Layer Tree
            root = QgsProject.instance().layerTreeRoot()
            position = len(root.children())
            root.insertLayer(position, rlayer)
            self.iface.messageBar().pushSuccess('Success', f'{name} Layer Loaded')
        else:
            self.iface.messageBar().pushCritical('Error', f'Invalid {name} Layer')
