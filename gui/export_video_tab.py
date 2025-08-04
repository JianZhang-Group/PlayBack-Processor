from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QSpinBox,
    QProgressBar,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from function.export_logic import ExportVideoThread


class ExportVideoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img_dir = None
        self.out_dir = None
        self.thread = None

        style_select = """
        QPushButton {
            background-color: #2d89ef; color: white; border-radius: 8px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #3aa0ff; }
        QPushButton:pressed { background-color: #1e5aad; }
        QPushButton:disabled { background-color: #7a7a7a; color: #dcdcdc; }
        """
        style_export = """
        QPushButton {
            background-color: #28a745; color: white; border-radius: 8px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #34c759; }
        QPushButton:pressed { background-color: #1c7c35; }
        QPushButton:disabled { background-color: #7a7a7a; color: #dcdcdc; }
        """

        self.label_info = QLabel("请选择图片文件夹，设置参数并导出视频")
        self.label_info.setFont(QFont("微软雅黑", 12))
        self.label_info.setAlignment(Qt.AlignCenter)
        self.label_info.setStyleSheet("margin-bottom: 10px;")

        self.btn_choose_img = QPushButton("选择图片文件夹")
        self.btn_choose_img.setStyleSheet(style_select)
        self.btn_choose_img.setFont(QFont("微软雅黑", 12))
        self.btn_choose_img.setFixedHeight(36)
        self.btn_choose_img.clicked.connect(self.choose_img_dir)

        self.fps_label = QLabel("帧率：")
        self.fps_label.setFont(QFont("微软雅黑", 12))
        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 120)
        self.fps_input.setValue(30)
        self.fps_input.setFont(QFont("微软雅黑", 12))
        self.fps_input.setFixedWidth(80)

        self.out_name_label = QLabel("输出文件名：")
        self.out_name_label.setFont(QFont("微软雅黑", 12))
        self.out_name_input = QLineEdit("output.mp4")
        self.out_name_input.setFont(QFont("微软雅黑", 12))
        self.out_name_input.setFixedWidth(200)

        self.btn_choose_out = QPushButton("选择保存文件夹")
        self.btn_choose_out.setStyleSheet(style_select)
        self.btn_choose_out.setFont(QFont("微软雅黑", 12))
        self.btn_choose_out.setFixedHeight(36)
        self.btn_choose_out.clicked.connect(self.choose_out_dir)

        self.btn_export = QPushButton("导出视频")
        self.btn_export.setStyleSheet(style_export)
        self.btn_export.setFont(QFont("微软雅黑", 12))
        self.btn_export.setFixedHeight(40)
        self.btn_export.clicked.connect(self.export_video)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(30)
        self.progress.setFont(QFont("微软雅黑", 12))

        param_layout = QHBoxLayout()
        param_layout.addWidget(self.fps_label)
        param_layout.addWidget(self.fps_input)
        param_layout.addWidget(self.out_name_label)
        param_layout.addWidget(self.out_name_input)
        param_layout.addWidget(self.btn_choose_out)
        param_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_info)
        main_layout.addWidget(self.btn_choose_img)
        main_layout.addLayout(param_layout)
        main_layout.addWidget(self.btn_export)
        main_layout.addWidget(self.progress)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def choose_img_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹", "")
        if dir_path:
            self.img_dir = dir_path
            self.label_info.setText(f"已选择图片文件夹：{dir_path}")

    def choose_out_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存文件夹", "")
        if dir_path:
            self.out_dir = dir_path
            self.label_info.setText(self.label_info.text() + f"\n输出目录：{dir_path}")

    def export_video(self):
        if not self.img_dir or not self.out_dir:
            QMessageBox.warning(self, "错误", "请先选择图片文件夹和保存文件夹")
            return
        out_name = self.out_name_input.text().strip()
        if not out_name:
            QMessageBox.warning(self, "错误", "请填写输出文件名")
            return
        fps = self.fps_input.value()
        self.progress.setValue(0)
        self.thread = ExportVideoThread(self.img_dir, fps, out_name, self.out_dir)
        self.thread.progress_signal.connect(self.progress.setValue)
        self.thread.finished_signal.connect(self.export_finished)
        self.thread.start()
        self.btn_export.setEnabled(False)

    def export_finished(self, msg):
        self.btn_export.setEnabled(True)
        self.progress.setValue(100)
        QMessageBox.information(self, "导出结果", msg)
