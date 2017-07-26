# -*- coding: utf-8 -*-
from thespian.actors import ActorTypeDispatcher
from models import HumanModel, ShoppingCartProductModel
import json

class HumanActor(ActorTypeDispatcher):

    def __init__(self, *args, **kw):
        super(HumanActor, self).__init__(*args, **kw)
        self.human = None

    def receiveMsg_HumanTakeProduct(self, message, sender):
        product = message.product
        opt = message.opt
        if opt == "02":
            if self.human is not None:
                self.human.shoppingCart.addProduct(product)
            else:
                print "用户已经离开"
        elif opt == "01":
            self.human.shoppingCart.removeProduct(product.productId)
        print self.human, self.human.humanId, product

    def receiveMsg_HumanLoc(self, message, sender):
        pass

    def receiveMsg_HumanOpt(self, message, sender):
        humantype = message.humantype
        humanId = message.humanId
        if humantype == 'cart':
            if self.human is not None:
                shopCart = self.human.shoppingCart
                print shopCart

                self.send(sender, str(shopCart))
            else:
                self.send(sender, None)

    def receiveMsg_HumanOut(self, message, sender):
        humanId = message.humanId
        time = message.time
        if self.human is not None:
            print "用户:", humanId, "在[", time, "]离开"
            self.human = None
        else:
            print "用户:", humanId, "已经离开"

    def receiveMsg_HumanCome(self, message, sender):
        humanId = message.humanId
        time = message.time
        loc = message.loc
        if self.human is None:
            self.human= HumanModel(humanId, loc, ShoppingCartProductModel(0))
            self.human.setComeTime(time)
            print "用户:", humanId, "在[", time, "]进入超市", type(humanId)
        else:
            print "存在用户:", humanId

class HumanBase():

    def __init__(self, humanId):
        self.humanId = humanId

class HumanCome(HumanBase):

    def __init__(self, humanId, time, loc):
        HumanBase.__init__(self, humanId)
        self.time = time
        self.loc = loc

class HumanOut(HumanBase):
    def __init__(self, humanId, time):
        HumanBase.__init__(self, humanId)
        self.time = time

class HumanTakeProduct():

    def __init__(self, product, opt):
        self.product=product
        self.opt=opt

class HumanOpt(HumanBase):
    def __init__(self, humanId, humantype):
        HumanBase.__init__(self, humanId)
        self.humantype = humantype