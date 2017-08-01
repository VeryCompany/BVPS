# -*- coding: utf-8 -*-
from thespian.actors import *
import logging
from bvps.config import cameras as cms
from bvps.config import camera_group as cg
import threading
import time
from multiprocessing.dummy import Pool as ThreadPool
import numpy as np

class PositionActorMsg(object):
    def __init__(self):
        pass


lock = threading.Lock()


class PositionActor(ActorTypeDispatcher):
    position_cache = {}

    def __init__(self, *args, **kw):
        super(PositionActor, self).__init__(*args, **kw)
        logging.info("system actor started")

    def processPosition(self):
        while True:
            self.process_position()
            time.sleep(1)

    def receiveMsg_tuple(self, message, sender):
        cameraId, uid, px, t0, sec = message
        x, y = px
        cgid = None
        for gid, params in cg.items():
            if cameraId in params["members"]:
                cgid = gid
        if cgid is not None:
            baseline_mm = cg["baseline_mm"]
            cx = cg["cx"]
            cy = cg["cy"]
            if uid not in self.position_cache:
                self.position_cache[uid] = {}
            if sec not in self.position_cache[uid]:
                self.position_cache[uid][sec] = {}
            if cgid not in self.position_cache[uid][sec]:
                self.position_cache[uid][sec][cgid] = {}
            if cameraId not in self.position_cache[uid][sec][cgid]:
                self.position_cache[uid][sec][cgid][cameraId] = []
            self.position_cache[uid][sec][cgid][cameraId].append(
                [x, y])
            """Xpx,Ypx,centreX,centreY,baseline_mm,pixel_per_mm"""

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

    def process_position(self):
        for uId, datas in self.position_cache:
            """发送用户Id，世界坐标x，世界坐标y，位置时间到定位中心"""
            positions = self.process_user_position(datas)
            logging.info("user:{} positions->:{}".format(uId, positions))

    def process_user_position(self, datas):
        pool = ThreadPool(8)
        current = int(time.time()) - 1
        map_in = []
        for sec, group in datas:
            if sec <= current:
                map_in.append((sec, group))
        user_position = pool.map_async(self._locate_user, map_in)
        pool.close()
        pool.join()
        return user_position

    def _locate_user(self, sec_group):
        camere_position = {}
        for sec, group in sec_group:
            multi_position_xy = {}
            for groupId,values in group:
                if len(values) < 2:
                    continue
                camera_group_xy = {"groupId":groupId}
                for camId, infos in values:
                    x_y = map(lambda info : [info[0],info[1]], infos)
                    # """需要考虑更好的滤波方式"""
                    sum_xy = reduce(lambda axy1,axy2: np.add(axy1,axy2), x_y)
                    # """当前时间1秒以内的像素平均坐标"""
                    average_xy= np.divide(sum_xy, len(x_y))
                    camera_group_xy[camId]["xy"] = average_xy
                    # pixel_mm = cms[camId]["parameters"]["pixel_mm"] / cms[camId]["scale"]
                    # focallength = cms[camId]["parameters"][focallength]
                    # camera_group_xy[camId]["pixel_mm"] = pixel_mm
                    # camera_group_xy[camId]["focallength"] = focallength
                    # if camId == cg["primary"]:
                    #     camera_group_xy["primary"] = camId
                    # else:
                    #     camera_group_xy["slave"] = camId

                multi_position_xy [groupId] = camera_group_xy
                """单位时间的画面坐标"""

            for gp in multi_position_xy:
                #groupId = multi_position_xy[gp]#gp["groupId"]
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

                camere_position[sec]={}
                camere_position[sec][gp]=[X,Y,Z]
        return camere_position
