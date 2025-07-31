from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from gui.main_window import MainWindow
import sys

def main():
    # 启用高DPI缩放
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()