# home_interface.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap,QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from qfluentwidgets import (ScrollArea, qconfig, Theme, isDarkTheme, FluentIcon)
from common.config import QUICKSTART_URL, REPO_URL, TEMPLATE_URL
from common.style_sheet import StyleSheet
from components.link_card import LinkCardView
from components.sample_card import SampleCardView
from common.icons import Icon

class BannerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)
        
        self.vBoxLayout = QVBoxLayout(self)
        self.StarterLabel = QLabel("Data Processing Tool", self)
        self.banner = QPixmap("./app/images/header1.png")
        self.linkCardView = LinkCardView(self)       
        self.StarterLabel.setObjectName("starterLabel")

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.StarterLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            FluentIcon.PLAY,
            self.tr("Read Me"),
            self.tr("Learn how to use this application to process your data."),
            QUICKSTART_URL
        )
        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr("Code Repository"),
            self.tr("View the source code of this application."),
            REPO_URL
        )
        self.linkCardView.addCard(
            FluentIcon.LIBRARY,
            self.tr("Used Templates"),
            self.tr("View the data templates of this application. (Need access)"),
            TEMPLATE_URL
        )        

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            
        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))

class HomeInterface(ScrollArea):
    """ Home interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadInterface()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadInterface(self):
        """load interface"""

        RoutineInspectionToolList = SampleCardView(
            self.tr("Routine Inspection Entrance"), self.view
        )
        RoutineInspectionToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Routine Inspection"),
            content= self.tr("Processing routine inspection data from projects."),
            routeKey="routineInspectionInterface",
            index=0
        )
        self.vBoxLayout.addWidget(RoutineInspectionToolList)
"""
        DataProcessingToolList = SampleCardView(
            self.tr("Data Processing Entrance"), self.view
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Polariscope"),
            content= self.tr("Processing Ellipticity data from polariscope inspection."),
            routeKey="polariscopeInterface",
            index=0
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Auto Aspheric Station"),
            content= self.tr("Processing PV/slope error data from auto aspheric station inspection."),
            routeKey="autoAsphericStationInterface",
            index=1
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Luphoscan"),
            content= self.tr("Processing PV/slope error data from Luphoscan inspection."),
            routeKey="luphoscanInterface",
            index=2
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Zygo Newview"),
            content= self.tr("Processing roughness data from Zygo Newview inspection."),
            routeKey="zygoNewviewInterface",
            index=3
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("OC3D 101 Dual"),
            content= self.tr("Processing decenter data from OC3D101Dual inspection."),
            routeKey="oc3d101DualInterface",
            index=4
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Axoscan"),
            content= self.tr("Processing ellipticity data from Axoscan inspection."),
            routeKey="axoscanInterface",
            index=5
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("WPA"),
            content= self.tr("Processing retardance data from WPA inspection."),
            routeKey="wpaInterface",
            index=6
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Hexagon"),
            content= self.tr("Processing FAIs data from Hexagon inspection."),
            routeKey="hexagonInterface",
            index=7
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Lambda 1050+"),
            content= self.tr("Processing transmittance/reflectance data from Lambda 1050+ inspection."),
            routeKey="lambda1050Interface",
            index=8
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Cary 7000"),
            content= self.tr("Processing transmittance/reflectance data from Cary 7000 inspection."),
            routeKey="cary7000Interface",
            index=9
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("Haze Gard i"),
            content= self.tr("Processing haze data from Haze Gard i inspection."),
            routeKey="hazeGardiInterface",
            index=10
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("ImageMasterHR"),
            content= self.tr("Processing MTF data from ImageMasterHR inspection."),
            routeKey="imageMasterHRInterface",
            index=11
        )
        DataProcessingToolList.addSampleCard(
            icon= Icon.PENCIL_INK_FILLED,
            title= self.tr("ProVR"),
            content= self.tr("Processing MTF data from ProVR inspection."),
            routeKey="proVRInterface",
            index=12
        )
        self.vBoxLayout.addWidget(DataProcessingToolList)
"""