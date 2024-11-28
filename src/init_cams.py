import cv2

from camera import Camera
from check_new_cams import check_new_cams


def init_cams(connected_cameras: list) -> list:
    """
    Возвращает список объектов камер.
    :param connected_cameras: Список уже подключенных объектов камер.
    :return: Возвращает список камер которые были подключены.
    """
    read_successful, cam_paths = check_new_cams(connected_cameras)
    cam_buffer = []

    if read_successful:
        for path in cam_paths:
            cam_buffer.append(Camera(path))
    else:
        print("Не удалось прочитать пути к камерам")

    for cam in cam_buffer:
        if not cam.capture.isOpened():
            print(f'Ошибка! Камера по пути {cam.link} не была подключена.')
            cam.release()

    return cam_buffer
