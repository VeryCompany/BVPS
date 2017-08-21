# -*- coding: utf-8 -*-
from flask import Flask, request, get_template_attribute, Response, json
from datetime import datetime
from rpsc.controls import ControlCenter
from rpsc.config.rackConfig import beaconList

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return get_template_attribute("error.html", 'error')("404")


@app.errorhandler(500)
def page_error(error):
    print(error)
    return get_template_attribute("error.html", 'error')("500")


@app.route('/comein/<user_id>')
def user_come_in(user_id):
    print("comein userId -> :", user_id)
    ControlCenter.human_in_shop(str(user_id), str(datetime.now()), [])
    return str(user_id) + " 进店"


@app.route('/usercart/<user_id>')
def get_user_cart(user_id):
    print("cart userId -> :", user_id)

    result = ControlCenter.get_human_cart(str(user_id))
    return Response(result, mimetype='application/json;charset=utf-8')
    # shopo_cart = []
    # product1 = {"product": {"productId": "1_1"}, "count": 1}
    # product2 = {"product": {"productId": "1_2"}, "count": 2}
    #
    # shopo_cart.append(product1)
    # shopo_cart.append(product2)
    # return Response(json.dumps(shopo_cart), mimetype='application/json;charset=utf-8')


@app.route('/comeout/<user_id>')
def user_come_out(user_id):
    print("comeout userId -> :", user_id)
    ControlCenter.human_out_shop(user_id, str(datetime.now()))
    return str(user_id) + " 出店"


@app.route('/<shop_id>/getBeaconDevices.json')
def get_beacon_devices(shop_id):
    print("shopId -> : ", shop_id)

    result_msg = dict()
    result_msg["beaconList"] = [0x5A02, 0x5783, 0x5920, 0x58C3, 0x5967]
    result_msg["beacons"] = {
        0x5A02: {"x": 30, "y": 30},
        0x5783: {"x": 30, "y": 420},
        0x5920: {"x": 600, "y": 30},
        0x58C3: {"x": 30, "y": 260},
        0x5967: {"x": 600, "y": 420}
    }
    result_msg["regions"] = [{"id": "COMFAST",
                              "uuid": "FDA50693-A4E2-4FB1-AFCF-C6EB07647825"}]
    return Response(json.dumps(result_msg), mimetype='application/json;charset=utf-8')


@app.route("/shop/locs", methods=["POST"])
def make_shop_loc():
    print("data->", request.data)
    print("form->", request.form)
    print("values->", request.values)
    print("json->", request.json)
    locs_msg = eval(request.data, {"x": "x", "y": "y", "map": "map"})
    loc_x = None
    loc_y = None
    rssis = None

    if "x" in locs_msg:
        loc_x = locs_msg["x"]
    if "y" in locs_msg:
        loc_y = locs_msg["y"]
    if "map" in locs_msg:
        rssis = locs_msg["map"]

    print(loc_x, loc_y, rssis, type(rssis))
    if rssis is not None:
        train_rssis = list()
        for beacon in beaconList:
            if str(beacon) in rssis:
                train_rssis.append(rssis[str(beacon)])
            else:
                train_rssis.append(-100)

        print(train_rssis)
        # ControlCenter.trainRssis(locx, locy, rssis)
    return "success"


@app.route('/user/rssis', methods=["POST"])
def user_rssis():
    user_id = None
    rssis = None
    rssi_time = None

    print(request.data)
    print(request.values)
    print(request.json)
    print(request.form)

    user_msg = request.values
    if "userId" in user_msg:
        user_id = user_msg["userId"]
    if "time" in user_msg:
        rssi_time = user_msg["time"]
    if "rssis" in user_msg:
        rssis = user_msg["rssis"]
        ControlCenter.send_human_rssi(user_id, rssis, rssi_time)
    print(user_id, rssis, rssi_time)

    # print request.data
    # locsmsg = eval(request.data, {"time": "time", "phoneonlynum": "phoneonlynum", "map": "map"})
    # rssitime = None
    # userId = None
    # rssis = None
    #
    # if locsmsg.has_key("time"):
    #     rssitime = locsmsg["time"]
    # if locsmsg.has_key("phoneonlynum"):
    #     userId = locsmsg["phoneonlynum"]
    # if locsmsg.has_key("map"):
    #     rssis = locsmsg["map"]
    #
    # if rssis is not None:
    #     userRssis = []
    #     for beacon in beaconList:
    #         if str(beacon) in rssis:
    #             userRssis.append(rssis[str(beacon)])
    #         else:
    #             userRssis.append(-100)
    #
    #     print userRssis
    #     if userId is not None and len(userRssis) > 4 and rssitime is not None:
    #         ControlCenter.sendHumanRssi(userId, userRssis, rssitime)

    return Response("{\"message\": \"success\"}", mimetype='application/json;charset=utf-8')


@app.route('/user/userloc', methods=["POST"])
def user_loc():
    user_id = None
    user_location = None
    user_loc_time = None

    user_msg = request.json
    print(user_msg)

    if "userloc" in user_msg:
        user_location = user_msg["userloc"]
    if "userId" in user_msg:
        user_id = user_msg["userId"]
    if "userloctime" in user_msg:
        user_loc_time = user_msg["userloctime"]

    if user_id is not None and user_location is not None:
        ControlCenter.send_human_loc(user_id, user_location, str(user_loc_time))

    return Response("{\"message\": \"success\"}", mimetype='application/json;charset=utf-8')


@app.route('/userfeedback/<user_id>', methods=["POST"])
def feedback_product_info(user_id):
    product_id = None
    product_sign_id = None
    user_status = None

    print("data->", request.data)
    print("form->", request.form)
    print("values->", request.values)
    print("json->", request.json)

    product_msg = request.values

    if "productId" in product_msg:
        product_id = product_msg["productId"]
    if "productSignId" in product_msg:
        product_sign_id = product_msg["productSignId"]
    if "userStatus" in product_msg:
        user_status = product_msg["userStatus"]

    if product_id is not None and product_sign_id is not None and user_status is not None:
        print(user_id, product_id, product_sign_id, user_status)
        ControlCenter.update_product_info(user_id, product_id, int(product_sign_id), int(user_status))
    return "success"


@app.route('/testsend')
def test_send():
    ControlCenter.test_send()
    return "success"


def start_http(asys):
    ControlCenter.set_asys(asys)
    print('Http Server Start ...')
    global app

    app.run(host='0.0.0.0', port='8080',threaded=True)
