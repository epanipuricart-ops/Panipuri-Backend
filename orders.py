from flask import (Flask, request, jsonify, send_from_directory)
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
from firebase_admin import credentials, auth
import firebase_admin
import pyrebase
import jwt
import json
import time
import os
import binascii
from datetime import datetime, date
from functools import wraps
from config import config as cfg
import re
import subprocess
import requests


INVOICE_PDF_FOLDER = 'public/invoice_pdf'

app = Flask(__name__, static_url_path='')

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://localhost:27017/panipuriKartz"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*",
                    logger=True, engineio_logger=True)
# socketio.init_app(app, cors_allowed_origins="*")
cred = credentials.Certificate('config/fbAdminSecret.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('config/fbConfig.json')))


spring_url = "http://15.207.147.88:8080/"


def verify_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('Authorization'):
            print(request.headers)
            return {'message': 'MissingParameters'}, 400
        try:
            user = auth.verify_id_token(request.headers['Authorization'])
            request.user = user
        except Exception:
            return {'message': 'Authentication Error'}, 401
        return f(*args, **kwargs)

    return wrap


def generate_custom_id():
    return (
        binascii.b2a_hex(os.urandom(4)).decode() +
        hex(int(time.time()*10**5) % 10**12)[2:]
    )


@app.route('/orderOnline/getMenu', methods=['GET'])
@cross_origin()
@verify_token
def getMenu():
    cartId = request.args.get("cartId")
    if not cartId:
        return jsonify({"message": "No Cart ID sent"}), 400
    cart = mongo.db.menu.find_one({"cartId": cartId}, {"_id": 0, "sid": 0})
    return jsonify(cart or {})


@app.route('/orderOnline/updateMenu/<field>', methods=['POST'])
@cross_origin()
@verify_token
def updateMenu(field):
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

    if field == "item":
        if not data.get("itemId"):
            return jsonify({"message": "No Item ID sent"}), 400

        valid_fields = [
            "name", "img", "desc", "price",
            "ingredients", "customDiscount", "isOutOfStock"]
        updateItem = {"menu.$.items.$[t]."+field: value for field,
                      value in data.items() if field in valid_fields}
        mongo.db.menu.update_one(
            {
                "menu.items.itemId": data.get("itemId")
            },
            {
                "$set": updateItem
            },
            array_filters=[{"t.itemId": data.get("itemId")}]
        )
    elif field == "category":
        if not data.get("categoryId"):
            return jsonify({"message": "No Category ID sent"}), 400

        valid_fields = ["category", "closeCategory"]
        updateCategory = {"menu.$."+field: value for field,
                          value in data.items() if field in valid_fields}
        mongo.db.menu.update_one(
            {
                "menu.categoryId": data.get("categoryId")
            },
            {
                "$set": updateCategory
            })
    elif field == "cart":
        if not data.get("cartId"):
            return jsonify({"message": "No Cart ID sent"}), 400
        valid_fields = ["deliveryCharge", "flatDiscount", "gst", "isActive"]
        updateCart = {field: value for field,
                      value in data.items() if field in valid_fields}
        mongo.db.menu.update_one(
            {
                "cartId": data.get("cartId")
            },
            {
                "$set": updateCart
            })
    else:
        return jsonify({"message": "Invalid field"}), 400
    return jsonify({"message": "Sucess"})


@app.route('/orderOnline/createMenu/<field>', methods=['POST'])
@cross_origin()
@verify_token
def createMenu(field):
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

    if field == "item":
        categoryId = data.get("categoryId")
        if not categoryId:
            return jsonify({"message": "No Category ID sent"}), 400

        valid_fields = [
            "name", "img", "desc", "price",
            "ingredients", "customDiscount", "isOutOfStock"]
        createItem = {field: value for field,
                      value in data.items() if field in valid_fields}

        if len(valid_fields) == len(createItem):
            createItem.update({"itemId": generate_custom_id()})
            mongo.db.menu.update_one(
                {
                    "menu.categoryId": categoryId
                },
                {
                    "$push": {"menu.$.items": createItem}
                }
            )
            return jsonify({"message": "Sucess"})
        return jsonify({"message": "Missing fields while creating item"}), 400
    elif field == "category":
        cartId = data.get("cartId")
        if not cartId:
            return jsonify({"message": "No Cart ID sent"}), 400

        valid_fields = ["category", "closeCategory"]
        createCategory = {field: value for field,
                          value in data.items() if field in valid_fields}

        if len(valid_fields) == len(createCategory):
            createCategory.update(
                {"categoryId": generate_custom_id(), "items": []})
            mongo.db.menu.update_one(
                {
                    "cartId": cartId
                },
                {
                    "$push": {"menu": createCategory}
                })
            return jsonify({"message": "Sucess"})
        return jsonify(
            {"message": "Missing fields while creating category"}), 400
    else:
        return jsonify({"message": "Invalid field"}), 400


@app.route('/orderOnline/deleteMenu/<field>', methods=['POST'])
@cross_origin()
@verify_token
def deleteMenu(field):
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

    if field == "item":
        itemId = data.get("itemId")
        if not itemId:
            return jsonify({"message": "No Item ID sent"}), 400

        mongo.db.menu.update_one(
            {
                "menu.items.itemId": itemId
            },
            {
                "$pull":
                {
                    "menu.$.items": {"itemId": itemId}
                }
            })
    elif field == "category":
        categoryId = data.get("categoryId")
        if not categoryId:
            return jsonify({"message": "No Category ID sent"}), 400

        mongo.db.menu.update_one(
            {
                "menu.categoryId": categoryId
            },
            {
                "$pull":
                    {
                        "menu": {"categoryId": categoryId}
                    }
            })
    else:
        return jsonify({"message": "Invalid field"}), 400
    return jsonify({"message": "Sucess"})


@app.route('/orderOnline/sendOTP', methods=['POST'])
@cross_origin()
def sendOTP():
    if 'phone' not in request.json:
        return jsonify({"message": "Missing Parameters"}), 400
    phone = request.json['phone']
    email = request.json['email']
    # email = 'jyotimay16@gmail.com'
    firstName = request.json['firstName']
    msg = "__OTP__ is your One Time Password for phone verification"
    typeOfMessage = 1
    data = {"message": msg, "phone": phone, "name": firstName,
            "email": email, "type": typeOfMessage,
            "mediaUrl": "http://15.207.147.88:5000/franchisee/getLogo"
            }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        response = requests.post(spring_url +
                                 'api/message/send-order-otp',
                                 data=json.dumps(data),
                                 headers=headers)
        return json.loads(response.text)
    except Exception:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route('/orderOnline/verifyOTP', methods=['POST'])
@cross_origin()
def verifyOTP():
    if (
        'phone' not in request.json
        or 'token' not in request.json
        or 'otp' not in request.json
    ):
        return jsonify({"message": "Missing Parameters"}), 400
    phone = request.json['phone']
    token = request.json['token']
    otp = request.json['otp']
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        target_url = 'api/message/verify-order-otp/{}/phone/{}/otp/{}'.format(
            token, phone, otp)
        response = requests.get(spring_url + target_url, headers=headers)
        return json.loads(response.text)
    except Exception:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route('/orderOnline/getAllLocations', methods=['GET'])
@cross_origin()
@verify_token
def getAllLocations():
    state = request.args.get("state")
    town = request.args.get("town")
    if state and town:
        locations = mongo.db.device_ids.find(
            {"state": state, "town": town},
            {"_id": 0, "location": 1, "device_id": 1})
        return jsonify({"locations": list(locations)})
    return jsonify({"message": "No State/City provided"}), 400


@app.route('/orderOnline/getCitiesByState', methods=['GET'])
@cross_origin()
@verify_token
def getCitiesByState():
    state = request.args.get("state")
    if state:
        locations = mongo.db.device_ids.find(
            {"state": re.compile(state, re.IGNORECASE)},
            {"_id": 0, "town": 1})
        return jsonify({"cities": list({x["town"] for x in locations})})
    return jsonify({"message": "No State provided"}), 400


@app.route('/orderOnline/orderStatus', methods=['GET'])
@cross_origin()
@verify_token
def orderStatus():
    orderId = request.args.get("orderId")
    if orderId:
        order = mongo.db.online_orders.find_one(
            {"orderId": orderId}, {"_id": 0})
        return jsonify(order)
    return jsonify({"message": "No orderId Sent"}), 400


@app.route('/orderOnline/getOrderCart', methods=['GET'])
@cross_origin()
@verify_token
def getOrderCart():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    cart = mongo.db.order_cart.find_one({"email": email}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items_dict = {}
    for item in cart.get("items", []):
        items_dict[item] = items_dict.get(item, 0)+1
    items = [{"itemId": k, "qty": v} for k, v in items_dict.items()]
    cart.update({"items": items})
    return jsonify(cart)


@app.route('/orderOnline/addToOrderCart', methods=['POST'])
@cross_origin()
@verify_token
def addToOrderCart():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    itemId = request.json.get("itemId")
    mongo.db.order_cart.update_one(
        {"email": email},
        {"$push": {
            "items": itemId
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/orderOnline/removeFromOrderCart', methods=['POST'])
@cross_origin()
@verify_token
def removeFromOrderCart():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    itemId = request.json.get("itemId")
    cart = mongo.db.order_cart.find_one({"email": email}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items = cart.get("items", [])
    if itemId in items:
        items.remove(itemId)
    mongo.db.order_cart.update_one(
        {"email": email},
        {"$set": {
            "items": items
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/orderOnline/placeOrder', methods=['POST'])
@cross_origin()
@verify_token
def placeOrder():
    data = request.json
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    valid_fields = [
        "cartId",
        "deliveryAddress",
        "orderType",
        "modeOfPayment",
        "transactionId"]
    if "orderType" not in data:
        data["orderType"] = "delivery"
    if "transactionId" not in data:
        data["transactionId"] = ""
    customerData = mongo.db.clients.find_one({"email": email})
    if not customerData:
        return jsonify({"message": "No such customer found"}), 400
    customerName = " ".join([
        customerData.get("title", ""),
        customerData.get("firstName"),
        customerData.get("lastName")])
    customerName = customerName.strip()
    data.update({"customerName": customerName, "customerEmail": email,
                 "customerPhone": customerData.get("mobile")})
    createOrder = {field: value for field,
                   value in data.items()}

    items_arr = []

    if True:
        email = createOrder['customerEmail']
        cart = mongo.db.order_cart.find_one(
            {"email": email}, {"_id": 0})
        if not cart:
            return jsonify({"message": "Cart Empty"}), 400
        itemsDict = {}
        for item in cart.get("items", []):
            itemsDict[item] = itemsDict.get(item, 0)+1

        data["items"] = [{"itemId": k, "qty": v} for k, v in itemsDict.items()]
        itemsList = list(itemsDict.keys())
        data = mongo.db.menu.aggregate(
            [
                {
                    "$match":
                    {"cartId": data["cartId"]}
                },
                {"$unwind": "$menu"},
                {
                    "$match":
                    {
                        "menu.items.itemId": {"$in": itemsList}
                    }
                },
                {"$unwind": "$menu.items"},
                {
                    "$match":
                    {"menu.items.itemId": {"$in": itemsList}}
                },
                {
                    "$project":
                    {
                        "_id": 0,
                        "itemId": "$menu.items.itemId",
                        "itemName": "$menu.items.name",
                        "gst": 1,
                        "sid": 1,
                        "isActive": 1,
                        "price": "$menu.items.price"
                    }
                }
            ])
        data = list(data)
        if not data[0]["isActive"]:
            return jsonify({"message": "Restaurant Offline"}), 400
        extraData = {"subTotal": 0,
                     "gst": data[0]["gst"], "sid": data[0]["sid"]}
        items_arr = []
        for d in data:
            qty = itemsDict.get(d["itemId"], 1)
            extraData["subTotal"] += float(d["price"])*int(qty)
            items_arr.append(
                {"itemId": d["itemId"], "itemName": d["itemName"],
                 "price": d["price"], "qty": qty})
        orderFields = {
            "orderId": generate_custom_id(),
            "timestamp": int(round(time.time() * 1000)),
            "orderStatus": "placed",
            "subTotal": extraData["subTotal"],
            "gst": extraData["gst"],
            "manualBilling": False,
            "total": round(
                (1+extraData["gst"])*extraData["subTotal"], 2)
        }
        createOrder.update(orderFields)
        createOrder["items"] = items_arr
        createOrder["deliveryCharge"] = 0.0
        createOrder["packingCharge"] = 0.0
        mongo.db.online_orders.insert_one(createOrder)
        mongo.db.daily_statistics.update_one({
            "cartId": createOrder["cartId"],
            "timestamp": datetime.combine(date.today(), datetime.min.time())
        },
            {
                "$inc": {"dailyCount": 1}
        },
            upsert=True)
        mongo.db.order_cart.delete_one({"email": email})
        createOrder.pop("_id", None)
        socketio.emit("receiveOrder", createOrder,
                      json=True, room=extraData["sid"])
        return jsonify(createOrder)
    return jsonify({"message": "Missing fields while creating order"}), 400

@app.route('/orderOnline/getStatistics', methods=['GET'])
@cross_origin()
@verify_token
def getStatistics():
    cartId = request.args.get("cartId")
    data = mongo.db.daily_statistics.find(
        {"cartId": cartId},
        {"_id": 0, "cartId": 0}).sort("timestamp", -1)
    newData = []
    for rec in data:
        rec["timestamp"] = rec["timestamp"].strftime("%d-%m-%Y")
        newData.append(rec)
    return jsonify({"stats": newData})

@app.route('/orderOnline/generateStatistics', methods=['POST'])
@cross_origin()
@verify_token
def generateStatistics():
    cartId = request.json.get("cartId")
    startms = request.json.get("startms")
    endms = request.json.get("endms")
    items = mongo.db.online_orders.find({
        "cartId": cartId,
        "timestamp": {"$gt":  startms, "$lt": endms}
    },
        {"_id": 0, "items": 1})
    sales = {}
    for itemrow in items:
        for item in itemrow["items"]:
            name = item["itemName"]
            sales[name] = sales.get(name, 0)+item["qty"]
    max_sales = max(sales, key=sales.get)
    return jsonify({"sales": sales, "max_sales_item": max_sales})

@app.route('/orderOnline/getOrderCartManual', methods=['GET'])
@cross_origin()
@verify_token
def getOrderCartManual():
    orderId = request.args.get("orderId")
    if not orderId:
        return jsonify({"message": "Missing orderId field"}), 400

    cart = mongo.db.order_cart.find_one({"orderId": orderId}, {"_id": 0})
    if not cart:
        return jsonify({"items": []})
    items_dict = {}
    for item in cart.get("items", []):
        items_dict[item] = items_dict.get(item, 0)+1
    items = [{"itemId": k, "qty": v} for k, v in items_dict.items()]
    cart.update({"items": items})
    return jsonify(cart)


@app.route('/orderOnline/addToOrderCartManual', methods=['POST'])
@cross_origin()
@verify_token
def addToOrderCartManual():
    orderId = request.json.get("orderId")
    if not orderId:
        return jsonify({"message": "Missing orderId field"}), 400

    itemId = request.json.get("itemId")
    mongo.db.order_cart.update_one(
        {"orderId": orderId},
        {"$push": {
            "items": itemId
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/orderOnline/removeFromOrderCartManual', methods=['POST'])
@cross_origin()
@verify_token
def removeFromOrderCartManual():
    orderId = request.json.get("orderId")
    if not orderId:
        return jsonify({"message": "Missing orderId field"}), 400

    itemId = request.json.get("itemId")
    cart = mongo.db.order_cart.find_one({"orderId": orderId}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items = cart.get("items", [])
    if itemId in items:
        items.remove(itemId)
    mongo.db.order_cart.update_one(
        {"orderId": orderId},
        {"$set": {
            "items": items
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/orderOnline/newOrderId', methods=['GET'])
@cross_origin()
@verify_token
def newOrderId():
    orderId = {"orderId": generate_custom_id()}
    mongo.db.online_orders.insert_one(orderId)
    orderId.pop("_id", None)
    return jsonify(orderId)


@app.route('/orderOnline/placeOrderManual', methods=['POST'])
@cross_origin()
@verify_token
def placeOrderManual():
    data = request.json
    valid_fields = [
        "cartId",
        "orderId",
        "customerName",
        "customerPhone",
        "customerEmail",
        "deliveryAddress",
        "orderType",
        "modeOfPayment",
        "transactionId",
        "manualBilling",
        "packingCharge",
        "deliveryCharge"]
    if "orderType" not in data:
        data["orderType"] = "delivery"
    for field in ["transactionId", "customerEmail", "deliveryAddress"]:
        if field not in data:
            data[field] = ""
    if "packingCharge" not in data:
        data["packingCharge"] = 0.0
    if "deliveryCharge" not in data:
        data["deliveryCharge"] = 0.0
    data["manualBilling"] = True
    createOrder = {field: value for field,
                   value in data.items() if field in valid_fields}

    items_arr = []

    if len(createOrder) == len(valid_fields):
        orderId = createOrder['orderId']
        cart = mongo.db.order_cart.find_one(
            {"orderId": orderId}, {"_id": 0})
        if not cart:
            return jsonify({"message": "Cart Empty"}), 400
        itemsDict = {}
        for item in cart.get("items", []):
            itemsDict[item] = itemsDict.get(item, 0)+1

        data["items"] = [{"itemId": k, "qty": v} for k, v in itemsDict.items()]
        itemsList = list(itemsDict.keys())
        data = mongo.db.menu.aggregate(
            [
                {
                    "$match":
                    {"cartId": data["cartId"]}
                },
                {"$unwind": "$menu"},
                {
                    "$match":
                    {
                        "menu.items.itemId": {"$in": itemsList}
                    }
                },
                {"$unwind": "$menu.items"},
                {
                    "$match":
                    {"menu.items.itemId": {"$in": itemsList}}
                },
                {
                    "$project":
                    {
                        "_id": 0,
                        "itemId": "$menu.items.itemId",
                        "itemName": "$menu.items.name",
                        "gst": 1,
                        "sid": 1,
                        "isActive": 1,
                        "price": "$menu.items.price"
                    }
                }
            ])
        data = list(data)
        if not data[0]["isActive"]:
            return jsonify({"message": "Restaurant Offline"}), 400
        extraData = {"subTotal": 0,
                     "gst": data[0]["gst"]}
        items_arr = []
        for d in data:
            qty = int(itemsDict.get(d["itemId"], 1))
            extraData["subTotal"] += float(d["price"])*qty
            items_arr.append(
                {"itemId": d["itemId"], "itemName": d["itemName"],
                 "price": d["price"], "qty": qty})
        orderFields = {
            "timestamp": int(round(time.time() * 1000)),
            "orderStatus": "confirmed",
            "subTotal": extraData["subTotal"],
            "gst": extraData["gst"],
            "manualBilling": True,
            "total": round(
                (1+extraData["gst"])*extraData["subTotal"], 2)
        }
        createOrder.update(orderFields)
        createOrder["items"] = items_arr
        mongo.db.online_orders.update_one(
            {"orderId": orderId},
            {"$set": createOrder})
        mongo.db.daily_statistics.update_one({
            "cartId": createOrder["cartId"],
            "timestamp": datetime.combine(date.today(), datetime.min.time())
        },
            {
                "$inc": {"dailyCount": 1}
        },
            upsert=True)
        mongo.db.order_cart.delete_one({"orderId": orderId})
        return jsonify(createOrder)
    return jsonify({"message": "Missing fields while creating order"})


@app.route('/orderOnline/updateOrderStatus', methods=['POST'])
@cross_origin()
@verify_token
def updateOrderStatus():
    data = request.json
    orderId = data.get("orderId")
    status = data.get("status")
    order_data = mongo.db.online_orders.find_one(
        {"orderId": orderId}, {"_id": 0})

    if orderId and status:
        if status == 'pending':
            deliveryCharge = float(data.get('deliveryCharge'))
            packingCharge = float(data.get('packingCharge'))
            clientEmail = order_data['customerEmail']
            sid_list = mongo.db.customer_sid.find_one(
                {"email": clientEmail}).get("sid", [])
            subTotal = order_data['subTotal']
            gst = order_data['gst']
            total = (subTotal + deliveryCharge + packingCharge) * (1+gst)
            total = round(total, 2)
            mongo.db.online_orders.update_one(
                {"orderId": orderId},
                {"$set": {
                    "orderStatus": status,
                    "total": total,
                    "packingCharge": packingCharge,
                    "deliveryCharge": deliveryCharge
                }})
            order_data = mongo.db.online_orders.find_one(
                {"orderId": orderId}, {"_id": 0})
            socketio.emit("receiveEditedOrder", order_data,
                          json=True, room=sid_list)
        elif status == 'confirmed' or status == 'canceled':
            mongo.db.online_orders.update_one(
                {"orderId": orderId},
                {"$set": {
                    "orderStatus": status
                }})
            order_data_updated = mongo.db.online_orders.find_one(
                {"orderId": orderId}, {"_id": 0})
            sid_list = mongo.db.menu.find_one(
                {"cartId": order_data["cartId"]})["sid"]
            socketio.emit("receiveConfirmedOrder", order_data_updated,
                          json=True, room=sid_list)
        else:
            mongo.db.online_orders.update_one(
                {"orderId": orderId},
                {"$set": {
                    "orderStatus": status
                }})
        return jsonify({"message": "Success"})
    return jsonify({"message": "Missing fields"}), 400


@app.route('/orderOnline/getOrderByTypeAndStatus', methods=['GET'])
@cross_origin()
@verify_token
def getOrderByTypeAndStatus():
    status = request.args.get("status")
    _type = request.args.get("type")
    cartId = request.args.get("cartId")
    if not status:
        return jsonify({"message": "No status arguments sent"}), 400
    query = {"orderStatus": status, "cartId": cartId}
    if _type:
        query.update({"orderType": _type})
    orders = mongo.db.online_orders.find(
        query, {"_id": 0}).sort("timestamp", -1)
    return jsonify({"orders": list(orders)})


@app.route('/orderOnline/ongoingOrders', methods=['GET'])
@cross_origin()
@verify_token
def ongoingOrders():
    _type = request.args.get("type")
    cartId = request.args.get("cartId")
    query = {
        "$or": [
            {"orderStatus": "pending"},
            {"orderStatus": "confirmed"},
            {"orderStatus": "dispatched"}
        ],
        "cartId": cartId
    }
    if _type and _type in ["dineIn", "delivery", "takeAway"]:
        query.update({"orderType": _type})
    orders = mongo.db.online_orders.find(
        query, {"_id": 0}).sort("timestamp", -1)
    return jsonify({"orders": list(orders)})


@app.route('/orderOnline/declinedOrders', methods=['GET'])
@cross_origin()
@verify_token
def declinesOrders():
    _type = request.args.get("type")
    cartId = request.args.get("cartId")
    query = {
        "$or": [
            {"orderStatus": "rejected"},
            {"orderStatus": "canceled"}
        ],
        "cartId": cartId
    }
    if _type and _type in ["dineIn", "delivery", "takeAway"]:
        query.update({"orderType": _type})
    orders = mongo.db.online_orders.find(
        query, {"_id": 0}).sort("timestamp", -1)
    return jsonify({"orders": list(orders)})


@app.route('/orderOnline/generateInvoice', methods=['GET'])
@cross_origin()
def generateInvoice():
    orderId = request.args.get("orderId")
    if not orderId:
        return {"message": "No ID Sent"}
    save_path = os.path.join(INVOICE_PDF_FOLDER, orderId+".pdf")
    if os.path.isfile(save_path):
        return send_from_directory(INVOICE_PDF_FOLDER, orderId+".pdf")
    order_data = mongo.db.online_orders.find_one(
        {"orderId": orderId}, {"_id": 0})
    if order_data:
        device_id = mongo.db.device_ids.find_one(
            {"device_id": order_data.get("cartId")})
        items_format = r"|itemName| & \centering |qty| & \centering RS. |price| & \multicolumn{1}{r}{ RS. |totalPrice| }\\"
        items_list = []
        for item in order_data["items"]:
            item_str = items_format
            item.update({"totalPrice": item["qty"]*item["price"]})
            for k, v in item.items():
                item_str = item_str.replace("|"+k+"|", str(v))
            items_list.append(item_str+"\n\\\\\n")
        order_data.update(
            {
                "location": device_id.get("location"),
                "gst": sum(
                    order_data[key]
                    for key in ["subTotal", "deliveryCharge", "packingCharge"]
                )
                * order_data["gst"],
                "timestamp": datetime.fromtimestamp(
                    order_data["timestamp"]//1000
                ).strftime('%d %B %Y, %I:%M %p'),
                "items": "".join(items_list)
            }
        )
        latex_data = open("invoice_template.tex").read()

        for k, v in order_data.items():
            latex_data = latex_data.replace("|"+k+"|", str(v))
        tmp_file = os.path.join(
            INVOICE_PDF_FOLDER, generate_custom_id()+".tex")
        with open(tmp_file, "w") as lfile:
            lfile.write(latex_data)
        process = subprocess.Popen([
            r'C:\Program Files\MiKTeX\miktex\bin\x64\latex.exe',
            '-output-format=pdf',
            '-job-name=' + save_path[:-4], tmp_file])
        process.wait()
        try:
            os.remove(tmp_file)
            os.remove(save_path[:-3]+"aux")
            os.remove(save_path[:-3]+"log")
        except Exception as e:
            print(e)
        return send_from_directory(INVOICE_PDF_FOLDER, orderId+".pdf")
    return jsonify({"message": "Invalid ID"})


@app.route('/orderOnline/getAddress', methods=['GET'])
@cross_origin()
@verify_token
def getAddress():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    address = mongo.db.address_book.find_one({"email": email})
    if address:
        return jsonify({"address": address.pop("address")})
    return jsonify({"address": []})


@app.route('/orderOnline/updateAddress/<field>', methods=['POST'])
@cross_origin()
@verify_token
def updateAddress(field):
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    if field == "add":
        address = request.json.get("address")
        mongo.db.address_book.update_one(
            {"email": email},
            {
                "$push":
                {
                    "address":
                    {
                        "addressId": generate_custom_id(),
                        "addressData": address
                    }
                }
            },
            upsert=True
        )
    elif field == "update":
        address = request.json.get("address")
        addressId = request.json.get("addressId")
        mongo.db.address_book.update_one(
            {
                "email": email,
                "address.addressId": addressId
            },
            {
                "$set": {
                    "address.$.addressData": address
                }
            }
        )
    elif field == "remove":
        addressId = request.json.get("addressId")
        mongo.db.address_book.update_one(
            {
                "email": email,
            },
            {
                "$pull": {
                    "address": {"addressId": addressId}
                }
            }
        )
    else:
        return jsonify({"message": "Invalid Data"})
    return jsonify({"message": "Success"})


@socketio.on('connect')
def connected():
    print("SID is", request.sid)
    emit("myresponse", {"status": "connected"})
    return {}


@socketio.on("registerSid")
@cross_origin()
def registerSidEvent(data):
    cartId = data.get("cartId")
    print("CartID: ", cartId)
    if cartId:
        mongo.db.menu.update_one({"cartId": cartId}, {
                                 "$push": {"sid": request.sid}})
        emit("regResponse", {"status": "registered"})
        return {}
    emit("regResponse", {"status": "failed"})
    return {}


@socketio.on("registerSidByCustomer")
@cross_origin()
def registerSidByCustomer(data):
    token = data.get("token")
    print("Token: ", token)
    clientEmail = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })['email']
    if clientEmail:
        mongo.db.customer_sid.update_one({"email": clientEmail}, {
            "$push": {"sid": request.sid}})
        emit("customerResponse", {"status": "registered"})
        return {}
    emit("customerResponse", {"status": "failed"})
    return {}


@socketio.on("getOrderByOrderId")
@cross_origin()
def getOrderByOrderIdEvent(data):
    orderId = data.get("orderId")
    if orderId:
        newOrders = mongo.db.online_orders.find_one(
            {"orderId": orderId},
            {"_id": 0})
        address = mongo.db.device_ids.find_one(
            {"device_id": newOrders['cartId']},
            {"_id": 0}
        )
        city = address['town']
        location = address['location']
        newOrders['location'] = location
        newOrders['city'] = city
        emit("getOrderByOrderId", newOrders, json=True)
        return {}
    emit("getOrderByOrderId", {"message": "No orderId sent"})
    return {}


@ socketio.on("allOrderStatus")
@ cross_origin()
def allOrderStatusEvent(data):
    token = data.get("token")
    clientEmail = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })['email']
    if clientEmail:
        orders = mongo.db.online_orders.find(
            {"customerEmail": clientEmail}, {"_id": 0})
        emit("allOrderStatus", {"orders": list(orders)}, json=True)
        return {}
    emit("allOrderStatus", {"message": "No clientEmail sent"})
    return {}


if __name__ == "__main__":
    print("starting...")
    socketio.run(app,
                 host=cfg.OrderFlask['HOST'],
                 port=cfg.OrderFlask['PORT'],
                 # threaded=cfg.OrderFlask['THREADED'],
                 debug=False)
