# -*- coding: utf-8 -*-

training_config = {
    "cap_nums":30
}
svm_param_grid = [
    {'C': [1, 10, 100, 1000],
     'kernel': ['linear']},
    {'C': [1, 10, 100, 1000],
     'gamma': [0.001, 0.0001],
     'kernel': ['rbf']}
]
cameras = {
    "camera1": {
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "sensor_width",4.8,
            "sensor_height",3.6,
            "distortion_ceof":{},
            "camera_matrix":[]
        }
        "device": 0,
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10001,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "video_properties": {
            cv2.CAP_PROP_FRAME_WIDTH: 1280,
            cv2.CAP_PROP_FRAME_HEIGHT: 720,
            cv2.CAP_PROP_FPS: 30
        },
        "crop_area": {}
    },
    "camera2": {
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "sensor_width",4.8,
            "sensor_height",3.6,
            "distortion_ceof":{},
            "camera_matrix":[]
        }
        "device": 1,
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10002,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "focallength": 5,
        "video_properties": {
            cv2.CAP_PROP_FRAME_WIDTH: 1280,
            cv2.CAP_PROP_FRAME_HEIGHT: 720,
            cv2.CAP_PROP_FPS: 60
        }
    },
    "camera3": {
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "sensor_width",4.8,
            "sensor_height",3.6,
            "distortion_ceof":{},
            "camera_matrix":[]
        }
        "device": 2,
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10003,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "focallength": 5,
        "video_properties": {
            cv2.CAP_PROP_FRAME_WIDTH: 1280,
            cv2.CAP_PROP_FRAME_HEIGHT: 720,
            cv2.CAP_PROP_FPS: 30
        }
    },
    "camera4": {
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "sensor_width",4.8,
            "sensor_height",3.6,
            "distortion_ceof":{},
            "camera_matrix":[]
        }
        "device": "rtsp://192.168.0.74:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10004,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "focallength": 5,
        "video_properties": {
            cv2.CAP_PROP_FPS: 25
        }
    },
    "camera5": {
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "sensor_width",4.8,
            "sensor_height",3.6,
            "distortion_ceof":{},
            "camera_matrix":[]
        }
        "device": "rtsp://192.168.0.114:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10005,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "focallength": 5,
        "video_properties": {
            cv2.CAP_PROP_FPS: 25
        }
    }
}
