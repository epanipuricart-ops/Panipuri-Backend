from flask import Flask,session,send_from_directory
from flask import request,redirect,url_for
from flask_pymongo import PyMongo
from flask import jsonify
from flask_cors import CORS , cross_origin
import time
import os
from datetime import datetime
import config.config as cfg
from modules import *



app = Flask(__name__, static_url_path= '')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://localhost:27017/panipuriKartz"
mongo = PyMongo(app)



@app.route('/upload', methods=['GET','POST'])
@cross_origin()
def upload():
    if request.method == "POST":
        timestamp = int(round(time.time() *1000))
        data = request.json["values"]
        uid = request.json["deviceId"]
        print(data)
        for ele in data:
            ele["date"] = timestamp
        existing_data = mongo.db.stats.find_one({"uid": uid})['data']
        new_data = existing_data + data
        mongo.db.stats.update_one({'uid': uid},{'$set':{"data": new_data}})
        concerned_names = []
        for ele in data:
            if ele['status'] == 1:
                concerned_names.append(ele["name"])
        arr = mongo.db.counter.find_one({"uid": uid})['data']
        for item in arr:
            if item["name"] in concerned_names:
                if item["count"][-1]["date"] == datetime.now().strftime("%m-%d-%Y"):
                    item["count"][-1]["dailyCount"] += 1 
                else:
                    d = {}
                    d["date"] = datetime.now().strftime("%m-%d-%Y") 
                    d["dailyCount"] = 1
                    item["count"].append(d)

        mongo.db.counter.update_one({'uid': uid},{'$set':{"data": arr}})                  
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization error"}), 403

@app.route('/uploadLevel', methods=['GET','POST'])
@cross_origin()
def uploadLevel():
    if request.method == "POST":
        timestamp = int(round(time.time() *1000))
        data = request.json["values"]
        uid = request.json["deviceId"]
        for ele in data:
            ele["date"] = timestamp
        existing_data = mongo.db.levels.find_one({"uid": uid})['data']
        new_data = existing_data + data
        mongo.db.levels.update_one({'uid': uid},{'$set':{"data": new_data}})                
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization error"}), 403


#route to register device
@app.route("/registerDevice", methods=['GET','POST'])
@cross_origin()
def registerDevice():
    if request.method == "POST":
        devices = mongo.db.devices
        uid = request.json["uid"]
        address = request.json["address"]
        owner = request.json["owner"]
        type_of_device = request.json["type"]
        activeDate = datetime.now().strftime("%m-%d-%Y")
        ownerType = request.json["ownerType"]
        post = {"uid": uid, "ownerType":ownerType,"fArray":[],"address": address, "owner": owner,"activeDate": activeDate, "type": type_of_device, "settings": "15","activeState": 0, "deviceState": 0, "mode": 0}
        devices.insert_one(post)
        p = {"uid": uid, "data": []}
        mongo.db.stats.insert_one(p)
        q = {"uid": uid, "data": []}
        mongo.db.levels.insert_one(q)
        arr = create_dict(type_of_device)
        for ele in arr:
            ele["count"] = [{"date": datetime.now().strftime("%m-%d-%Y"),"dailyCount": 0}]
        val = {"uid": uid, "data": arr}
        mongo.db.counter.insert_one(val)
        return jsonify({"message": "Registered Successfully"})
    else:
        return jsonify({"message": "Authorization Error"}), 403

#route to register device
@app.route("/addFranchise", methods=['GET','POST'])
@cross_origin()
def addFranchise():
    if request.method == "POST":
        uid = request.json["uid"]
        arr = request.json["values"]
        mongo.db.devices.update_one({"uid": uid},{"$addToSet": {"fArray":{"$each":arr}}})
        return jsonify({"message": "Updated Successfully"})
    else:
        return jsonify({"message": "Authorization Error"}), 403

#route to register device
@app.route("/verifyToken", methods=['GET','POST'])
@cross_origin()
def verifyToken():
    if request.method == "POST":
        token = request.headers['Authorization']
        ele = mongo.db.users.find_one({"token": token})
        if ele:
            return jsonify({"message": "VALID"})
        else:
            message, statusCode = checkValidity(token)
            if statusCode == 200:
                users = mongo.db.users
                post = {"uid":message['uid'],"token": token}
                users.insert_one(post)
                return jsonify({"message": message['status']})
            else:
                return jsonify({"message": message['status']}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403

@app.route("/deleteToken", methods=['GET','POST'])
@cross_origin()
def deleteToken():
    if request.method == "POST":
        token = request.headers['Authorizations']
        ele = mongo.db.users.find_one({"token":token})
        if ele:
            mongo.db.users.delete_one({"token": token})
            return jsonify({"message": "SUCCESS"})
        else:
            return jsonify({"message": "No record found"}), 
@app.route("/updateProfile", methods=['GET','POST'])
@cross_origin()
def updateProfile():
    if request.method == "POST":
        uid = request.json['uid']
        device = mongo.db.devices.find_one({"uid":uid})
        if device:
            address = request.json["address"]
            owner = request.json["owner"]
            try:
                mongo.db.devices.update_one({"uid": uid},{'$set':{"address": address, "owner": owner}})
            except:
                return jsonify({"message: Some Error Occured"}), 500
            return jsonify({"message": "Successfully Updated"})
        else:
            return jsonify({"message": "No such device found"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


#route to switch on/off
@app.route("/toggle", methods=['GET','POST'])
@cross_origin()
def toggle():
    if request.method == "POST":
        token = request.headers['Authorization']
        status,uid = authenticate(token)
        if status:
            devices = mongo.db.devices
            state = request.json["state"]
            devices.update_one({"uid":uid},{'$set':{"activeState": state}})
            response = devices.find_one({"uid": uid})
            if (response["activeState"] == 1) and (response["deviceState"] == 1):
                return jsonify({"message": "Device Started", "status": 1})
            elif (response["activeState"] == 0) and (response["deviceState"] == 0):
                return jsonify({"message": "Device Stopped", "status": 0})
            elif (response["activeState"] == 1) and (response["deviceState"] == 0):
                return jsonify({"message": "Start Request sent, waiting for device to respond", "status": 2})
            else:
                return jsonify({"message": "Stop Request sent, waiting for device to respond", "status": 3})

        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403

#route to toggle
@app.route("/switchMode", methods=['GET','POST'])
@cross_origin()
def switchmode():
    if request.method == "POST":
        token = request.headers['Authorization']
        status,uid = authenticate(token)
        if status:
            devices = mongo.db.devices
            mode = request.json["mode"]
            try:
                devices.update_one({"uid":uid},{'$set':{"mode": mode}})
                if mode == 0:
                    return jsonify({"mode": 0,"message": "Device set to operation mode"})
                else:
                    return jsonify({"mode": 1, "message": "Device set to cleaning mode"})
            except:
                return jsonify({"mode": 2, "message": "Some error occured"})
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403

@app.route("/postDeviceStatus", methods=['GET','POST'])
@cross_origin()
def postDeviceStatus():
    if request.method == "POST":
        uid = request.json["uid"]
        deviceStatus = request.json["status"]
        try:
            mongo.db.devices.update_one({"uid": uid},{'$set':{"deviceState": deviceStatus}})
        except:
            print("Error!")
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403

@app.route("/postPowerOut", methods=['GET','POST'])
@cross_origin()
def postPowerOut():
    if request.method == "POST":
        uid = request.json["uid"]
        mongo.db.devices.update({"uid": uid},{'$set':{"deviceState": 0, "activeState": 0}})
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403



@app.route("/postLogs", methods=['GET','POST'])
@cross_origin()
def postLogs():
    if request.method == "POST":
        uid = request.json["uid"]
        log_type = request.json["logType"]
        d = {}
        d['logType'] = log_type
        d['date'] = int(round(time.time() *1000))
        response = mongo.db.logs.find_one({"uid": uid})
        if response:
            response["data"].append(d)
            mongo.db.devices.update_one({"uid": uid},{'$set':{"data": response["data"]}})
        else:
            post = {"uid": uid, "data": [d]}
            mongo.db.logs.insert_one(post)
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403

#route to update settings
@app.route("/updateSettings", methods=['GET','POST'])
@cross_origin()
def updateSettings():
    if request.method == "POST":
        token = request.headers['Authorization']
        status,uid = authenticate(token)
        if status:
            devices = mongo.db.devices
            setting = request.json['setting']
            devices.update_one({"uid":uid},{'$set':{"settings": setting}})
            return jsonify({"message": "SUCCESS"})
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


#route to fetch device data
@app.route("/getDeviceData", methods=['GET','POST'])
@cross_origin()
def getDeviceData():
    token = request.headers['Authorization']
    status,uid = authenticate(token)
    if status:
        data = mongo.db.devices.find_one({"uid": uid})
        if data:
            d = {}
            if (data["activeState"] == 1) and (data["deviceState"] == 1):
                d["status"] = 1
            elif (data["activeState"] == 0) and (data["deviceState"] == 0):
                d["status"] = 0
            elif (data["activeState"] == 1) and (data["deviceState"] == 0):
                d["status"] = 2
            elif (data["activeState"] == 0) and (data["deviceState"] == 1):
                d["status"] = 3
            else:
                d["status"] = 4
            d["uid"] = data["uid"]
            d["date"] = data["activeDate"]
            d["address"] = data["address"]
            d["type"] = data["type"]
            d["owner"] = data["owner"]
            d["settings"] = data["settings"]
            d["mode"] = data["mode"]
            return jsonify(d)
        else:
            return jsonify({"message": "Invalid Device Id"}), 403
    else:
        return jsonify({"message": "Authentication error"}), 401

#route to fetch device data
@app.route("/getSwitchStatus", methods=['GET','POST'])
@cross_origin()
def getSwitchStatus():
    uid = request.args.get("uid")
    data = mongo.db.devices.find_one({"uid": uid})
    if data:
        d = {}
        d['activeState'] = data['activeState']
        d['settings'] = data['settings']
        d['mode'] = data['mode']
        return jsonify(d)
    else:
        return jsonify({"message": "Invalid Device Id"}), 403

@app.route("/getStats", methods=['GET','POST'])
@cross_origin()
def getStats():
    token = request.headers['Authorization']
    status,uid = authenticate(token)
    if status:
        available,data = sort(uid)
        if available:
            return jsonify({"result": data})
        else:
            return jsonify({"message": "No record found"}), 403
    else:
        return jsonify({"message":"Authentication Error"}), 401

@app.route("/getToday", methods=['GET','POST'])
@cross_origin()
def getToday():
    token = request.headers['Authorization']
    status,uid = authenticate(token)
    if status:
        data = mongo.db.stats.find_one({"uid":uid})['data']
        out = []
        for ele in data:
            if datetime.fromtimestamp(ele['date']/1000.0).strftime("%m-%d-%Y") == datetime.now().strftime("%m-%d-%Y"):
                out.append(ele)
        n1=0
        n2=0
        n3=0
        for item in out:
            if item['name'] == 'n1' and item['status'] == 1:
                n1 += 1
            elif item['name'] == 'n2' and item['status'] == 1:
                n2 += 1
            elif item['name'] == 'n3' and item['status'] == 1:
                n3 += 1
        return jsonify({"n1":n1, "n2": n2, "n3":n3})

@app.route("/getLevel", methods=['GET','POST'])
@cross_origin()
def getLevel():
    token = request.headers['Authorization']
    status,uid = authenticate(token)
    print(uid)
    if status:
        available,data = sort_level(uid)
        if available:
            return jsonify({"result": data})
        else:
            return jsonify({"message": "No record found"}), 403
    else:
        return jsonify({"message":"Authentication Error"}), 401

@app.route("/getCount", methods=['GET','POST'])
@cross_origin()
def getCount():
    token = request.headers['Authorization']
    status,uid = authenticate(token)
    if status:
        response = mongo.db.counter.find_one({"uid": uid})
        if response:
            arr = []
            for ele in response['data']:
                c = {}
                c['name'] = ele['name']
                if len(ele['count']) >= 20:
                    c['count'] = ele['count'][-20:]
                else:
                    c['count'] = ele['count']
                arr.append(c)

            return jsonify({"result": arr})
        else:
            return jsonify({"message": "No record found"}), 403
    else:
        return jsonify({"message": "Authentication Error"}), 401

@app.route("/getCountByDate", methods=['GET','POST'])
@cross_origin()
def getCountByDate():
    if request.method == 'POST':
        start = request.json['start']
        end = request.json['end']
        s =   int(datetime.strptime(start,"%m-%d-%Y").timestamp()*1000)
        e = int(datetime.strptime(end,"%m-%d-%Y").timestamp()*1000)
        token = request.headers['Authorization']
        status,uid = authenticate(token)
        if status:
            response = mongo.db.counter.find_one({"uid": uid})
            if response:
                arr = []
                if start == end:
                    for ele in response['data']:
                        c = {}
                        c['name'] = ele['name']
                        c['count'] = []
                        for item in ele['count']:
                            if item['date'] == start:
                                c['count'] = [{"date": start, "dailyCount": item["dailyCount"]}]
                                break
                        arr.append(c)
                    return jsonify({"result": arr})
                else:
                    for ele in response['data']:
                        mini_arr = []
                        c = {}
                        c['name'] = ele['name']
                        c['count'] = []
                        for item in ele['count']:
                            curr = int(datetime.strptime(item['date'],"%m-%d-%Y").timestamp()*1000)
                            if curr >= s and curr <= e:
                                mini_arr.append(item)
                        c['count'] = mini_arr
                        arr.append(c)
                    return jsonify({"result": arr})
            else:
                return jsonify({"message": "No record found"}), 403
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403
    

                
                        

if __name__ == "__main__":
    print("starting...")
    app.run(host= cfg.Flask['HOST'] , port=cfg.Flask['PORT'], threaded=cfg.Flask['THREADED'],debug=True)
    #app.run(debug=True)
