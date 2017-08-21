# -*- coding: utf-8 -*-
"""camera script."""
import logging as log
import multiprocessing
import cv2
from bvps.camera.common import StatValue, clock
from bvps.common import CameraType, mtnnDir
import sys
import traceback
from multiprocessing.pool import ThreadPool
from collections import deque
from bvps.camera.mtcnn import test_net


class DetectorProcessor(multiprocessing.Process):
    def __init__(self, camera, frame_in, frame_out, frame_out_2, gpuId):
        multiprocessing.Process.__init__(self, name="video_human_detector")
        DetectorProcessor.frame_in = frame_in
        DetectorProcessor.frame_out = frame_out
        DetectorProcessor.frame_out2 = frame_out_2
        self.camera = camera
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()
        self.gpuId = gpuId

    def run(self):
        log.info("ready to startup camera:{}'s' mtcnn detector".format(
            self.camera.cameraId))
        self.mtcnn_detector = test_net(self.gpuId)

        log.info("camera:{}'s' mtcnn detector successfully startup......".
                 format(self.camera.cameraId))
        log.info(self.mtcnn_detector)
        frame_stat = StatValue()
        humans_stat = StatValue()
        frame_interval_stat = StatValue()
        humans_latency_stat = StatValue()
        last_info_time = clock()
        stat_time = 30  # 一分钟统计一次
        while True:
            try:
                frame, t0, secs = DetectorProcessor.frame_in.get()
                humans = self.detect_humans(frame, t0, secs)
                frame_stat.update(frame_stat.value + 1)
                for human in humans:
                    if not DetectorProcessor.frame_out2.full():
                        DetectorProcessor.frame_out2.put(human)  # for 识别器
                        humans_stat.update(humans_stat.value + 1)
                    if self.camera.cameraType == CameraType.CAPTURE:
                        if not DetectorProcessor.frame_out.full():
                            DetectorProcessor.frame_out.put(
                                human)  # for Trainor
                tn = clock()
                self.frame_interval.update(tn - self.last_frame_time)
                self.latency.update(tn - t0)
                frame_interval_stat.value(frame_interval_stat.value +
                                          self.frame_interval.value)
                humans_latency_stat.value(humans_latency_stat.value +
                                          self.latency.value)
                if tn - last_info_time > stat_time:
                    time_cost = tn - last_info_time
                    last_info_time = tn
                    log.info(
                        "{}-平均帧率:{:0.1f},平均延迟:{:0.1f}s,处理frame:{:0.1f}s,处理人脸:{:0.1f}s".
                        format(self.camera.cameraId, frame_stat.value /
                               time_cost, humans_latency_stat.value /
                               time_cost, frame_interval_stat.value /
                               time_cost, humans_stat.value / time_cost))
                    frame_stat.update(0)
                    humans_latency_stat.update(0)
                    frame_interval_stat.update(0)
                    humans_stat.update(0)
                self.last_frame_time = tn
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))

    def detect_humans(self, image, t0, secs):
        validHuman = []
        try:
            if self.mtcnn_detector is None:
                log.error("mtcnn error!")
                return validHuman
            # log.info("image.shape:{}".format(image.shape))
            boxes, boxes_c = self.mtcnn_detector.detect_pnet(image)
            boxes, boxes_c = self.mtcnn_detector.detect_rnet(image, boxes_c)
            boxes, boxes_c = self.mtcnn_detector.detect_onet(image, boxes_c)

            if boxes_c is not None:
                #log.info("{} detected！".format(self.camera.cameraId))
                for b in boxes_c:
                    # cv2.rectangle(draw, (int(b[0]), int(b[1])),
                    #              (int(b[2]), int(b[3])), (0, 255, 255), 1)
                    center_x, center_y = (
                        (int(b[0]) + abs(int(b[0]) - int(b[2])) / 2),
                        (int(b[1]) + abs(int(b[1]) - int(b[3])) / 2))
                    log.debug("{}->{}:{}".format(self.camera.cameraId,
                                                 center_x, center_y))
                    w, h = (abs(int(b[0]) - int(b[2])) / 2,
                            abs(int(b[1]) - int(b[3])) / 2)
                    log.debug(
                        "{}->w:{},h:{}".format(self.camera.cameraId, w, h))
                    # crop image and resize....
                    face_img = image.copy()[int(b[1]):int(b[3]),
                                            int(b[0]):int(b[2])]
                    face_img = cv2.resize(
                        face_img, (96, 96), interpolation=cv2.INTER_AREA)
                    validHuman.append((face_img, t0, secs, (center_x,
                                                            center_y), (w, h)))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error(
                traceback.format_exception(exc_type, exc_value, exc_traceback))
            log.error(e)
        finally:
            return validHuman
