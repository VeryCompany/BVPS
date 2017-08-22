# -*- coding: utf-8 -*-
from bvps.config import cameras as cms
from bvps.config import camera_group as cg
from functools import reduce
import logging as log
import numpy as np
import sys
from thespian.actors import *
import threading
import time
import traceback
from multiprocessing.dummy import Pool as ThreadPool


class PositionActorMsg(object):
    def __init__(self):
        pass


class PositionActor(ActorTypeDispatcher):
    position_cache = {}
    lock = threading.Lock()

    def __init__(self):
        super(PositionActor, self).__init__()
        log.info("system actor started")

    def processPosition(self, uid, sec, groups):
        while True:
            try:
                self.lock.acquire()
                log.info("开始处理世界坐标！")
                self.process_position(uid, sec, groups)
                log.info("处理世界坐标结束！")
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(e)
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))
            finally:
                self.lock.release()

    def receiveMsg_tuple(self, message, sender):
        cameraId, uid, px, t0, sec = message
        x, y = px
        cgid = None
        log.info("cameraId:{},user:{},px:{},py:{},t0:{},sec:{}".format(
            cameraId, uid, x, y, t0, sec))
        for gid, params in cg.items():
            if cameraId in params["members"]:
                cgid = gid
        log.info("stero camera group {}".format(cgid))
        if cgid is not None:
            sec = int(round(sec))
            baseline_mm = cg[cgid]["baseline_mm"]
            cx = cg[cgid]["cx"]
            cy = cg[cgid]["cy"]
            try:
                self.lock.acquire()
                if uid not in self.position_cache:
                    self.position_cache[uid] = {}
                if sec not in self.position_cache[uid]:
                    self.position_cache[uid][sec] = {}
                if cgid not in self.position_cache[uid][sec]:
                    self.position_cache[uid][sec][cgid] = {}
                if cameraId not in self.position_cache[uid][sec][cgid]:
                    self.position_cache[uid][sec][cgid][cameraId] = []
                self.position_cache[uid][sec][cgid][cameraId].append([x, y])
                """Xpx,Ypx,centreX,centreY,baseline_mm,pixel_per_mm"""

                for uid, pxy in self.position_cache.items():
                    for sec_item, groups in pxy.items():
                        if sec_item >= sec - 3:
                            log.info("sec:{},{}".format(sec, groups))
                            self.processPosition(uid, sec, groups)

                if len(self.position_cache[uid]) > 10:
                    times = sorted(self.position_cache[uid].keys())
                    for locTime in times[:-10]:
                        self.position_cache[uid].pop(locTime)

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))
            finally:
                self.lock.release()

                # """
                # position_cache = {
                #     "uid":{
                #         1:{
                #             "groupid1":{
                #                 "cameraID1":[],
                #                 "cameraID2":[]
                #             }
                #              "groupid1":{
                #                 "cameraID1":[],
                #                 "cameraID2":[]
                #             }
                #         },
                # 2:{
                #             "groupid2":{
                #                 "cameraID3":[],
                #                 "cameraID4":[]
                #             }
                #         }
                #     }
                # }
                # """

    def process_position(self, uid, sec, groups):
        # for uId, datas in self.position_cache:
        #     """发送用户Id，世界坐标x，世界坐标y，位置时间到定位中心"""
        positions = self.process_user_position(groups)
        log.info("user:{} sec->:{}".format(uid, sec))

    def process_user_position(self, datas):
        pool = ThreadPool(8)
        # current = int(time.time()) - 1
        # map_in = []
        # for sec, group in datas:
        #     if sec <= current:
        #         map_in.append((sec, group))
        # user_position = pool.map_async(self._locate_user, map_in)
        user_position = pool.map_async(self._locate_user, datas)
        pool.close()
        pool.join()
        return user_position

    def _locate_user(self, sec_group):
        camere_position = {}
        # for sec, group in sec_group:
        multi_position_xy = {}
        for groupId, values in sec_group.items():
            if len(values) < 2:
                continue
            camera_group_xy = {"groupId": groupId}
            for camId,infos in values.items():
                x_y = list(map(lambda info: [info[0], info[1]], infos))
                # """需要考虑更好的滤波方式"""
                sum_xy = reduce(lambda axy1, axy2: np.add(axy1, axy2), x_y)
                # """当前时间1秒以内的像素平均坐标"""
                average_xy = np.divide(sum_xy, len(x_y))
                camera_group_xy[camId]["xy"] = average_xy
                # pixel_mm = cms[camId]["parameters"]["pixel_mm"] / cms[camId]["scale"]
                # focallength = cms[camId]["parameters"][focallength]
                # camera_group_xy[camId]["pixel_mm"] = pixel_mm
                # camera_group_xy[camId]["focallength"] = focallength
                # if camId == cg["primary"]:
                #     camera_group_xy["primary"] = camId
                # else:
                #     camera_group_xy["slave"] = camId

            multi_position_xy[groupId] = camera_group_xy
            """单位时间的画面坐标"""

        for gp in multi_position_xy.items():
            # groupId = multi_position_xy[gp]#gp["groupId"]
            camera_group_xy = multi_position_xy[gp]
            primary = None
            slave = None
            for camId in cg[gp]["members"]:
                if camId == cg[gp]["primary"]:
                    primary = camId
                else:
                    slave = camId
            primary_xy = camera_group_xy[primary]["xy"]
            slave_xy = camera_group_xy[slave]["xy"]

            x1 = primary_xy[0]
            y1 = primary_xy[1]
            x2 = slave_xy[0]
            y2 = slave_xy[1]

            baseline = int(cg[gp]["baseline_mm"])
            d = abs(x1 - x2)

            f = int(cms[gp]["parameters"]["focallength"])
            Z = f * baseline / d

            X = x1 * Z / f
            Y = y1 * Z / f

            # camere_position = {}
            camere_position[gp] = [X, Y, Z]
            log.info("position X->:{} Y->:{} Z->:{}".format(X, Y, Z))
        return camere_position
