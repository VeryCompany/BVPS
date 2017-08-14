# -*- coding: utf-8 -*-
"""camera script."""
import logging as log
import multiprocessing
import os

import cv2
from bvps.camera.common import StatValue, clock
from bvps.common import CameraType, mtnnDir

import sys, traceback, time
from multiprocessing.pool import ThreadPool
from collections import deque

# numpy: image and matice computation
import numpy as np
# mxnet: deep learning
import mxnet as mx
# symbol: define the network structure
from core.symbol import P_Net, R_Net, O_Net
# detector: bind weight with structure and create a detector class
from core.detector import Detector
# fcn_detector: bind weight with structure and create a detector class
from core.fcn_detector import FcnDetector
# load_model: load model from .param file
from tools.load_model import load_param
# MtcnnDetector: concatenate the three networks
from core.MtcnnDetector import MtcnnDetector


class DetectorProcessor(multiprocessing.Process):
    def __init__(self, camera, frame_in, frame_out, frame_out_2):
        multiprocessing.Process.__init__(self, name="video_human_detector")
        DetectorProcessor.frame_in = frame_in
        DetectorProcessor.frame_out = frame_out
        DetectorProcessor.frame_out2 = frame_out_2
        self.camera = camera
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()
        self.mtcnn_detector = self.test_net(
            prefix=[
                os.path.join(mtnnDir, 'pnet'),
                os.path.join(mtnnDir, 'rnet'),
                os.path.join(mtnnDir, 'onet')
            ],
            epoch=[16, 16, 16],
            batch_size=[2048, 256, 16],
            ctx=mx.gpu(0),
            thresh=[0.5, 0.5, 0.7],
            min_face_size=40,
            stride=2)
        log.info("_"*50)
        log.info(self.mtcnn_detector)
        log.info("_"*50)


    def test_net(self,
                 prefix=[
                     os.path.join(mtnnDir, 'pnet'),
                     os.path.join(mtnnDir, 'rnet'),
                     os.path.join(mtnnDir, 'onet')
                 ],
                 epoch=[16, 16, 16],
                 batch_size=[2048, 256, 16],
                 ctx=mx.gpu(0),
                 thresh=[0.5, 0.5, 0.7],
                 min_face_size=40,
                 stride=2):
        try:
            # load pnet model
            args, auxs = load_param(prefix[0], epoch[0], convert=True, ctx=ctx)
            PNet = FcnDetector(P_Net("test"), ctx, args, auxs)

            # load rnet model
            args, auxs = load_param(prefix[1], epoch[0], convert=True, ctx=ctx)
            RNet = Detector(R_Net("test"), 24, batch_size[1], ctx, args, auxs)

            # load onet model
            args, auxs = load_param(prefix[2], epoch[2], convert=True, ctx=ctx)
            ONet = Detector(O_Net("test"), 48, batch_size[2], ctx, args, auxs)

            mtcnn_detector = MtcnnDetector(
                detectors=[PNet, RNet, ONet],
                ctx=ctx,
                min_face_size=min_face_size,
                stride=stride,
                threshold=thresh,
                slide_window=False)
            return mtcnn_detector
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error(
                traceback.format_exception(exc_type, exc_value, exc_traceback))

    def run(self):
        # brt_times = 0
        threadn = cv2.getNumberOfCPUs()
        pool = ThreadPool(processes=threadn)
        pending = deque()

        while True:
            try:
                """
                todo://比较画面是否有变化，如果没有变化可以不进行处理，提高效率！
                """

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

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))

    def detect_humans(self, image, t0, secs):
        boxes, boxes_c = self.mtcnn_detector.detect_pnet(image)
        boxes, boxes_c = self.mtcnn_detector.detect_rnet(image, boxes_c)
        boxes, boxes_c = self.mtcnn_detector.detect_onet(image, boxes_c)
        log.info(boxes)
        log.info(boxes_c)
        if boxes_c is not None:
            for b in boxes_c:
                # cv2.rectangle(draw, (int(b[0]), int(b[1])),
                #              (int(b[2]), int(b[3])), (0, 255, 255), 1)
                # crop image and resize....
                # return faces......
                log.info(b)
