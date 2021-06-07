from flask import (Flask, session, send_from_directory, send_file,
                   render_template)
from flask import request, redirect, url_for
from flask_pymongo import PyMongo
from flask import jsonify
from flask_cors import CORS, cross_origin
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

UPLOAD_FOLDER = 'public/img'
AGREEMENT_PDF_FOLDER = 'public/agreement_pdf'
# INTERMEDIATE_FOLDER = 'intermediate'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, static_url_path='')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://localhost:27017/panipuriKartz"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

cred = credentials.Certificate('config/fbAdminSecret.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('config/fbConfig.json')))
global_key = "ueQ4sZ"
spring_url = "http://15.207.147.88:8080/"
agreement_url = "http://15.207.147.88:8081/"
mailer_url = "http://15.207.147.88:8082/"
payment_url = "http://15.207.147.88:8083/"


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
    data = mongo.db.city_wise_count.find_one_and_update({},
                                                        {"$inc": {
                                                            city: 1
                                                        }})
    if data:
        new_id = "epanipuricart." + city + "." + str(data[city])
    else:
        new_id = "epanipuricart.dummy.5"
    return new_id


@app.route('/register/<path:path>', methods=['POST'])
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
            "roles": ['subscriber', 'customer']
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
        except:
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
            "roles": ['customer']
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
        except:
            return jsonify({"message": "Some error occurred"}), 500


@app.route('/login/<path:path>', methods=['POST'])
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


@app.route('/getProfile', methods=['GET'])
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


@app.route('/sendOTP', methods=['POST'])
@cross_origin()
def sendOTP():
    msg = "__OTP__ is your One Time Password for phone verification"
    typeOfMessage = 1
    if 'phone' in request.json:
        phone = request.json['phone']
        data = {"message": msg, "phone": phone, "type": typeOfMessage}
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


@app.route('/verifyOTP', methods=['POST'])
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


@app.route('/resendOTP', methods=['POST'])
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


@app.route('/saveGeneralInformation', methods=['POST'])
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


@app.route('/getGeneralInformation', methods=['GET'])
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


@app.route('/getCosting', methods=['GET'])
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


@app.route('/updateCosting', methods=['POST'])
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


@app.route('/payNow', methods=['POST'])
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
        "http://15.207.147.88:5000/payuSuccess",
        "furl":
        "http://15.207.147.88:5000/payuFailure",
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


@app.route('/checkPaymentStatus', methods=['POST'])
@cross_origin()
@verify_token
def checkPaymentStatus():
    hash_uid = request.json['payment_uid']
    payment_status = mongo.db.hash_map.find_one({"hash_uid":
                                                 hash_uid})['status']
    return jsonify({"payment_status": payment_status})


@app.route('/payuSuccess', methods=['POST'])
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
    order_id = mongo.db.order_num.find_one({"id": 1})['order_id']
    mongo.db.orders.insert_one({
        "email": txn_data['email'],
        "order_id": "EK-" + str(order_id),
        "model_uid": txn_data['model_uid'],
        "date": date,
        "status": "pending",
        "deliveryDate": ""
    })
    city = mongo.db.general_forms.find_one({"email":
                                            txn_data['email']})['town']
    device_id = get_last_id(city)
    mongo.db.device_ids.insert_one({
        "email": txn_data['email'],
        "device_id": device_id
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


@app.route('/payuFailure', methods=['POST'])
@cross_origin()
def payuFailure():
    transaction_id = request.form['txnid']
    mongo.db.hash_map.update_one({"transaction_id": transaction_id},
                                 {"$set": {
                                     "status": -1
                                 }})
    return render_template('fail.html')


@app.route('/getPrescription', methods=['GET'])
@cross_origin()
def prescription():
    return render_template('prescription.html')


@app.route('/getImg', methods=['GET'])
@cross_origin()
def getImg():
    return send_from_directory('templates', 'about_sign.png')


@app.route('/getModelImage/<path:path>', methods=['GET'])
@cross_origin()
@verify_token
def getModelImage(path):
    return send_from_directory('public/model-images', path)


@app.route('/getAgreementData', methods=['GET'])
@cross_origin()
@verify_token
def getAgreementData():
    return jsonify({
        "result": [{
            "variablePdf": "sample.pdf",
            "fixedPdf": "sample1.pdf",
            "order_id": "EK-125"
        }]
    })


@app.route('/getLatestOrder', methods=['GET'])
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


@app.route('/getAllOrders', methods=['GET'])
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
            email = mongo.db.docs.find_one({"order_id": items['order_id']})['email']
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


@app.route('/uploadDocuments', methods=['POST'])
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
        #base_path = r"C:\Users\Administrator\Desktop\EPanipuriKartz\Backend"
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


@app.route('/getMOU', methods=['GET', 'POST'])
@cross_origin()
@verify_token
def getMOU():
    path = request.args.get('path')
    try:
        return send_file(path, as_attachment=True)
    except:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route("/getFigures", methods=['GET'])
@cross_origin()
def getFigures():
    obj = mongo.db.company_figures.find_one({"id": 1})
    data = {}
    for ele in obj:
        if ele != "_id":
            data[ele] = obj[ele]
    return jsonify(data)


@app.route("/saveFigures", methods=['POST'])
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


@app.route('/updateOrder', methods=['POST'])
@cross_origin()
@verify_token
def updateOrder():
    order_id = request.json['order_id']
    status = request.json['status']
    deliveryDate = request.json['deliveryDate']
    try:
        mongo.db.orders.update_one({"order_id": order_id}, {
            "$set": {
                "status": status,
                "date": int(round(time.time() * 1000)),
                "deliverDate": deliveryDate
            }
        })
        mongo.db.order_history.insert_one({
            "order_id":
            order_id,
            "status":
            status,
            "date":
            int(round(time.time() * 1000))
        })
        return jsonify({"message": "Success"})
    except:
        return jsonify({"message": "Some Error Occurred"}), 500


@app.route('/getPersonalOrders', methods=['GET'])
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
    orders_list = mongo.db.orders.find({
        "email": email
    }, {
        "_id": 0
    }).sort("date", -1)
    return jsonify(list(orders_list))


@app.route('/getTrackingHistory', methods=['GET'])
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


@app.route('/uploadAgreement', methods=['POST'])
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
        hex_form = binascii.b2a_hex(os.urandom(5)).decode()
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


if __name__ == "__main__":
    print("starting...")
    app.run(host=cfg.Flask['HOST'],
            port=cfg.Flask['PORT'],
            threaded=cfg.Flask['THREADED'],
            debug=True)
    # app.run(debug=True)
