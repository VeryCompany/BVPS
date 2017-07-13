# -*- coding: utf-8 -*-
from thespian.actors import *
import numpy as np
import cv2
import thread
#需要支持网络摄像头和本地USB摄像头
class Camera(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(Camera, self).__init__(*args, **kw)
        self.threadPool = {} #cameraName:threadID
    def receiveMsg_CameraCmd(self, cmd, sender):
        if CameraCmdType.START_CAPTURE_FOR_POSITION == cmd.cmdType:
            if self.threadPool.exit(cmd.cameraName):
                #如果已经启动线程做响应的处理
                pass
            cps = [self.createActor(HumanDetector),self.createActor(videoRecord)]
            self.threadPool.set(cmd.cameraName,thread.start_new_thread(startCapture, cmd.cameraName, cmd.values["device"],cps))
        elif CameraCmdType.STOP_CAPTURE == cmd.cmdType:
            if self.threadPool.exit(cmd.cameraName):
                #如果已经启动线程做响应的处理
                pass
        elif CameraCmdType.RESTART_CAPTURE == cmd.cmdType:
            if self.threadPool.exit(cmd.cameraName):
                #如果已经启动线程做响应的处理
                pass
        elif CameraCmdType.START_CAPTURE_FOR_COLLECTION == cmd.cmdType:
            if self.threadPool.exit(cmd.cameraName):
                #如果已经启动线程做响应的处理
                pass
                cps = [self.createActor(HumanDetector),self.createActor(videoRecord)]
                self.threadPool.set(cmd.cameraName,thread.start_new_thread(startCapture, cmd.cameraName, cmd.values["device"],cps))
    def startCapture(self,cameraName,url,processors=[]]):
        video = cv2.VideoCapture(url)
        while True:
            success, image = self.video.read()
            for processor in processors:
                self.send(processor,(cameraName,success,image))



#摄像头命令类型定义
class CameraCmdType(Enum):
    START_CAPTURE_FOR_POSITION = 1
    STOP_CAPTURE = 2
    RESTART_CAPTURE = 3
    START_CAPTURE_FOR_COLLECTION = 4
#摄像头命令定义
class CameraCmd(object):
    def __init__(self,cmdType=CameraCmdType.START_CAPTURE,cameraName=None,values={}:
        self.cmdType = cmdType
        self.values = values
        self.cameraName = cameraName

#训练模型
class HumanModelTrainer(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(HumanModelTrainer, self).__init__(*args, **kw)
    def receiveMsg_CMD(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass
#识别人
class HumanRecognizer(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(HumanRecognizer, self).__init__(*args, **kw)
    def receiveMsg_CMD(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass

class videoRecord(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(videoRecord, self).__init__(*args, **kw)
    def receiveMsg_tuple(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass
#检测人-->（人+上半身+脸+鼻子+眼睛）-->识别人
class HumanDetector(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(HumanDetector, self).__init__(*args, **kw)
    def receiveMsg_tuple(self, message, sender):
        print "received CMD"
        print type(message[2])
    def receiveMsg_Image(self, message, sender):
        pass
