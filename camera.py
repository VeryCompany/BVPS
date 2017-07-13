# -*- coding: utf-8 -*-
from thespian.actors import *
import numpy as np
import cv2
import threading

from common import clock, draw_str

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
            cps = [self.createActor(HumanDetector),self.createActor(VideoRecord)]
            cct = CameraCaptureThread(self, cmd.cameraName, cmd.values["device"], cps)
            self.threadPool.set(cmd.cameraName,cct)
            cct.setDaemon()
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
            cps = [self.createActor(HumanDetector),self.createActor(VideoRecord)]
            cct = CameraCaptureThread(self, cmd.cameraName, cmd.values["device"], cps)
            self.threadPool.set(cmd.cameraName,cct)
            cct.setDaemon()
            cct.start()
            self.send(sender,"started ok!")

class CameraCaptureThread(threading.Thread):
    def __init__(self,camera,cameraName,cameraDevice,processors=[]):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.camera = camera
        self.cameraName = cameraName
        self.cameraDevice = cameraDevice
        self.processors = processors
    def startCapture(self):
        video = cv2.VideoCapture(url)
        while True:
            if self.stopped():
                break
            success, image = video.read()
            for processor in self.processors:
                self.camera.send(processor,(cameraName,success,image))
    def run(self):
        startCapture()
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()

#摄像头命令类型定义
class CameraCmdType(Enum):
    START_CAPTURE = 1
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

class VideoRecord(ActorTypeDispatcher):
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
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )
        faceClassifier = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
        eyeClassifier = cv2.CascadeClassifier("haarcascade_eye.xml")
        upperBodyClassifier = cv2.CascadeClassifier("haarcascade_upperbody.xml")
        self.HumanRecognizerProcessors = [self.createActor(HumanRecognizer)]
    def receiveMsg_tuple(self, message, sender):
        cameraName = message[0]
        image = message[2]
        validHuman = []
        for body in self.fullBodyDetector(image):
            for upb in self.upperBodyDetector(body):
                for face in self.faceDetector(upb):
                    validHuman.append((body,upb,face))
                    continue
        for person in validHuman:
            for recognizer in self.HumanRecognizerProcessors:
                self.send(recognizer,person)
                
    def fullBodyDetector(self,image):
        found, w = self.hog.detectMultiScale(image, winStride=(8,8), padding=(32,32), scale=1.05)
        draw_detections(image, found)
        return self.cropImage(image, found)

    def upperBodyDetector(self,image):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        t = clock()
        rects = detect(gray, self.upperBodyClassifier)
        uppers = []
        self.draw_detections(img, rects, thickness = 0.1)
        for x1, y1, x2, y2 in rects:
            roi = img[y1:y2, x1:x2]
            uppers.append(roi)
            continue
        dt = clock() - t
        draw_str(img, (20, 20), 'time: %.1f ms' % (dt*1000))
        return uppers
    def faceDetector(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        t = clock()
        rects = detect(gray, self.faceClassifier)
        faces = []
        self.draw_detections(img, rects, thickness = 0.1)
        if not nested.empty():
            for x1, y1, x2, y2 in rects:
                roi = img[y1:y2, x1:x2]
                subrects = detect(roi.copy(), self.eyeClassifier)
                if len(subrects) > 0:
                    faces.append(roi)
                    continue
        dt = clock() - t
        draw_str(img, (20, 20), 'time: %.1f ms' % (dt*1000))
        return faces

    def faceDetector_2(self,image):
        pass

    def inside(self,r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh

    def cropImage(self,image,rects):
        crops = []
        for x, y, w, h in rects:
            crops.append(image[y:y+h,x:x+w])
        return crops

    def detect(img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
        return rects

    def draw_detections(self,img, rects, thickness = 0.1):
        for x, y, w, h in rects:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            pad_w, pad_h = int(0.15*w), int(0.05*h)
            cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)
