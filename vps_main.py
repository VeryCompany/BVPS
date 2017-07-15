# -*- coding: utf-8 -*-
from thespian.actors import ActorSystem
import sys
import os
from camera import CameraCmd,CameraCmdType,Camera

asys = ActorSystem((sys.argv + ['multiprocQueueBase'])[1])

#未来会从数据库或者配置文件中读取
#定位摄像头 type == 1
#采集摄像头 type == 2
cameras = {
"camera1":{"x":"","y":"","z":"","device":0,"user":"","password":"","type":1}#,
#"camera2":{"x":"","y":"","z":"","device":"rtsp://192.168.0.199:554","user":"","password":"","type":1},
#"camera3":{"x":"","y":"","z":"","device":"rtsp://192.168.0.199:554","user":"","password":"","type":2}
}
#启动采集摄像头
#todo:消息反馈处理和异常处理
for camId,params in cameras.items():
    cama = asys.createActor(Camera,globalName=camId)
    if params["type"] == 1:
        asys.tell(cama, CameraCmd(CameraCmdType.START_CAPTURE,camId,params))
    elif params["type"] == 2:
        asys.tell(cama, CameraCmd(CameraCmdType.START_CAPTURE_FOR_COLLECTION,camId,params))
while True:
    pass
asys.shutdown()
