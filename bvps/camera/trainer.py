# -*- coding: utf-8 -*-
from thespian.actors import *
from thespian.troupe import troupe
import logging as log
import sys, traceback, os

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC
import copy
import threading
from bvps.camera.camera import clock
import multiprocessing
import inspect
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC

from bvps.common import TrainingCMD
import time
import numpy as np
# from bvps.config import svm_param_grid as spg
import pickle
#from bvps.common import net

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
openfaceModelDir = os.path.join(modelDir, 'openface')

net = TorchNeuralNet(
    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)

spg = [{
    'C': [1, 10, 100, 1000],
    'kernel': ['linear']
}, {
    'C': [1, 10, 100, 1000],
    'gamma': [0.001, 0.0001],
    'kernel': ['rbf']
}]
tc = {"cap_nums": 20}


class TrainingProcessor(multiprocessing.Process):
    human_map = {}  # 应该持久化的map,持久化后可以使用多线程提高性能
    model_updated = False

    def __init__(self, camera, in_queue, out_queue):
        multiprocessing.Process.__init__(self, name="training_processor")
        TrainingProcessor.in_queue = in_queue
        TrainingProcessor.out_queue = out_queue
        self.camera = camera


    def run(self):
        global tc
        trth = threading.Thread(target=self.auto_training, args=())
        trth.setDaemon(True)
        trth.start()
        try:
            with open("./samples.pk", 'rb') as infile:
                self.human_map = pickle.load(infile)
                self.model_updated = True
        except Exception as  e:
            log.error(e)

        while True:
            message = TrainingProcessor.in_queue.get()
            if isinstance(message, TrainingCMD):
                receiver = threading.Thread(
                    target=self.receive_samples,
                    args=(TrainingProcessor.in_queue, self.human_map,
                          message.uid, message.msg, ))
                receiver.start()
                receiver.join()

    def receive_samples(self, inqueue, hm, uid, start_time):
        log.info("receive_samples called!!")
        num = 0
        while num < tc["cap_nums"]:
            message, t0, sec = TrainingProcessor.in_queue.get()
            human, roi, px, py = message
            if t0 < start_time or t0 - start_time > 1000000:
                continue
            if uid not in self.human_map:
                self.human_map[uid] = []
            if len(self.human_map[uid]) < tc["cap_nums"]:
                self.human_map[uid].append(human)
            log.info("human.size():{} {}".format(len(human), human.shape))
            num += 1
        if num < tc["cap_nums"]:
            # todo://样板数据搜集失败，应该返回不能开门
            log.info("用户{}的样本数量{}！".format(uid, len(self.human_map[uid])))
        self.model_updated = True
        log.info("接收到用户{}的样本图片，样本数量{}".format(uid, len(self.human_map[uid])))

    def auto_training(self):
        while True:
            try:
                if self.model_updated:
                    if len(self.human_map) < 2:
                        continue
                    log.info('ready to process generate model...')
                    hums = copy.deepcopy(self.human_map)
                    ready = False
                    for uid, imgs in hums.items():
                        if len(imgs) < tc["cap_nums"]:
                            log.error("wait moments...")
                            ready = False
                            break
                        ready = True
                        log.info("ready:{},process {}'s images to model.".format(
                            ready, uid))
                    if ready:
                        log.info("begin to train svm model....")
                        svm = self.train()
                        TrainingProcessor.out_queue.put(svm)
                        self.model_updated = False
                        with open("./samples.pk", 'wb') as outfile:
                            pickle.dump(self.human_map, outfile, 1)
                        log.info("ending to train svm model....")

                time.sleep(1)
            except Exception as  e:
                log.error(e)
    def train(self):
        try:
            global spg
            uids, images = [], []
            hums = copy.deepcopy(self.human_map)
            for uid, imgs in hums.items():
                for img in imgs:
                    # im = img.flatten()
                    rep = net.forward(img)
                    images.append(rep)
                uids.extend([uid for x in range(len(imgs))])
            X = np.vstack(images)
            y = np.array(uids)
            log.debug(
                "typeX:{}---typey:{}---lenx:{},leny:{}, X.shape:{}, y.shape:{}".
                format(type(X), type(y), len(X), len(y), X.shape, y.shape))
            return GridSearchCV(SVC(C=1), spg, cv=5, n_jobs=4).fit(X, y)
        except Exception as  e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error(
                traceback.format_exception(exc_type, exc_value, exc_traceback))
