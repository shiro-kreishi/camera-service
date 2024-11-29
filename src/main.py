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


@app.get(f"{Camera_Service_Settings.image_none_buffer}"+"{cam_index}")
async def get_camera_frame_non_buffer(cam_index: int):
    """
        Эндпоинт для получения кадра камеры.
    """
    frame = server.connected_cameras[cam_index].get_frame()
    if frame is not None:
        _, img_encoded = cv2.imencode('.jpg', frame)
        return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")
    else:
        return {"error": "Камера не найдена или кадр отсутствует"}


@app.get(f"{Camera_Service_Settings.image_raw_non_buffer}"+"{cam_index}")
async def get_camera_frame_raw_non_buffer(cam_index: int):
    frame = server.connected_cameras[cam_index].get_frame()
    if frame is not None:
        frame_data = frame.tolist()
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
