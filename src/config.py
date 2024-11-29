

# Cam service
class Camera_Service_Settings:
    root_url = '0.0.0.0'
    root_port_int = 8001
    root_full_path = 'http://' + root_url + ':' + str(root_port_int)
    list_cameras = '/cameras'
    image = '/image/'
    image_raw = '/image-raw/'
    refresh = '/refresh'


class Recognition_Service_Settings:
    root_url = '127.0.0.1'
    root_port_int = 8002
    root_full_path = 'http://' + root_url + ':' + str(root_port_int)
    refresh = '/refresh'


class User_Config_Settings:
    user = 'admin'
    password = 'pgZqfq86'
    user_password = user + ':' + password