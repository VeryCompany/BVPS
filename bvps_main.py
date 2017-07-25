# -*- coding: utf-8 -*-
from thespian.actors import ActorSystem
import sys
import os
import logging as log
from bvps.logger import logcfg
from bvps.system.sysActor import SystemActor
from bvps.camera.camera import Camera, CameraCmdType, CameraCmd, TrainingCMD, CameraType
from bvps.camera.trainer import HumanModelTrainer

import cv2

try:

    asys = ActorSystem(systemBase="multiprocUDPBase", logDefs=logcfg)
    sa = asys.createActor(
        SystemActor,
        targetActorRequirements=None,
        globalName="SystemActor",
        sourceHash=None)

    trainor = asys.createActor(
        HumanModelTrainer,
        targetActorRequirements=None,
        globalName="HumanModelTrainer",
        sourceHash=None)
    #未来会从数据库或者配置文件中读取
    #定位摄像头 type == 1
    #采集摄像头 type == 2
    cameras = {
        "camera1": {
            "x": "",
            "y": "",
            "z": "",
            "device": 0,
            "user": "",
            "password": "",
            "cameraType": CameraType.POSITION,
            "port": 10001,
            "fourcc": ('M', 'J', 'P', 'G'),
            "processNum": 4,
            "focallength": 5,
            "video_properties": {
                cv2.CAP_PROP_FRAME_WIDTH: 1280,
                cv2.CAP_PROP_FRAME_HEIGHT: 720,
                cv2.CAP_PROP_FPS: 30
            },
            "crop_area": {}
        },
        "camera2": {
            "x": "",
            "y": "",
            "z": "",
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
            "x": "",
            "y": "",
            "z": "",
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
            "x": "",
            "y": "",
            "z": "",
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
            "x": "",
            "y": "",
            "z": "",
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
    #启动采集摄像头
    #todo:消息反馈处理和异常处理
    for camId, params in cameras.items():
        cama = asys.createActor(Camera, globalName=camId)
        cameras[camId]["address"] = cama
        print("启动摄像头{}，命令CameraCmdType.START_CAPTURE".format(camId))
        asys.tell(cama, CameraCmd(CameraCmdType.START_CAPTURE, camId, params))

        asys.tell(cama, TrainingCMD(CameraCmdType.TRAINOR_INIT, trainor))

except KeyboardInterrupt:
    print 'Interrupted'
    try:
        asys.shutdown()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
