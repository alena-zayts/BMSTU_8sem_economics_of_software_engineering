import os
import sys

import numpy as np
from matplotlib import pyplot as plt
from PyQt5 import QtCore, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QHeaderView, QTableWidgetItem

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

EAF_ATTRIBUTES_VALUES = {
    'RELY': [0.75, 0.86, 1.0, 1.15, 1.40],
    'DATA': [0.94, 1.0, 1.08, 1.16],
    'CPLX': [0.70, 0.85, 1.0, 1.15, 1.30],
    'TIME': [1.00, 1.11, 1.50],
    'STOR': [1.00, 1.06, 1.21],
    'VIRT': [0.87, 1.00, 1.15, 1.30],
    'TURN': [0.87, 1.00, 1.07, 1.15],
    'ACAP': [1.46, 1.19, 1.00, 0.86, 0.71],
    'AEXP': [1.29, 1.15, 1.00, 0.91, 0.82],
    'PCAP': [1.42, 1.17, 1.00, 0.86, 0.70],
    'VEXP': [1.21, 1.10, 1.00, 0.90],
    'LEXP': [1.14, 1.07, 1.00, 0.95],
    'MODP': [1.24, 1.10, 1.00, 0.91, 0.82],
    'TOOL': [1.24, 1.10, 1.00, 0.91, 0.82],
    'SCED': [1.23, 1.08, 1.00, 1.04, 1.10],
}

CONSTANTS_FOR_PROJECTS_MODES = [
    {'c1': 3.2, 'p1': 1.05, 'c2': 2.5, 'p2': 0.38},
    {'c1': 3.0, 'p1': 1.12, 'c2': 2.5, 'p2': 0.35},
    {'c1': 2.8, 'p1': 1.2, 'c2': 2.5, 'p2': 0.32},
]


def PM(c1, p1, EAF, SIZE):
    return 3.2 * EAF * (SIZE ** 1.05)


def TM(c2, p2, PM):
    return 2.5 * (PM ** 0.38)


def calc_EAF(params: list):
    return np.prod(params)


class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = self.load_ui()

        self.ui.wbsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.classicTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_ui(self):
        # program is frozen exe
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        # program is a .py script
        else:
            base_path = os.getcwd()
        ui_path = os.path.join(base_path, 'mainwindow.ui')
        return uic.loadUi(ui_path, self)

    def convert_eaf_attribute_combobox_to_value(self, eaf_attribute_name: str) -> float:
        chosen_index = getattr(self, f'{eaf_attribute_name.lower()}ComboBox').currentIndex()
        real_value = EAF_ATTRIBUTES_VALUES[eaf_attribute_name.upper()][chosen_index]
        return real_value

    def calc_full_eaf(self):
        return np.prod([self.convert_eaf_attribute_combobox_to_value(eaf_attribute_name)
                        for eaf_attribute_name in EAF_ATTRIBUTES_VALUES.keys()])

    def calc_labor(self):
        project_mode = self.projectModeComboBox.currentIndex()
        c1 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['c1']
        p1 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['p1']

        project_size = self.sizeSpinBox.value()

        return c1 * self.calc_full_eaf() * (project_size ** p1)

    def calc_time(self):
        project_mode = self.projectModeComboBox.currentIndex()
        c2 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['c2']
        p2 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['p2']

        return c2 * (self.calc_labor() ** p2)

    @pyqtSlot(name="on_projectButton_clicked")
    def calculate_project(self):
        labor_clean = round(self.calc_labor(), 2)
        time_clean = round(self.calc_time(), 2)

        labor = round(labor_clean * 1.08, 2)
        time = round(time_clean * 1.36, 2)

        self.ui.laborLabel.setText(f'Трудоемкость: {labor}')
        self.ui.timeLabel.setText(f'Время разработки: {time}')

        for i in range(8):
            self.ui.wbsTable.setItem(i, 1, QTableWidgetItem(str(round(labor * int(self.ui.wbsTable.item(i, 0).text()) / 100.0, 2))))

        self.ui.wbsTable.setItem(8, 1, QTableWidgetItem(str(labor)))

        self.ui.classicTable.setItem(0, 0, QTableWidgetItem(str(round(labor_clean * 0.08, 2))))
        self.ui.classicTable.setItem(1, 0, QTableWidgetItem(str(round(labor_clean * 0.18, 2))))
        self.ui.classicTable.setItem(2, 0, QTableWidgetItem(str(round(labor_clean * 0.25, 2))))
        self.ui.classicTable.setItem(3, 0, QTableWidgetItem(str(round(labor_clean * 0.26, 2))))
        self.ui.classicTable.setItem(4, 0, QTableWidgetItem(str(round(labor_clean * 0.31, 2))))
        self.ui.classicTable.setItem(5, 0, QTableWidgetItem(str(round(labor_clean, 2))))
        self.ui.classicTable.setItem(6, 0, QTableWidgetItem(str(round(labor, 2))))
        self.ui.classicTable.setItem(0, 1, QTableWidgetItem(str(round(time_clean * 0.36, 2))))
        self.ui.classicTable.setItem(1, 1, QTableWidgetItem(str(round(time_clean * 0.36, 2))))
        self.ui.classicTable.setItem(2, 1, QTableWidgetItem(str(round(time_clean * 0.18, 2))))
        self.ui.classicTable.setItem(3, 1, QTableWidgetItem(str(round(time_clean * 0.18, 2))))
        self.ui.classicTable.setItem(4, 1, QTableWidgetItem(str(round(time_clean * 0.28, 2))))
        self.ui.classicTable.setItem(5, 1, QTableWidgetItem(str(round(time_clean, 2))))
        self.ui.classicTable.setItem(6, 1, QTableWidgetItem(str(round(time, 2))))

        y = []
        for i in range(5):
            t = round(float(self.ui.classicTable.item(i, 1).text()))
            for _ in range(t):
                y.append(round(round(float(self.ui.classicTable.item(i, 0).text())) / t))

        x = [i + 1 for i in range(len(y))]

        plt.bar(x, y)
        plt.show()

    @pyqtSlot(name="on_task1Button_clicked")
    def calculate_task1(self):
        project_size = 100
        # очень низкий, номинальный, очень высокий
        for cplx_index in [0, 2, 4]:
            cplx_value = EAF_ATTRIBUTES_VALUES['CPLX'][cplx_index]
            # обычный, промежуточный, встроенный
            for mode_index in range(3):
                mode_constants = CONSTANTS_FOR_PROJECTS_MODES[mode_index]
                c1, p1, c2, p2 = mode_constants['c1'], mode_constants['p1'], mode_constants['c2'], mode_constants['p2']
                y_acap_labor = []
                y_aexp_labor = []
                y_pcap_labor = []
                y_lexp_labor = []
                y_acap_time = []
                y_aexp_time = []
                y_pcap_time = []
                y_lexp_time = []

                x = [1, 2, 3]

                # Способности аналитика -- низкий, номинальный, высокий
                for pers_quality_index in range(1, 4):
                    acap_value = EAF_ATTRIBUTES_VALUES['ACAP'][pers_quality_index]
                    aexp_value = EAF_ATTRIBUTES_VALUES['AEXP'][pers_quality_index]
                    pcap_value = EAF_ATTRIBUTES_VALUES['PCAP'][pers_quality_index]
                    lexp_value = EAF_ATTRIBUTES_VALUES['LEXP'][pers_quality_index]

                    y_acap_labor.append(PM(c1, p1, calc_EAF([acap_value, cplx_value]), project_size))
                    y_acap_time.append(TM(c2, p2, y_acap_labor[-1]))

                    y_aexp_labor.append(PM(c1, p1, calc_EAF([aexp_value, cplx_value]), project_size))
                    y_aexp_time.append(TM(c2, p2, y_aexp_labor[-1]))

                    y_pcap_labor.append(PM(c1, p1, calc_EAF([pcap_value, cplx_value]), project_size))
                    y_pcap_time.append(TM(c2, p2, y_pcap_labor[-1]))

                    y_lexp_labor.append(PM(c1, p1, calc_EAF([lexp_value, cplx_value]), project_size))
                    y_lexp_time.append(TM(c2, p2, y_lexp_labor[-1]))

                plt.suptitle(f'PM, TM; mode={mode_index}, CPLX={cplx_index}')
                plt.subplot(121)
                line1, = plt.plot(x, y_acap_labor, 'r', label='ACAP')
                line2, = plt.plot(x, y_aexp_labor, 'g', label='AEXP')
                line3, = plt.plot(x, y_pcap_labor, 'b', label='PCAP')
                line4, = plt.plot(x, y_lexp_labor, 'y', label='LEXP')
                plt.subplot(122)
                plt.plot(x, y_acap_time, 'r', x, y_aexp_time, 'g', x, y_pcap_time, 'b', x, y_lexp_time, 'y')
                plt.legend(handles=[line1, line2, line3, line4])
                plt.show()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
