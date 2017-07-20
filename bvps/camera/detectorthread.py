# -*- coding: utf-8 -*-
from thespian.actors import *
import os
import numpy as np
import cv2
import threading
from enum import Enum
from bvps.camera.common import clock, draw_str, StatValue
from thespian.troupe import troupe
import openface
import logging as log
#检测人-->（人+上半身+脸+鼻子+眼睛）-->识别人
fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
harrsDir = os.path.join(fileDir, '..', 'haars')
openfaceModelDir = os.path.join(modelDir, 'openface')
align = openface.AlignDlib(
    os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(
    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)

class HumanDetector():
    num = 1
    def __init__(self, *args, **kw):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.bodyClassifier = cv2.CascadeClassifier(
            os.path.join(harrsDir, "haarcascade_upperbody.xml"))
        self.faceClassifier = cv2.CascadeClassifier(
            os.path.join(harrsDir, "haarcascade_frontalface_alt.xml"))
        self.upperBodyClassifier = cv2.CascadeClassifier(
            os.path.join(harrsDir, "haarcascade_upperbody.xml"))
        self.HumanRecognizerProcessors = []
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()

    def detect_humans(self, cameraName,image,t0):
        validHuman = []
        for body in self.fullBodyHaarDetector(image):
            #cv2.imwrite("images/{}.body.jpg".format(self.num), body)
            faces = self.faceDetector(body[0])
            if len(faces) > 0:
                log.debug("发现{}个人脸".format(len(faces)))
            if len(faces) > 1:
                continue
            for face in faces:
                #cv2.imwrite("images/{}.face.jpg".format(self.num), face)
                validHuman.append((body, face,t0))
            self.num += 1
        t = clock()
        self.latency.update(t - t0)
        self.frame_interval.update(t - self.last_frame_time)
        if len(validHuman) > 0:
            log.debug("发现有效人物目标{}个 图像延迟:{:0.1f} 目标检测器用时：{:0.1f} ms".format(
            len(validHuman),self.latency.value * 1000, self.frame_interval.value * 1000))
        self.last_frame_time = t
        return validHuman

    def fullBodyDetector(self, image):
        found, w = self.hog.detectMultiScale(
            image, winStride=(8, 8), padding=(32, 32), scale=1.05)
        self.draw_detections(image, found)
        #print "found {} person".format(len(found))
        return self.cropImage(image, found)

    def fullBodyHaarDetector(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            #t = clock()
            rects = self.detect(gray, self.bodyClassifier)
            bodys = []

            if len(rects) > 0:
                self.draw_detections(image, rects, thickness = 1)
                log.debug("发现{}个人体图像".format(len(rects)))
            for x1, y1, x2, y2 in rects:

                roi = image.copy()[y1:y2, x1:x2]
                bodys.append((roi,max(x1,x2)-abs(x1-x2)/2,max(y1,y2)-abs(y1-y2)/2))
            #dt = clock() - t
            #draw_str(image, (20, 20), 'time: %.1f ms' % (dt*1000))
            return bodys
        except Exception, e:
            log.info(e.message)
            return []

    def upperBodyDetector(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        t = clock()
        rects = self.detect(gray, self.upperBodyClassifier)
        uppers = []
        self.draw_detections(image, rects, thickness=1)
        #print "found {} upper body".format(len(rects))
        for x1, y1, x2, y2 in rects:
            roi = image[y1:y2, x1:x2]
            uppers.append(roi)
            continue
        dt = clock() - t
        draw_str(image, (20, 20), 'time: %.1f ms' % (dt * 1000))
        return uppers

    def faceDetector(self, frame):
        faces = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        bbs = align.getAllFaceBoundingBoxes(gray)
        for bb in bbs:
            # print(len(bbs))
            landmarks = align.findLandmarks(gray, bb)
            alignedFace = align.align(
                96,
                frame,
                bb,
                landmarks=landmarks,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
            if alignedFace is None:
                continue

            roi = frame[bb.top():bb.bottom(), bb.left():bb.right()]
            faces.append((alignedFace,abs(bb.top()-bb.bottom())/2,abs(bb.left()-bb.right())/2))
        return faces

    def faceDetector_2(self, image):
        pass

    def inside(self, r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh

    def cropImage(self, image, rects):
        crops = []
        for x, y, w, h in rects:
            crops.append(image.copy()[y:y + h, x:x + w])
        return crops

    def detect(self, img, cascade):
        rects = cascade.detectMultiScale(
            img,
            scaleFactor=1.05,
            minNeighbors=4,
            minSize=(100, 100),
            maxSize=(500,500),
            flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects

    def draw_detections(self, img, rects, thickness=1):
        for x, y, w, h in rects:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            pad_w, pad_h = int(0.15 * w), int(0.05 * h)
            cv2.rectangle(img, (x + pad_w, y + pad_h),
                          (x + w - pad_w, y + h - pad_h), (0, 255,
                                                           0), thickness)
