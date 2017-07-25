# -*- coding: utf-8 -*-
from models import RackModel

racks = dict()

def addRack(rack=None):
    global racks

    if rack == None: return;
    if rack.rackId in racks: return;

    racks[rack.rackId] = rack

def addProduct(rackId, product):
    global racks

    if not (rackId in racks): racks[rackId] = RackModel(rackId);
    msg = "error"
    try:
        product.setProduct2Rack(rackId)
        racks[rackId].addProductList(product)
        msg = "success"
    except Exception as addProductErr:
        print addProductErr
        msg = "error"
    finally:
        #print racks[rackId]
        return msg

def removeLocProduct(rackId, productLoc):
    global racks
    if not (rackId in racks): return ;

    product = None
    msg = "error"
    try:
        for pro in racks[rackId].productList:
            if pro.productLoc == productLoc:
                product = pro
                racks[rackId].productList.remove(pro)
                break
        msg = "success"
    except Exception as removeProductErr:
        print removeProductErr
        msg = "error"
    finally:
        #print racks[rackId]
        return msg, product

def removeWeightProduct(rackId, productWeight):
    global racks
    if not (rackId in racks): return ;

    product = None
    msg = "error"
    try:
        for pro in racks[rackId].productList:
            if pro.weight == productWeight:
                product = pro
                racks[rackId].productList.remove(pro)
                break
        msg = "success"
    except Exception as removeProductErr:
        print removeProductErr
        msg = "error"
    finally:
        #print racks[rackId]
        return msg, product

def getRack(rackid, loc):
    if not (rackid in racks): return False;
    rack = racks[rackid]
    print rack.getProductSize()

    if rack.getProductSize() > 0:
        product = None
        for prod in rack.productList:
            if prod.productLoc == loc:
                print "位置", loc, "已经有产品 ->:", prod
                product = prod
                break
        if product is None:
            return False
        else:
            return True
    else:
        return False
