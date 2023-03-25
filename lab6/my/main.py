import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from PyQt5 import QtCore, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QHeaderView, QTableWidgetItem

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

LIFE_STAGES_PM_PERCENTS = [8, 18, 25, 26, 31, 100, 108]
LIFE_STAGES_TM_PERCENTS = [36, 36, 18, 18, 28, 100, 136]
WBS_PERCENTS = [4, 12, 44, 6, 14, 7, 7, 6, 100]

CONSTANTS_FOR_PROJECTS_MODES = [
    #{'c1': 1.46, 'p1': 1.05, 'c2': 2.5, 'p2': 0.38},
    {'c1': 3.2, 'p1': 1.05, 'c2': 2.5, 'p2': 0.38},
    {'c1': 3.0, 'p1': 1.12, 'c2': 2.5, 'p2': 0.35},
    {'c1': 2.8, 'p1': 1.2, 'c2': 2.5, 'p2': 0.32},
]

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
            cur_pm = round(PM * LIFE_STAGES_PM_PERCENTS[i] / 100.0, round_to)
            cur_tm = round(TM * LIFE_STAGES_TM_PERCENTS[i] / 100.0, round_to)

            pm_str = f'{cur_pm} ({LIFE_STAGES_PM_PERCENTS[i]} %)'
            tm_str = f'{cur_tm} ({LIFE_STAGES_TM_PERCENTS[i]} %)'
            if i == 0:
                pm_str = f'(+{pm_str})'
                tm_str = f'(+{tm_str})'
            if i < 5:
                cur_pm = round(cur_pm)
                cur_tm = round(cur_tm)
                y.extend([round(cur_pm / cur_tm)] * cur_tm)

            self.tableLifeStages.setItem(i, 0, QTableWidgetItem(pm_str))
            self.tableLifeStages.setItem(i, 1, QTableWidgetItem(tm_str))

        for i in range(len(WBS_PERCENTS)):
            budget_percents_str = f'{WBS_PERCENTS[i]}%'
            person_months_str = f'{round(PM * WBS_PERCENTS[i] / 100.0, round_to)}'
            self.tableWBS.setItem(i, 0, QTableWidgetItem(budget_percents_str))
            self.tableWBS.setItem(i, 1, QTableWidgetItem(person_months_str))

        y = pd.Series(y, index=[i + 1 for i in range(len(y))])
        ax = y.plot(kind='bar')
        rects = ax.patches
        ax.set_title('Количество работников на протяжении всего цикла создания продукта')
        ax.set_xlabel('Номер месяца')
        ax.set_ylabel('Количество работников')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        labels = [f"{v}" for v in y]
        for rect, label in zip(rects, labels):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, label, ha="center", va="bottom")

        plt.show()

    @pyqtSlot(name="on_task4EstimateVarProjectButton_clicked")
    def task4EstimateVarProject(self):
        for eaf_attribute_name in EAF_ATTRIBUTES_VALUES.keys():
            box = getattr(self, f'{eaf_attribute_name.lower()}ComboBox')
            box.setCurrentText('Номинальный')

        self.sizeSpinBox.setValue(25.)
        self.pcapComboBox.setCurrentText('Высокий')
        self.lexpComboBox.setCurrentText('Высокий')
        self.modpComboBox.setCurrentText('Очень высокий')
        self.toolComboBox.setCurrentText('Высокий')
        self.projectModeComboBox.setCurrentText('Обычный')

        self.task2EstimateProject()

    @pyqtSlot(name="on_task3ExperimentButton_clicked")
    def task3Experiment(self):
        project_size = 100
        mode_index, mode_name = 1, 'промежуточный'
        mode_constants = CONSTANTS_FOR_PROJECTS_MODES[mode_index]
        c1, p1, c2, p2 = mode_constants['c1'], mode_constants['p1'], mode_constants['c2'], mode_constants['p2']

        cplx_indexes = [0, 2, 4]
        cplx_dots = ['^-', 'empty', 'o-', 'empty', '*-']
        cplx_names = ['очень низкий', 'номинальный', 'очень высокий']

        pq_indexes = [0, 1, 2, 3]
        pq_names = ['очень низкий', 'низкий', 'номинальный', 'высокий']

        pq_attribute_names = ['ACAP', 'AEXP', 'PCAP', 'LEXP']
        pq_attribute_colors = ['r', 'b', 'g', 'y']

        ys_PM = {cplx_name: {pq_attribute_name: [] for pq_attribute_name in pq_attribute_names}
                 for cplx_name in cplx_names}
        ys_TM = {cplx_name: {pq_attribute_name: [] for pq_attribute_name in pq_attribute_names}
                 for cplx_name in cplx_names}

        f, (ax_PM, ax_TM) = plt.subplots(1, 2)
        x = [1, 2, 3, 4]

        for cplx_index, cplx_name in zip(cplx_indexes, cplx_names):
            cplx_value = EAF_ATTRIBUTES_VALUES['CPLX'][cplx_index]

            for pq_attribute_index, pq_attribute_name in enumerate(pq_attribute_names):
                for pq_index, pq_name in zip(pq_indexes, pq_names):
                    pq_attribute_value = EAF_ATTRIBUTES_VALUES[pq_attribute_name][pq_index]
                    ys_PM[cplx_name][pq_attribute_name].append(calc_PM(
                        c1, p1, calc_EAF([pq_attribute_value, cplx_value]), project_size))
                    ys_TM[cplx_name][pq_attribute_name].append(calc_TM(c2, p2, ys_PM[cplx_name][pq_attribute_name][-1]))

                format_ = f'{pq_attribute_colors[pq_attribute_index]}{cplx_dots[cplx_index]}'
                label_ = f'{pq_attribute_name}, CPLX: {cplx_name}'

                ax_PM.plot(ys_PM[cplx_name][pq_attribute_name], format_, label=label_)
                ax_TM.plot(x, ys_TM[cplx_name][pq_attribute_name], format_, label=label_)

        ax_PM.set_title('Трудозатраты (PM)')
        ax_PM.set_xlabel('Уровень атрибута персонала')
        ax_PM.set_ylabel('Трудозатраты (в человеко-месяцах)')
        ax_PM.set_xticklabels(['', 'очень низкий', '', 'низкий', '', 'номинальный', '', 'высокий'])
        ax_PM.grid()
        ax_PM.legend()

        ax_TM.set_title('Время (TM)')
        ax_TM.set_xlabel('Уровень атрибута персонала')
        ax_TM.set_ylabel('Время (в месяцах)')
        ax_TM.set_xticklabels(['', 'очень низкий', '', 'низкий', '', 'номинальный', '', 'высокий'])
        ax_TM.grid()
        ax_TM.legend()

        f.suptitle(f'SIZE: {project_size}, mode: {mode_name}')
        plt.show()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())

# pyinstaller --add-data "mainwindow.ui;." main.py



