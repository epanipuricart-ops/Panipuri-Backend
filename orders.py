from flask import (Flask, request, jsonify)
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from firebase_admin import credentials, auth
import pyrebase
import json
import time
import os
import binascii
from functools import wraps
from config import config as cfg


app = Flask(__name__, static_url_path='')

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://localhost:27017/panipuriKartz"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
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


@app.route('/getMenu', methods=['GET'])
@cross_origin()
@verify_token
def getMenu():
    cartId = request.args.get("cartId")
    if not cartId:
        return jsonify({"message": "No Cart ID sent"}), 400
    cart = mongo.db.menu.find_one({"cartId": cartId}, {"_id": 0})
    return jsonify(cart or {})


@app.route('/updateMenu/<field>', methods=['POST'])
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
        valid_fields = ["isActive"]
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


@app.route('/createMenu/<field>', methods=['POST'])
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


if __name__ == "__main__":
    print("starting...")
    app.run(host=cfg.OrderFlask['HOST'],
            port=cfg.OrderFlask['PORT'],
            threaded=cfg.OrderFlask['THREADED'],
            debug=True)
