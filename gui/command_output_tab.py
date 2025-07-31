import sys
import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPlainTextEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont


class EmittingStream(QObject):
    text_written = pyqtSignal(str, bool)  # 第二个参数标识是否为错误

    def write(self, text):
        if text.strip():
            self.text_written.emit(text, False)

    def flush(self):
        pass


class EmittingErrorStream(QObject):
    text_written = pyqtSignal(str, bool)

    def write(self, text):
        if text.strip():
            self.text_written.emit(text, True)

    def flush(self):
        pass


class CommandOutputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        style_button = """
        QPushButton {
            background-color: #2d89ef; color: white; border-radius: 8px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #3aa0ff; }
        QPushButton:pressed { background-color: #1e5aad; }
        QPushButton:disabled { background-color: #7a7a7a; color: #dcdcdc; }
        """

        # 标签
        self.label_info = QLabel("程序运行日志：")
        self.label_info.setFont(QFont("微软雅黑", 12))
        self.label_info.setAlignment(Qt.AlignCenter)
        self.label_info.setStyleSheet("margin-bottom: 10px;")

        # 输出框
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 11))
        self.output_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")

        # 清空按钮
        self.btn_clear = QPushButton("清空日志")
        self.btn_clear.setFont(QFont("微软雅黑", 12))
        self.btn_clear.setStyleSheet(style_button)
        self.btn_clear.setFixedHeight(36)
        self.btn_clear.clicked.connect(self.clear_output)

        # 布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_info)
        main_layout.addWidget(self.output_area)
        main_layout.addWidget(self.btn_clear)
        main_layout.addStretch()
        self.setLayout(main_layout)

        # 重定向 stdout/stderr
        self.stdout_stream = EmittingStream()
        self.stderr_stream = EmittingErrorStream()
        self.stdout_stream.text_written.connect(self.append_text)
        self.stderr_stream.text_written.connect(self.append_text)

        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    def append_text(self, text, is_error=False):
        """将日志追加到输出框，并加时间戳"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if is_error:
            self.output_area.appendHtml(
                f'<span style="color: red;">[{timestamp}] [ERROR] {text}</span>'
            )
        else:
            self.output_area.appendHtml(
                f'<span style="color: lightgreen;">[{timestamp}] [INFO] {text}</span>'
            )
        self.output_area.verticalScrollBar().setValue(
            self.output_area.verticalScrollBar().maximum()
        )

    def clear_output(self):
        self.output_area.clear()

    def closeEvent(self, event):
        """关闭时恢复 stdout/stderr"""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        event.accept()
