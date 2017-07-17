# -*- coding: utf-8 -*-
from thespian.actors import *
import os
import numpy as np
import cv2
import threading
from enum import Enum
from bvps.camera.common import clock, draw_str, StatValue
from thespian.troupe import troupe
from bvps.camera.recognizer import HumanRecognizer
import openface
import logging as log
#检测人-->（人+上半身+脸+鼻子+眼睛）-->识别人
fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')
align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96,cuda=False)

class HumanDetector(ActorTypeDispatcher):
    num=0
    def __init__(self, *args, **kw):
        log.info("init HumanDetector actor...")
        super(HumanDetector, self).__init__(*args, **kw)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )
        self.bodyClassifier = cv2.CascadeClassifier("haarcascade_upperbody.xml")
        self.faceClassifier = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
        self.upperBodyClassifier = cv2.CascadeClassifier("haarcascade_upperbody.xml")
        self.HumanRecognizerProcessors = []
        log.info("init HumanDetector actor ok!") 


    def receiveMsg_tuple(self, message, sender):
        cameraName = message[0]
        image = message[2]
        validHuman = []
        self.num += 1
        if len(self.HumanRecognizerProcessors) == 0:
            self.HumanRecognizerProcessors = [self.createActor(HumanRecognizer,globalName="{}-human-recognizer".format(cameraName))]
        for body in self.fullBodyHaarDetector(image):
            #cv2.imwrite('images/{}.jpg'.format(self.num),body)
            #for upb in self.upperBodyDetector(body):
            faces = self.faceDetector(body)
            if len(faces) > 1:
                continue
            for face in faces:
                validHuman.append(body,face)
            #        continue
        #cv2.imwrite('images/old-{}.jpg'.format(self.num),image)
        for person in validHuman:
            for recognizer in self.HumanRecognizerProcessors:
                self.send(recognizer,person)

    def fullBodyDetector(self,image):
        found, w = self.hog.detectMultiScale(image, winStride=(8,8), padding=(32,32), scale=1.05)
        self.draw_detections(image, found)
        #print "found {} person".format(len(found))
        return self.cropImage(image, found)

    def fullBodyHaarDetector(self,image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        #t = clock()
        rects = self.detect(gray, self.bodyClassifier)
        bodys = []
        #self.draw_detections(image, rects, thickness = 1)
        #print "found {}  bodys".format(len(rects))
        for x1, y1, x2, y2 in rects:
            roi = image.copy()[y1:y2, x1:x2]
            bodys.append(roi)
        #dt = clock() - t
        #draw_str(image, (20, 20), 'time: %.1f ms' % (dt*1000))
        return bodys
    def upperBodyDetector(self,image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        t = clock()
        rects = self.detect(gray, self.upperBodyClassifier)
        uppers = []
        self.draw_detections(image, rects, thickness = 1)
        #print "found {} upper body".format(len(rects))
        for x1, y1, x2, y2 in rects:
            roi = image[y1:y2, x1:x2]
            uppers.append(roi)
            continue
        dt = clock() - t
        draw_str(image, (20, 20), 'time: %.1f ms' % (dt*1000))
        return uppers
    def faceDetector(self,frame):
        faces = []
        bbs = align.getAllFaceBoundingBoxes(frame)
        for bb in bbs:
            # print(len(bbs))
            landmarks = align.findLandmarks(frame, bb)
            alignedFace = align.align(96, frame, bb,
                                      landmarks=landmarks,
                                      landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
            if alignedFace is None:
                continue

            roi = frame[bb.top():bb.bottom(), bb.left():bb.right()]
            faces.append(roi)
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
            crops.append(image.copy()[y:y+h,x:x+w])
        return crops

    def detect(self,img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=3, minNeighbors=1, minSize=(150, 150),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
        return rects

    def draw_detections(self,img, rects, thickness = 1):
        for x, y, w, h in rects:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            pad_w, pad_h = int(0.15*w), int(0.05*h)
            cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)
