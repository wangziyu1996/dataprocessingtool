# coding: utf-8
from PyQt5.QtCore import QUrl, QSize, QTimer, Qt
from PyQt5.QtGui import QIcon, QDesktopServices, QColor
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen, SystemThemeListener, isDarkTheme, InfoBar, InfoBarPosition)
from qfluentwidgets import FluentIcon as FIF

from view.home_interface import HomeInterface
from view.gallery_interface import GalleryInterface
from view.routineinspection_interface import RoutineInspectionInterface, PivotInterface
from view.polariscope_interface import PolariscopeInterface
from view.autoasphericstation_interface import AutoAsphericStationInterface
from view.axoscan_interface import AxoscanInterface
from view.cary7000_interface import Cary7000Interface
from view.lambda1050_interface import Lambda1050Interface
from view.imagemasterhr_interface import ImageMasterHRInterface
from view.zygonewview_interface import ZygoNewviewInterface
from view.provr_interface import ProVRInterface
from view.hexagon_interface import HexagonInterface
from view.luphoscan_interface import LuphoscanInterface
from view.oc3d101dual_interface import OC3D101DualInterface
from view.wpa_interface import WPAInterface
from view.hazegardi_interface import HazeGardiInterface
from view.setting_interface import SettingInterface
from common.config import cfg
from common.icons import Icon
from common.signal_bus import signalBus
from common.translator import Translator
from common import resource


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        self.routineInspectionInterface = RoutineInspectionInterface(self)
        self.polariscopeInterface = PolariscopeInterface(self)
        self.autoAsphericStationInterface = AutoAsphericStationInterface(self)
        self.axoscanInterface = AxoscanInterface(self)
        self.cary7000Interface = Cary7000Interface(self)
        self.hazeGardiInterface = HazeGardiInterface(self)
        self.imageMasterHRInterface = ImageMasterHRInterface(self)
        self.hexagonInterface = HexagonInterface(self)
        self.lambda1050Interface = Lambda1050Interface(self)
        self.luphoscanInterface = LuphoscanInterface(self)
        self.oc3d101DualInterface = OC3D101DualInterface(self)
        self.provrInterface = ProVRInterface(self)
        self.zygoNewViewInterface = ZygoNewviewInterface(self)
        self.wpaInterface = WPAInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        # start theme listener
        self.themeListener.start()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)

        # Connect the status signal from the processing interface to the info bar slot
        pivot_interface = self.routineInspectionInterface.findChild(PivotInterface)
        if pivot_interface:
            pivot_interface.processingStatusChanged.connect(self.show_info_bar)

    def show_info_bar(self, status, message):
        """ Create and show an InfoBar. """
        if status == 'Success':
            InfoBar.success(
                title='Success',
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,  # 5 seconds
                parent=self
            )
        elif status == 'Error':
            InfoBar.error(
                title='Error',
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,  # Persists until closed
                parent=self
            )
        else:  # Info
            InfoBar.info(
                title='Info',
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()

        self.addSubInterface(self.routineInspectionInterface, FIF.PENCIL_INK, t.routineInspection)
        """
        self.addSubInterface(self.polariscopeInterface, FIF.PENCIL_INK, t.polariscope)
        self.addSubInterface(self.autoAsphericStationInterface, FIF.PENCIL_INK, t.autoAsphericStation)
        self.addSubInterface(self.luphoscanInterface, FIF.PENCIL_INK, t.luphoscan)
        self.addSubInterface(self.zygoNewViewInterface, FIF.PENCIL_INK, t.zygoNewView)
        self.addSubInterface(self.oc3d101DualInterface, FIF.PENCIL_INK, t.oc3d101Dual)
        self.addSubInterface(self.axoscanInterface, FIF.PENCIL_INK, t.axoscan)
        self.addSubInterface(self.wpaInterface, FIF.PENCIL_INK, t.wpa)
        self.addSubInterface(self.hexagonInterface, FIF.PENCIL_INK, t.hexagon)
        self.addSubInterface(self.lambda1050Interface, FIF.PENCIL_INK, t.lambda1050)
        self.addSubInterface(self.cary7000Interface, FIF.PENCIL_INK, t.cary7000)
        self.addSubInterface(self.hazeGardiInterface, FIF.PENCIL_INK, t.hazeGardi)
        self.addSubInterface(self.imageMasterHRInterface, FIF.PENCIL_INK, t.imageMasterHR)
        self.addSubInterface(self.provrInterface, FIF.PENCIL_INK, t.provr)
        """
        # add custom widget to bottom
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon("./app/images/kunkun.png"))
        self.setWindowTitle('Data Processing Tool')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # retry
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
#                w.scrollToCard(index)