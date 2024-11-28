import os
import re

import cv2
import numpy as np
from init_cams import init_cams


class CamServer:
    def __init__(self):
        self.connected_cameras = []
        self.get_new_cameras()
        # self.display_thread = Thread(target=self.display_frames)
        # self.display_thread.daemon = True
        # self.display_thread.start()

    def get_new_cameras(self) -> None:
        """
        Метод инициализирует подключение к новым камерам.
        """
        self.connected_cameras += init_cams(self.connected_cameras)

    def display_frames(self):
        """
        Отображает и сохраняет кадры от каждой подключённой камеры в одном окне OpenCV.
        """
        while True:
            frames = []

            for index, cam in enumerate(self.connected_cameras):
                frame = cam.get_frame()  # Получаем последний кадр камеры
                if frame is not None:
                    folder_path = os.path.join("camera_images", f"camera_{index}")
                    os.makedirs(folder_path, exist_ok=True)
                    file_path = os.path.join(folder_path, "current_frame.jpg")
                    cv2.imwrite(file_path, frame)  # Сохраняем кадр

                    frame_resized = cv2.resize(frame, (320, 240))
                    frames.append(frame_resized)

            if frames:
                cols = 2
                rows = (len(frames) + cols - 1) // cols
                while len(frames) < rows * cols:
                    frames.append(np.zeros((240, 320, 3), dtype=np.uint8))

                mosaic = []
                for i in range(0, len(frames), cols):
                    mosaic.append(np.hstack(frames[i:i + cols]))
                final_frame = np.vstack(mosaic)
                cv2.imshow("Camera Feeds", final_frame)

            if cv2.waitKey(33) == 27:
                break

        cv2.destroyAllWindows()

    def get_camera_list(self):
        """
        Возвращает список камер с их индексами и путями.
        """
        return [{"index": idx, "path": cam.link} for idx, cam in enumerate(self.connected_cameras)]

    def shutdown(self):
        for cam in self.connected_cameras:
            cam.capture.release()
        self.connected_cameras = []
