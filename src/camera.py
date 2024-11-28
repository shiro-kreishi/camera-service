import cv2
import threading
from threading import Lock


class Camera:
    def __init__(self, rtsp_link):
        # Инициализация атрибутов
        self.last_frame = None
        self.result = False
        self.lock = Lock()
        self.link = rtsp_link
        self.capture = cv2.VideoCapture(rtsp_link)
        self.is_running = True  # Флаг для управления потоком
        # Запускаем поток для чтения кадров
        self.thread = threading.Thread(target=self.rtsp_cam_buffer, args=(), name="rtsp_read_thread")
        self.thread.daemon = True
        self.thread.start()

    def rtsp_cam_buffer(self):
        # Постоянное чтение кадров из RTSP-потока
        while self.is_running:
            with self.lock:
                success = self.capture.grab()
                if not success:
                    continue
                # Получаем и сохраняем последний кадр
                self.result, self.last_frame = self.capture.retrieve()

    def get_frame(self):
        # Возвращаем копию последнего успешного кадра
        if self.last_frame is not None and self.result:
            return self.last_frame.copy()
        else:
            return None

    def release(self):
        # Останавливаем поток, освобождаем захват видео и завершение работы потока
        self.is_running = False
        if self.capture.isOpened():
            self.capture.release()
        self.thread.join()

