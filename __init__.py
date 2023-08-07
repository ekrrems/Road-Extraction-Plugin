# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RoadExtractor
                                 A QGIS plugin
 This plugin automatically extracts roads from satellite images
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-08-01
        copyright            : (C) 2023 by Ekrrems
        email                : ekremserdarozturk@hotmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RoadExtractor class from file RoadExtractor.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .road_extractor import RoadExtractor
    return RoadExtractor(iface)
