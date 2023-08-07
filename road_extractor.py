# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QCursor, QColor
from qgis.PyQt.QtWidgets import QAction, QLabel, QVBoxLayout, QWidget
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsMapToolPan, QgsMapMouseEvent, QgsMapCanvas
from qgis.core import QgsRectangle, QgsWkbTypes, QgsPoint, QgsGeometry, QgsPointXY
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QRect
from .resources import *
from .road_extractor_dialog import RoadExtractorDialog
import os.path
import time
import numpy as np
import qimage2ndarray
import sys
from keras.models import load_model

sys.path.append('C:\OSGeo4W\apps\qgis\python\plugins\road_extractor')
from .sat_image_segmentation import get_segmentation, save_prediction
import cv2



class RoadExtractor:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        #self.canvas = iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RoadExtractor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Road Extractor')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.start_point = None
        self.map_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.rubberband = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
        self.rubberband.setColor(Qt.red)
        self.rubberband.setWidth(4)
        #self.rubberband.setFillColor(Qt.transparent)
        fill_color = QColor(64, 224, 208, 51)
        self.rubberband.setFillColor(fill_color)
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RoadExtractor', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/road_extractor/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Extracts roads from satellite images'),
            callback=self.run,
            parent=self.iface.mainWindow())
        # will be set False in run()
        self.first_start = True
        self.map_tool.canvasClicked.connect(self.on_canvas_click)
        

        # self.action_draw_rectangle = QAction("Draw Rectangle", self.iface.mainWindow())
        # self.action_draw_rectangle.triggered.connect(self.activate_rectangle_drawing)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Road Extractor'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = RoadExtractorDialog()
            self.clicked = None

        self.iface.mapCanvas().setMapTool(self.map_tool)
        

        # show the dialog
        #self.dlg.show()
        # # Run the dialog event loop
        # result = self.dlg.exec_()
        # # See if OK was pressed
        # if result:
        #     # Do something useful here - delete the line containing pass and
        #     # substitute with your code.
        #     pass

    def on_canvas_click(self, point, button):
        if button == Qt.LeftButton and not self.clicked:
            self.rubberband.reset()
            self.start_point = point
            self.rubberband.addPoint(point)
            self.clicked = True

        elif button == Qt.RightButton and self.clicked:
            self.end_point = point
            self.update_rectangle(self.start_point, self.end_point)
            self.clicked = False

        elif button == Qt.RightButton and not self.clicked:
            pan_tool = QgsMapToolPan(self.iface.mapCanvas())
            self.iface.mapCanvas().setMapTool(pan_tool)
            self.clicked = None
            self.show_ui()
            
    
    def show_ui(self):
        rubberband_geometry = self.rubberband.asGeometry()
        rect = rubberband_geometry.boundingBox()
        canvas_extent = self.iface.mapCanvas().extent()
        self.rubberband.hide()
        self.iface.mapCanvas().setExtent(rect)
        self.iface.mapCanvas().refresh()

        #Captrue Screenshot
        screenshot = QPixmap(self.iface.mapCanvas().size())
        painter = QPainter(screenshot)
        self.iface.mapCanvas().render(painter)
        painter.end()
        #send_image_to_kafka(screenshot)
        
        screenshot_segment = self.road_segmentation(screenshot)
        

        self.iface.mapCanvas().setExtent(canvas_extent)
        self.rubberband.show()
        self.iface.mapCanvas().refresh()
        self.dlg.screenshot_label.setPixmap(screenshot_segment)
        self.dlg.exec_()


    def update_rectangle(self, start_point, end_point):
        rect = QgsRectangle(start_point, end_point)
        points = [QgsPointXY(rect.xMinimum(), rect.yMinimum()),
                  QgsPointXY(rect.xMaximum(), rect.yMinimum()),
                  QgsPointXY(rect.xMaximum(), rect.yMaximum()),
                  QgsPointXY(rect.xMinimum(), rect.yMaximum())]
        self.rubberband.setToGeometry(QgsGeometry.fromPolygonXY([points]), None)

    

    def road_segmentation(self, screenshot):
        size = screenshot.size()
        h = size.width()
        w = size.height()

        # Get the QImage Item and convert it to a byte string
        qimg = screenshot.toImage()
        img_array = qimage2ndarray.rgb_view(qimg)
        self.dlg.results_text_edit.append(str(img_array.shape))
        

        # Get Road Segmentation of the image
        segmentation = get_segmentation(img_array,w,h)
        cv2.imwrite(r"C:\Users\EkremSerdar\Downloads\segmented_image\segmented.png", segmentation)
        #save_prediction(segmentation)
        self.dlg.results_text_edit.append(str(segmentation.shape))
     
        # Turn Segmentation image to QPixmap
        qimage = qimage2ndarray.array2qimage(segmentation)
        pixmap = QPixmap.fromImage(qimage)
        
        return pixmap


        

   


    
