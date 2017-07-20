# -*- coding: utf-8 -*-
from thespian.actors import ActorSystem
import sys
import os
import logging as log
from bvps.logger import logcfg
from bvps.system.sysActor import SystemActor
from bvps.camera.camera import Camera, CameraCmdType, CameraCmd

try:

    asys = ActorSystem(systemBase="multiprocTCPBase", logDefs=logcfg)
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
            "device": "0",
            "user": "",
            "password": "",
            "type": CameraCmdType.START_CAPTURE,
            "port": 10000
        # },
        # "camera2": {
        #     "x": "",
        #     "y": "",
        #     "z": "",
        #     "device": "rtsp://192.168.0.205:554",
        #     "user": "",
        #     "password": "",
        #     "type": CameraCmdType.START_CAPTURE,
        #     "port": 10001
        # },
        # "camera3": {
        #     "x": "",
        #     "y": "",
        #     "z": "",
        #     "device": "rtsp://192.168.0.114:554",
        #     "user": "",
        #     "password": "",
        #     "type": CameraCmdType.START_CAPTURE,
        #     "port": 10002
        # }
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
