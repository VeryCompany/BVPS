# -*- coding: utf-8 -*-
from thespian.actors import *
from thespian.troupe import troupe
import logging as log

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC
import copy
import threading
from bvps.camera.camera import clock
import multiprocessing

from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
# from bvps.config import svm_param_grid as spg

spg = [{
    'C': [1, 10, 100, 1000],
    'kernel': ['linear']
}, {
    'C': [1, 10, 100, 1000],
    'gamma': [0.001, 0.0001],
    'kernel': ['rbf']
}]
tc = {"cap_nums": 10}


class TrainingProcessor(multiprocessing.Process):
    human_map = {}  # 应该持久化的map,持久化后可以使用多线程提高性能
    model_updated = False

    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self, name="training_processor")
        TrainingProcessor.in_queue = in_queue
        TrainingProcessor.out_queue = out_queue

    def run(self):
        global tc
        trth = threading.Thread(target=self.auto_training, args=())
        trth.setDaemon(True)
        trth.start()

        while True:
            message = TrainingProcessor.in_queue.get()
            if message.__class__ == TrainingCMD.__class__:
                receiver = threading.thread(
                    target=self.receive_samples,
                    args=(TrainingServer.in_queue, self.human_map, message.uid,
                          message.msg, ))
                receiver.start()
                receiver.join()

    def receive_samples(self, inqueue, hm, uid, start_time):
        num = 0
        while num < tc["cap_nums"]:
            message, t0, sec = TrainingServer.in_queue.get()
            human = message[0][0]
            if t0 < start_time or t0 - start_time > 1000000:
                continue
            if uid not in self.human_map:
                self.human_map[uid] = []
            if len(self.human_map[uid]) < tc["cap_nums"]:
                self.human_map[uid].append(human)
            num += 1
        if num < tc["cap_nums"]:
            # todo://样板数据搜集失败，应该返回不能开门
            log.info("用户{}的样本数量{}！".format(uid, len(self.human_map[uid])))
            pass
        self.model_updated = True
        log.info("接收到用户{}的样本图片，样本数量{}".format(uid, len(self.human_map[uid])))

    def auto_training(self):
        while self.model_updated:
            if len(self.human_map) < 2:
                continue
            hums = copy.deepcopy(self.human_map)
            for uid, imgs in hums.items():
                if len(imgs) != tc["cap_nums"]:
                    log.error("msg")
            svm = self.train()
            TrainingServer.out_queue.put(svm)
            time.sleep(1)

    def train(self):
        try:
            global spg
            uids, images = [], []
            hums = copy.deepcopy(self.human_map)
            for uid, imgs in hums.items():
                for img in imgs:
                    log.info("msg--type:{}".format(type(img)))
                    images.append(img.flatten())
                log.info("type:{}".format(type(imgs)))
                log.info("images-type:{}".format(type(images)))
                uids.extend([uid for x in range(len(imgs))])

            X = np.vstack(images)
            y = np.array(uids)
            log.info("typeX:{}---typey:{}---lenx:{},leny:{}".format(
                type(X), type(y), len(X), len(y)))
            return GridSearchCV(SVC(C=1), spg, cv=5).fit(X, y)
        except Exception as e:
            log.error(e)
