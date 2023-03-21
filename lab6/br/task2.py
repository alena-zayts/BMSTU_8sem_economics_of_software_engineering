import sys

from PyQt5.QtWidgets import QApplication

from ui.start_window import TaskWindow


if __name__ == '__main__':
    app = QApplication([])
    application = TaskWindow()
    application.show()

    sys.exit(app.exec())