from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QSizePolicy
from qfluentwidgets import (Pivot, qrouter, SegmentedWidget, TabBar, CheckBox, ComboBox,
                            TabCloseButtonDisplayMode, BodyLabel, SpinBox, BreadcrumbBar,
                            SegmentedToggleToolWidget, FluentIcon)
from view.gallery_interface import GalleryInterface
from view.dataprocessinggroup import DataProcessingGroup
from common.translator import Translator
from common.style_sheet import StyleSheet

class RoutineInspectionInterface(GalleryInterface):
    """
    Routine Inspection GUI
    """
    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.routineInspection,
            subtitle="Routine inspection data visualization",
            parent=parent
        )
    
        self.setObjectName('routineInspectionInterface')
        self.addExampleCard(
            title=self.tr('Which Project?'),
            widget=SegmentedWidget(self),
            stretch=1
        )

class PivotInterface(QWidget):
    """ Pivot interface """
    Nav = Pivot
    processingStatusChanged = pyqtSignal(str, str)  # Signal to forward status to MainWindow

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumHeight(140)
        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.LomaInterface = DataProcessingGroup(self)
        self.LomaInterface.processingStatusChanged.connect(self.processingStatusChanged)

        self.HummingbirdInterface = DataProcessingGroup(self)
        self.HummingbirdInterface.processingStatusChanged.connect(self.processingStatusChanged)

        #add items to pivot
        self.addSubInterface(self.LomaInterface, 'Loma', self.tr('Loma'))
        self.addSubInterface(self.HummingbirdInterface, 'Hummingbird', self.tr('Hummingbird'))

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        StyleSheet.ROUTINEINSPECTION_INTERFACE.apply(self)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.LomaInterface)
        self.pivot.setCurrentItem(self.LomaInterface.objectName())

        qrouter.setDefaultRouteKey(self.stackedWidget, self.LomaInterface.objectName())
    
    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        if isinstance(widget, QLabel):
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