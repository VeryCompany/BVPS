# -*- coding: utf-8 -*-

import logging as log
import multiprocessing
import os
import pickle
import sys
import socket
import traceback
from time import sleep
from bvps.camera.camera import StatValue, clock
from bvps.common import ModelUpdateCmd


fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
openfaceModelDir = os.path.join(modelDir, 'openface')

# net = TorchNeuralNet(
#    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)

HOST = '192.168.0.163'
PORT = 8992

class SVMRecognizer(multiprocessing.Process):
    def __init__(self, camera, in_queue, out_queue):
        multiprocessing.Process.__init__(self, name="video_human_recognizer")
        SVMRecognizer.in_queue = in_queue
        SVMRecognizer.out_queue = out_queue
        self.camera = camera
        self.model = None
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()
        self.socket_client = None
        self.do_connect()

    def do_connect(self):
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client.connect((HOST, PORT))

    def whoru(self, human):
        face = human
        # rep = self.actor_system.ask(self.net, (self.camera.cameraId, face), 5)

        try:
            # rep = self.net.forward(face)
            self.socket_client.sendall(face)
            receive_data = self.socket_client.recv(4096*1000)
            rep = pickle.loads(receive_data)
        except socket.error as tcpConnectErr:
            print("tcpConnectErr:", tcpConnectErr)
            sleep(3)
            self.do_connect()
        except Exception as tcpReceiveErr:
            print("tcp Receive Err:", tcpReceiveErr)
        identity = None
        if self.model is not None:
            identity = self.model.predict(rep)[0]
        return identity

    def run(self):

        while True:
            try:
                msg = SVMRecognizer.in_queue.get()
                if isinstance(msg, ModelUpdateCmd):
                    self.model = msg.model
                    continue
                human, t0, sec, center, size = msg
                px, py = center
                uid = self.whoru(human)
                if uid is not None:
                    # 用户uid出现在图片坐标(px,py),精确时间t0,秒时间sec
                    log.info(
                        "user:{},px:{},py:{},sec:{}".format(uid, px, py, sec))
                    SVMRecognizer.out_queue.put((self.camera.cameraId, uid,
                                                 (px, py), t0, sec))
                t = clock()
                self.latency.update(t - t0)
                self.frame_interval.update(t - self.last_frame_time)
                self.last_frame_time = t
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))
