import math
import sys

from PyQt5 import QtCore, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QComboBox, QLabel, QLineEdit, QMainWindow, QSpinBox

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

points_levels_table = {
    'EI': [3, 4, 6],
    'EO': [4, 5, 7],
    'EQ': [3, 4, 6],
    'ILF': [7, 10, 15],
    'EIF': [5, 7, 10]
}

languages_FP_to_LOC_table = {
    'ASM': 320,
    'C': 128,
    'Cobol': 106,
    'Fortran': 106,
    'Pascal': 90,
    'CPP': 53,
    'Java': 53,
    'CSharp': 53,
    'Ada': 49,
    'SQL': 125,
    'VCPP': 34,
    'Delphi': 29,
    'Perl': 21,
    'Prolog': 54
}

arch_labour_table = {
    'PERS': [1.62, 1.26, 1.00, 0.83, 0.63, 0.50],
    'RCPX': [0.60, 0.83, 1.00, 1.33, 1.91, 2.72],
    'RUSE': [0.95, 1.00, 1.07, 1.15, 1.24],
    'PDIF': [0.87, 1.00, 1.29, 1.81, 2.61],
    'PREX': [1.33, 1.22, 1.00, 0.87, 0.74, 0.62],
    'FCIL': [1.30, 1.10, 1.00, 0.87, 0.73, 0.62],
    'SCED': [1.43, 1.14, 1.00, 1.00, 1.00]
}

p_params_levels_table = {
    'PREC': [6.2, 4.96, 3.72, 2.48, 1.24, 0.0],
    'FLEX': [5.07, 4.05, 3.04, 2.03, 1.01, 0.0],
    'RESL': [7.07, 5.65, 4.24, 2.83, 1.41, 0.0],
    'TEAM': [5.48, 4.38, 3.29, 2.19, 1.10, 0.0],
    'PMAT': [7.8, 6.24, 4.68, 3.12, 1.56, 0.0]
}



experience_levels = [4, 7, 13, 25, 50]

difficulties = ['Simple', 'Medium', 'Difficult']


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi("ui.ui", self)

        self.LOC = 0
        self.p = 0

    ############### tab1
    def get_sys_params(self):
        return [self.tab_1.findChild(QSpinBox, f'spinBox_{i}').value() for i in range(1, 15)]

    def get_languages_percents(self):
        return {lang: float(self.tab_1.findChild(QLineEdit, f'{lang}Edit').text()) for lang in
                languages_FP_to_LOC_table.keys()}

    def get_table_point_dif_amount(self):
        return [{
            characteristic: int(self.tab_1.findChild(QLineEdit, f'{characteristic}Edit{i}').text())
            for characteristic in points_levels_table.keys()
        } for i in range(1, 4)]

    def show_tab1_results(self, characteristics_results, NormFP, FP, LOC):
        for characteristic in points_levels_table.keys():
            self.tab_1.findChild(QLabel, f'{characteristic}Label').setText(str(characteristics_results[characteristic]))

        self.tab_1.findChild(QLabel, 'ResLabel').setText(str(sum(characteristics_results.values())))

        self.tab_1.findChild(QLabel, 'NormFPLabel').setText(str(NormFP))
        self.tab_1.findChild(QLabel, 'FPLabel').setText(str(FP))
        self.tab_1.findChild(QLabel, 'LOCLabel').setText(str(LOC))

    @pyqtSlot(name='on_calculateButton_clicked')
    def calc_tab1(self):
        table_point_dif_amount = self.get_table_point_dif_amount()
        point_results = {point: 0 for point in points_levels_table.keys()}
        for difficulty_level in range(3):
            for point in point_results.keys():
                point_results[point] += points_levels_table[point][difficulty_level] * \
                                        table_point_dif_amount[difficulty_level][point]
        total_points_amount = sum(point_results.values())

        sys_params = self.get_sys_params()
        languages_percents = self.get_languages_percents()
        total_points_amount_corrected = total_points_amount * (0.65 + 0.01 * sum(sys_params))

        # Пересчет FP-оценок в LOC-оценки
        self.LOC = 0
        for lang in languages_FP_to_LOC_table.keys():
            self.LOC += float(total_points_amount_corrected) * languages_percents[lang] * languages_FP_to_LOC_table[
                lang] / 100.0

        self.show_tab1_results(point_results, round(total_points_amount_corrected, 2), total_points_amount,
                               int(self.LOC))

    ######################## tab2
    ######### p
    def get_p_params(self):
        return {p_param: self.tab_2.findChild(QComboBox, f'powComboBox_{i + 1}').currentIndex()
                for i, p_param in enumerate(p_params_levels_table.keys())}

    def show_p_result(self):
        self.tab_2.findChild(QLabel, 'PLabel').setText(str(round(self.p, 3)))

    @pyqtSlot(name='on_pCalculateButton_clicked')
    def calculate_p(self):
        p_params = self.get_p_params()
        sum_p_params = sum([p_params_levels_table[p_param][p_params[p_param]] for p_param in p_params.keys()])

        self.p = sum_p_params / 100 + 1.01
        self.show_p_result()

    ######### arch
    def get_arch_params_levels(self):
        return [self.tab_2.findChild(QComboBox, f'archComboBox_{i}').currentIndex() for i in range(1, 8)]

    def get_avg_salary(self):
        return float(self.tab_2.findChild(QLineEdit, 'avgSalaryEdit').text())

    def show_arch_results(self, labor, time, budget):
        self.tab_2.findChild(QLabel, 'archLabLabel').setText(str(labor))
        self.tab_2.findChild(QLabel, 'archTimeLabel').setText(str(time))
        self.tab_2.findChild(QLabel, 'archBudgetLabel').setText(str(budget))

    @pyqtSlot(name='on_archCalculateButton_clicked')
    def calculate_arch(self):
        self.calc_tab1()
        avg_salary = self.get_avg_salary()
        arch_params_levels = self.get_arch_params_levels()
        earch = (arch_labour_table['PERS'][arch_params_levels[0]] * arch_labour_table['RCPX'][arch_params_levels[1]] *
                 arch_labour_table['RUSE'][arch_params_levels[2]] * arch_labour_table['PDIF'][arch_params_levels[3]] *
                 arch_labour_table['PREX'][arch_params_levels[4]] * arch_labour_table['FCIL'][arch_params_levels[5]] *
                 arch_labour_table['SCED'][arch_params_levels[6]])

        self.calculate_p()
        print(self.p)
        labor = round(2.45 * earch * math.pow(self.LOC / 1000.0, self.p), 2)
        time = round(3 * math.pow(labor, 0.33 + 0.2 * (self.p - 1.01)), 2)
        budget = round(avg_salary * labor, 2)

        self.show_arch_results(labor, time, budget)

    ######### composition model
    def get_screen_forms_sum(self):
        screen_forms = [float(self.tab_2.findChild(QLineEdit, f'screen{difficulty}Edit').text()) for difficulty in difficulties]
        return 1 * screen_forms[0] + 2 * screen_forms[1] + 3 * screen_forms[2]

    def get_report_sum(self):
        reports = [float(self.tab_2.findChild(QLineEdit, f'report{difficulty}Edit').text()) for difficulty in difficulties]
        return 2 * reports[0] + 5 * reports[1] + 8 * reports[2]

    def get_3gen_modules_amount(self):
        return float(self.tab_2.findChild(QLineEdit, 'gen3Edit').text())

    def get_ruse_percent(self):
        return float(self.tab_2.findChild(QLineEdit, 'RUSEEdit').text())

    def get_experience_level(self):
        return self.tab_2.findChild(QComboBox, 'expComboBox').currentIndex()

    def show_comp_results(self, labor, time, budget):
        self.tab_2.findChild(QLabel, 'compLabLabel').setText(str(labor))
        self.tab_2.findChild(QLabel, 'compTimeLabel').setText(str(time))
        self.tab_2.findChild(QLabel, 'compBudgetLabel').setText(str(budget))

    @pyqtSlot(name='on_compCalculateButton_clicked')
    def calculate_comp(self):
        avg_salary = self.get_avg_salary()
        ruse_percent = self.get_ruse_percent()
        exp_level = experience_levels[self.get_experience_level()]

        screen_forms_sum = self.get_screen_forms_sum()
        reports_sum = self.get_report_sum()
        gen3_modules_amount = self.get_3gen_modules_amount()

        total_points_amount = screen_forms_sum + reports_sum + gen3_modules_amount * 10

        NOP = total_points_amount * (100 - ruse_percent) / 100
        labor = round(NOP / exp_level, 2)
        time = round(3 * math.pow(labor, 0.33 + 0.2 * (self.p - 1.01)), 2)
        budget = round(avg_salary * labor, 2)

        self.show_comp_results(labor, time, budget)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
