# Camera service

## DEV setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Cameras config
example of camera configuration: `src/cameras.txt`
```
rtsp://admin:pgZqfq86@192.168.88.91:554/live/av0
rtsp://admin:pgZqfq86@192.168.88.93:554/live/av0
```
or
```
0
1
```

# Camera Service API Documentation

## Overview
This API provides functionality to manage connected cameras and retrieve frames in real-time. It allows users to get the list of connected cameras, fetch frames in JPEG format or as raw data, and refresh the camera list.

## Docs
Use FastAPI Swagger:
```
http://127.0.0.1:8001/docs
```

## API Endpoints

### 1. Get List of Connected Cameras
**Method**: `GET`  
**URL**: `/list_cameras`

#### Description
Returns a list of all connected cameras with their IDs and paths.

#### Example Response
```json
[
  {"id": 0, "name": "Camera 1", "path": "/dev/video0"},
  {"id": 1, "name": "Camera 2", "path": "/dev/video1"}
]
```

### 2. Get the Latest Frame from a Camera (JPEG)
**Method**: `GET`  
**URL**: `/image/{cam_index}`

#### Description
Retrieves the latest frame from the specified camera in JPEG format.

#### URL Parameters
`cam_index (int)`: Index of the camera in the buffer.

#### Example Response (on success)
Returns the image in `image/jpeg` format as a streaming response.

```json
{"error": "Camera not found or frame unavailable"}
```

### 3. Get the Latest Frame as a Raw Numpy Array
**Method**: `GET`  
**URL**: `/image_raw/{cam_index}`

#### Description
Retrieves the latest frame from the specified camera as a raw numpy array.

#### URL Parameters
`cam_index (int)`: Index of the camera in the buffer.

#### Example Response
```json
{
  "frame": [[0, 0, 0], [255, 255, 255], ...]
}
```

#### Example Error Response
```json
{
  "error": "Camera not found or frame unavailable"
}
```

### 4. Refresh the List of Connected Cameras
**Method**: `GET`  
**URL**: `/image_raw/{cam_index}`

#### Description
Asynchronously refreshes the list of connected cameras.

#### Example Response
```json
{
  "status": "Cameras are being refreshed"
}
```

### Common Errors
- <b>500 Internal Server Error:</b> Server encountered an unexpected error.
- <b>404 Not Found:</b> Specified camera not found or unavailable.

### Configuration Settings
The following settings are defined in `Camera_Service_Settings`:

 - `list_cameras`: Endpoint for listing cameras (/list_cameras).
 - `image`: Endpoint for retrieving frames (/image/).
 - `image_raw`: Endpoint for retrieving frames as raw data (/image_raw/).
 - `refresh`: Endpoint for refreshing camera list (/refresh).
 - `root_url`: Server host URL.
 - `root_port_int`: Server port.

### Example Usage
#### Start the Server
```bash
cd src/
uvicorn main:app --host 127.0.0.1 --port 8000
# or
python main.py
```
#### Get the List of Cameras
```bash
curl -X GET http://127.0.0.1:8000/list_cameras
```
#### Get a Frame from Camera 0 (JPEG)
```bash
curl -X GET http://127.0.0.1:8000/image/0
```
#### Refresh the Camera List
```bash
curl -X POST http://127.0.0.1:8000/refresh
```
