# coding: utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.text = self.tr('Text')
        self.view = self.tr('View')
        self.menus = self.tr('Menus & toolbars')
        self.icons = self.tr('Icons')
        self.layout = self.tr('Layout')
        self.dialogs = self.tr('Dialogs & flyouts')
        self.scroll = self.tr('Scrolling')
        self.material = self.tr('Material')
        self.dateTime = self.tr('Date & time')
        self.navigation = self.tr('Navigation')
        self.basicInput = self.tr('Basic input')
        self.statusInfo = self.tr('Status & info')
        self.price = self.tr("Price")
        self.polariscope = self.tr("Polariscope")
        self.autoAsphericStation = self.tr("Auto Aspheric Station")
        self.axoscan = self.tr("Axoscan")
        self.cary7000 = self.tr("Cary 7000")
        self.hazeGardi = self.tr("Haze Gard i")
        self.imageMasterHR = self.tr("ImageMasterHR")
        self.hexagon = self.tr("Hexagon")
        self.lambda1050 = self.tr("Lambda 1050+")
        self.luphoscan = self.tr("Luphoscan")
        self.oc3d101Dual = self.tr("OC3D 101 Dual")
        self.provr = self.tr("Pro VR")
        self.zygoNewView = self.tr("Zygo Newview")
        self.wpa = self.tr("WPA")
        self.routineInspection = self.tr("Routine Inspection")
