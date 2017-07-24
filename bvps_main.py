# -*- coding: utf-8 -*-
from thespian.actors import ActorSystem
import sys
import os
import logging as log
from bvps.logger import logcfg
from bvps.system.sysActor import SystemActor
from bvps.camera.camera import Camera, CameraCmdType, CameraCmd

try:

    asys = ActorSystem(systemBase="multiprocUDPBase", logDefs=logcfg)
    sa = asys.createActor(
        SystemActor,
        targetActorRequirements=None,
        globalName="SystemActor",
        sourceHash=None)
    #未来会从数据库或者配置文件中读取
    #定位摄像头 type == 1
    #采集摄像头 type == 2
    cameras = {
        "camera1": {
            "x": "",
            "y": "",
            "z": "",
            "device": "http://192.168.0.163:8090",
            "user": "",
            "password": "",
            "type": CameraCmdType.START_CAPTURE,
            "port": 10000,
            "frequency":30,
            "width":1280,
            "height":720,
            "fourcc":('M', 'J', 'P', 'G')
        }
        ,
        "camera2": {
            "x": "",
            "y": "",
            "z": "",
            "device": "http://192.168.0.163:8091",
            "user": "",
            "password": "",
            "type": CameraCmdType.START_CAPTURE,
            "port": 10001,
            "frequency":60,
            "width":1280,
            "height":720,
            "fourcc":('M', 'J', 'P', 'G')
        }
        ,
        "camera3": {
            "x": "",
            "y": "",
            "z": "",
            "device": "http://192.168.0.163:8092",
            "user": "",
            "password": "",
            "type": CameraCmdType.START_CAPTURE,
            "port": 10002,
            "frequency":30,
            "width":1280,
            "height":720,
            "fourcc":('M', 'J', 'P', 'G')
        }
        ,
        "camera4": {
            "x": "",
            "y": "",
            "z": "",
            "device": "rtsp://192.168.0.74:554",
            "user": "",
            "password": "",
            "type": CameraCmdType.START_CAPTURE,
            "port": 10003,
            "frequency":30,
            "width":1280,
            "height":720
        }
        # ,
        # "camera5": {
        #     "x": "",
        #     "y": "",
        #     "z": "",
        #     "device": "rtsp://192.168.0.205:554",
        #     "user": "",
        #     "password": "",
        #     "type": CameraCmdType.START_CAPTURE,
        #     "port": 10004,
        #     "frequency":30,
        #     "width":1280,
        #     "height":720
        # }
        ,
        "camera6": {
            "x": "",
            "y": "",
            "z": "",
            "device": "rtsp://192.168.0.114:554",
            "user": "",
            "password": "",
            "type": CameraCmdType.START_CAPTURE,
            "port": 10005,
            "frequency":30,
            "width":1280,
            "height":720
        }
    }
    #启动采集摄像头
    #todo:消息反馈处理和异常处理
    for camId, params in cameras.items():
        cama = asys.createActor(Camera, globalName=camId)
        if params["type"] == CameraCmdType.START_CAPTURE:
            print("启动摄像头{}，命令CameraCmdType.START_CAPTURE".format(camId))
            asys.tell(cama,
                      CameraCmd(CameraCmdType.START_CAPTURE, camId, params))
        elif params["type"] == CameraCmdType.START_CAPTURE_FOR_COLLECTION:
            print("启动摄像头{}，命令CameraCmdType.START_CAPTURE_FOR_COLLECTION".
                  format(camId))
            asys.tell(cama,
                      CameraCmd(CameraCmdType.START_CAPTURE_FOR_COLLECTION,
                                camId, params))

except KeyboardInterrupt:
    print 'Interrupted'
    try:
        asys.shutdown()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
