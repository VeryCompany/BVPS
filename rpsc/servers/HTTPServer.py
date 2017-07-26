# -*- coding: utf-8 -*-
from flask import *
from datetime import datetime
from controls import ControlCenter

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

@app.route("/user/userloc",methods=["POST"])
def userLoc():
    # print "userId->:",request.form['userId']
    print request.json
    # print request.values["userId"]
    #userloc= str(request.form['userloc'])
    #print "userloc->", userloc, type(userloc)
    print "urlPath->:",request.args.get("urlpath","---")
    return Response("{\"message\": \"success\"}",mimetype='application/json;charset=utf-8')

def startHTTP():
    print "Http Server Start ..."
    app.run(host='',port='8080')