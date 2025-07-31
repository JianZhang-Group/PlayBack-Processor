from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QCheckBox, QSizePolicy, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from function.playback_logic import PlaybackThread
from function.path_check import PathChecker


class PlaybackTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel("请选择 .bag 文件并开始回放")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(1280, 480)
        self.label.setFont(QFont("微软雅黑", 14))
        self.label.setStyleSheet("border: 1px solid #aaa; background: #222; color: #fff;")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 样式表
        style_open = """
        QPushButton {
            background-color: #2d89ef; color: white; border-radius: 8px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #3aa0ff; }
        QPushButton:pressed { background-color: #1e5aad; }
        QPushButton:disabled { background-color: #7a7a7a; color: #dcdcdc; }
        """
        style_start = """
        QPushButton {
            background-color: #28a745; color: white; border-radius: 8px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #34c759; }
        QPushButton:pressed { background-color: #1c7c35; }
        QPushButton:disabled { background-color: #7a7a7a; color: #dcdcdc; }
        """
        style_stop = """
        QPushButton {
            background-color: #dc3545; color: white; border-radius: 8px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #ff4d5b; }
        QPushButton:pressed { background-color: #a71d2a; }
        QPushButton:disabled { background-color: #7a7a7a; color: #dcdcdc; }
        """

        # 按钮初始化
        self.btn_open = QPushButton("打开 .bag 文件"); self.btn_open.setStyleSheet(style_open)
        self.btn_start = QPushButton("开始回放"); self.btn_start.setStyleSheet(style_start)
        self.btn_pause = QPushButton("暂停"); self.btn_pause.setStyleSheet(style_stop)
        self.btn_resume = QPushButton("继续"); self.btn_resume.setStyleSheet(style_start)
        self.btn_stop = QPushButton("停止"); self.btn_stop.setStyleSheet(style_stop)
        self.btn_choose_dir = QPushButton("选择保存文件夹"); self.btn_choose_dir.setStyleSheet(style_open)

        for btn in [self.btn_open, self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop, self.btn_choose_dir]:
            btn.setFont(QFont("微软雅黑", 12))
            btn.setFixedHeight(40)

        self.save_checkbox = QCheckBox("保存图片")
        self.save_video_checkbox = QCheckBox("保存视频")
        self.save_checkbox.setFont(QFont("微软雅黑", 12))
        self.save_checkbox.setStyleSheet("margin-left: 10px; margin-right: 10px;")
        self.save_video_checkbox.setFont(QFont("微软雅黑", 12))
        self.save_video_checkbox.setStyleSheet("margin-left: 10px; margin-right: 10px;")

        self.fps_label = QLabel("帧率：")
        self.fps_label.setFont(QFont("微软雅黑", 12))
        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 30)
        self.fps_input.setValue(10)
        self.fps_input.setFont(QFont("微软雅黑", 12))
        self.fps_input.setFixedWidth(80)

        self.save_dir = None

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_choose_dir.setEnabled(False)
        self.save_checkbox.setEnabled(False)
        self.save_video_checkbox.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_resume)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.save_checkbox)
        btn_layout.addWidget(self.save_video_checkbox)
        btn_layout.addWidget(self.fps_label)
        btn_layout.addWidget(self.fps_input)
        btn_layout.addWidget(self.btn_choose_dir)
        btn_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.bag_path = None
        self.thread = None

        self.btn_open.clicked.connect(self.open_file)
        self.btn_start.clicked.connect(self.start_playback)
        self.btn_pause.clicked.connect(self.pause_playback)
        self.btn_resume.clicked.connect(self.resume_playback)
        self.btn_stop.clicked.connect(self.stop_playback)
        self.btn_choose_dir.clicked.connect(self.choose_save_dir)
        self.save_checkbox.stateChanged.connect(self.save_checkbox_changed)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 .bag 文件", "", "Bag Files (*.bag)")
        path_checker = PathChecker(path)
        if path_checker.contains_chinese_or_space():
            QMessageBox.warning(self, "错误", "文件路径中不能包含中文或空格")
            return
        if path:
            self.bag_path = path
            self.btn_start.setEnabled(True)
            self.label.setText("已选择文件：" + path)
            self.btn_choose_dir.setEnabled(True)
            self.save_checkbox.setEnabled(True)
            self.save_video_checkbox.setEnabled(True)

    def choose_save_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存文件夹", "")
        if dir_path:
            self.save_dir = dir_path
            self.label.setText(self.label.text() + f"\n保存目录：{dir_path}")

    def save_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.btn_choose_dir.setEnabled(True)
        else:
            self.btn_choose_dir.setEnabled(False)

    def start_playback(self):
        if not self.bag_path:
            QMessageBox.warning(self, "错误", "请先选择 .bag 文件")
            return
        if self.save_checkbox.isChecked() and not self.save_dir:
            QMessageBox.warning(self, "错误", "请先选择保存文件夹")
            return
        self.thread = PlaybackThread(
            self.bag_path,
            save_images=self.save_checkbox.isChecked(),
            save_dir=self.save_dir,
            save_video=self.save_video_checkbox.isChecked(),
            fps=self.fps_input.value()
        )
        self.thread.frame_signal.connect(self.update_image)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_start.setEnabled(False)
        self.fps_input.setEnabled(False)

    def pause_playback(self):
        if self.thread:
            self.thread.pause()
            self.btn_resume.setEnabled(True)
            self.btn_pause.setEnabled(False)

    def resume_playback(self):
        if self.thread:
            self.thread.resume()
            self.btn_resume.setEnabled(False)
            self.btn_pause.setEnabled(True)

    def stop_playback(self):
        if self.thread:
            self.thread.stop()
            self.thread.wait()
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.fps_input.setEnabled(True)

    def update_image(self, img):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.label.setPixmap(QPixmap.fromImage(qimg))

    def on_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)