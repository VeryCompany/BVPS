# -*- coding: utf-8 -*-
from bvps.common import CameraType

"""摄像头配置信息"""
cameras = {
    "camera1": {
        "groupId": "group_1",
        "parameters": {
            "x": "",
            "y": "",
            "z": "",
            "angle_x": 0,
            "angle_y": 0,
            "angle_z": 0,
            "focallength": 6,
            "sensor_width": 4.8,
            "sensor_height": 2.7,
            "pixel_mm": 0.00375,
            "distortion_ceof": {},
            "camera_matrix": []
        },
        "scale": 1.0/3.0,
        "device": "rtsp://192.168.0.81:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10004,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 8,
        "video_properties": {
            5: 25,  # cv2.CAP_PROP_FPS
            3: 1280,  # cv2.CAP_PROP_FRAME_WIDTH
            4: 720  # cv2.CAP_PROP_FRAME_HEIGHT
        }
    },
    "camera2": {
        "groupId": "group_1",
        "parameters": {
            "x": "",
            "y": "",
            "z": "",
            "angle_x": 0,
            "angle_y": 0,
            "angle_z": 0,
            "focallength": 6,
            "sensor_width": 4.8,
            "sensor_height": 2.7,
            "pixel_mm": 0.00375,
            "distortion_ceof": {},
            "camera_matrix": []
        },
        "scale": 1.0/3.0,
        "device": "rtsp://192.168.0.82:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.POSITION,
        "port": 10005,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 8,
        "video_properties": {
            5: 25,  # cv2.CAP_PROP_FPS
            3: 1280,  # cv2.CAP_PROP_FRAME_WIDTH
            4: 720  # cv2.CAP_PROP_FRAME_HEIGHT
        }
    },
    "camera3": {
        "parameters": {
            "x": "",
            "y": "",
            "z": "",
            "angle_x": 0,
            "angle_y": 0,
            "angle_z": 0,
            "focallength": 6,
            "sensor_width": 4.8,
            "sensor_height": 2.7,
            "pixel_mm": 0.00375,
            "distortion_ceof": {},
            "camera_matrix": []
        },
        "scale": 1.0/3.0,
        "device": "rtsp://192.168.0.80:554",
        "user": "",
        "password": "",
        "cameraType": CameraType.CAPTURE,
        "port": 10006,
        "fourcc": ('M', 'J', 'P', 'G'),
        "processNum": 8,
        "video_properties": {
            5: 25,  # cv2.CAP_PROP_FPS
            3: 1280,  # cv2.CAP_PROP_FRAME_WIDTH
            4: 720  # cv2.CAP_PROP_FRAME_HEIGHT
        }
    }
}
"""双目摄像头分组信息"""
camera_group = {
    "group_1": {
        "members": ["camera4", "camera5"],
        "primary": "camera4",
        "baseline_mm": 220,
        "cx": 0,
        "cy": 0
    }

}
