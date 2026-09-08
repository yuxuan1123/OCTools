"""独立运行入口：python -m home"""

import sys

from PySide6.QtWidgets import QApplication

from home.tab_home import TabHome


def main():
    app = QApplication(sys.argv)
    win = TabHome()
    win.resize(760, 900)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
