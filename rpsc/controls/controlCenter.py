# -*- coding: utf-8 -*-

from rpsc.actors.human import *
from rpsc.actors.rack import *
from rpsc.actors.core import *
from rpsc.utils.elinkUtils import *
import time


class ControlCenter:
    aSys = None
    rackActor = None
    coreActor = None

    phoneCenter = None
    notSureProduct = dict()

    @staticmethod
    def set_asys(asys):
        if ControlCenter.aSys is None:
            ControlCenter.aSys = asys
            ControlCenter.rackActor = ControlCenter.aSys.createActor(RackActor)
            ControlCenter.coreActor = ControlCenter.aSys.createActor(CoreActor, globalName="coreActor")
        else:
            print("init aSys")

    @staticmethod
    def send_loc_product_msg(msg, opt):
        loc = [msg[0], msg[1]]
        result, product = ControlCenter.aSys.ask(ControlCenter.rackActor, LocProduct(loc, opt))
        print("LocProduct", product, loc)
        if result == "success":
            # print ControlCenter.coreActor.userList, ControlCenter.coreActor.userCount
            user_list, user_count = ControlCenter.aSys.ask(ControlCenter.coreActor,
                                                           FindUser(product.rackId, int(time.time())))
            # TODO 根据商品位置找到对应位置的人
            print(product.rackId)
            if user_count == 1:
                human_id = user_list[0]
                human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(human_id))
                ControlCenter.aSys.ask(human, HumanTakeProduct(product, opt))
                ControlCenter.phoneCenter.send_msg2phone(human_id, "2")
            else:
                product_sign_id = get_next_random_id()
                product_status = dict()
                product_status["productId"] = product.productId
                user_status = dict()
                for user_ids in range(user_count):
                    human_id = user_list[user_ids]
                    user_status[human_id] = 2
                    ask_message = dict()
                    ask_message["userId"] = human_id
                    ask_message["productId"] = product.productId
                    ask_message["productSignId"] = product_sign_id
                    ControlCenter.phoneCenter.send_msg2phone(human_id, "1", ask_message)
                product_status["userStatus"] = user_status
                ControlCenter.notSureProduct[product_sign_id] = product_status
        return result

    @staticmethod
    def send_weight_product_msg(msg, opt):
        weight = msg[0] << 8 | msg[1]
        result, product = ControlCenter.aSys.ask(ControlCenter.rackActor, WeightProduct(weight, opt))
        print("WeightProduct", product, weight)
        if result == "success":
            # TODO 根据商品位置找到对应位置的人
            # print ControlCenter.coreActor.userList, ControlCenter.coreActor.userCount
            user_list, user_count = ControlCenter.aSys.ask(ControlCenter.coreActor,
                                                           FindUser(product.rackId, int(time.time())))
            if user_count == 1:
                human_id = user_list[0]
                human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(human_id))
                ControlCenter.aSys.ask(human, HumanTakeProduct(product, opt))
                ControlCenter.phoneCenter.send_msg2phone(human_id, "2")
            else:
                product_sign_id = get_next_random_id()
                product_status = dict()
                product_status["product"] = product
                user_status = dict()
                for user_ids in range(user_count):
                    human_id = user_list[user_ids]
                    user_status[human_id] = 2
                    ask_message = dict()
                    ask_message["userId"] = human_id
                    ask_message["productId"] = product.productId
                    ask_message["productSignId"] = product_sign_id
                    ControlCenter.phoneCenter.send_msg2phone(human_id, "1", ask_message)
                product_status["userStatus"] = user_status
                ControlCenter.notSureProduct[product_sign_id] = product_status
        return result

    @staticmethod
    def send_human_loc(user_id, user_loc, user_loc_time):
        ControlCenter.aSys.tell(ControlCenter.coreActor, UserLoc(user_id, user_loc_time, user_loc, device="app"))

    @staticmethod
    def init_rack():
        ControlCenter.aSys.tell(ControlCenter.rackActor, "init")

    @staticmethod
    def human_in_shop(human_id, in_time, loc):
        human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(human_id))
        ControlCenter.aSys.tell(human, HumanCome(human_id, in_time, loc))

    @staticmethod
    def human_out_shop(human_id, out_time):
        human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(human_id))
        ControlCenter.aSys.tell(human, HumanOut(human_id, out_time))

    @staticmethod
    def get_human_cart(human_id):
        human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(human_id))
        result = ControlCenter.aSys.ask(human, HumanOpt(human_id, "cart"))
        if result is None:
            return "[]"
        else:
            return result

    @staticmethod
    def send_human_rssi(human_id, rssis, rssi_time):
        human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(human_id))
        ControlCenter.aSys.tell(human, HumanRssis(human_id=human_id, rssis=rssis, rssi_time=rssi_time))

    @staticmethod
    def train_rssis(train_id, rssis):
        ControlCenter.aSys.tell(ControlCenter.coreActor, TrainRssis(train_id, rssis))

    @staticmethod
    def set_phone_center(phone_center):
        if ControlCenter.phoneCenter is None:
            print("set phone center ... ")
            ControlCenter.phoneCenter = phone_center

    @staticmethod
    def update_product_info(user_id, product_id, product_sign_id, user_status_code):
        print(product_id)
        if product_sign_id in ControlCenter.notSureProduct:
            finish_feedback = False
            has_know = False
            product_info = ControlCenter.notSureProduct[product_sign_id]
            product = product_info["product"]
            user_status = product_info["userStatus"]
            if user_id in user_status:
                user_status[user_id] = user_status_code

            for humanId, user_code in user_status.items():
                if user_code == 2:
                    finish_feedback = False
                    break
                if user_code == 0:
                    has_know = True
                    finish_feedback = True
                    break

            if user_status_code == 0:
                human = ControlCenter.aSys.createActor(HumanActor, globalName="human-{}".format(user_id))
                ControlCenter.aSys.tell(human, HumanTakeProduct(product, "02"))
                ControlCenter.phoneCenter.send_msg2phone(user_id, "2")
                has_know = True

            if finish_feedback and not has_know:
                # TODO tell the market maneger
                pass

    @staticmethod
    def test_send():
        mess = dict()
        mess["productId"] = "12334456"
        mess["productSignId"] = "120000056"
        # ControlCenter.phoneCenter.send_msg2phone("0864502020459038", "2", "333")
        ControlCenter.phoneCenter.send_msg2phone("0864502020459038","1", mess)
