# -*- coding: utf-8 -*-
from thespian.actors import *
from thespian.troupe import troupe
import logging as log

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC
from bvps.config import training_config as tc
from bvps.config import svm_param_grid as spg
import copy

tc = {"cap_nums": 10}

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


class TrainingProcessor(multiprocessing.Process):
    human_map = {}  # 应该持久化的map

    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        TrainingServer.in_queue = in_queue
        TrainingServer.out_queue = out_queue

    def run(self):
        global tc
        last_uid = None
        while True:
            """
            接收N张照片，如果接收到足够数量的样本，返回消息
            """
            log.info("-------------------")
            message = TrainingServer.in_queue.get()
            human = message[0][0][0]
            uid = message[1]
            t0 = message[0][2]
            log.info("receive uid:{},faces".format(uid))
            if uid == last_uid:
                continue
            log.info("newuser {}".format(uid))
            if uid not in self.human_map:
                self.human_map[uid] = []
            if len(self.human_map[uid]) < tc["cap_nums"]:
                self.human_map[uid].append(human)
                log.info("msg")

            log.info(
                "接收到用户{}的样本图片，样本数量{}".format(uid, len(self.human_map[uid])))
            if len(self.human_map[uid]) >= tc["cap_nums"]:
                if len(self.human_map) > 1:
                    log.info("开始训练样品。。。")
                    self.train()
                    log.info(self.svm)
                    log.info("训练样本完成。。。")
                    TrainingServer.out_queue.put_nowait(self.svm)
                last_uid = uid

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
            self.svm = GridSearchCV(SVC(C=1), spg, cv=5).fit(X, y)
        except Exception as e:
            log.error(e)
