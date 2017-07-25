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
class CameraServer(multiprocessing.Process):

    def __init__(self,queue,cmd,camera,cct):
        multiprocessing.Process.__init__(self)
        CameraServer.queue = queue
        self.cmd = cmd
        self.camera = camera
        self.cct = cct
        self.detector = detector()
        self.recognizer = recognizer(None)
        self.threadn=cv2.getNumberOfCPUs()
        self.pools={}
    def run(self):
        latency = StatValue()
        while True:
            frame,t0 = CameraServer.queue.get()
            self.process_frame(frame,t0)
            t = clock()
            latency.update(t - t0)
            log.debug("摄像头[{}]进程{}处理数据，处理耗时{:0.1f}ms...".format(self.cmd.cameraName,self.pid,latency.value * 1000))

    def process_frame(self,frame,t0):
        humans = self.detector.detect_humans(self.cmd.cameraName, frame, t0)
        #if self.camera. startTrainning():
        """
        sending humans to trainning actors
        通过通道的人，需要开始和结束时间，基准时间t0
        """
        if len(humans) > 0:
            if self.camera.training_started and t0 > self.camera.training_start_time and t0 < self.camera.training_end_time:
                for human in humans:
                    self.camera.send(self.trainor,human)
            else:
                users = self.recognizeParallel(
                    self.process_recognize, humans)

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

    def process_recognize(self, human):
        """识别检测到的人体图片，返回人对应的用户Id"""
        #log.debug("开始识别人！")
        try:
            uid = self.recognizer.whoru(human, t0) if self.recognizer.svm is not None else None
            log.info("摄像头{}识别用户id：{},x:{},y:{}".format(self.cmd.cameraName,uid,human[0][1],human[0][2]))
            #发送至定位中枢，确定用户坐标
            return human, uid
        except Exception, e:
            log.info(e.message)
            return human,None