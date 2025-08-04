import os
import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class ExportVideoThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, img_dir, fps, out_name, out_dir):
        super().__init__()
        self.img_dir = img_dir
        self.fps = fps
        self.out_name = out_name
        self.out_dir = out_dir

    def run(self):
        img_files = sorted(
            [
                f
                for f in os.listdir(self.img_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
            ],
            key=lambda x: int("".join(filter(str.isdigit, x)) or 0),
        )
        if not img_files:
            self.finished_signal.emit("未找到图片文件！")
            print("未找到图片文件！")
            return
        first_img = cv2.imread(os.path.join(self.img_dir, img_files[0]))
        h, w, _ = first_img.shape
        out_path = os.path.join(self.out_dir, self.out_name)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(out_path, fourcc, self.fps, (w, h))
        total = len(img_files)
        print(f"正在导出视频到: {out_path}，总计 {total} 张图片")
        for idx, fname in enumerate(img_files):
            img = cv2.imread(os.path.join(self.img_dir, fname))
            if img is None:
                continue
            video_writer.write(img)
            self.progress_signal.emit(int((idx + 1) / total * 100))
        video_writer.release()
        self.finished_signal.emit(f"导出完成: {out_path}")
        print(f"导出完成: {out_path}")
