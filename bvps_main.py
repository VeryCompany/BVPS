# -*- coding: utf-8 -*-
import sys
import os
import logging as log

from bvps.actor_system import actor_system as asys
from bvps.system.sysActor import SystemActor
from bvps.system.position_actor import PositionActor
from bvps.torch.torch_actor import TorchActor
from bvps.camera.camera import Camera
from rpsc.start import server_start
from bvps.common import CameraCmdType, CameraCmd
import time

try:
    # server_start(asys)
    sa = asys.createActor(SystemActor, globalName="SystemActor")
    position = asys.createActor(
        PositionActor, globalName="CameraPositionActor")
    # 未来会从数据库或者配置文件中读取
    # 定位摄像头 type == 1
    # 采集摄像头 type == 2
    from bvps.config import cameras
    # 启动采集摄像头
    # todo:消息反馈处理和异常处理

    for camId, params in cameras.items():
        cama = asys.createActor(Camera, globalName=camId)
        cameras[camId]["address"] = cama
        print("启动摄像头{}，命令CameraCmdType.START_CAPTURE,address:{}".format(
            camId, cama))
        msg = asys.ask(cama,
                       CameraCmd(CameraCmdType.START_CAPTURE, camId, params),
                       600)
        print("camera:{} result:{}".format(camId, msg))
    ta = asys.createActor(TorchActor, globalName="TorchActor")


except KeyboardInterrupt:
    print('Interrupted')
    try:
        asys.shutdown()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
