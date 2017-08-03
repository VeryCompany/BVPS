# -*- coding: utf-8 -*-
"""camera script."""
import logging as log
import multiprocessing
import os
from enum import Enum

import cv2
import numpy as np
import openface
from bvps.camera.common import StatValue, clock, draw_str
from bvps.common import align, net, harrsDir, CameraType

import sys, traceback, time
import threading
from multiprocessing.pool import ThreadPool
from collections import deque


class DetectorProcessor(multiprocessing.Process):
    def __init__(self, camera, frame_in, frame_out, frame_out_2):
        multiprocessing.Process.__init__(self, name="video_human_detector")
        DetectorProcessor.frame_in = frame_in
        DetectorProcessor.frame_out = frame_out
        DetectorProcessor.frame_out2 = frame_out_2
        self.camera = camera
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.bodyClassifier = cv2.CascadeClassifier(
            os.path.join(harrsDir, "haarcascade_upperbody.xml"))
        self.faceClassifier = cv2.CascadeClassifier(
            os.path.join(harrsDir, "haarcascade_frontalface_alt.xml"))
        self.upperBodyClassifier = cv2.CascadeClassifier(
            os.path.join(harrsDir, "haarcascade_upperbody.xml"))

        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()

    def run(self):
        # brt_times = 0
        threadn = cv2.getNumberOfCPUs()
        pool = ThreadPool(processes=threadn * 6)
        pending = deque()

        while True:
            try:
                """
                todo://比较画面是否有变化，如果没有变化可以不进行处理，提高效率！
                """
                # frame, t0, secs = DetectorProcessor.frame_in.get()
                # for bt in range(
                #         min(brt_times, DetectorProcessor.frame_in.qsize())):
                #     frame, t0, secs = DetectorProcessor.frame_in.get()
                #
                # humans = self.detect_humans(frame, t0, secs)
                # if len(humans) > 0:
                #     log.debug("检测到{}个人".format(len(humans)))
                #     for human in humans:
                #         DetectorProcessor.frame_out2.put(human)  # for 识别器
                #         if self.camera.cameraType == CameraType.CAPTURE:
                #             DetectorProcessor.frame_out.put(human)  # for Trainor
                #     brt_times = -5
                # else:
                #     brt_times += 1
                #     log.debug("没有检测到人，跳过{}帧".format(brt_times))
                # if brt_times > 2:
                #     brt_times = -5
                # log.debug("detector_{},latency:{:0.1f}ms,process time:{:0.1f}ms".
                #           format(self.camera.cameraId, self.latency.value * 1000,
                #                  self.frame_interval.value * 1000))
                #
                # t = clock()
                # self.latency.update(t - t0)
                # self.frame_interval.update(t - self.last_frame_time)
                # self.last_frame_time = t
                while len(pending) > 0 and pending[0].ready():
                    humans = pending.popleft().get()
                    for human in humans:
                        DetectorProcessor.frame_out2.put(human)  # for 识别器
                        if self.camera.cameraType == CameraType.CAPTURE:
                            DetectorProcessor.frame_out.put(
                                human)  # for Trainor
                if len(pending) < threadn:
                    frame, t0, secs = DetectorProcessor.frame_in.get()
                    task = pool.apply_async(self.detect_humans, (frame, t0,
                                                                 secs))
                    pending.append(task)
                    t = clock()
                    self.latency.update(t - t0)
                    self.frame_interval.update(t - self.last_frame_time)
                    self.last_frame_time = t
                log.debug(
                    "detector_{},latency:{:0.1f}ms,process time:{:0.1f}ms".
                    format(self.camera.cameraId, self.latency.value * 1000,
                           self.frame_interval.value * 1000))

            except Exception, e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))

    def detect_humans(self, image, t0, secs):
        validHuman = []
        faces = self.faceDetector(image)
        for face in faces:
            validHuman.append((face, t0, secs))
        return validHuman

    def fullBodyDetector(self, image):
        found, w = self.hog.detectMultiScale(
            image, winStride=(8, 8), padding=(32, 32), scale=1.05)
        self.draw_detections(image, found)
        return self.cropImage(image, found)

    def fullBodyHaarDetector(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            rects = self.detect(gray, self.bodyClassifier)
            bodys = []
            for x1, y1, x2, y2 in rects:
                roi = image.copy()[y1:y2, x1:x2]
                bodys.append((roi, max(x1, x2) - abs(x1 - x2) / 2,
                              max(y1, y2) - abs(y1 - y2) / 2))
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

            roi = frame.copy()[bb.top():bb.bottom(), bb.left():bb.right()]
            faces.append((alignedFace, roi, bb.dcenter().x, bb.dcenter().y))
        return faces

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
            minSize=(30, 30),
            maxSize=(300, 300),
            flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects

    def draw_detections(self, img, rects, thickness=1):
        for x, y, w, h in rects:
            pad_w, pad_h = int(0.15 * w), int(0.05 * h)
            cv2.rectangle(img, (x + pad_w, y + pad_h),
                          (x + w - pad_w, y + h - pad_h), (0, 255,
                                                           0), thickness)
