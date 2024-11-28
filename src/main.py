import io
import time
from datetime import datetime
from threading import Lock, Thread

import cv2
import pytz as pytz
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from CamServer import CamServer
from config import Camera_Service_Settings
server = CamServer()

# Инициализация буфера и блокировки для доступа к буферу
frame_buffer = {}
buffer_lock = Lock()


def update_frame_buffer():
    """
    Функция для периодического обновления буфера кадров.
    Запускается в отдельном потоке и обновляет кадры всех подключенных камер.
    """
    while True:
        with buffer_lock:
            for index, cam in enumerate(server.connected_cameras):
                frame = cam.get_frame()
                if frame is not None:
                    frame_buffer[index] = frame  # Обновляем кадр в буфере
        time.sleep(0.1)  # Обновление буфера каждую секунду (можно настроить)


# Запуск обновления буфера в отдельном потоке
buffer_thread = Thread(target=update_frame_buffer, daemon=True)
buffer_thread.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Сервер запущен {datetime.now(pytz.utc)}")
    yield
    server.shutdown()
    cv2.destroyAllWindows()  # Завершаем и закрываем окна OpenCV
    print(f"Сервер завершил работу {datetime.now(pytz.utc)}")


# Инициализация FastAPI с использованием lifespan
app = FastAPI(lifespan=lifespan)


@app.get(f"{Camera_Service_Settings.list_cameras}")
async def get_camera_list():
    """
    Эндпоинт для получения списка подключённых камер с их путями.
    """
    camera_list = server.get_camera_list()
    return JSONResponse(content=camera_list)


@app.get(f"{Camera_Service_Settings.image}"+"{cam_index}")
async def get_camera_frame(cam_index: int):
    """
    Эндпоинт для получения последнего кадра от указанной камеры из буфера.
    """
    with buffer_lock:
        frame = frame_buffer.get(cam_index)  # Берем кадр из буфера
    if frame is not None:
        _, img_encoded = cv2.imencode('.jpg', frame)
        return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")
    else:
        return {"error": "Камера не найдена или кадр отсутствует"}


@app.get(f"{Camera_Service_Settings.image_raw}"+"{cam_index}")
async def get_camera_frame_raw(cam_index: int):
    """
    Эндпоинт для получения последнего кадра от указанной камеры в виде массива numpy из буфера.
    """
    with buffer_lock:
        frame = frame_buffer.get(cam_index)
    if frame is not None:
        frame_data = frame.tolist()  # Преобразование numpy массива в список
        return JSONResponse(content={"frame": frame_data})
    else:
        return JSONResponse(content={"error": "Камера не найдена или кадр отсутствует"})


@app.post(f"{Camera_Service_Settings.refresh}")
async def refresh_cameras(background_tasks: BackgroundTasks):
    """
    Эндпоинт для обновления списка подключённых камер.
    """
    background_tasks.add_task(server.get_new_cameras)
    return {"status": "Камеры обновляются"}


if __name__ == "__main__":
    uvicorn.run(app, host=f"{Camera_Service_Settings.root_url}", port=Camera_Service_Settings.root_port_int)
