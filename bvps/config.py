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
"""摄像头配置信息"""
cameras = {
    "camera4": {
        "groupId":"group_1",
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "focallength": 6,
            "sensor_width":4.8,
            "sensor_height":2.7,
            "pixel_mm":0.00375,
            "distortion_ceof":{},
            "camera_matrix":[]
        },
        "scale":1.0/2.0,
        "device": "rtsp://192.168.0.198:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10004,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "video_properties": {
            cv2.CAP_PROP_FPS: 25,
            cv2.CAP_PROP_FRAME_WIDTH: 1280,
            cv2.CAP_PROP_FRAME_HEIGHT: 720
        }
    },
    "camera5": {
        "groupId":"group_1",
        "parameters":{
            "x": "",
            "y": "",
            "z": "",
            "angle_x":0,
            "angle_y":0,
            "angle_z":0,
            "focallength": 6,
            "sensor_width":4.8,
            "sensor_height":2.7,
            "pixel_mm":0.00375,
            "distortion_ceof":{},
            "camera_matrix":[]
        },
        "scale":1.0/2.0,
        "device": "rtsp://192.168.0.114:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10005,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 4,
        "video_properties": {
            cv2.CAP_PROP_FPS: 25,
            cv2.CAP_PROP_FRAME_WIDTH: 1280,
            cv2.CAP_PROP_FRAME_HEIGHT: 720
        }
    }
}
"""双目摄像头分组信息"""
camera_group = {
    "group_1":{
        "members":["camera4","camera5"],
        "primary":"camera4"
        "baseline_mm":220,
        "cx":0,
        "cy":0
    }

}
