# -*- coding: utf-8 -*-
from thespian.actors import ActorSystem
from actors.human import *
from actors.rack import *
import json

class ControlCenter():

    asys = ActorSystem()
    rackactor = asys.createActor(RackActor)

    @staticmethod
    def sendLocProductMsg(msg, opt):
        loc = [ord(msg[0]),ord(msg[1])]
        result, product = ControlCenter.asys.ask(ControlCenter.rackactor, LocProduct(loc, opt))
        if result == "success":
            # TODO 根据商品位置找到对应位置的人
            humanId = "00002"
            human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(humanId))
            ControlCenter.asys.ask(human, HumanTakeProduct(product, opt))
        return result

    @staticmethod
    def sendWeightProductMsg(msg, opt):
        weight = ord(msg[0])<<8|ord(msg[1])
        result, product = ControlCenter.asys.ask(ControlCenter.rackactor, WeightProduct(weight, opt))
        if result == "success":
            # TODO 根据商品位置找到对应位置的人
            humanId= "00001"
            human = ControlCenter.asys.createActor(HumanActor, globalName="human-{}".format(humanId))
            ControlCenter.asys.ask(human, HumanTakeProduct(product, opt))
        return result

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