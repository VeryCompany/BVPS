# -*- coding: utf-8 -*-
from thespian.actors import *
import numpy as np
import cv2
import threading
from enum import Enum
from bvps.camera.common import clock, draw_str, StatValue
from thespian.troupe import troupe
from bvps.camera.detector import HumanDetector
from bvps.camera.videoRecord import VideoRecord
#需要支持网络摄像头和本地USB摄像头


class Camera(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(Camera, self).__init__(*args, **kw)
        self.threadPool = {} #cameraName:threadID
    def receiveMsg_CameraCmd(self, cmd, sender):
        #todo:异常处理！！！！！
        if CameraCmdType.START_CAPTURE == cmd.cmdType:
            if cmd.cameraName in self.threadPool and self.threadPool[cmd.cameraName].isAlive():
                self.threadPool[cmd.cameraName].stop()
                self.threadPool[cmd.cameraName].join()
                self.send(sender,"camera stopped!")
            cps = [self.createActor(HumanDetector,globalName="{}-human-detector".format(cmd.cameraName)),self.createActor(VideoRecord,globalName="{}-video-record".format(cmd.cameraName))]
            cct = CameraCaptureThread(self, cmd.cameraName, cmd.values["device"], cps)
            self.threadPool[cmd.cameraName]=cct
            cct.setDaemon(True)
            cct.start()
            self.send(sender,"started ok!")
        elif CameraCmdType.STOP_CAPTURE == cmd.cmdType:
            if self.threadPool.exit(cmd.cameraName):
                self.threadPool[cmd.cameraName].stop()
                self.threadPool[cmd.cameraName].join()
            self.send(sender,"camera stopped!")
        elif CameraCmdType.RESTART_CAPTURE == cmd.cmdType:
            if cmd.cameraName in self.threadPool and self.threadPool[cmd.cameraName].isAlive():
                self.threadPool[cmd.cameraName].stop()
                self.threadPool[cmd.cameraName].join()
                self.send(sender,"camera stopped!")
            cps = [self.createActor(HumanDetector,globalName="{}-human-detector".format(cmd.cameraName)),self.createActor(VideoRecord,globalName="{}-video-record".format(cmd.cameraName))]
            cct = CameraCaptureThread(self, cmd.cameraName, cmd.values["device"], cps)
            self.threadPool[cmd.cameraName]=cct
            cct.setDaemon(True)
            cct.start()
            self.send(sender,"started ok!")
    def receiveMsg_HumanMsg(self, cmd, sender):
        pass

from multiprocessing.pool import ThreadPool
from collections import deque

class CameraCaptureThread(threading.Thread):
    def __init__(self,camera,cameraName,cameraDevice,processors=[]):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.camera = camera
        self.cameraName = cameraName
        self.cameraDevice = cameraDevice
        self.processors = processors
    def process_frame(self,ret,frame, t0):
        # some intensive computation...
        #frame = cv2.medianBlur(frame, 19)
        #frame = cv2.medianBlur(frame, 19)
        for processor in self.processors:
            if ret :
                self.camera.send(processor,(self.cameraName, ret, frame))
        return ret,frame, t0
    def startCapture(self):
        video = cv2.VideoCapture(self.cameraDevice)
        threadn = cv2.getNumberOfCPUs()
        pool = ThreadPool(processes = threadn)
        pending = deque()
        threaded_mode = True
        latency = StatValue()
        frame_interval = StatValue()
        last_frame_time = clock()
        while True:
            if self.stopped():
                break
            while len(pending) > 0 and pending[0].ready():
                ret, res, t0 = pending.popleft().get()
                latency.update(clock() - t0)
                #print "threaded      :  " + str(threaded_mode)
                #print "latency        :  %.1f ms" % (latency.value*1000)
                #print "frame interval :  %.1f ms" % (frame_interval.value*1000)
                latency.update(clock() - t0)
            if len(pending) < threadn:
                ret, frame = video.read()
                t = clock()
                frame_interval.update(t - last_frame_time)
                last_frame_time = t
                task = pool.apply_async(self.process_frame, (ret, frame.copy(), t))
                pending.append(task)
    def run(self):
        self.startCapture()
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()

class HumanMsg(object):

    def __init__(self,**kwargs):
        self.vmap = {}
        for name, value in kwargs.items():
            self.vmap[name]=value

#摄像头命令类型定义
class CameraCmdType(Enum):
    START_CAPTURE = 1
    STOP_CAPTURE = 2
    RESTART_CAPTURE = 3
    START_CAPTURE_FOR_COLLECTION = 4
#摄像头命令定义
class CameraCmd(object):
    def __init__(self,cmdType=CameraCmdType.START_CAPTURE,cameraName=None,values={}):
        self.cmdType = cmdType
        self.values = values
        self.cameraName = cameraName
