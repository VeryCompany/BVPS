# -*- coding: utf-8 -*-
from thespian.actors import *
import numpy as np
import cv2
import threading
#需要支持网络摄像头和本地USB摄像头
class Camera(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(Camera, self).__init__(*args, **kw)
    def receiveMsg_CMD(self, cmd, sender):
        detector = self.createActor(HumanDetector)
        VideoCapture("1", "3",self,detector,cmd).start()

#需要支持网络摄像头和本地USB摄像头
class VideoCapture (threading.Thread):
    def __init__(self,threadID,name,camera,detector,cmd):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        url = cmd.vars[0]
        self.video = cv2.VideoCapture(url)
        self.detector = detector
        self.camera = camera
    def run(self):
        while True:
            success, image = self.video.read()
            self.camera.send(self.detector, CMD(100,(success,image)))
#命令对象
class CMD(object):
    def __init__(self,cmd=0,ts=()):
        self.cmd = cmd
        self.vars = ts
#训练模型
class HumanModelTrainer(ActorTypeDispatcher):
    def __init__(self):
        pass
    def receiveMsg_CMD(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass
#识别人
class HumanRecognizer(ActorTypeDispatcher):
    def __init__(self):
        pass
    def receiveMsg_CMD(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass
#检测人-->（人+上半身+脸+鼻子+眼睛）-->识别人
class HumanDetector(ActorTypeDispatcher):
    def __init__(self):
        pass
    def receiveMsg_CMD(self, message, sender):
        print "received CMD"
        print type(message.vars[1])
    def receiveMsg_Image(self, message, sender):
        pass
