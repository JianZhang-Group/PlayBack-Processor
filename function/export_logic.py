import os
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed


class ExportVideoThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, img_dir, fps, out_name, out_dir, num_workers=8):
        super().__init__()
        self.img_dir = img_dir
        self.fps = fps
        self.out_name = out_name
        self.out_dir = out_dir
        self.num_workers = num_workers

    def run(self):
        img_files = sorted(
            [f for f in os.listdir(self.img_dir)
             if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))],
            key=lambda x: int("".join(filter(str.isdigit, x)) or 0),
        )
        if not img_files:
            self.finished_signal.emit("未找到图片文件！")
            return

        # 获取视频尺寸
        first_img = cv2.imread(os.path.join(self.img_dir, img_files[0]))
        if first_img is None:
            self.finished_signal.emit("首张图片读取失败！")
            return
        h, w, _ = first_img.shape
        out_path = os.path.join(self.out_dir, self.out_name)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(out_path, fourcc, self.fps, (w, h))
        total = len(img_files)
        total_steps = total * 2  # 读取+写入

        print(f"正在导出视频到: {out_path}，总计 {total} 张图片")

        frames = [None] * total  # 预分配内存

        # 用线程池并发读取
        def load(idx, fname):
            img = cv2.imread(os.path.join(self.img_dir, fname))
            return idx, img

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [executor.submit(load, idx, fname)
                       for idx, fname in enumerate(img_files)]
            for i, fut in enumerate(as_completed(futures), 1):
                idx, img = fut.result()
                frames[idx] = img
                self.progress_signal.emit(int(i / total_steps * 100))

        # 写视频
        for j, frame in enumerate(frames, 1):
            if frame is not None:
                video_writer.write(frame)
            self.progress_signal.emit(int((total + j) / total_steps * 100))

        video_writer.release()
        self.finished_signal.emit(f"导出完成: {out_path}")
        print(f"导出完成: {out_path}")
