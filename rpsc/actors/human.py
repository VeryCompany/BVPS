# -*- coding: utf-8 -*-
from rpsc.models import HumanModel, ShoppingCartProductModel
from rpsc.actors.core import *
from rpsc.utils.kalmanFilter import KalmanFilter
import rpsc.config as rack_config

# from bvps.config import cameras
# from bvps.camera.camera import Camera
# from bvps.common import CameraType, TrainingCMD, CameraCmdType
# import time


class HumanActor(ActorTypeDispatcher):
    def __init__(self):
        super().__init__()
        self.human = None
        self.coreActor = None
        self.filter = None
        self.lastTime = None

    def get_core_actor(self):
        if self.coreActor is None:
            self.coreActor = self.createActor(CoreActor, globalName="coreActor")
        return self.coreActor

    def init_filter(self, rssis, rssi_time):
        if self.filter is None:
            self.lastTime = rssi_time
            self.filter = KalmanFilter(x0=rssis)

    def receiveMsg_HumanTakeProduct(self, message, sender):
        product = message.product
        opt = message.opt
        product_count = message.productCount
        print("Human Take Product ->:", product_count, type(product_count))
        if opt == "02":
            if self.human is not None:
                for i in range(product_count):
                    self.human.shoppingCart.add_product(product)
            else:
                print("用户已经离开")
        elif opt == "01":
            for i in range(product_count):
                self.human.shoppingCart.remove_product(product.productId)
        print(self.human, self.human.humanId, product, sender)

    def receiveMsg_HumanRssis(self, message, sender):
        human_id = message.humanId
        original_rssis = message.rssis
        rssi_time = message.rssiTime

        beacons = rack_config.beaconList
        rssis = list()
        for beacon in beacons:
            if beacon in original_rssis:
                beacon_val = original_rssis[beacon]
                rssis.append(beacon_val)
            else:
                rssis.append(-100)

        # print(human_id, "rssis -> ", rssis)

        if self.lastTime is None or self.filter is None:
            self.init_filter(rssis, rssi_time)
        diff_time = 1
        if self.lastTime is not None:
            last_time = self.lastTime
            diff_time = int(rssi_time) - int(last_time)
        find_rssis = rssis
        if diff_time >= 0:
            filter_rssis, var_rssis = self.filter.update(rssis, diff_time)
            find_rssis = filter_rssis
        else:
            print("time later ... ", sender)
        self.lastTime = rssi_time

        self.send(self.get_core_actor(), UserLoc(human_id, int(int(rssi_time) / 1000), find_rssis, "app"))

    def receiveMsg_HumanOpt(self, message, sender):
        human_type = message.humanType
        human_id = message.humanId
        print(human_id)
        if human_type == 'cart':
            if self.human is not None:
                shop_cart = self.human.shoppingCart
                print(shop_cart)
                self.send(sender, str(shop_cart))
            else:
                self.send(sender, None)

    def receiveMsg_HumanOut(self, message, sender):
        try:
            human_id = message.humanId
            out_time = message.outTime
            if self.human is not None:
                print("用户:", human_id, "在[", out_time, "]离开", sender)
                self.send(self.get_core_actor(), UserEvent(human_id, "out"))
                # ControlCenter.asys.tell(ControlCenter.coreActor, UserEvent(humanId, "out"))
                self.human = None
                self.filter = None
            else:
                print("用户:", human_id, "已经离开")
        except Exception as outErr:
            print("outErr", outErr)

    def receiveMsg_HumanCome(self, message, sender):
        try:
            human_id = message.humanId
            user_time = message.inTime
            loc = message.loc
            if self.human is None:
                self.human = HumanModel(human_id, loc, ShoppingCartProductModel(0))
                self.human.set_come_time(user_time)
                print("用户:", human_id, "在[", user_time, "]进入超市", type(human_id), sender)
                self.send(self.get_core_actor(), UserEvent(human_id, "in"))

                # for cam_id, params in cameras.items():
                #     if "cameraType" in params and params["cameraType"] == CameraType.CAPTURE:
                #         cam = self.createActor(Camera, globalName=cam_id)
                #         self.send(cam, TrainingCMD(CameraCmdType.TRAINOR_START, time.time(), human_id))

            else:
                print("存在用户:", human_id)
        except Exception as inErr:
            print("inErr:", inErr)


class HumanBase:
    def __init__(self, human_id):
        self.humanId = human_id


class HumanCome(HumanBase):
    def __init__(self, human_id, in_time, loc):
        HumanBase.__init__(self, human_id)
        self.inTime = in_time
        self.loc = loc


class HumanOut(HumanBase):
    def __init__(self, human_id, out_time):
        HumanBase.__init__(self, human_id)
        self.outTime = out_time


class HumanTakeProduct:
    def __init__(self, product, opt, product_count=1):
        self.product = product
        self.opt = opt
        self.productCount = product_count


class HumanOpt(HumanBase):
    def __init__(self, human_id, human_type):
        HumanBase.__init__(self, human_id)
        self.humanType = human_type


class HumanRssis(HumanBase):
    def __init__(self, human_id, rssis, rssi_time):
        HumanBase.__init__(self, human_id)
        self.rssis = rssis
        self.rssiTime = rssi_time
