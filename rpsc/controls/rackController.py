# -*- coding: utf-8 -*-
from rpsc.models import RackModel

racks = dict()


def add_rack(rack=None):
    global racks

    if rack is None:
        return
    if rack.rackId in racks:
        return
    racks[rack.rackId] = rack


def add_product(rack_id, product):
    global racks

    if not (rack_id in racks):
        racks[rack_id] = RackModel(rack_id)
    msg = "error"
    try:
        product.set_product2rack(rack_id)
        racks[rack_id].add_product_list(product)
        msg = "success"
    except Exception as addProductErr:
        print(addProductErr)
        msg = "error"
    finally:
        # print racks[rack_id]
        return msg


def remove_loc_product(rack_id, product_loc):
    global racks
    if not (rack_id in racks):
        return

    product = None
    msg = "error"
    try:
        for pro in racks[rack_id].productList:
            if pro.productLoc == product_loc:
                product = pro
                racks[rack_id].productList.remove(pro)
                break
        if product is None:
            msg = "error"
        else:
            msg = "success"
    except Exception as removeProductErr:
        print(removeProductErr)
        msg = "error"
    finally:
        # print racks[rackId]
        return msg, product


def remove_weight_product(rack_id, product_weight):
    global racks
    if not (rack_id in racks):
        return

    product = None
    msg = "error"
    try:
        for pro in racks[rack_id].productList:
            if pro.weight == product_weight:
                product = pro
                racks[rack_id].productList.remove(pro)
                break
        msg = "success"
    except Exception as removeProductErr:
        print(removeProductErr)
        msg = "error"
    finally:
        # print(racks[rack_id])
        return msg, product


def get_rack(rack_id, loc):
    if not (rack_id in racks):
        return False
    rack = racks[rack_id]
    print(rack.get_product_size())

    if rack.get_product_size() > 0:
        product = None
        for prod in rack.productList:
            if prod.productLoc == loc:
                print("位置", loc, "已经有产品 ->:", prod)
                product = prod
                break
        if product is None:
            return False
        else:
            return True
    else:
        return False
