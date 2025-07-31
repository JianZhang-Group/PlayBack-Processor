from PyQt5.QtWidgets import QMainWindow, QTabWidget, QApplication
from PyQt5.QtGui import QFont, QIcon
from gui.playback_tab import PlaybackTab
from gui.export_video_tab import ExportVideoTab
from gui.command_output_tab import CommandOutputTab



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlayBack Processor GUI")
        self.setMinimumSize(1350, 600)
        self.move(
            QApplication.desktop().screen().rect().center() - self.rect().center()
        )

        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("微软雅黑", 12))
        self.tabs.setStyleSheet("QTabBar::tab { height: 40px; width: 160px; }")
        self.playback_tab = PlaybackTab()
        self.export_tab = ExportVideoTab()
        self.command_output_tab = CommandOutputTab()
        self.tabs.addTab(self.playback_tab, "回放")
        self.tabs.addTab(self.export_tab, "图片转视频")
        self.tabs.addTab(self.command_output_tab, "日志")

        self.setCentralWidget(self.tabs)