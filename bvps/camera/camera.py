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
from bvps.camera.cameraServer import CameraServer

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
    training_start_time,training_end_time = clock(),clock()
    def __init__(self, *args, **kw):
        super(Camera, self).__init__(*args, **kw)
        self.frameQueue = multiprocessing.Queue(64)
        self.processQueue = multiprocessing.Queue(64)
        self.webserver = None
        self.cameraServer = None
        self.cct = None
        self.cps = []
    def receiveMsg_CameraCmd(self, cmd, sender):
        if self.webserver is not None:
            log.info(self.webserver.pid)
        #todo:异常处理！！！！！
        if CameraCmdType.START_CAPTURE == cmd.cmdType:
            if self.cct is not None and self.cct.isAlive():
                return
            log.info("摄像头 {} 接收到 START_CAPTURE 命令".format(cmd.cameraName))
            self.cct = CameraCaptureThread(self, cmd.cameraName,
                                      cmd.values["device"], self.cps,cmd)
            self.cct.setDaemon(True)
            self.cct.start()
            from bvps.web.server import WebServer
            log.info("启动摄像头web服务器...")
            self.webserver = WebServer(self.frameQueue, cmd.values["port"])
            self.webserver.start()
            log.info("摄像头web服务器启动完成...")
            log.info("启动摄像头[{}]图像处理服务器......".format(cmd.cameraName))
            pn = cmd.values["processNum"]
            for p in range(0, pn, 1):
                cams = CameraServer(self.frameQueue,cmd,self,self.cct)
                cams.start()
            log.info("启动摄像头[{}]图像处理服务器成功！启动了[{}]个实例.".format(cmd.cameraName,pn))
        elif CameraCmdType.STOP_CAPTURE == cmd.cmdType:
            if self.cct is not None and self.cct.isAlive():
                self.cct.stop()
                self.cct.join(timeout=10)
            self.send(sender, "camera stopped!")

    def receiveMsg_TrainingCMD(self, cmd, sender):
        log.info("训练器是我{}".format(cmd.msg))
        if cmd.cctype == CameraCmdType.TRAINOR_INIT:
            self.trainor = cmd.msg
            self.send(self.trainor,"训练器初始化ok!")
        elif cmd.cctype == CameraCmdType.TRAINOR_START:
            self.training_started = True
            self.training_start_time = cmd.msg
            self.training_uid = cmd.uid
        elif cmd.cctype == CameraCmdType.TRAINOR_END:
            self.training_started = False
            self.training_end_time = cmd.msg
            self.training_uid = cmd.uid

    def receiveMsg_HumanMsg(self, cmd, sender):
        pass



from bvps.camera.detectorthread import HumanDetector as detector
from bvps.camera.recognizer import OpenFaceRecognizer as recognizer


class CameraCaptureThread(threading.Thread):

    """
    摄像头抓取线程类，比较初级，健壮性不足，未来需要重写
    """
    def __init__(self, camera, cameraName, cameraDevice, processors=[],initCmd=None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.camera = camera
        self.cameraName = cameraName
        self.cameraDevice = cameraDevice
        self.processors = processors
        self.detector = detector()
        self.recognizer = recognizer(None)
        self.threadn=cv2.getNumberOfCPUs()*4
        self.pools={}
        self.initCmd = initCmd
    def process_recognize(self, human):
        """识别检测到的人体图片，返回人对应的用户Id"""
        #log.debug("开始识别人！")
        try:
            uid = self.recognizer.whoru(human, t0) if self.recognizer.svm is not None else None
            log.info("摄像头{}识别用户id：{},x:{},y:{}".format(self.cameraName,uid,human[0][1],human[0][2]))
            #发送至定位中枢，确定用户坐标
            return human, uid
        except Exception, e:
            log.info(e.message)
            return human,None

    def recognizeParallel(self, method, humans):
        """多线程并行运算，提高运算速度"""
        kt=clock()
        pool = ThreadPool(processes=self.threadn)
        self.pools[kt]=pool
        results = pool.map_async(method, humans)
        pool.close()
        pool.join()
        pool.terminate()
        self.pools.pop(kt, None)
        return results

    def process_frame(self, ret, frame, t0):
        """
        处理摄像头抓取到的每一帧图像，找出有效的人和脸的照片。
        是否需要设置专用的采集摄像头？还是所有的摄像头都可以用于采集？
        如果处于采集状态，检测到的有效人体照片发送给后端进行学习。
        """
        try:
            humans = self.detector.detect_humans(self.cameraName, frame, t0)


            """
            sending humans to trainning actors
            通过通道的人，需要开始和结束时间，基准时间t0
            """
            #   pass
            if len(humans) > 0:
                if self.camera.training_started and t0 > self.camera.training_start_time and t0 < self.camera.training_end_time:
                    for human in humans:
                        self.camera.send(self.trainor,human)
                else:
                    users = self.recognizeParallel(
                        self.process_recognize, humans)

        except Exception, e:
            log.info(e.message)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=10, file=sys.stdout)
        finally:
            return ret, frame, t0

    def startCapture(self):
        try:
            video = cv2.VideoCapture(self.cameraDevice)
            # video.set(cv2.CAP_PROP_FPS,self.initCmd.values["frequency"])
            # video.set(cv2.CAP_PROP_FRAME_WIDTH,self.initCmd.values["width"])
            # video.set(cv2.CAP_PROP_FRAME_HEIGHT,self.initCmd.values["height"])
            log.info("摄像头{}初始化参数".format(self.cameraName))
            for k,v in self.initCmd.values["video_properties"].items():
                video.set(k,v)
                log.info("video.set({},{})".format(k,v))
            forcc = self.initCmd.values["fourcc"] if "fourcc" in self.initCmd.values else None
            if forcc is not None:
                video.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(forcc[0],forcc[1],forcc[2],forcc[3]))
            width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            codec = video.get(cv2.CAP_PROP_FOURCC)

            log.info("摄像头fps[{}] width:{} height:{} codec:{}".format(video.get(cv2.CAP_PROP_FPS),width,height,codec))
            log.info("亮度:{}".format(video.get(cv2.CAP_PROP_BRIGHTNESS)))
            log.info("对比度:{}".format(video.get(cv2.CAP_PROP_CONTRAST)))
            log.info("饱和度:{}".format(video.get(cv2.CAP_PROP_SATURATION)))
            log.info("色调:{}".format(video.get(cv2.CAP_PROP_HUE)))
            log.info("图像增益:{}".format(video.get(cv2.CAP_PROP_GAIN)))
            log.info("曝光:{}".format(video.get(cv2.CAP_PROP_EXPOSURE)))
            log.info("ISO:{}".format(video.get(cv2.CAP_PROP_ISO_SPEED)))
            log.info("RGB?:{}".format(video.get(cv2.CAP_PROP_CONVERT_RGB)))

            latency = StatValue()
            frame_interval = StatValue()
            last_frame_time = clock()
            num=10
            while True:
                try:
                    if self.stopped():
                        break
                    if video.grab():
                        ret,frame = video.retrieve()
                        if num % 50 == 0:
                            log.debug("读取摄像头{}frame{}".format(self.cameraName,"成功" if ret else "失败！"))
                        t = clock()
                        frame_interval.update(t - last_frame_time)
                        if num % 50 == 0:
                            log.info("摄像头{}.当前fps:{}".format(self.cameraName,int(1000/(frame_interval.value * 1000))))
                        if ret:
                            if not self.camera.processQueue.full():
                                self.camera.processQueue.put_nowait((frame,t))
                            if not self.camera.frameQueue.full():
                                self.camera.frameQueue.put_nowait((frame,t))
                        last_frame_time = t
                    num+=1
                except Exception, e:
                    log.info(e.message)
        except Exception, e:
            log.info(e.message)


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
    TRAINOR_INIT = 5
    TRAINOR_START = 6
    TRAINOR_END = 7

class TrainingCMD(object):
    def __init__(self,cctype,msg,uid=None):
        self.cctype = cctype
        self.msg = msg
        self.uid = uid

#摄像头命令定义
class CameraCmd(object):
    def __init__(self,
                 cmdType=CameraCmdType.START_CAPTURE,
                 cameraName=None,
                 values={}):
        self.cmdType = cmdType
        self.values = values
        self.cameraName = cameraName
