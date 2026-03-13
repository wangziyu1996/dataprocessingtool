from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QSizePolicy
from qfluentwidgets import (Pivot, qrouter, SegmentedWidget, TabBar, CheckBox, ComboBox,
                            TabCloseButtonDisplayMode, BodyLabel, SpinBox, BreadcrumbBar,
                            SegmentedToggleToolWidget, FluentIcon)
from view.gallery_interface import GalleryInterface
from common.translator import Translator
from common.style_sheet import StyleSheet

class WPAInterface(GalleryInterface):
    """
    WPA GUI
    """
    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.wpa,
            subtitle="Data Processing for WPA",
            parent=parent
        )
    
        self.setObjectName('wpaInterface')
        self.addExampleCard(
            title=self.tr('Which kind of data do you want to process?'),
            widget=SegmentedWidget(self),
            stretch=1
        )

class PivotInterface(QWidget):
    """ Pivot interface """
    Nav = Pivot

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumHeight(140)
        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.grrInterface = QLabel('GRR Interface', self)
        self.correlationInterface = QLabel('Correlation Interface', self)

        #add items to pivot
        self.addSubInterface(self.grrInterface, 'GRR', self.tr('GRR'))
        self.addSubInterface(self.correlationInterface, 'Correlation', self.tr('Correlation'))

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        StyleSheet.WPA_INTERFACE.apply(self)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.grrInterface)
        self.pivot.setCurrentItem(self.grrInterface.objectName())

        qrouter.setDefaultRouteKey(self.stackedWidget, self.grrInterface.objectName())
    
    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget))

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())
    

class SegmentedWidget(PivotInterface):
    """ Segmented widget"""
    Nav = SegmentedWidget
    def __init__(self, parent = None):
        super().__init__(parent)
        self.vBoxLayout.removeWidget(self.pivot)
        self.vBoxLayout.insertWidget(0, self.pivot)