# -*- coding: utf-8 -*-

from rpsc.actors.human import *
from rpsc.actors.rack import *
from rpsc.actors.core import *

class ControlCenter():

    asys = None
    rackactor = None
    coreActor = None

    @staticmethod
    def setAsys(asys):
        if ControlCenter.asys is None:
            ControlCenter.asys = asys
            ControlCenter.rackactor = ControlCenter.asys.createActor(RackActor)
            ControlCenter.coreActor = ControlCenter.asys.createActor(CoreActor,globalName="coreActor")
        else:
            print "init asys"

    @staticmethod
    def sendLocProductMsg(msg, opt):
        loc = [ord(msg[0]),ord(msg[1])]
        result, product = ControlCenter.asys.ask(ControlCenter.rackactor, LocProduct(loc, opt))
        if result == "success":
            # print ControlCenter.coreActor.userList, ControlCenter.coreActor.userCount
            userlist, usercont = ControlCenter.asys.ask(ControlCenter.coreActor, FindUser())
            # TODO 根据商品位置找到对应位置的人
            humanId = "00002"
            if usercont == 1:
                humanId = userlist[0]
            else:
                pass
            human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(humanId))
            ControlCenter.asys.ask(human, HumanTakeProduct(product, opt))
        return result

    @staticmethod
    def sendWeightProductMsg(msg, opt):
        weight = ord(msg[0])<<8|ord(msg[1])
        result, product = ControlCenter.asys.ask(ControlCenter.rackactor, WeightProduct(weight, opt))
        if result == "success":
            # TODO 根据商品位置找到对应位置的人
            # print ControlCenter.coreActor.userList, ControlCenter.coreActor.userCount
            userlist, usercont = ControlCenter.asys.ask(ControlCenter.coreActor, FindUser())
            humanId= "00001"
            if usercont == 1:
                humanId = userlist[0]
            else:
                pass
            human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(humanId))
            ControlCenter.asys.ask(human, HumanTakeProduct(product, opt))
        return result

    @staticmethod
    def sendHumanLoc(userId, userLoc, userloctime):
        ControlCenter.asys.tell(ControlCenter.coreActor, UserLoc(userId, userloctime, userLoc,device="app"))

    @staticmethod
    def initRack():
        ControlCenter.asys.tell(ControlCenter.rackactor, "init")

    @staticmethod
    def humanInShop(id, time, loc):
        human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(id))
        ControlCenter.asys.tell(human, HumanCome(id, time, loc))

    @staticmethod
    def humanOutShop(id, time):
        human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(id))
        ControlCenter.asys.tell(human, HumanOut(id, time))

    @staticmethod
    def getHumanCart(id):
        human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(id))
        result = ControlCenter.asys.ask(human, HumanOpt(id, "cart"))
        if result is None:
            return "[]"
        else:
            return result