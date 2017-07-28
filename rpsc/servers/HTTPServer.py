# -*- coding: utf-8 -*-
from flask import *
from datetime import datetime
from rpsc.controls import ControlCenter

app = Flask(__name__)

@app.errorhandler(404)
def pageNotFound(error):
    return get_template_attribute("error.html", 'error')("404")

@app.errorhandler(500)
def pageNotFound(error):
    return get_template_attribute("error.html", 'error')("500")

@app.route("/comein/<userId>")
def userComeIn(userId):
    ControlCenter.humanInShop(str(userId), str(datetime.now()), [])
    return str(userId) + " 进店"

@app.route("/usercart/<userId>")
def getUserCart(userId):
    result = ControlCenter.getHumanCart(str(userId))

    # print "result -> :", result
    # return json.dumps(result, ensure_ascii=False)
    return Response(result,mimetype='application/json;charset=utf-8')

@app.route("/comeout/<userId>")
def userComeOut(userId):
    ControlCenter.humanOutShop(userId, str(datetime.now()))
    return str(userId) + " 出店"

@app.route("/user/rssis",methods=["POST"])
def userRssis():
    userId = None
    rssis = None
    rssitime = None

    usermsg = request.values
    if usermsg.has_key("userId"):
        userId = usermsg["userId"]
    if usermsg.has_key("time"):
        rssitime = int(usermsg["time"]) /1000
    if usermsg.has_key("rssis"):
        rssis = usermsg["rssis"]

    print userId, rssis, rssitime

    return Response("{\"message\": \"success\"}",mimetype='application/json;charset=utf-8')

@app.route("/user/userloc",methods=["POST"])
def userLoc():
    # print "userId->:",request.form['userId']
    userId = None
    userloc = None
    userloctime = None

    usermsg = request.json
    print usermsg

    if usermsg.has_key("userloc"):
        userloc = usermsg["userloc"]
    if usermsg.has_key("userId"):
        userId = usermsg["userId"]
    if usermsg.has_key("userloctime"):
        userloctime = usermsg["userloctime"]
        print userloctime

    if userId is not None and userloc is not None:
        ControlCenter.sendHumanLoc(userId, userloc, str(userloctime))

    # print request.values["userId"]
    #userloc= str(request.form['userloc'])
    #print "userloc->", userloc, type(userloc)
    # print "urlPath->:",request.args.get("urlpath","---")
    return Response("{\"message\": \"success\"}",mimetype='application/json;charset=utf-8')

def startHTTP(asys):
    ControlCenter.setAsys(asys)
    print "Http Server Start ..."
    global app

    app.run(host='',port='8080',debug=True,use_reloader=False)
