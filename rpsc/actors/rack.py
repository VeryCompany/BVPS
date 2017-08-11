# -*- coding: utf-8 -*-
from thespian.actors import ActorTypeDispatcher
from rpsc.controls import rackController
from rpsc.models import RackModel, ProductModel
import rpsc.config as rack_config
import datetime


class RackActor(ActorTypeDispatcher):
    def __init__(self):
        super(RackActor, self).__init__()

    def receiveMsg_LocProduct(self, message, sender):
        rack_id = message.rackId
        loc = message.loc
        opt = message.opt
        result = "error"
        product_real = None
        if opt == "01":
            if not rackController.get_rack(rack_id, loc):
                product = None
                for prod in rack_config.productList:
                    if "loc" in prod and prod["loc"] == loc:
                        product = ProductModel(prod["productId"], prod["productName"], product_loc=prod["loc"],
                                               price=prod["price"])
                        break
                if product is not None:
                    result = rackController.add_product(rack_id, product)
                    product_real = product
                    print(datetime.datetime.now(), "产品 ->", product, " 被放回!")
            else:
                result = "error"
        elif opt == "02":
            result, take_product = rackController.remove_loc_product(rack_id, loc)
            if take_product is not None:
                print(datetime.datetime.now(), "产品 ->", take_product, " 被拿走!")
                product_real = take_product
                # self.createActor()
        self.send(sender, (result, product_real))

    def receiveMsg_WeightProduct(self, message, sender):
        rack_id = message.rackId
        weight = message.weight
        opt = message.opt
        result = "error"
        product_real = None
        if opt == "01":
            product = None
            for prod in rack_config.productList:
                if "weight" in prod and prod["weight"] == weight:
                    product = ProductModel(prod["productId"], prod["productName"], weight=prod["weight"],
                                           price=prod["price"])
                    break
            if product is not None:
                result = rackController.add_product(rack_id, product)
                product_real = product
                print(datetime.datetime.now(), "产品 ->", product, " 被放回!")
        elif opt == "02":
            result, take_product = rackController.remove_weight_product(rack_id, weight)
            if take_product is not None:
                print(datetime.datetime.now(), "产品 ->", take_product, " 被拿走!")
                product_real = take_product
        self.send(sender, (result, product_real))

    def receiveMsg_str(self, message, sender):
        if message == "init":
            print(datetime.datetime.now(), "... 初始化货架 ...")
            for rack in rack_config.rackList:
                rack = RackModel(rack["id"], list(), rack_loc=rack["loc"])
                rackController.add_rack(rack)
            for prod in rack_config.productList:
                product = None
                if "loc" in prod:
                    product = ProductModel(prod["productId"], prod["productName"], product_loc=prod["loc"],
                                           price=prod["price"])
                elif "weight" in prod:
                    product = ProductModel(prod["productId"], prod["productName"], weight=prod["weight"],
                                           price=prod["price"])
                if product is not None:
                    rackController.add_product(prod["rackId"], product)
            print(rackController.racks, sender)


class RackProduct():
    def __init__(self, rack_id, opt):
        self.rackId = rack_id
        self.opt = opt


class LocProduct(RackProduct):
    def __init__(self, loc, opt):
        RackProduct.__init__(self, "1", opt)
        self.loc = loc


class WeightProduct(RackProduct):
    def __init__(self, weight, opt):
        RackProduct.__init__(self, "2", opt)
        self.weight = weight
