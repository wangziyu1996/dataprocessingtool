# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    HOME_INTERFACE = "home_interface"
    ICON_INTERFACE = "icon_interface"
    VIEW_INTERFACE = "view_interface"
    SETTING_INTERFACE = "setting_interface"
    GALLERY_INTERFACE = "gallery_interface"
    POLARISCOPE_INTERFACE = "polariscope_interface"
    AUTOASPHERICSTATION_INTERFACE = "autoasphericstation_interface"
    IMAGEMASTERHR_INTERFACE = "imagemasterhr_interface"
    PROVR_INTERFACE = "provr_interface"
    CARY7000_INTERFACE = "cary7000_interface"
    LAMBDA1050_INTERFACE = "lambda1050_interface"
    HAZEGARDI_INTERFACE = "hazegardi_interface"
    HEXAGON_INTERFACE = "hexagon_interface"
    LUPHOSCAN_INTERFACE = "luphoscan_interface"
    OC3D101DUAL_INTERFACE = "oc3d101dual_interface"
    AXOSCAN_INTERFACE = "axoscan_interface"
    ZYGONEWVIEW_INTERFACE = "zygonewview_interface"
    WPA_INTERFACE = "wpa_interface"
    ROUTINEINSPECTION_INTERFACE = "routineinspection_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"app/resource/qss/{theme.value.lower()}/{self.value}.qss"
