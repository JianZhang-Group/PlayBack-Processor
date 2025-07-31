import os
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from pyorbbecsdk import *
from function.utils import frame_to_bgr_image
import numpy as np

class PlaybackThread(QThread):
    frame_signal = pyqtSignal(object)
    finished_signal = pyqtSignal()

    def __init__(self, bag_path, save_images=False, save_dir=None, save_video=False):
        super().__init__()
        self.bag_path = bag_path
        self.running = True
        self.paused = False
        self.save_images = save_images
        self.save_dir = save_dir
        self.save_video = save_video

    def run(self):
        pipeline = Pipeline(self.bag_path)
        playback = pipeline.get_playback()
        pipeline.start()
        idx = 0
        video_writer = None

        # 获取 bag 文件名（去掉扩展名）
        base_name = os.path.splitext(os.path.basename(self.bag_path))[0]

        # 保存路径： save_dir / bag_name
        root_save_dir = None
        color_dir, depth_dir = None, None
        if self.save_images and self.save_dir:
            root_save_dir = os.path.join(self.save_dir, base_name)
            depth_dir = os.path.join(root_save_dir, 'depth')
            color_dir = os.path.join(root_save_dir, 'color')
            os.makedirs(depth_dir, exist_ok=True)
            os.makedirs(color_dir, exist_ok=True)

        while self.running:
            if self.paused:
                self.msleep(100)
                continue
            frames = pipeline.wait_for_frames(100)
            if frames is None:
                continue
            depth_frame = frames.get_depth_frame()
            if depth_frame is None:
                continue

            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_data = depth_data.reshape((height, width))
            depth_data = depth_data.astype(float) * scale
            depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

            color_image = frame_to_bgr_image(frames.get_color_frame())

            images = []
            if depth_image is not None:
                images.append(depth_image)
                if self.save_images and depth_dir:
                    cv2.imwrite(os.path.join(depth_dir, f'depth_{idx}.png'), depth_image)

            if color_image is not None:
                images.append(color_image)
                if self.save_images and color_dir:
                    cv2.imwrite(os.path.join(color_dir, f'color_{idx}.png'), color_image)

            if images:
                show_img = np.hstack([cv2.resize(img, (640, 480)) for img in images])
                if self.save_video:
                    if idx == 0:
                        os.makedirs("output", exist_ok=True)
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        video_writer = cv2.VideoWriter(
                            f'output/{base_name}_playback.mp4',
                            fourcc, 30, (show_img.shape[1], show_img.shape[0])
                        )
                    if video_writer:
                        video_writer.write(show_img)
                self.frame_signal.emit(show_img)

            idx += 1

        if video_writer:
            video_writer.release()
        pipeline.stop()
        self.finished_signal.emit()

    def stop(self):
        self.running = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
