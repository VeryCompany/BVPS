# -*- coding: utf-8 -*-
from thespian.actors import ActorTypeDispatcher
from rpsc.controls import rackController
from rpsc.models import RackModel, ProductModel
from rpsc.config import RackConfig
import datetime

class RackActor(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(RackActor, self).__init__(*args, **kw)

    def receiveMsg_LocProduct(self, message, sender):
        rackId = message.rackId
        loc = message.loc
        opt = message.opt
        result = "error"
        productReal = None
        if opt == "01":
            if not rackController.getRack(rackId, loc):
                product = None
                for prod in RackConfig.productList:
                    if prod.has_key("loc") and prod["loc"] == loc:
                        product = ProductModel(prod["productId"], prod["productName"], productLoc=prod["loc"], price=prod["price"])
                        break
                if product is not None:
                    result = rackController.addProduct(rackId, product)
                    productReal = product
                    print datetime.datetime.now(), "产品 ->", product, " 被放回!"
            else:
                result = "error"
        elif opt == "02":
            result, takeProduct = rackController.removeLocProduct(rackId, loc)
            if takeProduct is not None:
                print datetime.datetime.now(), "产品 ->", takeProduct, " 被拿走!"
                productReal = takeProduct
                # self.createActor()
        self.send(sender, (result, productReal))

    def receiveMsg_WeightProduct(self, message, sender):
        rackId = message.rackId
        weight = message.weight
        opt = message.opt
        result = "error"
        productReal = None
        if opt == "01":
            product = None
            for prod in RackConfig.productList:
                if prod.has_key("weight") and prod["weight"] == weight:
                    product = ProductModel(prod["productId"], prod["productName"], weight=prod["weight"], price=prod["price"])
                    break
            if product is not None:
                result = rackController.addProduct(rackId, product)
                productReal = product
                print datetime.datetime.now(), "产品 ->", product, " 被放回!"
        elif opt == "02":
            result, takeProduct = rackController.removeWeightProduct(rackId, weight)
            if takeProduct is not None:
                print datetime.datetime.now(), "产品 ->", takeProduct, " 被拿走!"
                productReal = takeProduct
        self.send(sender, (result, productReal))

    def receiveMsg_str(self, message, sender):
        if message == "init":
            print datetime.datetime.now(), "... 初始化货架 ..."
            for rack in RackConfig.rackList:
                rack = RackModel(rack["id"], [], rackLoc=rack["loc"])
                rackController.addRack(rack)
            for prod in RackConfig.productList:
                product = None
                if prod.has_key("loc"):
                    product = ProductModel(prod["productId"], prod["productName"], productLoc=prod["loc"], price=prod["price"])
                elif prod.has_key("weight"):
                    product = ProductModel(prod["productId"], prod["productName"], weight=prod["weight"], price=prod["price"])
                if product is not None:
                    rackController.addProduct(prod["rackId"], product)
            print rackController.racks

class RackProduct():

    def __init__(self, rackid, opt):
        self.rackId = rackid
        self.opt = opt

class LocProduct(RackProduct):

    def __init__(self, loc, opt):
        RackProduct.__init__(self, "1", opt)
        self.loc=loc

class WeightProduct(RackProduct):

    def __init__(self, weight, opt):
        RackProduct.__init__(self, "2", opt)
        self.weight = weight
