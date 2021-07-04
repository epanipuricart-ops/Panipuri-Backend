from flask import (Flask, request, jsonify)
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
from functools import wraps
from config import config as cfg


app = Flask(__name__, static_url_path='')

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb+srv://gnosticplayer:hacked123@cluster0.qarzu.mongodb.net/panipuri"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
socketio = SocketIO(app)
cred = credentials.Certificate('config/fbAdminSecret.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('config/fbConfig.json')))


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
    valid_fields = [
        "cartId",
        "customerName",
        "customerPhone",
        "customerEmail",
        "deliveryAddress",
        "orderType",
        "modeOfPayment",
        "transactionId"]
    if "orderType" not in data:
        data["orderType"] = "delivery"
    if "transactionId" not in data:
        data["transactionId"] = ""
    createOrder = {field: value for field,
                   value in data.items() if field in valid_fields}

    if len(createOrder) == len(valid_fields):
        email = createOrder['customerEmail']
        cart = mongo.db.order_cart.find_one_and_delete(
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
                        "gst": 1,
                        "sid": 1,
                        "price": "$menu.items.price"
                    }
                }
            ])

        data = list(data)
        extraData = {"subTotal": 0,
                     "gst": data[0]["gst"], "sid": data[0]["sid"]}
        for d in data:
            extraData["subTotal"] += d["price"]*itemsDict.get(d["itemId"], 1)
        orderFields = {
            "orderId": generate_custom_id(),
            "timestamp": int(round(time.time() * 1000)),
            "orderStatus": "placed",
            "subTotal": extraData["subTotal"],
            "gst": extraData["gst"],
            "total": round(
                (1+extraData["gst"]/100)*extraData["subTotal"], 2)
        }
        createOrder.update(orderFields)
        mongo.db.online_orders.insert_one(createOrder)
        createOrder.pop("_id")
        socketio.emit("receiveOrder", createOrder,
                      json=True, room=extraData["sid"])
        return jsonify(createOrder)
    return jsonify({"message": "Missing fields while creating order"})


@app.route('/orderOnline/updateOrderStatus', methods=['POST'])
@cross_origin()
@verify_token
def updateOrderStatus():
    data = request.json
    orderId = data.get("orderId")
    status = data.get("status")
    if orderId and status:
        mongo.db.online_orders.update_one(
            {"orderId": orderId},
            {"$set": {
                "orderStatus": status
            }})
        return jsonify({"message": "Success"})
    return jsonify({"message": "Missing fields"}), 400


@socketio.on("registerSid")
def registerSidEvent(data):
    cartId = data.get("cartId")
    if cartId:
        mongo.db.menu.update_one({"cartId": cartId}, {
                                 "$set": {"sid": request.sid}})


@socketio.on("getOrderByOrderId")
def getOrderByOrderIdEvent(data):
    orderId = data.get("orderId")
    if orderId:
        newOrders = mongo.db.online_orders.find_one(
            {"orderId": orderId},
            {"_id": 0})
        emit("getOrderByOrderId", newOrders, json=True)
        return
    emit("getOrderByOrderId", {"message": "No orderId sent"})


@socketio.on("allOrderStatus")
def allOrderStatusEvent(data):
    clientEmail = data.get("clientEmail")
    if clientEmail:
        orders = mongo.db.online_orders.find(
            {"customerEmail": clientEmail}, {"_id": 0})
        emit("allOrderStatus", {"orders": list(orders)}, json=True)
        return
    emit("allOrderStatus", {"message": "No clientEmail sent"})


if __name__ == "__main__":
    print("starting...")
    socketio.run(app,
                 host=cfg.OrderFlask['HOST'],
                 port=cfg.OrderFlask['PORT'],
                 threaded=cfg.OrderFlask['THREADED'],
                 debug=True)
