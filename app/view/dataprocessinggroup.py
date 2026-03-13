import sys
import os
import re
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QSizePolicy
from qfluentwidgets import (PushSettingCard, SettingCard, PushButton, PrimaryPushButton, FluentIcon)

# 确保 Python 能找到 app/config 目录
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from functions.visRoutineInspection import VisRoutineInspection
from config.kpi_mapping import kpi_df
from components.range_slider_card import RangeSliderCard


class CustomFileSettingCard(SettingCard):
    chooseFileClicked = pyqtSignal()
    extraButtonClicked = pyqtSignal()

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.contentLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.contentLabel.setMinimumWidth(1)
        self.chooseFileButton = PushButton("Choose File", self)
        self.extraButton = PushButton("Load Data", self)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.chooseFileButton)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addWidget(self.extraButton)
        self.hBoxLayout.addSpacing(16)
        self.chooseFileButton.clicked.connect(self.chooseFileClicked)
        self.extraButton.clicked.connect(self.extraButtonClicked)

class DataProcessingGroup(QWidget):
    sourcePathChanged = pyqtSignal(str)
    destinationPathChanged = pyqtSignal(str)
    processingStatusChanged = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.inputFilePath = "FILE_PATH"
        self.processor = None
        self.vLayout = QVBoxLayout(self)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(10)
        self.sourceSelectionCard = CustomFileSettingCard(
            icon=FluentIcon.DOCUMENT,
            title="Input File",
            content=self.inputFilePath
        )
        self.rangeCard = RangeSliderCard(
            FluentIcon.DATE_TIME,
            "Processing Date Range",
            "N/A",
            parent=self
        )
        self.rangeCard.set_value_formatter(
            lambda x: datetime.fromordinal(x).strftime('%Y-%m-%d')
        )
        self.processButton = PrimaryPushButton('Generate Report', self)
        self.vLayout.addWidget(self.sourceSelectionCard)
        self.vLayout.addWidget(self.rangeCard)
        hLayout = QHBoxLayout()
        hLayout.addStretch(1)
        hLayout.addWidget(self.processButton)
        hLayout.addStretch(1)
        self.vLayout.addLayout(hLayout)
        self.sourceSelectionCard.chooseFileClicked.connect(self._onSourceSelectClicked)
        self.sourceSelectionCard.extraButtonClicked.connect(self._onLoadDataClicked)
        self.processButton.clicked.connect(self._onStartProcessingClicked)

    def _onLoadDataClicked(self):
        if self.inputFilePath != "FILE_PATH":
            try:
                self.processor = VisRoutineInspection(self.inputFilePath, None)
                min_date, max_date = self.processor.datacleansing()
                if min_date and max_date:
                    min_ordinal = min_date.toordinal()
                    max_ordinal = max_date.toordinal()
                    self.rangeCard.setRange(min_ordinal, max_ordinal)
                    self.rangeCard.setValue((min_ordinal, max_ordinal))
                self.processingStatusChanged.emit('Success', 'Data loaded and cleansed successfully. Ready to generate report.')
            except Exception as e:
                self.processingStatusChanged.emit('Error', f'An error occurred during data loading: {e}')
        else:
            self.processingStatusChanged.emit('Info', 'Please select an input file first.')

    def _onStartProcessingClicked(self):
        if not self.processor:
            self.processingStatusChanged.emit('Info', 'Please load data first by clicking the "Load Data" button.')
            return
        output_html_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report As", "", "HTML Files (*.html)"
        )
        if not output_html_path:
            return
        try:
            # --- 关键修复：从 kpi_df (DataFrame) 动态构建 kpi_mapping (字典) ---
            kpi_mapping_dict = {}
            for index, row in kpi_df.iterrows():
                kpi_name = row['KPI']
                tester_name = row['Tester']
                usl = row['USL']
                lsl = row['LSL']
                
                sheet_name = None
                y_columns = []

                # 1. 为 OC 数据设置明确的映射规则
                if 'OC-L1S1' in kpi_name:
                    sheet_name = 'OC-L1'
                    y_columns = ['S1 Decenter(μm)-x', 'S1 Decenter(μm)-y', 'S1 Decenter(μm)-abs']
                elif 'OC-L1S2' in kpi_name:
                    sheet_name = 'OC-L1'
                    y_columns = ['S2 Decenter(μm)-x', 'S2 Decenter(μm)-y', 'S2 Decenter(μm)-abs']
                elif 'OC-L1tilt' in kpi_name:
                    sheet_name = 'OC-L1'
                    y_columns = ['tilt(\')-x', 'tilt(\')-y', 'tilt(\')-abs']
                elif 'OC-L2S1' in kpi_name:
                    sheet_name = 'OC-L2'
                    y_columns = ['S1 Decenter(μm)-x', 'S1 Decenter(μm)-y', 'S1 Decenter(μm)-abs']
                elif 'OC-L2S2' in kpi_name:
                    sheet_name = 'OC-L2'
                    y_columns = ['S2 Decenter(μm)-x', 'S2 Decenter(μm)-y', 'S2 Decenter(μm)-abs']
                elif 'OC-L2tilt' in kpi_name:
                    sheet_name = 'OC-L2'
                    y_columns = ['tilt(\')-x', 'tilt(\')-y', 'tilt(\')-abs']

                if sheet_name and y_columns:
                    kpi_mapping_dict[kpi_name] = {
                        'sheet_name': sheet_name,
                        'tester_name': tester_name,
                        'y_columns': y_columns,
                        'USL': usl,
                        'LSL': lsl
                    }
            
            # 获取用户选择的日期范围
            start_ordinal, end_ordinal = self.rangeCard.value()
            start_date = datetime.fromordinal(start_ordinal)
            end_date = datetime.fromordinal(end_ordinal)
            
            self.processor.outputFilePath = output_html_path
            # 修改：传递正确的参数给visualization方法
            charts, min_date, max_date = self.processor.visualization(start_date, end_date, output_html_path)
            self.processingStatusChanged.emit('Success', f'Report successfully generated at {output_html_path}')
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.processingStatusChanged.emit('Error', f'An error occurred during report generation: {e}')

    def _onSourceSelectClicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Source File", '.', "Excel Files (*.xlsx)"
        )
        if file_path:
            self.inputFilePath = file_path
            self.sourceSelectionCard.contentLabel.setText(file_path)
            self.sourcePathChanged.emit(file_path)
