# -*- coding: utf-8 -*-
from thespian.actors import *
import numpy as np
import cv2
import threading
from enum import Enum
from bvps.camera.common import clock, draw_str, StatValue
from thespian.troupe import troupe
from bvps.camera.videoRecord import VideoRecord
import multiprocessing
#需要支持网络摄像头和本地USB摄像头
import logging as log
import sys, traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception



class Camera(ActorTypeDispatcher):
    svm_model = None
    svm_model_updated = False
    training_started = False
    def __init__(self, *args, **kw):
        super(Camera, self).__init__(*args, **kw)
        self.threadPool = {}  #cameraName:threadID
        self.frameQueue = multiprocessing.Queue(64)
        self.webserver = None
    @property
    def svmModel(self):
        self.svm_model_updated = False
        return svm_model
    @svmModel.setter
    def svmModel(self,svm_model):
        self.svm_model = svm_model
    @property
    def modelupdated(self):
        return self.svm_model_updated
    @property
    def startTrainning(self):
        return self.training_started
    def receiveMsg_CameraCmd(self, cmd, sender):
        if self.webserver is not None:
            log.info(self.webserver.pid)
        #todo:异常处理！！！！！
        if CameraCmdType.START_CAPTURE == cmd.cmdType:
            if cmd.cameraName in self.threadPool and self.threadPool[cmd.
                                                                     cameraName].isAlive(
                                                                     ):
                log.info("摄像头 {} 接收到 START_CAPTURE 命令,但是摄像头已经启动".format(cmd.cameraName))
                return

            cps = [
                self.createActor(
                    VideoRecord,
                    globalName="{}-video-record".format(cmd.cameraName))
            ]
            log.info("摄像头 {} 接收到 START_CAPTURE 命令".format(cmd.cameraName))
            cct = CameraCaptureThread(self, cmd.cameraName,
                                      cmd.values["device"], cps)
            self.threadPool[cmd.cameraName] = cct
            cct.setDaemon(True)
            cct.start()
            from bvps.web.server import WebServer
            log.info("启动摄像头web服务器...")
            self.webserver = WebServer(self.frameQueue, cmd.values["port"])
            self.webserver.start()

            log.info("摄像头web服务器启动完成...")
            self.send(sender, "started ok!")
        elif CameraCmdType.STOP_CAPTURE == cmd.cmdType:
            if self.threadPool.exit(cmd.cameraName):
                self.threadPool[cmd.cameraName].stop()
                self.threadPool[cmd.cameraName].join()
            self.send(sender, "camera stopped!")
        elif CameraCmdType.RESTART_CAPTURE == cmd.cmdType:
            if cmd.cameraName in self.threadPool and self.threadPool[cmd.
                                                                     cameraName].isAlive(
                                                                     ):
                self.threadPool[cmd.cameraName].stop()
                self.threadPool[cmd.cameraName].join()
                self.send(sender, "camera stopped!")
            cps = [

                self.createActor(
                    VideoRecord,
                    globalName="{}-video-record".format(cmd.cameraName))
            ]
            cct = CameraCaptureThread(self, cmd.cameraName,
                                      cmd.values["device"], cps)
            self.threadPool[cmd.cameraName] = cct
            cct.setDaemon(True)
            cct.start()
            self.send(sender, "started ok!")

    def receiveMsg_TrainingCMD(self, cmd, sender):
        self.training_started = True

    def receiveMsg_HumanMsg(self, cmd, sender):
        pass


from multiprocessing.dummy import Pool as ThreadPool
from collections import deque
from bvps.camera.detectorthread import HumanDetector as detector
from bvps.camera.recognizer import OpenFaceRecognizer as recognizer


class CameraCaptureThread(threading.Thread):
    """
    摄像头抓取线程类，比较初级，健壮性不足，未来需要重写
    """
    def __init__(self, camera, cameraName, cameraDevice, processors=[]):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.camera = camera
        self.cameraName = cameraName
        self.cameraDevice = cameraDevice
        self.processors = processors
        self.detector = detector()
        self.recognizer = recognizer(None)

    def process_recognize(self, human):
        """识别检测到的人体图片，返回人对应的用户Id"""

        log.debug("开始识别人！")
        uid = self.recognizer.whoru(human, t0) if self.recognizer.svm is not None else None
        log.debug("识别用户id：{},x:{},y:{}".format(uid,human[0][1],human[0][2]))
        return human, uid

    def recognizeParallel(self, method, humans):
        threads=cv2.getNumberOfCPUs()
        """多线程并行运算，提高运算速度"""
        pool = ThreadPool(threads if threads <= len(humans) else len(humans))
        results = pool.map(method, humans)
        pool.close()
        pool.join()
        return results

    def process_frame(self, ret, frame, t0):
        """
        处理摄像头抓取到的每一帧图像，找出有效的人和脸的照片。
        是否需要设置专用的采集摄像头？还是所有的摄像头都可以用于采集？
        如果处于采集状态，检测到的有效人体照片发送给后端进行学习。
        """
        try:
            humans = self.detector.detect_humans(self.cameraName, frame, t0)
            #if self.camera. startTrainning():
            """
            sending humans to trainning actors
            通过通道的人，需要开始和结束时间，基准时间t0
            """
            #    pass
            if len(humans) > 0:
                users = self.recognizeParallel(
                    self.process_recognize, humans)
                for human in humans:
                    faceX = human[1][1]
                    faceY = human[1][2]
                    #给用户的脸部中心画一个圈
                    cv2.circle(fame, (faceX,faceY), 5,  (0,255,0), thickness=3, lineType=8, shift=0)
                #识别出用户，将用户的Id，图像坐标位置发送给中枢Actor做处理

            if not self.camera.frameQueue.full():
                self.camera.frameQueue.put_nowait(frame)
        except Exception, e:
            log.info(e.message)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
        finally:
            return ret, frame, t0

    def startCapture(self):
        try:
            video = cv2.VideoCapture(self.cameraDevice)
            threadn = cv2.getNumberOfCPUs()
            pool = ThreadPool(processes=threadn)
            pending = deque()
            latency = StatValue()
            frame_interval = StatValue()
            last_frame_time = clock()
            while True:
                if self.stopped():
                    break
                while len(pending) > 0 and pending[0].ready():
                    ret, res, t0 = pending.popleft().get()
                    latency.update(clock() - t0)
                if len(pending) < threadn:
                    ret, frame = video.read()
                    t = clock()
                    frame_interval.update(t - last_frame_time)
                    last_frame_time = t
                    task = pool.apply_async(self.process_frame, (ret, frame, t))
                    pending.append(task)
        except Exception, e:
            log.info(e.message)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)


    def run(self):
        self.startCapture()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class HumanMsg(object):
    def __init__(self, **kwargs):
        self.vmap = {}
        for name, value in kwargs.items():
            self.vmap[name] = value


#摄像头命令类型定义
class CameraCmdType(Enum):
    START_CAPTURE = 1
    STOP_CAPTURE = 2
    RESTART_CAPTURE = 3
    START_CAPTURE_FOR_COLLECTION = 4


#摄像头命令定义
class CameraCmd(object):
    def __init__(self,
                 cmdType=CameraCmdType.START_CAPTURE,
                 cameraName=None,
                 values={}):
        self.cmdType = cmdType
        self.values = values
        self.cameraName = cameraName
