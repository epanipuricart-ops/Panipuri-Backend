from flask import (Flask, session, send_from_directory, send_file,
                   render_template)
from flask import request, redirect, url_for
from flask_pymongo import PyMongo
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_apscheduler import APScheduler
import time
import os
import binascii
from werkzeug.utils import secure_filename
from datetime import datetime
import config.config as cfg
from modules import *
import firebase_admin
import pyrebase
from firebase_admin import credentials, auth
import jwt
from functools import wraps
import requests
import json
import random
import shutil
import re

UPLOAD_FOLDER = 'public/img'
AGREEMENT_PDF_FOLDER = 'public/agreement_pdf'
BLOG_PHOTO_FOLDER = 'public/blog'
# INTERMEDIATE_FOLDER = 'intermediate'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, static_url_path='')

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://localhost:27017/panipuriKartz"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

cred = credentials.Certificate('config/fbAdminSecret.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('config/fbConfig.json')))
global_key = "ueQ4sZ"
spring_url = "http://15.207.147.88:8080/"
agreement_url = "http://15.207.147.88:8081/"
mailer_url = "http://15.207.147.88:8082/"
payment_url = "http://15.207.147.88:8083/"

ZOHO_TOKEN = {"access_token": "", "timestamp": time.time()}


def verify_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('Authorization'):
            print(request.headers)
            return {'message': 'MissingParameters'}, 400
        try:
            user = auth.verify_id_token(request.headers['Authorization'])
            request.user = user
        except:
            return {'message': 'Authentication Error'}, 401
        return f(*args, **kwargs)

    return wrap


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_last_id(city):
    data = mongo.db.city_wise_count.find_one_and_update(
        {"city": re.compile(city, re.IGNORECASE)},
        {"$inc": {
            "value": 1
        }})
    if data:
        new_id = "epanipuricart." + data["city"] + "." + str(data["value"])
    else:
        new_id = "epanipuricart.dummy.5"
    return new_id


def generate_custom_id():
    return (
        binascii.b2a_hex(os.urandom(4)).decode() +
        hex(int(time.time()*10**5) % 10**12)[2:]
    )


def refresh_zoho_access_token():
    if (
        ZOHO_TOKEN["access_token"] == "" or
        time.time()-ZOHO_TOKEN["timestamp"] >= 1800
    ):
        refresh_token_url = "https://accounts.zoho.in/oauth/v2/token"
        response = requests.post(
            refresh_token_url,
            data={
                "refresh_token": cfg.ZohoConfig["refresh_token"],
                "client_id": cfg.ZohoConfig["client_id"],
                "client_secret": cfg.ZohoConfig["client_secret"],
                "grant_type": "refresh_token"
            }).json()
        ZOHO_TOKEN["access_token"] = response["access_token"]
        ZOHO_TOKEN["timestamp"] = time.time()


def send_data_to_zoho(clients):
    zoho_records = [{
        "First_Name": client.get("firstName"),
        "Last_Name": client.get("lastName"),
        "Email": client.get("email"),
        "Phone": client.get("mobile")
    } for client in clients]
    refresh_zoho_access_token()
    contacts = "https://www.zohoapis.in/crm/v2/Contacts"
    header = {"Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]}
    data = {
        "data": zoho_records,
        "trigger": [
            "approval",
            "workflow",
            "blueprint"
        ]
    }
    response = requests.post(contacts, headers=header, json=data).json()
    zoho_customers = []
    for i, client in enumerate(clients):
        response_record = response["data"][i]
        if response_record["code"].upper() == "SUCCESS":
            zoho_customers.append({
                "email": client.get("email"),
                "zohoId": response_record["details"]["id"]})
    mongo.db.zoho_customer.insert_many(zoho_customers)


@app.route('/franchisee/register/<path:path>', methods=['POST'])
@cross_origin()
def register(path):
    token = request.headers['Authorization']
    if path.lower() == 'subscriber':
        decoded = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })
        email = decoded['email']
        firebase_id = decoded['user_id']
        mobile = request.json['mobile']
        title = request.json['title']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        doc = {
            "email": email,
            "mobile": mobile,
            "title": title,
            "firstName": firstName,
            "lastName": lastName,
            "firebase_id": firebase_id,
            "roles": ['subscriber', 'customer'],
            "exportedZoho": False
        }
        try:
            mongo.db.clients.insert_one(doc)
            # send_data_to_zoho(doc)
            return jsonify({
                "title": doc['title'],
                "firstName": doc['firstName'],
                "lastName": doc['lastName'],
                "email": doc['email'],
                "mobile": doc['mobile'],
                "roles": doc['roles']
            })
        except Exception:
            return jsonify({"message": "Some error occurred"}), 500

    elif path.lower() == 'customer':
        decoded = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })
        email = decoded['email']
        firebase_id = decoded['user_id']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        mobile = request.json['mobile']
        title = request.json['title']
        doc = {
            "email": email,
            "mobile": mobile,
            "firstName": firstName,
            "title": title,
            "lastName": lastName,
            "firebase_id": firebase_id,
            "roles": ['customer'],
            "exportedZoho": False
        }
        try:
            mongo.db.clients.insert_one(doc)
            return jsonify({
                "title": doc['title'],
                "firstName": doc['firstName'],
                "lastName": doc['lastName'],
                "email": doc['email'],
                "mobile": doc['mobile'],
                "roles": doc['roles']
            })
        except Exception:
            return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/login/<path:path>', methods=['POST'])
@cross_origin()
@verify_token
def login(path):
    if path.lower() == 'subscriber':
        token = request.headers['Authorization']
        decoded = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })
        data = mongo.db.clients.find_one({'firebase_id': decoded['user_id']})
        if data:
            if 'subscriber' in data['roles']:
                return jsonify({
                    "title": data['title'],
                    'firstName': data['firstName'],
                    'lastName': data['lastName'],
                    'email': data['email'],
                    'id': data['firebase_id'],
                    'mobile': data['mobile'],
                    'roles': data['roles']
                })
            else:
                if 'customer' in data['roles']:
                    mongo.db.clients.update_one(
                        {'firebase_id': decoded['user_id']},
                        {'$push': {
                            'roles': 'subscriber'
                        }})
                else:
                    return jsonify({'message': 'Unauthorised Access'}), 403
        else:
            return jsonify({"message": "User not registered"}), 401

    elif path.lower() == 'customer':
        token = request.headers['Authorization']
        decoded = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })
        data = mongo.db.clients.find_one({'firebase_id': decoded['user_id']})
        if data:
            if 'customer' in data['roles']:
                return jsonify({
                    "title": data['title'],
                    'firstName': data['firstName'],
                    'lastName': data['lastName'],
                    'email': data['email'],
                    'id': data['firebase_id'],
                    'mobile': data['mobile'],
                    'roles': data['roles']
                })
            else:
                return jsonify({'message': 'Unauthorised Access'}), 403
        else:
            return jsonify({"message": "User not registered"}), 401

    elif path.lower() == 'super':
        token = request.headers['Authorization']
        decoded = jwt.decode(token,
                             options={
                                 "verify_signature": False,
                                 "verify_aud": False
                             })
        data = mongo.db.clients.find_one({'firebase_id': decoded['user_id']})
        if data:
            if 'super' in data['roles']:
                return jsonify({
                    'name': data['name'],
                    'email': data['email'],
                    'id': data['firebase_id'],
                    'mobile': data['mobile'],
                    'roles': data['roles']
                })
            else:
                return jsonify({"message": "User Not Authorised"}), 403
        else:
            return jsonify({"message": "User not registered"}), 401


@app.route('/franchisee/getProfile', methods=['GET'])
@cross_origin()
@verify_token
def getProfile():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    try:
        obj = mongo.db.clients.find_one({"email": email})
        if obj:
            data = {}
            for ele in obj:
                if ele != "_id":
                    data[ele] = obj[ele]
            return data
        else:
            return jsonify({"message", "No data found"}), 404
    except:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/sendOTP', methods=['POST'])
@cross_origin()
def sendOTP():
    msg = "__OTP__ is your One Time Password for phone verification"
    typeOfMessage = 1
    if 'phone' in request.json:
        phone = request.json['phone']
        email = request.json['email']
        #email = 'jyotimay16@gmail.com'
        name = request.json['firstName']
        data = {"message": msg, "phone": phone, "name": name,
                "email": email, "type": typeOfMessage}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        num = mongo.db.clients.find_one({"mobile": phone})
        if False:
            return jsonify({"message":
                            "Mobile number already registered"}), 423
        else:
            try:
                response = requests.post(spring_url +
                                         'api/message/send-message',
                                         data=json.dumps(data),
                                         headers=headers)
                json_resp = json.loads(response.text)
                return json_resp
            except:
                return jsonify({"message": "Some Error Occurred"}), 500
    else:
        return jsonify({"message": "Missing Parameters"}), 400


@app.route('/franchisee/verifyOTP', methods=['POST'])
@cross_origin()
def verifyOTP():
    if ('phone' in request.json) and ('token'
                                      in request.json) and ('otp'
                                                            in request.json):
        phone = request.json['phone']
        token = request.json['token']
        otp = request.json['otp']
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            target_url = 'api/message/verify-otp/{}/phone/{}/otp/{}'.format(
                token, phone, otp)
            response = requests.get(spring_url + target_url, headers=headers)
            json_resp = json.loads(response.text)
            return json_resp
        except:
            return jsonify({"message": "Some Error Occurred"}), 500
    else:
        return jsonify({"message": "Missing Parameters"}), 400


@app.route('/franchisee/resendOTP', methods=['POST'])
@cross_origin()
def reSendOTP():
    msg = "__OTP__ is your One Time Password for phone verification"
    typeOfMessage = 3
    if 'phone' in request.json:
        phone = request.json['phone']
        token = request.json['token']
        data = {"message": msg, "phone": phone, "type": typeOfMessage}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            response = requests.post(
                spring_url + 'api/message/send-message?token={}'.format(token),
                data=json.dumps(data),
                headers=headers)
            json_resp = json.loads(response.text)
            return json_resp
        except:
            return jsonify({"message": "Some Error Occurred"}), 500
    else:
        return jsonify({"message": "Missing Parameters"}), 400


@app.route('/franchisee/saveGeneralInformation', methods=['POST'])
@cross_origin()
@verify_token
def saveGeneralForm():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    obj = mongo.db.general_forms.find_one({'email': email})
    if 'title' in request.json:
        title = str(request.json['title'])
    else:
        title = ''
    if 'firstName' in request.json:
        firstName = str(request.json['firstName'])
    else:
        firstName = ''
    if 'lastName' in request.json:
        lastName = str(request.json['lastName'])
    else:
        lastName = ''
    if 'mobile' in request.json:
        mobile = str(request.json['mobile'])
    else:
        mobile = ''
    if 'aadhar' in request.json:
        aadhar = str(request.json['aadhar'])
    else:
        aadhar = ''

    if 'fatherName' in request.json:
        fatherName = str(request.json['fatherName'])
    else:
        fatherName = ''

    if 'address' in request.json:
        address = str(request.json['address'])
    else:
        address = ''

    if 'town' in request.json:
        town = str(request.json['town'])
    else:
        town = ''

    if 'pincode' in request.json:
        pincode = str(request.json['pincode'])
    else:
        pincode = ''

    if 'state' in request.json:
        state = str(request.json['state'])
    else:
        state = ''

    if 'location' in request.json:
        location = str(request.json['location'])
    else:
        location = ''

    if 'termsAndConditions' in request.json:
        termsAndConditions = str(request.json['termsAndConditions'])
    else:
        termsAndConditions = ''

    if obj:
        try:
            mongo.db.general_forms.update_one({"email": email}, {
                "$set": {
                    "title": title,
                    "firstName": firstName,
                    "lastName": lastName,
                    "mobile": mobile,
                    "aadhar": aadhar,
                    "fatherName": fatherName,
                    "address": address,
                    "town": town,
                    "pincode": pincode,
                    "state": state,
                    "location": location,
                    "termsAndConditions": termsAndConditions
                }
            })
            return jsonify({"message": "Successfully saved"})
        except:
            return jsonify({"message": "Some error occurred"}), 500
    else:
        try:
            mongo.db.general_forms.insert_one({
                "title":
                title,
                "firstName":
                firstName,
                "lastName":
                lastName,
                "mobile":
                mobile,
                "aadhar":
                aadhar,
                "email":
                email,
                "fatherName":
                fatherName,
                "address":
                address,
                "town":
                town,
                "pincode":
                pincode,
                "state":
                state,
                "termsAndConditions":
                termsAndConditions
            })
            return jsonify({"message": "Successfully saved"})
        except:
            return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/getGeneralInformation', methods=['GET'])
@cross_origin()
@verify_token
def getGeneralInformation():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    try:
        obj = mongo.db.general_forms.find_one({"email": email})
        if obj:
            data = {}
            for ele in obj:
                if ele != "_id":
                    data[ele] = obj[ele]
            return data
        else:
            return jsonify({"message", "No saved data"}), 404
    except:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/getCosting', methods=['GET'])
@cross_origin()
@verify_token
def getCosting():
    try:
        data = mongo.db.costing.find()
        arr = []
        for ele in data:
            d = {}
            d['name'] = ele['name']
            d['dateModified'] = ele['dateModified']
            d['price'] = ele['price']
            d['uid'] = ele['uid']
            d['modelType'] = ele['modelType']
            d['extension'] = ele['extension']
            arr.append(d)
        return jsonify({"items": arr})

    except:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route('/franchisee/updateCosting', methods=['POST'])
@cross_origin()
@verify_token
def updateCosting():
    uid = request.json['uid']
    price = float(request.json['price'])
    try:
        data = mongo.db.costing.find_one({"uid": uid})
        mongo.db.costing.update_one({"uid": uid}, {
            "$set": {
                "price": price,
                "dateModified": int(round(time.time() * 1000))
            }
        })
        post = {}
        for ele in data:
            if ele != "_id":
                post[ele] = data[ele]
        mongo.db.costing_history.insert_one(post)
        return jsonify({"message": "Success"})
    except:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route('/franchisee/payNow', methods=['POST'])
@cross_origin()
@verify_token
def payNow():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    model_uid = int(request.json['uid'])
    model_data = mongo.db.costing.find_one({"uid": model_uid})
    email = decoded['email']
    client_data = mongo.db.clients.find_one({"email": email})
    firstName = client_data['firstName']
    phone = client_data['mobile']

    post = {
        "key":
        global_key,
        "amount":
        str(0.5 * model_data['price']),
        "phone":
        phone,
        "productinfo":
        (model_data['name'] + " " + model_data['extension']).rstrip(),
        "surl":
        "http://15.207.147.88:5000/franchisee/payuSuccess",
        "furl":
        "http://15.207.147.88:5000/franchisee/payuFailure",
        "firstname":
        firstName,
        "email":
        email,
        "service_provider":
        "payu_paisa"
    }
    # print(post)
    res = requests.post(payment_url + '/api/payment/checkout', json=post)
    res = res.json()
    # print(res)
    hash_uid = mongo.db.hash_counter.find_one({"id": 1})['hash_uid']
    res['payment_uid'] = hash_uid
    mongo.db.hash_map.insert_one({
        "hash_uid":
        hash_uid,
        "initiated_date":
        int(round(time.time() * 1000)),
        "hash":
        res['hash'],
        "email":
        email,
        "model_uid":
        model_uid,
        "amount":
        0.5 * model_data['price'],
        "status":
        0,
        "transaction_id":
        res['txnid'],
        "bank_ref_num":
        "",
        "mihpayid":
        ""
    }),
    mongo.db.hash_counter.update_one({"id": 1},
                                     {"$set": {
                                         "hash_uid": hash_uid + 1
                                     }})
    return res


@app.route('/franchisee/checkPaymentStatus', methods=['POST'])
@cross_origin()
@verify_token
def checkPaymentStatus():
    hash_uid = request.json['payment_uid']
    payment_status = mongo.db.hash_map.find_one({"hash_uid":
                                                 hash_uid})['status']
    return jsonify({"payment_status": payment_status})


@app.route('/franchisee/payuSuccess', methods=['POST'])
@cross_origin()
def payuSuccess():
    date = int(round(time.time() * 1000))
    bank_ref_num = request.form['bank_ref_num']
    mihpayid = request.form['mihpayid']
    transaction_id = request.form['txnid']
    txn_data = mongo.db.hash_map.find_one({"transaction_id": transaction_id})
    mongo.db.hash_map.update_one({"transaction_id": transaction_id}, {
        "$set": {
            "status": 1,
            "bank_ref_num": bank_ref_num,
            "mihpayid": mihpayid
        }
    })
    mongo.db.clients.update_one({"email": txn_data['email']},
                                {"$addToSet": {
                                    "roles": "paid_subscriber"
                                }})
    mongo.db.transaction_history.insert_one({
        "transaction_id": transaction_id,
        "completedDate": date
    })

    model_uid = txn_data['model_uid']
    model_image = mongo.db.costing.find_one({"uid": model_uid})['model_image']
    order_id = mongo.db.order_num.find_one({"id": 1})['order_id']
    mongo.db.orders.insert_one({
        "email": txn_data['email'],
        "order_id": "EK-" + str(order_id),
        "model_uid": txn_data['model_uid'],
        "date": date,
        "status": "pending",
        "model_image": model_image,
        "deliveryDate": ""
    })
    data = mongo.db.general_forms.find_one({"email": txn_data['email']})
    city = data['town']
    device_id = get_last_id(city)
    mongo.db.device_ids.insert_one({
        "email": txn_data['email'],
        "device_id": device_id,
        "state": data.get("state"),
        "town": city,
        "location": data.get("location"),
        "order_id": "EK-" + str(order_id)
    })
    mongo.db.order_history.insert_one({
        "order_id": order_id,
        "status": "pending",
        "date": date
    })
    mongo.db.order_num.update_one({"id": 1},
                                  {"$set": {
                                      "order_id": order_id + 1
                                  }})
    payload = {
        "attachmentPaths": [],
        "bccAddresses": [],
        "ccAddresses": [],
        "mailBody": "Your payment is confirmed.",
        "mailSubject": "Payment Confirmation",
        "toAddresses": [txn_data['email'], "ceo@epanipuricart.com"]
    }
    requests.post(mailer_url + 'send-mail', json=payload)
    return render_template('index.html')


@app.route('/franchisee/payuFailure', methods=['POST'])
@cross_origin()
def payuFailure():
    transaction_id = request.form['txnid']
    mongo.db.hash_map.update_one({"transaction_id": transaction_id},
                                 {"$set": {
                                     "status": -1
                                 }})
    return render_template('fail.html')


@app.route('/franchisee/getPrescription', methods=['GET'])
@cross_origin()
def prescription():
    return render_template('prescription.html')


@app.route('/franchisee/getModelImage/<path:path>', methods=['GET'])
@cross_origin()
@verify_token
def getModelImage(path):
    return send_from_directory('public/model-images', path)


@app.route('/franchisee/getAgreementData', methods=['GET'])
@cross_origin()
@verify_token
def getAgreementData():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded["email"]
    response = mongo.db.docs.find(
        {
            "email": email,
            "eAadharSign": 1
        }, {"_id": 0})
    result = []
    for document in response:
        result.append(
            {
                "variablePdf": document.get("pdf"),
                "fixedPdf": document.get("agreement_pdf"),
                "order_id": document.get("order_id"),
                "eAadharSign": 1
            })
    return jsonify({
        "result": result
    })


@app.route('/franchisee/getLatestOrder', methods=['GET'])
@cross_origin()
@verify_token
def getLatestOrder():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    try:
        data = mongo.db.orders.find({"email": email}).sort("date", -1)
        d = {}
        for x in data[0]:
            if x != "_id":
                d[x] = data[0][x]
        return d
    except:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/getAllOrders', methods=['GET'])
@cross_origin()
@verify_token
def getAllOrders():

    data = mongo.db.orders.find().sort("date", -1)
    all_orders = []
    for items in data:
        if items['status'] != 'pending':
            d = {}
            email = mongo.db.docs.find_one({"order_id":
                                            items['order_id']})['email']
            name1 = mongo.db.clients.find_one({"email": email})['firstName']
            name2 = mongo.db.clients.find_one({"email": email})['lastName']
            d['email'] = email
            d['name'] = name1 + " " + name2
            for keys in items:
                if keys != "_id":
                    d[keys] = items[keys]
            all_orders.append(d)

    return jsonify({"orders": all_orders})
    '''try:
        data = mongo.db.orders.find().sort("date",-1)
        all_orders = []
        for items in data:
            d = {}
            email = mongo.db.docs.find_one(
                {"order_id": items['order_id']})['email']
            name = mongo.db.clients.find_one({"email"})['name']
            d['email'] = email
            d['name'] = name
            for keys in items:
                if keys != "_id":
                    d[keys] = items[keys]
            all_orders.append(d)

        return jsonify({"orders": all_orders})
    except:
        return jsonify({"message": "Some error occurred"}), 500'''


@app.route('/franchisee/uploadDocuments', methods=['POST'])
@cross_origin()
@verify_token
def uploadDocuments():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    user_id = decoded['user_id']
    order_id = request.form['order_id']
    if 'files[]' not in request.files:
        return jsonify({"message": "Missing files"}), 400
    else:
        data = mongo.db.docs.find_one({"order_id": order_id})
        if data is None:
            mongo.db.docs.insert_one({
                "email": email,
                "sign": "",
                "aadhar": "",
                "photo": "",
                "order_id": order_id,
                "pdf": "",
                "agreement-pdf": "",
                "eAadharSign": -1
            })
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                for ele in request.form:
                    if file.filename.lower() == request.form[ele].lower():
                        filename_temp = secure_filename(file.filename)
                        extension = filename_temp.split('.')[-1]
                        timestamp = int(round(time.time() * 1000))
                        hex_form = str(hex(timestamp *
                                           random.randint(1, 5)))[2:]
                        enc_filename = str(ele) + "_" + hex_form + str(
                            user_id[-4:]) + "." + extension
                        try:
                            mongo.db.docs.update_one(
                                {"order_id": order_id},
                                {"$set": {
                                    str(ele): enc_filename
                                }})
                            file.save(
                                os.path.join(app.config['UPLOAD_FOLDER'],
                                             enc_filename))

                        except:
                            return jsonify({"message":
                                            "Some Error Occurred"}), 500

        user_data = mongo.db.general_forms.find_one({"email": email})
        docs_data = mongo.db.docs.find_one({"email": email})
        # base_path = r"C:\Users\Administrator\Desktop\EPanipuriKartz\Backend"
        name = user_data['title'] + user_data['firstName'] + " " + user_data[
            'lastName']
        aadhar = user_data['aadhar']
        brand = "E-Panipurii Kartz"
        customer_id = "epanipuricart.dummy.1"
        model = "Table Top"
        model_extension = "3-nozzle system"
        fName = user_data['fatherName']
        address = user_data['address'] + ',' + user_data[
            'state'] + ',' + user_data['town'] + ',' + str(
                user_data['pincode'])
        mobile = user_data['mobile']
        amount = "6000"
        aadharLogoPath = os.path.join(app.config['UPLOAD_FOLDER'],
                                      docs_data['aadhar'])
        ap = str(os.path.abspath(aadharLogoPath))
        customerPhotoPath = os.path.join(app.config['UPLOAD_FOLDER'],
                                         docs_data['photo'])
        cp = str(os.path.abspath(customerPhotoPath))
        customerSignaturePath = os.path.join(app.config['UPLOAD_FOLDER'],
                                             docs_data['sign'])
        cs = str(os.path.abspath(customerSignaturePath))
        post = {
            "name": name,
            "email": email,
            "aadhar": aadhar,
            "address": address,
            "brand": brand,
            "customerId": customer_id,
            "model": model,
            "extension": model_extension,
            "fname": fName,
            "mobile": mobile,
            "amount": amount,
            "aadharLogoPath": ap,
            "customerPhotoPath": cp,
            "customerSignaturePath": cs
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            response = requests.post(agreement_url + 'generate-agreement',
                                     data=json.dumps(post),
                                     headers=headers)
            print(response.text)
            mongo.db.clients.update_one({"email": email},
                                        {"$addToSet": {
                                            "roles": "franchisee"
                                        }})
            mongo.db.orders.update_one({"order_id": order_id},
                                       {"$set": {
                                           "status": "placed"
                                       }})
            mongo.db.order_history.insert_one({
                "order_id":
                order_id,
                "status":
                "placed",
                "date":
                int(round(time.time() * 1000))
            })
            mongo.db.docs.update_one({"order_id": order_id},
                                     {"$set": {
                                         "pdf": str(response.text)
                                     }})
            # payload = {
            #             "attachmentPaths": [
            #                 response.text
            #             ],
            #             "bccAddresses": [],
            #             "ccAddresses": [],
            #             "mailBody": "Test Agreement Mail",
            #             "mailSubject": "Agreement Mail",
            #             "toAddresses": [
            #                 email, "ceo@epanipuricart.com", "jyotimay16@gmail.com"
            #             ]
            #         }
            # requests.post(mailer_url+'send-mail',json=payload)
            return jsonify({"output": str(response.text)})
        except Exception:
            return jsonify({"message": "Service Error"}), 423


@app.route('/franchisee/getMOU', methods=['GET', 'POST'])
@cross_origin()
@verify_token
def getMOU():
    path = request.args.get('path')
    try:
        return send_file(path, as_attachment=True)
    except:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route("/franchisee/getFigures", methods=['GET'])
@cross_origin()
def getFigures():
    obj = mongo.db.company_figures.find_one({"id": 1})
    data = {}
    for ele in obj:
        if ele != "_id":
            data[ele] = obj[ele]
    return jsonify(data)


@app.route("/franchisee/saveFigures", methods=['POST'])
@cross_origin()
@verify_token
def saveFigures():
    town = request.json['town']
    masterKitchen = request.json['masterKitchen']
    ePanipuriKartz = request.json['ePanipuriKartz']
    customer = request.json['customer']
    mongo.db.company_figures.update_one({'id': 1}, {
        "$set": {
            "customer": customer,
            "ePanipuriKartz": ePanipuriKartz,
            "town": town,
            "masterKitchen": masterKitchen
        }
    })
    return jsonify({"message": "Success"})


@app.route('/franchisee/updateOrder', methods=['POST'])
@cross_origin()
@verify_token
def updateOrder():
    order_id = request.json['order_id']
    status = request.json['status']
    deliveryDate = request.json.get('deliveryDate')
    order = {"order_id": order_id, "status": status}
    if mongo.db.order_history.find_one(order):
        return jsonify({"message": "Status already used"}), 500
    if deliveryDate:
        order.update({"deliverDate": deliveryDate})
    try:
        mongo.db.orders.update_one(
            {"order_id": order_id},
            {"$set": order})
        mongo.db.order_history.insert_one({
            "order_id": order_id,
            "status": status,
            "date": int(round(time.time() * 1000))
        })
        return jsonify({"message": "Success"})
    except Exception:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route('/franchisee/getPersonalOrders', methods=['GET'])
@cross_origin()
@verify_token
def getPersonalOrders():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    orders_list = mongo.db.orders.find(
        {"email": email},
        {"_id": 0}).sort("date", -1)
    return jsonify(list(orders_list))


@app.route('/franchisee/getTrackingHistory', methods=['GET'])
@cross_origin()
@verify_token
def getTrackingHistory():
    order_id = request.args.get('order_id')
    order_history = mongo.db.order_history.find({
        "order_id": order_id
    }, {
        "_id": 0
    }).sort("date", -1)
    return jsonify(list(order_history))


@app.route('/franchisee/getOrderById', methods=['GET'])
@cross_origin()
@verify_token
def getOrderById():
    order_id = request.args.get('order_id')
    order_status = mongo.db.orders.find_one({
        "order_id": order_id
    }, {
        "_id": 0
    })
    return jsonify(order_status or {})


@app.route('/franchisee/uploadAgreement', methods=['POST'])
@cross_origin()
@verify_token
def uploadAgreement():
    orderId = request.form.get('orderId')
    agreement_file = request.files.get('file')
    if not orderId:
        return jsonify({"message": "No order ID provided"}), 400
    if not agreement_file:
        return jsonify({"message": "No file provided"}), 400
    if agreement_file.filename.endswith(".pdf"):
        hex_form = generate_custom_id()
        enc_filename = "agreement_" + orderId + "_" + hex_form + ".pdf"
        enc_filename = secure_filename(enc_filename)
        try:
            save_path = os.path.abspath(
                os.path.join(AGREEMENT_PDF_FOLDER, enc_filename))
            mongo.db.docs.update_one({"order_id": orderId},
                                     {"$set": {
                                         "agreement_pdf": save_path,
                                         "eAadharSign": 0
                                     }})
            agreement_file.save(save_path)

            return jsonify({"message": "Success"})
        except Exception:
            return jsonify({"message": "Some Error Occurred"}), 500
    return jsonify({"message": "Only PDF files allowed"}), 400


@app.route('/franchisee/subscribeNewsletter', methods=['POST'])
@cross_origin()
def subscribeNewsletter():
    emailID = request.json.get('email')
    if emailID:
        if mongo.db.newsletter.find_one({"email": emailID}):
            return jsonify({"message": "EMail already subscribed"})
        mongo.db.newsletter.insert_one({"email": emailID})
        return jsonify({"message": "Success"})
    return jsonify({"message": "No email provided"}), 400


@app.route('/franchisee/saveBlog', methods=['POST'])
@cross_origin()
@verify_token
def saveBlog():
    title = request.form.get('title')
    photo = request.files.get('photo')
    content = request.form.get('content')
    if not photo:
        return jsonify({"message": "No file provided"}), 400
    ext = photo.filename.lower().split(".")[-1]
    if ext in ["jpg", "png", "PNG", "jpeg"]:
        hex_form = generate_custom_id()
        enc_filename = "photo_" + hex_form + "." + ext
        enc_filename = secure_filename(enc_filename)
        try:
            save_path = os.path.join(BLOG_PHOTO_FOLDER, enc_filename)
            mongo.db.blogs.insert_one(
                {
                    "blogId": hex_form,
                    "title": title,
                    "content": content,
                    "photo": enc_filename,
                    "date": int(round(time.time() * 1000)),
                })
            photo.save(save_path)
            return jsonify({"message": "Success"})
        except Exception:
            return jsonify({"message": "Some Error Occurred"}), 500
    return jsonify({"message": "Only JPG/PNG files allowed"}), 400


@app.route('/franchisee/getAllBlogs', methods=['GET'])
@cross_origin()
def getAllBlogs():
    blogs_list = mongo.db.blogs.find({}, {"_id": 0})
    return jsonify({"blogs": list(blogs_list)})


@app.route('/franchisee/getBlogImage/<path:path>', methods=['GET'])
@cross_origin()
def getBlogImage(path):
    return send_from_directory('public/blog', path)


@app.route('/franchisee/deleteBlog', methods=['POST'])
@cross_origin()
@verify_token
def deleteBlog():
    blogId = request.form.get('blogId')
    if not blogId:
        return jsonify({"message": "No Blog ID provided"}), 400
    data = mongo.db.blogs.find_one_and_delete({"blogId": blogId})
    try:
        os.remove(os.path.abspath(
            os.path.join(BLOG_PHOTO_FOLDER, data['photo'])))
    except Exception:
        pass
    return jsonify({"message": "Success"})


@app.route('/franchisee/updateBlog', methods=['POST'])
@cross_origin()
@verify_token
def updateBlog():
    title = request.form.get('title')
    photo = request.files.get('photo')
    content = request.form.get('content')
    blogId = request.form.get('blogId')
    oldBlog = mongo.db.blogs.find_one({"blogId": blogId})
    if not oldBlog:
        return jsonify({"message": "No such blog found"}), 400
    newBlog = {}
    if title:
        newBlog.update({"title": title})
    if content:
        newBlog.update({"content": content})
    if photo:
        try:
            os.remove(os.path.abspath(
                os.path.join(BLOG_PHOTO_FOLDER, oldBlog['photo'])))
        except Exception:
            pass
        ext = photo.filename.lower().split(".")[-1]
        if ext in ["jpg", "png"]:
            hex_form = generate_custom_id()
            enc_filename = "photo_" + hex_form + "." + ext
            enc_filename = secure_filename(enc_filename)
            try:
                save_path = os.path.abspath(
                    os.path.join(BLOG_PHOTO_FOLDER, enc_filename))
                photo.save(save_path)
                newBlog.update({"photo": enc_filename})
            except Exception:
                return jsonify({"message": "Some Error Occurred"}), 500
        else:
            return jsonify({"message": "Only JPG/PNG files allowed"}), 400
    if not newBlog:
        return jsonify({"message": "No changes done."})
    newBlog.update({"date": int(round(time.time() * 1000))})
    mongo.db.blogs.update_one(
        {"blogId": blogId},
        {"$set": newBlog})
    return jsonify({"message": "Success"})


@app.route('/franchisee/getClients', methods=['GET'])
@cross_origin()
@verify_token
def getClients():
    roles_list = request.args.get('roles', "").split(",")
    clients = mongo.db.clients.find(
        {"roles": {"$all": roles_list}},
        {"_id": 0, "firebase_id": 0})
    return jsonify({"clients": list(clients)})


@app.route('/franchisee/getCartId', methods=['GET'])
@cross_origin()
@verify_token
def getCartId():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    all_carts = mongo.db.device_ids.find({"email": email}, {"_id": 0})
    return jsonify({"result": list(all_carts)})


@app.route('/login/wizard', methods=['POST'])
@cross_origin()
def wizardLogin():
    email = request.json['email']
    device_id = request.json['customerId']
    data = mongo.db.device_ids.find_one({'device_id': device_id})
    alias_data = mongo.db.alias_data.find({'device_id': device_id})
    list_alias_email = []
    if alias_data:
        for ele in alias_data:
            list_alias_email.append(ele['alias_email'])
    if (email == data['email']):
        return jsonify({
            "message": "Successful Login",
            "customerId": device_id,
            "role": "franchisee"})
    elif (email in list_alias_email):
        return jsonify({
            "message": "Successful Login",
            "customerId": device_id,
            "role": "alias"})
    else:
        return jsonify({"message": "Authentication Error"}), 401


@app.route('/franchisee/addAliasData', methods=['POST'])
@cross_origin()
def addAliasData():
    alias_email = request.json['aliasEmail']
    alias_name = request.json['aliasName']
    device_id = request.json['customerId']
    data = mongo.db.alias_data.find({'device_id': device_id}, {"_id": 0})
    if (len(list(data)) == 2):
        return jsonify({"message": "Cannot Add more data"}), 400
    else:
        mongo.db.alias_data.insert_one({
            "device_id": device_id,
            "alias_email": alias_email,
            "alias_name": alias_name})
        return jsonify({"message": "Succesfully added"})


@app.route('/franchisee/getAliasData', methods=['GET'])
@cross_origin()
def getAliasData():
    device_id = request.args.get('customerId')
    data = mongo.db.alias_data.find({'device_id': device_id}, {"_id": 0})
    if data:
        print('debug')
        return jsonify({"result": list(data)})
    else:
        return jsonify({"result": "No result found"}), 404


@app.route('/franchisee/getMenu', methods=['GET'])
@cross_origin()
@verify_token
def getMenu():
    cartId = request.args.get("cartId")
    if not cartId:
        return jsonify({"message": "No Cart ID sent"}), 400
    cart = mongo.db.menu.find_one({"cartId": cartId}, {"_id": 0, "sid": 0})
    return jsonify(cart or {})


@app.route('/franchisee/updateMenu/<field>', methods=['POST'])
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


@app.route('/franchisee/getAllLocations', methods=['GET'])
@cross_origin()
@verify_token
def getAllLocations():
    state = request.args.get("state")
    town = request.args.get("town")
    if state and town:
        locations = mongo.db.device_ids.find(
            {"state": re.compile(state, re.IGNORECASE),
             "town": re.compile(town, re.IGNORECASE)},
            {"_id": 0, "location": 1, "device_id": 1})
        return jsonify({"locations": list(locations)})
    return jsonify({"message": "No State/City provided"}), 400


@app.route('/franchisee/getAllCategories', methods=['GET'])
@cross_origin()
@verify_token
def getAllCategories():
    categories = mongo.db.shopping_menu.find(
        {}, {"_id": 0, "categoryId": 1, "category": 1})
    return jsonify({"categories": list(categories)})


@app.route('/franchisee/getItemByCategory', methods=['GET'])
@cross_origin()
@verify_token
def getItemByCategory():
    category_list = request.args.get('categoryId', "").split(",")
    items = mongo.db.shopping_menu.find(
        {"categoryId": {"$in": category_list}},
        {"_id": 0})
    return jsonify({"items": list(items)})


@app.route('/franchisee/createShopCategory', methods=['POST'])
@cross_origin()
# @verify_token
def createShopCategory():
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

    valid_fields = ["category", "closeCategory"]
    createCategory = {field: value for field,
                      value in data.items() if field in valid_fields}

    if len(valid_fields) == len(createCategory):
        createCategory.update(
            {"categoryId": generate_custom_id(), "items": []})
        mongo.db.shopping_menu.insert_one(createCategory)
        return jsonify({
            "message": "Success",
            "categoryId": createCategory["categoryId"]})
    return jsonify({"message": "Missing fields while creating category"}), 400


@app.route('/franchisee/createShopItem', methods=['POST'])
@cross_origin()
# @verify_token
def createShopItem():
    data = request.json
    if data is None:
        return jsonify({"message": "No JSON data sent"}), 400

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
        mongo.db.shopping_menu.update_one(
            {
                "categoryId": categoryId
            },
            {
                "$push": {"items": createItem}
            })
        return jsonify({"message": "Success"})
    return jsonify({"message": "Missing fields while creating item"}), 400


@app.route('/franchisee/addToShoppingCart', methods=['POST'])
@cross_origin()
@verify_token
def addToShoppingCart():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    itemId = request.json.get("itemId")
    mongo.db.shopping_cart.update_one(
        {"email": email},
        {"$push": {
            "items": itemId
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/franchisee/removeFromShoppingCart', methods=['POST'])
@cross_origin()
@verify_token
def removeFromShoppingCart():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    itemId = request.json.get("itemId")
    cart = mongo.db.shopping_cart.find_one({"email": email}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items = cart.get("items", [])
    if itemId in items:
        items.remove(itemId)
    mongo.db.shopping_cart.update_one(
        {"email": email},
        {"$set": {
            "items": items
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/franchisee/getShoppingCart', methods=['GET'])
@cross_origin()
@verify_token
def getShoppingCart():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    cart = mongo.db.shopping_cart.find_one({"email": email}, {"_id": 0})
    if not cart:
        return jsonify({"message": "Cart Empty"}), 400
    items_dict = {}
    for item in cart.get("items", []):
        items_dict[item] = items_dict.get(item, 0)+1
    items = [{"itemId": k, "qty": v} for k, v in items_dict.items()]
    cart.update({"items": items})
    return jsonify(cart)


@app.route('/franchisee/getShoppingItemById', methods=['GET'])
@cross_origin()
@verify_token
def getShoppingItemById():
    itemId = request.args.get("itemId")
    if not itemId:
        return jsonify({"message": "No Item ID sent"})
    itemDetail = mongo.db.shopping_menu.aggregate(
        [
            {"$match": {"items.itemId": itemId}},
            {"$unwind": "$items"},
            {"$match": {"items.itemId": itemId}}
        ])
    itemDetail = list(itemDetail)
    if itemDetail:
        return jsonify(itemDetail[0]["items"])
    return jsonify({"message": "No such Item Found"})


@app.route('/franchisee/getFavourites', methods=['GET'])
@cross_origin()
@verify_token
def getFavourites():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    favourites = mongo.db.shopping_favourites.find_one(
        {"email": email}, {"_id": 0})
    if not favourites:
        return jsonify({"message": "Cart Empty"}), 400
    models = {"models": list(set(favourites.get("models", [])))}
    return jsonify(models)


@app.route('/franchisee/addToFavourites', methods=['POST'])
@cross_origin()
@verify_token
def addToFavourites():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    modelUid = request.json.get("uid")
    mongo.db.shopping_favourites.update_one(
        {"email": email},
        {"$push": {
            "models": modelUid
        }},
        upsert=True)
    return jsonify({"message": "Success"})


@app.route('/franchisee/removeFromFavourites', methods=['POST'])
@cross_origin()
@verify_token
def removeFromFavourites():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    modelUid = request.json.get("uid")
    mongo.db.shopping_favourites.update_one(
        {"email": email},
        {"$pull": {
            "models": modelUid
        }})
    return jsonify({"message": "Success"})


@app.route('/franchisee/createEstimate', methods=['POST'])
@cross_origin()
@verify_token
def createEstimate():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    modelUid = request.json.get("uid")
    return jsonify({"message": "Success"})


@scheduler.task('cron', id='zoho_crm_create', minute='*/30')
def zoho_crm_create():
    records = []
    record = mongo.db.clients.find_one_and_update(
        {"exportedZoho": False}, {"$set": {"exportedZoho": True}})
    while record and len(records) < 100:
        records.append(record)
    if records:
        send_data_to_zoho(records)


@scheduler.task('cron', id='move_pdf', minute=0, hour=0)
def move_agreement_pdf():
    source_dir = 'public/agreement_pdf'
    target_dir = 'tmp/backup_pdf'
    os.makedirs(target_dir, exist_ok=True)
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        shutil.move(os.path.join(source_dir, file_name), target_dir)
    print(str(len(file_names)) + " Moved!!")


if __name__ == "__main__":
    print("starting...")
    app.run(host=cfg.Flask['HOST'],
            port=cfg.Flask['PORT'],
            threaded=cfg.Flask['THREADED'],
            debug=True)
    # app.run(debug=True)
