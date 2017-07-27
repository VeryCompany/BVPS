# -*- coding: utf-8 -*-
import sys
import os
import logging as log
import multiprocessing
import cv2

from bvps.camera.common import clock, draw_str, StatValue
from bvps.camera.detectorthread import HumanDetector as detector
from bvps.camera.recognizer import OpenFaceRecognizer as recognizer
from multiprocessing.dummy import Pool as ThreadPool
from bvps.system.position_actor import PositionActor


class CameraServer(multiprocessing.Process):
    def __init__(self, queue, cmd, camera, cct):
        multiprocessing.Process.__init__(self)
        CameraServer.queue = queue
        self.cmd = cmd
        self.camera = camera
        self.cct = cct
        self.detector = detector()
        self.recognizer = recognizer(None)
        self.threadn = cv2.getNumberOfCPUs()
        self.pools = {}
        position = camera.createActor(
            PositionActor,
            targetActorRequirements=None,
            globalName="CameraPositionActor",
            sourceHash=None)

    def run(self):
        latency = StatValue()
        while True:
            frame, t0, secs = CameraServer.queue.get()
            self.process_frame(frame, t0, secs)
            t = clock()
            latency.update(t - t0)
            log.debug("摄像头[{}]进程{}处理数据，处理耗时{:0.1f}ms...".format(
                self.cmd.cameraName, self.pid, latency.value * 1000))

    def process_frame(self, frame, t0, secs):
        if self.camera.svm_model_updated:
            self.recognizer.svm = self.camera.svm_model
            self.camera.svm_model_updated = False
        humans = self.detector.detect_humans(self.cmd.cameraName, frame, t0,
                                             secs)
        #if self.camera. startTrainning():
        """
        sending humans to trainning actors
        通过通道的人，需要开始和结束时间，基准时间t0
        """
        if len(humans) > 0:
            if (self.camera.training_start_time is not None
                    and t0 > self.camera.training_start_time) and (
                        self.camera.training_end_time is None
                        or t0 < self.camera.training_end_time):
                for human in humans:
                    self.camera.send(self.trainor, (human, self.training_uid))
            if self.camera.svm_model is not None:
                users = self.recognizeParallel(self.process_recognize, humans)

    def recognizeParallel(self, method, humans):
        """多线程并行运算，提高运算速度"""
        kt = clock()
        pool = ThreadPool(processes=self.threadn)
        self.pools[kt] = pool
        results = pool.map_async(method, humans)
        pool.close()
        pool.join()
        pool.terminate()
        self.pools.pop(kt, None)
        return results

    def process_recognize(self, human):
        """识别检测到的人体图片，返回人对应的用户Id"""
        #log.debug("开始识别人！")

        try:
            t0 = human[2]
            secs = human[3]
            uid = self.recognizer.whoru(
                human) if self.recognizer.svm is not None else None
            log.debug("摄像头{}识别用户id：{},x:{},y:{}".format(
                self.cmd.cameraName, uid, human[0][1], human[0][2]))
            if uid is not None:
                msg = (self.cmd.cameraName, uid, human[0][1], human[0][2],
                       human[0][0], self.cct.resolution,0, secs)
                self.camera.send(self.position, msg)
            return human, uid
        except Exception, e:
            log.info(e.message)
            return human, None
