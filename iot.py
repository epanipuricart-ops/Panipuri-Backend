from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
import time
import datetime
import os
import binascii
import jwt
from config import config as cfg
from modules import *
from datetime import datetime, timedelta, date
from flask_apscheduler import APScheduler
import requests

app = Flask(__name__, static_url_path="")

CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["MONGO_URI"] = "mongodb://localhost:27017/panipuriKartz"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

global_key = "ueQ4sZ"
payment_url = "http://15.207.147.88:8083/"
ZOHO_TOKEN = {"access_token": "", "timestamp": time.time()}


def generate_custom_id():
    return (
        binascii.b2a_hex(os.urandom(4)).decode()
        + hex(int(time.time() * 10**5) % 10**12)[2:]
    )


def refresh_zoho_access_token(force=False):
    if (
        force
        or ZOHO_TOKEN["access_token"] == ""
        or time.time() - ZOHO_TOKEN["timestamp"] >= 1800
    ):
        refresh_token_url = "https://accounts.zoho.in/oauth/v2/token"
        response = requests.post(
            refresh_token_url,
            data={
                "refresh_token": cfg.ZohoConfig["refresh_token"],
                "client_id": cfg.ZohoConfig["client_id"],
                "client_secret": cfg.ZohoConfig["client_secret"],
                "grant_type": "refresh_token",
            },
        ).json()
        ZOHO_TOKEN["access_token"] = response["access_token"]
        ZOHO_TOKEN["timestamp"] = time.time()


def create_zoho_retainer_invoice(customer_id, item_name, price):
    response = requests.post(
        "https://books.zoho.in/api/v3/retainerinvoices",
        params={"organization_id": cfg.ZohoConfig.get("organization_id")},
        headers={"Authorization": "Zoho-oauthtoken " +
                 ZOHO_TOKEN["access_token"]},
        json={
            "customer_id": customer_id,
            "date": date.today().strftime("%Y-%m-%d"),
            "line_items": [{"description": item_name, "rate": price}],
        },
    ).json()
    if response.get("code") == 0:
        print(response)
        return response.get("retainerinvoice").get("retainerinvoice_id")


@scheduler.task("cron", id="zoho_token_refresh", minute="*/30")
def zoho_token_refresh():
    refresh_zoho_access_token(force=True)


@app.route("/wizard/login", methods=["POST"])
@cross_origin()
def wizardLogin():
    email = request.json["email"]
    data = list(mongo.db.device_ids.find({"email": email}))
    alias_data = list(mongo.db.alias_data.find({"alias_email": email}))
    if len(data) != 0:
        out = []
        for ele in data:
            out.append(ele["device_id"])
        try:
            name = mongo.db.clients.find_one({"email": email})["firstName"]
            res = {"email": email, "name": name,
                   "devices": out, "role": "franchisee"}
            return jsonify(res)
        except:
            return jsonify({"message": "Some error occurred"}), 500
    elif len(alias_data) != 0:
        out = []
        for ele in alias_data:
            out.append(ele["device_id"])
        data = {
            "email": email,
            "name": alias_data[0]["alias_name"],
            "devices": out,
            "role": "alias",
        }
        return jsonify(data)
    else:
        return jsonify({"message": "Unauthorized Access"}), 403


@app.route("/upload", methods=["GET", "POST"])
@cross_origin()
def upload():
    if request.method == "POST":
        timestamp = int(round(time.time() * 1000))
        data = request.json["values"]
        uid = request.json["deviceId"]
        print(data)
        for ele in data:
            ele["date"] = timestamp
        existing_data = mongo.db.stats.find_one({"uid": uid})["data"]
        new_data = existing_data + data
        mongo.db.stats.update_one({"uid": uid}, {"$set": {"data": new_data}})
        concerned_names = []
        for ele in data:
            if ele["status"] == 1:
                concerned_names.append(ele["name"])
        arr = mongo.db.counter.find_one({"uid": uid})["data"]
        for item in arr:
            if item["name"] in concerned_names:
                if item["count"][-1]["date"] == datetime.now().strftime("%m-%d-%Y"):
                    item["count"][-1]["dailyCount"] += 1
                else:
                    d = {}
                    d["date"] = datetime.now().strftime("%m-%d-%Y")
                    d["dailyCount"] = 1
                    item["count"].append(d)

        mongo.db.counter.update_one({"uid": uid}, {"$set": {"data": arr}})
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization error"}), 403


@app.route("/uploadLevel", methods=["GET", "POST"])
@cross_origin()
def uploadLevel():
    if request.method == "POST":
        timestamp = int(round(time.time() * 1000))
        data = request.json["values"]
        uid = request.json["deviceId"]
        for ele in data:
            ele["date"] = timestamp
        existing_data = mongo.db.levels.find_one({"uid": uid})["data"]
        new_data = existing_data + data
        mongo.db.levels.update_one({"uid": uid}, {"$set": {"data": new_data}})
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization error"}), 403


# route to register device
@app.route("/wizard/registerDevice", methods=["GET", "POST"])
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
        post = {
            "uid": uid,
            "ownerType": ownerType,
            "fArray": [],
            "address": address,
            "owner": owner,
            "activeDate": activeDate,
            "type": type_of_device,
            "settings": "15",
            "activeState": 0,
            "deviceState": 0,
            "mode": 0,
        }
        devices.insert_one(post)
        p = {"uid": uid, "data": []}
        mongo.db.stats.insert_one(p)
        q = {"uid": uid, "data": []}
        mongo.db.levels.insert_one(q)
        arr = create_dict(type_of_device)
        for ele in arr:
            ele["count"] = [
                {"date": datetime.now().strftime("%m-%d-%Y"), "dailyCount": 0}
            ]
        val = {"uid": uid, "data": arr}
        mongo.db.counter.insert_one(val)
        return jsonify({"message": "Registered Successfully"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


# route to register device


@app.route("/addFranchise", methods=["GET", "POST"])
@cross_origin()
def addFranchise():
    if request.method == "POST":
        uid = request.json["uid"]
        arr = request.json["values"]
        mongo.db.devices.update_one(
            {"uid": uid}, {"$addToSet": {"fArray": {"$each": arr}}}
        )
        return jsonify({"message": "Updated Successfully"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


# route to register device


@app.route("/verifyToken", methods=["GET", "POST"])
@cross_origin()
def verifyToken():
    if request.method == "POST":
        token = request.headers["Authorization"]
        ele = mongo.db.users.find_one({"token": token})
        if ele:
            return jsonify({"message": "VALID"})
        else:
            message, statusCode = checkValidity(token)
            if statusCode == 200:
                users = mongo.db.users
                post = {"uid": message["uid"], "token": token}
                users.insert_one(post)
                return jsonify({"message": message["status"]})
            else:
                return jsonify({"message": message["status"]}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/deleteToken", methods=["GET", "POST"])
@cross_origin()
def deleteToken():
    if request.method == "POST":
        token = request.headers["Authorizations"]
        ele = mongo.db.users.find_one({"token": token})
        if ele:
            mongo.db.users.delete_one({"token": token})
            return jsonify({"message": "SUCCESS"})
        else:
            return (jsonify({"message": "No record found"}),)


@app.route("/updateProfile", methods=["GET", "POST"])
@cross_origin()
def updateProfile():
    if request.method == "POST":
        uid = request.json["uid"]
        device = mongo.db.devices.find_one({"uid": uid})
        if device:
            address = request.json["address"]
            owner = request.json["owner"]
            try:
                mongo.db.devices.update_one(
                    {"uid": uid}, {"$set": {"address": address, "owner": owner}}
                )
            except:
                return jsonify({"message: Some Error Occured"}), 500
            return jsonify({"message": "Successfully Updated"})
        else:
            return jsonify({"message": "No such device found"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


# route to switch on/off
@app.route("/toggle", methods=["GET", "POST"])
@cross_origin()
def toggle():
    if request.method == "POST":
        token = request.headers["Authorization"]
        status, uid = authenticate(token)
        if status:
            devices = mongo.db.devices
            state = request.json["state"]
            devices.update_one({"uid": uid}, {"$set": {"activeState": state}})
            response = devices.find_one({"uid": uid})
            if (response["activeState"] == 1) and (response["deviceState"] == 1):
                return jsonify({"message": "Device Started", "status": 1})
            elif (response["activeState"] == 0) and (response["deviceState"] == 0):
                return jsonify({"message": "Device Stopped", "status": 0})
            elif (response["activeState"] == 1) and (response["deviceState"] == 0):
                return jsonify(
                    {
                        "message": "Start Request sent, waiting for device to respond",
                        "status": 2,
                    }
                )
            else:
                return jsonify(
                    {
                        "message": "Stop Request sent, waiting for device to respond",
                        "status": 3,
                    }
                )

        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


# route to toggle


@app.route("/wizard/toggle", methods=["GET", "POST"])
@cross_origin()
def wizardToggle():
    if request.method == "POST":
        uid = request.json["customerId"]
        if True:
            devices = mongo.db.devices
            state = request.json["state"]
            devices.update_one({"uid": uid}, {"$set": {"activeState": state}})
            response = devices.find_one({"uid": uid})
            if (response["activeState"] == 1) and (response["deviceState"] == 1):
                return jsonify({"message": "Device Started", "status": 1})
            elif (response["activeState"] == 0) and (response["deviceState"] == 0):
                return jsonify({"message": "Device Stopped", "status": 0})
            elif (response["activeState"] == 1) and (response["deviceState"] == 0):
                return jsonify(
                    {
                        "message": "Start Request sent, waiting for device to respond",
                        "status": 2,
                    }
                )
            else:
                return jsonify(
                    {
                        "message": "Stop Request sent, waiting for device to respond",
                        "status": 3,
                    }
                )

    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/switchMode", methods=["GET", "POST"])
@cross_origin()
def switchmode():
    if request.method == "POST":
        token = request.headers["Authorization"]
        status, uid = authenticate(token)
        if status:
            devices = mongo.db.devices
            mode = request.json["mode"]
            try:
                devices.update_one({"uid": uid}, {"$set": {"mode": mode}})
                if mode == 0:
                    return jsonify(
                        {"mode": 0, "message": "Device set to operation mode"}
                    )
                else:
                    return jsonify(
                        {"mode": 1, "message": "Device set to cleaning mode"}
                    )
            except:
                return jsonify({"mode": 2, "message": "Some error occured"})
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/wizard/switchMode", methods=["GET", "POST"])
@cross_origin()
def switchMode():
    if request.method == "POST":
        uid = request.json["customerId"]
        if True:
            devices = mongo.db.devices
            mode = request.json["mode"]
            try:
                devices.update_one({"uid": uid}, {"$set": {"mode": mode}})
                if mode == 0:
                    return jsonify(
                        {"mode": 0, "message": "Device set to operation mode"}
                    )
                else:
                    return jsonify(
                        {"mode": 1, "message": "Device set to cleaning mode"}
                    )
            except:
                return jsonify({"mode": 2, "message": "Some error occured"})
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/postDeviceStatus", methods=["GET", "POST"])
@cross_origin()
def postDeviceStatus():
    if request.method == "POST":
        uid = request.json["uid"]
        deviceStatus = request.json["status"]
        try:
            mongo.db.devices.update_one(
                {"uid": uid}, {"$set": {"deviceState": deviceStatus}}
            )
        except:
            print("Error!")
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/postPowerOut", methods=["GET", "POST"])
@cross_origin()
def postPowerOut():
    if request.method == "POST":
        uid = request.json["uid"]
        mongo.db.devices.update(
            {"uid": uid}, {"$set": {"deviceState": 0, "activeState": 0}}
        )
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/postLogs", methods=["GET", "POST"])
@cross_origin()
def postLogs():
    if request.method == "POST":
        uid = request.json["uid"]
        log_type = request.json["logType"]
        d = {}
        d["logType"] = log_type
        d["date"] = int(round(time.time() * 1000))
        response = mongo.db.logs.find_one({"uid": uid})
        if response:
            response["data"].append(d)
            mongo.db.devices.update_one(
                {"uid": uid}, {"$set": {"data": response["data"]}}
            )
        else:
            post = {"uid": uid, "data": [d]}
            mongo.db.logs.insert_one(post)
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


# route to update settings


@app.route("/updateSettings", methods=["GET", "POST"])
@cross_origin()
def updateSettings():
    if request.method == "POST":
        token = request.headers["Authorization"]
        status, uid = authenticate(token)
        if status:
            devices = mongo.db.devices
            setting = request.json["setting"]
            devices.update_one({"uid": uid}, {"$set": {"settings": setting}})
            return jsonify({"message": "SUCCESS"})
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/wizard/updateSettings", methods=["POST"])
@cross_origin()
def wizardUpdateSettings():
    if request.method == "POST":
        uid = request.json["customerId"]
        if True:
            devices = mongo.db.devices
            setting = request.json["setting"]
            devices.update_one({"uid": uid}, {"$set": {"settings": setting}})
            return jsonify({"message": "SUCCESS"})
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


# route to fetch device data


@app.route("/getDeviceData", methods=["GET", "POST"])
@cross_origin()
def getDeviceData():
    token = request.headers["Authorization"]
    status, uid = authenticate(token)
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


# route to fetch device data


@app.route("/wizard/getDeviceData", methods=["GET", "POST"])
@cross_origin()
def getWizardDeviceData():
    uid = request.args.get("customerId")
    if True:
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


@app.route("/getSwitchStatus", methods=["GET", "POST"])
@cross_origin()
def getSwitchStatus():
    uid = request.args.get("uid")
    data = mongo.db.devices.find_one({"uid": uid})
    if data:
        d = {}
        d["activeState"] = data["activeState"]
        d["settings"] = data["settings"]
        d["mode"] = data["mode"]
        return jsonify(d)
    else:
        return jsonify({"message": "Invalid Device Id"}), 403


@app.route("/getStats", methods=["GET", "POST"])
@cross_origin()
def getStats():
    token = request.headers["Authorization"]
    status, uid = authenticate(token)
    if status:
        available, data = sort(uid)
        if available:
            return jsonify({"result": data})
        else:
            return jsonify({"message": "No record found"}), 403
    else:
        return jsonify({"message": "Authentication Error"}), 401


@app.route("/wizard/getStats", methods=["GET", "POST"])
@cross_origin()
def wizardGetStats():
    uid = request.args.get("customerId")
    if True:
        available, data = sort(uid)
        if available:
            return jsonify({"result": data})
        else:
            return jsonify({"message": "No record found"}), 403


@app.route("/getToday", methods=["GET", "POST"])
@cross_origin()
def getToday():
    token = request.headers["Authorization"]
    status, uid = authenticate(token)
    if status:
        data = mongo.db.stats.find_one({"uid": uid})["data"]
        out = []
        for ele in data:
            if datetime.fromtimestamp(ele["date"] / 1000.0).strftime(
                "%m-%d-%Y"
            ) == datetime.now().strftime("%m-%d-%Y"):
                out.append(ele)
        n1 = 0
        n2 = 0
        n3 = 0
        for item in out:
            if item["name"] == "n1" and item["status"] == 1:
                n1 += 1
            elif item["name"] == "n2" and item["status"] == 1:
                n2 += 1
            elif item["name"] == "n3" and item["status"] == 1:
                n3 += 1
        return jsonify({"n1": n1, "n2": n2, "n3": n3})


@app.route("/getLevel", methods=["GET", "POST"])
@cross_origin()
def getLevel():
    token = request.headers["Authorization"]
    status, uid = authenticate(token)
    print(uid)
    if status:
        available, data = sort_level(uid)
        if available:
            return jsonify({"result": data})
        else:
            return jsonify({"message": "No record found"}), 403
    else:
        return jsonify({"message": "Authentication Error"}), 401


@app.route("/wizard/getLevel", methods=["GET", "POST"])
@cross_origin()
def wizardGetLevel():
    uid = request.args.get("customerId")
    if True:
        available, data = sort_level(uid)
        if available:
            return jsonify({"result": data})
        else:
            return jsonify({"message": "No record found"}), 403


@app.route("/getCount", methods=["GET", "POST"])
@cross_origin()
def getCount():
    token = request.headers["Authorization"]
    status, uid = authenticate(token)
    if status:
        response = mongo.db.counter.find_one({"uid": uid})
        if response:
            arr = []
            for ele in response["data"]:
                c = {}
                c["name"] = ele["name"]
                if len(ele["count"]) >= 20:
                    c["count"] = ele["count"][-20:]
                else:
                    c["count"] = ele["count"]
                arr.append(c)

            return jsonify({"result": arr})
        else:
            return jsonify({"message": "No record found"}), 403
    else:
        return jsonify({"message": "Authentication Error"}), 401


@app.route("/wizard/getCount", methods=["GET", "POST"])
@cross_origin()
def wizardGetCount():
    uid = request.args.get("customerId")
    if True:
        response = mongo.db.counter.find_one({"uid": uid})
        if response:
            arr = []
            for ele in response["data"]:
                c = {}
                c["name"] = ele["name"]
                if len(ele["count"]) >= 20:
                    c["count"] = ele["count"][-20:]
                else:
                    c["count"] = ele["count"]
                arr.append(c)

            return jsonify({"result": arr})
        else:
            return jsonify({"message": "No record found"}), 403


@app.route("/getCountByDate", methods=["GET", "POST"])
@cross_origin()
def getCountByDate():
    if request.method == "POST":
        start = request.json["start"]
        end = request.json["end"]
        s = int(datetime.strptime(start, "%m-%d-%Y").timestamp() * 1000)
        e = int(datetime.strptime(end, "%m-%d-%Y").timestamp() * 1000)
        token = request.headers["Authorization"]
        status, uid = authenticate(token)
        if status:
            response = mongo.db.counter.find_one({"uid": uid})
            if response:
                arr = []
                if start == end:
                    for ele in response["data"]:
                        c = {}
                        c["name"] = ele["name"]
                        c["count"] = []
                        for item in ele["count"]:
                            if item["date"] == start:
                                c["count"] = [
                                    {"date": start,
                                        "dailyCount": item["dailyCount"]}
                                ]
                                break
                        arr.append(c)
                    return jsonify({"result": arr})
                else:
                    for ele in response["data"]:
                        mini_arr = []
                        c = {}
                        c["name"] = ele["name"]
                        c["count"] = []
                        for item in ele["count"]:
                            curr = int(
                                datetime.strptime(
                                    item["date"], "%m-%d-%Y").timestamp()
                                * 1000
                            )
                            if curr >= s and curr <= e:
                                mini_arr.append(item)
                        c["count"] = mini_arr
                        arr.append(c)
                    return jsonify({"result": arr})
            else:
                return jsonify({"message": "No record found"}), 403
        else:
            return jsonify({"message": "Authentication error"}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/wizard/getCountByDate", methods=["GET", "POST"])
@cross_origin()
def wizardGetCountByDate():
    if request.method == "POST":
        start = request.json["start"]
        end = request.json["end"]
        s = int(datetime.strptime(start, "%m-%d-%Y").timestamp() * 1000)
        e = int(datetime.strptime(end, "%m-%d-%Y").timestamp() * 1000)
        uid = request.json.get("customerId")
        if True:
            response = mongo.db.counter.find_one({"uid": uid})
            if response:
                arr = []
                if start == end:
                    for ele in response["data"]:
                        c = {}
                        c["name"] = ele["name"]
                        c["count"] = []
                        for item in ele["count"]:
                            if item["date"] == start:
                                c["count"] = [
                                    {"date": start,
                                        "dailyCount": item["dailyCount"]}
                                ]
                                break
                        arr.append(c)
                    return jsonify({"result": arr})
                else:
                    for ele in response["data"]:
                        mini_arr = []
                        c = {}
                        c["name"] = ele["name"]
                        c["count"] = []
                        for item in ele["count"]:
                            curr = int(
                                datetime.strptime(
                                    item["date"], "%m-%d-%Y").timestamp()
                                * 1000
                            )
                            if curr >= s and curr <= e:
                                mini_arr.append(item)
                        c["count"] = mini_arr
                        arr.append(c)
                    return jsonify({"result": arr})
            else:
                return jsonify({"message": "No record found"}), 403
        else:
            return jsonify({"message": "Authentication error"}), 401


@app.route("/wizard/getProfile", methods=["GET"])
@cross_origin()
def getProfile():
    device_id = request.args.get("deviceId")
    if device_id:
        profile = mongo.db.wizard_profile.find_one(
            {"deviceId": device_id}, {"_id": 0})
        return jsonify(profile)
    return jsonify({"message": "No deviceId sent"}), 400


@app.route("/wizard/updateProfile", methods=["POST"])
@cross_origin()
def updateProfileWizard():
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

    device_id = request.args.get("deviceId")
    if device_id is None:
        return jsonify({"message": "No deviceId sent"}), 400
    valid_fields = ["lat", "lon"]
    updateProfileCol = {
        field: value for field, value in data.items() if field in valid_fields
    }
    mongo.db.wizard_profile.update_one(
        {"deviceId": device_id}, {"$set": updateProfileCol}
    )
    return jsonify({"message": "Success"})


@app.route("/wizard/postESPStatus", methods=["POST"])
@cross_origin()
def postESPStatus():
    data = request.json
    print(data["position"] + " " + "of " + data["deviceId"] + " is healthy")
    return jsonify({"message": "Success"})


@app.route("/wizard/updatePayment/<action>", methods=["POST"])
@cross_origin()
def updatePayment(action):
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

    device_id = request.json.get("deviceId")
    if device_id is None:
        return jsonify({"message": "No deviceId sent"}), 400
    if action == "add":
        valid_fields = ["paymentMode", "phoneNumber", "upi"]
        updatePay = {
            field: value for field, value in data.items() if field in valid_fields
        }
        if len(updatePay) != len(valid_fields):
            return jsonify({"message": "Missing fields"}), 400
        updatePay["methodId"] = generate_custom_id()
        mongo.db.wizard_profile.update_one(
            {"deviceId": device_id},
            {"$push": {"paymentMethods": updatePay}},
            upsert=True,
        )
    elif action == "remove":
        methodId = data.get("methodId")
        if not methodId:
            return jsonify({"message": "Missing fields"}), 400
        mongo.db.wizard_profile.update_one(
            {"deviceId": device_id},
            {"$pull": {"paymentMethods": {"methodId": methodId}}},
        )
    else:
        return jsonify({"message": "Invalid field"}), 400

    return jsonify({"message": "Sucess"})


@app.route("/wizard/getShoppingMenu", methods=["GET"])
@cross_origin()
# @verify_token
def getShoppingMenu():
    items = mongo.db.shopping_menu.find({}, {"_id": 0})
    return jsonify({"items": list(items)})


@app.route("/wizard/getAllCategories", methods=["GET"])
@cross_origin()
# @verify_token
def getAllCategories():
    categories = mongo.db.shopping_menu.find(
        {}, {"_id": 0, "categoryId": 1, "category": 1}
    )
    return jsonify({"categories": list(categories)})


@app.route("/wizard/getItemByCategory", methods=["GET"])
@cross_origin()
# @verify_token
def getItemByCategory():
    category_list = request.args.get("categoryId", "").split(",")
    items = mongo.db.shopping_menu.find(
        {"categoryId": {"$in": category_list}}, {"_id": 0}
    )
    return jsonify({"items": list(items)})


@app.route("/wizard/addToShoppingCart", methods=["POST"])
@cross_origin()
# @verify_token
def addToShoppingCart():
    token = request.headers["Authorization"]
    decoded = jwt.decode(
        token, options={"verify_signature": False, "verify_aud": False}
    )
    email = decoded["email"]
    itemId = request.json.get("itemId")
    mongo.db.shopping_cart.update_one(
        {"email": email}, {"$push": {"items": itemId}}, upsert=True
    )
    return jsonify({"message": "Success"})


@app.route("/wizard/removeFromShoppingCart", methods=["POST"])
@cross_origin()
# @verify_token
def removeFromShoppingCart():
    token = request.headers["Authorization"]
    decoded = jwt.decode(
        token, options={"verify_signature": False, "verify_aud": False}
    )
    email = decoded["email"]
    itemId = request.json.get("itemId")
    cart = mongo.db.shopping_cart.find_one({"email": email}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items = cart.get("items", [])
    if itemId in items:
        items.remove(itemId)
    mongo.db.shopping_cart.update_one(
        {"email": email}, {"$set": {"items": items}}, upsert=True
    )
    return jsonify({"message": "Success"})


@app.route("/wizard/getShoppingCart", methods=["GET"])
@cross_origin()
# @verify_token
def getShoppingCart():
    token = request.headers["Authorization"]
    decoded = jwt.decode(
        token, options={"verify_signature": False, "verify_aud": False}
    )
    email = decoded["email"]
    cart = mongo.db.shopping_cart.find_one({"email": email}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items_dict = {}
    for item in cart.get("items", []):
        items_dict[item] = items_dict.get(item, 0) + 1
    items = [{"itemId": k, "qty": v} for k, v in items_dict.items()]
    cart.update({"items": items})
    return jsonify(cart)


@app.route("/wizard/payNow", methods=["POST"])
@cross_origin()
# @verify_token
def payNowWizard():
    token = request.headers["Authorization"]
    decoded = jwt.decode(
        token, options={"verify_signature": False, "verify_aud": False}
    )
    email = decoded["email"]
    client_data = mongo.db.clients.find_one({"email": email})
    phone = client_data["mobile"]
    data = request.json
    valid_fields = ["deliveryAddress"]
    customerData = mongo.db.clients.find_one({"email": email})
    if not customerData:
        return jsonify({"message": "No such customer found"}), 400

    customerName = client_data["firstName"]
    data.update(
        {
            "customerName": customerName,
            "customerEmail": email, "customerPhone": phone
        }
    )
    createOrder = data
    valid_flag = all(field in data for field in valid_fields)
    items_arr = []

    if valid_flag:
        cart = mongo.db.shopping_cart.find_one({"email": email}, {"_id": 0})
        if not cart:
            return jsonify({"message": "Cart Empty"}), 400
        itemsDict = {}
        for item in cart.get("items", []):
            itemsDict[item] = itemsDict.get(item, 0) + 1

        data["items"] = [{"itemId": k, "qty": v} for k, v in itemsDict.items()]
        itemsList = list(itemsDict.keys())
        data = mongo.db.shopping_menu.aggregate(
            [
                {"$unwind": "$items"},
                {"$match": {"items.itemId": {"$in": itemsList}}},
                {
                    "$project": {
                        "_id": 0,
                        "itemId": "$items.itemId",
                        "itemName": "$items.name",
                        "gst": 1,
                        "price": "$items.price",
                        "closeCategory": 1,
                    }
                },
            ]
        )
        data = list(data)
        if any(d["closeCategory"] for d in data):
            return (
                jsonify({
                    "message": "One or more items are ordered from a closed category"
                }
                ),
                400,
            )
        subTotal = 0
        items_arr = []
        for d in data:
            qty = itemsDict.get(d["itemId"], 1)
            subTotal += float(d["price"]) * int(qty)
            items_arr.append(
                {
                    "itemId": d["itemId"],
                    "itemName": d["itemName"],
                    "price": d["price"],
                    "qty": qty,
                }
            )
        orderFields = {
            "orderId": generate_custom_id(),
            "timestamp": int(round(time.time() * 1000)),
            "orderStatus": "placed",
            "subTotal": subTotal,
            "manualBilling": False,
            "total": round(subTotal, 2),
            "status": "ncnf",
        }
        createOrder.update(orderFields)
        createOrder["items"] = items_arr
        # mongo.db.shopping_cart.delete_one({"email": email})
        createOrder.pop("_id", None)
        post = {
            "key": global_key,
            "amount": str(orderFields["total"]),
            "phone": phone,
            "productinfo": ("Spices").rstrip(),
            "surl": "http://15.207.147.88:5002/wizard/payuSuccessWizard",
            "furl": "http://15.207.147.88:5002/wizard/payuFailureWizard",
            "firstname": customerName,
            "email": email,
            "service_provider": "payu_paisa",
        }
    # print(post)
    res = requests.post(payment_url + "/api/payment/checkout", json=post)
    res = res.json()
    # Create retainer invoice
    customer_id = mongo.db.zoho_customer.find_one({"email": email})
    if customer_id:
        invoice_id = create_zoho_retainer_invoice(
            customer_id["zohoId"], post["productinfo"], float(post["amount"])
        )
        mongo.db.retainer_invoices.insert_one(
            {
                "email": email,
                "invoice_id": invoice_id,
                "customer_id": customer_id["zohoId"],
                "amount": float(post["amount"]),
                "timestamp": int(round(time.time() * 1000)),
            }
        )
    print(res)
    hash_uid = mongo.db.hash_counter.find_one({"id": 1})["hash_uid"]
    res["payment_uid"] = hash_uid
    mongo.db.hash_map_wizard.insert_one(
        {
            "hash_uid": hash_uid,
            "initiated_date": int(round(time.time() * 1000)),
            "hash": res["hash"],
            "email": email,
            "amount": orderFields["total"],
            "status": 0,
            "transaction_id": res["txnid"],
            "bank_ref_num": "",
            "mihpayid": "",
            "orderId": createOrder["orderId"],
        }
    ),
    mongo.db.hash_counter_wizard.update_one(
        {"id": 1}, {"$set": {"hash_uid": hash_uid + 1}}
    )
    # res['orderDetails'] = createOrder
    createOrder["payu_response"] = res
    mongo.db.shopping_orders.insert_one(createOrder)
    return jsonify({"orderId": createOrder["orderId"]}), 200


@app.route("/wizard/renderPayment/<orderId>", methods=["GET"])
@cross_origin()
# @verify_token
def renderPaymentWizard(orderId):
    order = mongo.db.shopping_orders.find_one({"orderId": orderId})
    if not order:
        return jsonify({"message": "No such order found"}), 400
    return render_template("payment.html", **order["payu_response"])


@app.route("/wizard/checkPaymentStatus", methods=["GET"])
@cross_origin()
def checkPaymentStatus():
    orderId = request.args.get("orderId")
    if orderId:
        order = mongo.db.shopping_orders.find_one(
            {"orderId": orderId},
            {"_id": 0, "payu_response": 0})
        if not order:
            return jsonify({"message": "No such order found"}), 400
        return jsonify(order)
    return jsonify({"message": "No orderId found"}), 400


@app.route('/wizard/payuSuccessWizard', methods=['POST'])
@cross_origin()
def payuSuccessWizard():
    # date = int(round(time.time() * 1000))
    bank_ref_num = request.form['bank_ref_num']
    mihpayid = request.form['mihpayid']
    transaction_id = request.form['txnid']
    txn_data = mongo.db.hash_map_wizard.find_one(
        {"transaction_id": transaction_id})
    mongo.db.hash_map_wizard.update_one({"transaction_id": transaction_id}, {
        "$set": {
            "status": 1,
            "bank_ref_num": bank_ref_num,
            "mihpayid": mihpayid
        }
    })
    mongo.db.shopping_orders.update_one({"orderId": txn_data["orderId"]}, {
        "$set": {
            "status": "cnf",
        }
    })
    mongo.db.shopping_cart.delete_one({"email": txn_data["email"]})
    return render_template('index.html')


@app.route('/wizard/payuFailureWizard', methods=['POST'])
@cross_origin()
def payuFailureWizard():
    transaction_id = request.form['txnid']
    txn_data = mongo.db.hash_map_wizard.find_one_and_update(
        {"transaction_id": transaction_id},
        {"$set": {
            "status": -1
        }})
    mongo.db.shopping_orders.update_one({"orderId": txn_data["orderId"]}, {
        "$set": {
            "status": "fail",
        }
    })
    return render_template('fail.html')


if __name__ == "__main__":
    print("starting...")
    refresh_zoho_access_token(force=True)
    app.run(
        host=cfg.IOTFlask["HOST"],
        port=cfg.IOTFlask["PORT"],
        threaded=cfg.IOTFlask["THREADED"],
        debug=True,
    )
