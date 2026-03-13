from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import SettingCard, BodyLabel, Slider
from datetime import datetime


class RangeSliderCard(SettingCard):
    """ A setting card with two sliders to select a range """
    rangeChanged = pyqtSignal(int, int)

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.value_formatter = str  # Default formatter


        self.slider_widget = QWidget(self)
        slider_layout = QVBoxLayout(self.slider_widget)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(5)

        # Start slider
        start_layout = QHBoxLayout()
        self.start_label = BodyLabel("Start: 0")
        self.start_slider = Slider(Qt.Horizontal)
        self.start_slider.setMinimumWidth(200)
        start_layout.addWidget(self.start_label)
        start_layout.addWidget(self.start_slider, 0, Qt.AlignRight)

        # End slider
        end_layout = QHBoxLayout()
        self.end_label = BodyLabel("End: 100")
        self.end_slider = Slider(Qt.Horizontal)
        self.end_slider.setMinimumWidth(200)
        end_layout.addWidget(self.end_label)
        end_layout.addWidget(self.end_slider, 0, Qt.AlignRight)

        slider_layout.addLayout(start_layout)
        slider_layout.addLayout(end_layout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.slider_widget)

        self.start_slider.valueChanged.connect(self._on_slider_value_changed)
        self.end_slider.valueChanged.connect(self._on_slider_value_changed)

        self.setRange(0, 100)
        self.end_slider.setValue(100)

    def _on_slider_value_changed(self):
        start_val = self.start_slider.value()
        end_val = self.end_slider.value()

        # identify which slider was moved
        sender = self.sender()

        # ensure start <= end
        if sender is self.start_slider and start_val > end_val:
            self.end_slider.setValue(start_val)
        elif sender is self.end_slider and end_val < start_val:
            self.start_slider.setValue(end_val)

        self._update_labels()
        self.rangeChanged.emit(self.start_slider.value(), self.end_slider.value())

    def set_value_formatter(self, formatter):
        """ Set a function to format the integer value for display """
        self.value_formatter = formatter
        self._update_labels()


    def setRange(self, start, end):
        """ Set the range for the sliders """
        self.start_slider.setRange(start, end)
        self.end_slider.setRange(start, end)
        self.start_slider.setValue(start)
        self.end_slider.setValue(end)
        self._update_labels()

    def value(self):
        """ Get the current range value """
        return self.start_slider.value(), self.end_slider.value()

    def _update_labels(self):
        """ Update the labels with the current slider values """
        start_val = self.start_slider.value()
        end_val = self.end_slider.value()

        try:
            start_text = self.value_formatter(start_val)
            end_text = self.value_formatter(end_val)
        except (ValueError, TypeError):
            # Fallback to string conversion if formatter fails (e.g., on initial values)
            start_text = str(start_val)
            end_text = str(end_val)

        self.start_label.setText(f"Start: {start_text}")
        self.end_label.setText(f"End: {end_text}")
        self.contentLabel.setText(f"{start_text} - {end_text}")