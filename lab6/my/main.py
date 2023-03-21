import os
import sys

import numpy as np
from matplotlib import pyplot as plt
from PyQt5 import QtCore, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QHeaderView, QTableWidgetItem, QLineEdit

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

LIFE_STAGES_PM_PERCENTS = [8, 18, 25, 26, 31, 100, 108]
LIFE_STAGES_TM_PERCENTS = [36, 36, 18, 18, 28, 100, 136]
WBS_PERCENTS = [4, 12, 44, 6, 14, 7, 7, 6, 100]


def calc_PM(c1: float, p1: float, EAF: float, SIZE: float) -> float:
    return c1 * EAF * (SIZE ** p1)


def calc_TM(c2: float, p2: float, PM: float) -> float:
    return c2 * (PM ** p2)


def calc_EAF(eaf_attributes: list) -> float:
    return float(np.prod(eaf_attributes))


class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = self.load_ui()

        self.tableWBS.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableLifeStages.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWBS.resizeColumnsToContents()
        self.tableLifeStages.resizeColumnsToContents()

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

    def calc_EAF_from_ui(self) -> float:
        eaf_attributes = [self.convert_eaf_attribute_combobox_to_value(eaf_attribute_name)
                          for eaf_attribute_name in EAF_ATTRIBUTES_VALUES.keys()]

        return calc_EAF(eaf_attributes)

    def calc_PM_from_ui(self):
        project_mode = self.projectModeComboBox.currentIndex()
        c1 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['c1']
        p1 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['p1']
        EAF = self.calc_EAF_from_ui()
        SIZE = self.sizeSpinBox.value()

        return calc_PM(c1, p1, EAF, SIZE)

    def calc_TM_from_ui(self):
        project_mode = self.projectModeComboBox.currentIndex()
        c2 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['c2']
        p2 = CONSTANTS_FOR_PROJECTS_MODES[project_mode]['p2']
        PM = self.calc_PM_from_ui()

        return calc_TM(c2, p2, PM)

    @pyqtSlot(name="on_task2EstimateProjectButton_clicked")
    def task2EstimateProject(self):
        round_to = 2
        PM = round(self.calc_PM_from_ui(), round_to)
        TM = round(self.calc_TM_from_ui(), round_to)

        self.lineEditPM.setText(str(PM))
        self.lineEditTM.setText(str(TM))

        y = []
        for i in range(len(LIFE_STAGES_PM_PERCENTS)):
            cur_pm = PM * LIFE_STAGES_PM_PERCENTS[i] / 100.0
            cur_tm = TM * LIFE_STAGES_TM_PERCENTS[i] / 100.0

            pm_str = f'{round(cur_pm, round_to)} ({LIFE_STAGES_PM_PERCENTS[i]} %)'
            tm_str = f'{round(cur_tm, round_to)} ({LIFE_STAGES_TM_PERCENTS[i]} %)'
            if i == 0:
                pm_str = f'(+{pm_str})'
                tm_str = f'(+{tm_str})'
            if i < 5:
                for _ in range(round(cur_tm)):
                    y.append(round(round(cur_pm) / round(cur_tm)))

            self.tableLifeStages.setItem(i, 0, QTableWidgetItem(pm_str))
            self.tableLifeStages.setItem(i, 1, QTableWidgetItem(tm_str))

        for i in range(len(WBS_PERCENTS)):
            budget_percents_str = f'{WBS_PERCENTS[i]}%'
            person_months_str = f'{round(PM * WBS_PERCENTS[i] / 100.0, round_to)}'
            self.tableWBS.setItem(i, 0, QTableWidgetItem(budget_percents_str))
            self.tableWBS.setItem(i, 1, QTableWidgetItem(person_months_str))


        x = [i + 1 for i in range(len(y))]

        plt.bar(x, y)
        plt.show()

    @pyqtSlot(name="on_task4EstimateVarProjectButton_clicked")
    def task4EstimateVarProject(self):
        # labor_clean = round(self.calc_PM_from_ui(), 2)
        # time_clean = round(self.calc_TM_from_ui(), 2)
        #
        # labor = round(labor_clean * 1.08, 2)
        # time = round(time_clean * 1.36, 2)
        #
        # self.ui.laborLabel.setText(f'Трудоемкость: {labor}')
        # self.ui.timeLabel.setText(f'Время разработки: {time}')
        #
        # for i in range(8):
        #     self.ui.wbsTable.setItem(i, 1, QTableWidgetItem(
        #         str(round(labor * int(self.ui.wbsTable.item(i, 0).text()) / 100.0, 2))))
        #
        # self.ui.wbsTable.setItem(8, 1, QTableWidgetItem(str(labor)))
        #
        # self.ui.classicTable.setItem(0, 0, QTableWidgetItem(str(round(labor_clean * 0.08, 2))))
        # self.ui.classicTable.setItem(1, 0, QTableWidgetItem(str(round(labor_clean * 0.18, 2))))
        # self.ui.classicTable.setItem(2, 0, QTableWidgetItem(str(round(labor_clean * 0.25, 2))))
        # self.ui.classicTable.setItem(3, 0, QTableWidgetItem(str(round(labor_clean * 0.26, 2))))
        # self.ui.classicTable.setItem(4, 0, QTableWidgetItem(str(round(labor_clean * 0.31, 2))))
        # self.ui.classicTable.setItem(5, 0, QTableWidgetItem(str(round(labor_clean, 2))))
        # self.ui.classicTable.setItem(6, 0, QTableWidgetItem(str(round(labor, 2))))
        # self.ui.classicTable.setItem(0, 1, QTableWidgetItem(str(round(time_clean * 0.36, 2))))
        # self.ui.classicTable.setItem(1, 1, QTableWidgetItem(str(round(time_clean * 0.36, 2))))
        # self.ui.classicTable.setItem(2, 1, QTableWidgetItem(str(round(time_clean * 0.18, 2))))
        # self.ui.classicTable.setItem(3, 1, QTableWidgetItem(str(round(time_clean * 0.18, 2))))
        # self.ui.classicTable.setItem(4, 1, QTableWidgetItem(str(round(time_clean * 0.28, 2))))
        # self.ui.classicTable.setItem(5, 1, QTableWidgetItem(str(round(time_clean, 2))))
        # self.ui.classicTable.setItem(6, 1, QTableWidgetItem(str(round(time, 2))))
        #
        # y = []
        # for i in range(5):
        #     t = round(float(self.ui.classicTable.item(i, 1).text()))
        #     for _ in range(t):
        #         y.append(round(round(float(self.ui.classicTable.item(i, 0).text())) / t))
        #
        # x = [i + 1 for i in range(len(y))]
        #
        # plt.bar(x, y)
        # plt.show()
        '''
        Режим: обычный
        KLOC=25000
        Планируется привлечь высококвалифицированную команду программистов с высоким знанием языков программирования.
        В проекте будут использованы самые современные методы программирования.
        Также планируется высокий уровень автоматизации процесса разработки за счет использования эффективных программных инструментов.

        Произвести оценку по методике COCOMO для обычного режима
        '''
        pass

    @pyqtSlot(name="on_task3ExperimentButton_clicked")
    def task3Experiment(self):
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

                    y_acap_labor.append(calc_PM(c1, p1, calc_EAF([acap_value, cplx_value]), project_size))
                    y_acap_time.append(calc_TM(c2, p2, y_acap_labor[-1]))

                    y_aexp_labor.append(calc_PM(c1, p1, calc_EAF([aexp_value, cplx_value]), project_size))
                    y_aexp_time.append(calc_TM(c2, p2, y_aexp_labor[-1]))

                    y_pcap_labor.append(calc_PM(c1, p1, calc_EAF([pcap_value, cplx_value]), project_size))
                    y_pcap_time.append(calc_TM(c2, p2, y_pcap_labor[-1]))

                    y_lexp_labor.append(calc_PM(c1, p1, calc_EAF([lexp_value, cplx_value]), project_size))
                    y_lexp_time.append(calc_TM(c2, p2, y_lexp_labor[-1]))

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
    # sys.exit(main())
    app = QApplication([])
    application = MainWindow()
    application.show()
    sys.exit(app.exec())
