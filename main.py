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
from datetime import datetime, timedelta
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
PROFILE_FOLDER = 'public/profile'
AGREEMENT_PDF_FOLDER = r'C:\agreement-pdf'
BLOG_PHOTO_FOLDER = 'public/blog'
MOU_PDF_PATH = "C:\\agreement-service\\mou-pdfs"
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
mailer_url = "http://15.207.147.88:8080/"
payment_url = "http://15.207.147.88:8083/"
iot_api_url = "http://15.207.147.88:5002/"

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
        return "epanipuricart." + data["city"] + "." + str(data["value"])
    else:
        return "epanipuricart.dummy.5"


def generate_custom_id():
    return (
        binascii.b2a_hex(os.urandom(4)).decode() +
        hex(int(time.time()*10**5) % 10**12)[2:]
    )


def refresh_zoho_access_token(force=False):
    if (
        force or
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


def create_zoho_book_contact(client):
    contacts = "https://books.zoho.in/api/v3/contacts"
    header = {"Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]}
    name = (client.get("firstName") + " " + client.get("lastName")).strip()
    data = {
        "contact_name": name,
        "contact_persons": [
            {
                "salutation": client.get("title"),
                "first_name": client.get("firstName"),
                "last_name": client.get("lastName"),
                "email": client.get("email"),
                "phone": client.get("mobile"),
                "mobile": client.get("mobile"),
                "is_primary_contact": True,
            }]
    }
    response = requests.post(
        contacts,
        params={
            "organization_id": cfg.ZohoConfig.get("organization_id")
        },
        headers=header, json=data).json()
    if response["code"] == 0:
        mongo.db.zoho_customer.update_one(
            {
                "email": client.get("email")
            }, {
                "$set": {
                    "zohoId": response["contact"]["contact_id"]
                }
            },
            upsert=True)
    else:
        print("ZOHO BOOKS:"+str(response))


def update_zoho_book_contact(client):
    email = client.get("email")
    attn = client.get("title")+client.get("firstName")
    address = {
        "attention": attn,
        "address": client.get("address"),
        "state_code": "OD",
        "city": client.get("town"),
        "state": "OD",
        "zip": int(client.get("pincode")),
        "country": "India",
        "phone": client.get("mobile")
    }
    data = {
        "billing_address": address,
        "shipping_address": address,
        "gst_no": client.get("gst_no"),
        "gst_treatment": client.get("gst_treatment")
    }
    zohoId = mongo.db.zoho_customer.find_one({"email": email}, {"_id": 0})
    contacts = "https://books.zoho.in/api/v3/contacts/" + \
        str(zohoId.get("zohoId"))
    header = {"Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]}
    response = requests.post(
        contacts,
        params={
            "organization_id": cfg.ZohoConfig.get("organization_id")
        },
        headers=header, json=data).json()
    print("ZOHO BOOKS UPDATE:"+str(response))


def upsert_zoho_crm_contact(client):
    contacts = "https://www.zohoapis.in/crm/v2/Contacts/upsert"
    header = {"Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]}
    data = {
        "data": [client],
        "trigger": [
            "approval",
            "workflow",
            "blueprint"
        ]
    }
    response = requests.post(contacts, headers=header, json=data).json()
    print(response)
    return response


def send_estimate_mail(estimate, email):
    estimate_id = estimate.get("estimate_id")
    if not estimate_id:
        return
    user_data = {
        "est_num": estimate.get("estimate_number"),
        "name": estimate.get("customer_name"),
        "date": estimate.get("date"),
        "amount": estimate.get("total")
    }
    body = cfg.estimate_mail_body
    return requests.post(
        "https://books.zoho.in/api/v3/estimates/"+estimate_id+"/email",
        params={
            "organization_id": cfg.ZohoConfig.get("organization_id")
        },
        headers={
            "Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]
        },
        json={
            "send_from_org_email_id": True,
            "to_mail_ids": [
                email
            ],
            "cc_mail_ids": [
                "gyanaranjan7205@gmail.com", "jyotimay16@gmail.com"
            ],
            "subject": ("Estimate - " +
                        user_data["est_num"]+" is awaiting your approval"),
            "body": body.format(**user_data)
        }).json()


def create_zoho_estimate(customer_id, item_id):
    response = requests.post(
        "https://books.zoho.in/api/v3/estimates",
        params={
            "organization_id": cfg.ZohoConfig.get("organization_id")
        },
        headers={
            "Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]
        },
        json={
            "customer_id": customer_id,
            "line_items": [
                {
                    "item_id": item_id
                }
            ]
        }).json()
    if response.get("code") == 0:
        return response.get("estimate")


def send_sales_mail(salesorder_id, email):
    if not salesorder_id:
        return
    body = """
    Dear Customer,
    Thanks for your interest in our services.
    Please find our sales order attached with this mail.

    Assuring you of our best services at all times.
    Regards,
    Harish K. Neotia
    E-PanipuriKart
    """
    return requests.post(
        "https://books.zoho.in/api/v3/salesorders/"+salesorder_id+"/email",
        params={
            "organization_id": cfg.ZohoConfig.get("organization_id")
        },
        headers={
            "Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]
        },
        json={
            "send_from_org_email_id": True,
            "to_mail_ids": [
                email
            ],
            "cc_mail_ids": [
                "gyanaranjan7205@gmail.com", "jyotimay16@gmail.com"
            ],
            "subject": "Sales Order Statement",
            "body": body
        }).json()


def create_zoho_sales_order(customer_id, item_id):
    response = requests.post(
        "https://books.zoho.in/api/v3/salesorders",
        params={
            "organization_id": cfg.ZohoConfig.get("organization_id")
        },
        headers={
            "Authorization": "Zoho-oauthtoken "+ZOHO_TOKEN["access_token"]
        },
        json={
            "customer_id": customer_id,
            "line_items": [
                {
                    "item_id": item_id
                }
            ]
        }).json()
    if response.get("code") == 0:
        return response.get("salesorder").get("salesorder_id")


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
            "exportedZoho": False,
            "date": int(round(time.time() * 1000))
        }

        mongo.db.clients.insert_one(doc)
        create_zoho_book_contact(doc)
        return jsonify({
            "title": doc['title'],
            "firstName": doc['firstName'],
            "lastName": doc['lastName'],
            "email": doc['email'],
            "mobile": doc['mobile'],
            "roles": doc['roles']
        })
        # try:
        #     mongo.db.clients.insert_one(doc)
        #     create_zoho_book_contact(doc)
        #     return jsonify({
        #         "title": doc['title'],
        #         "firstName": doc['firstName'],
        #         "lastName": doc['lastName'],
        #         "email": doc['email'],
        #         "mobile": doc['mobile'],
        #         "roles": doc['roles']
        #     })
        # except Exception:
        #     return jsonify({"message": "Some error occurred"}), 500

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
            "exportedZoho": False,
            "date": int(round(time.time() * 1000))
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


@app.route('/franchisee/startMeeting', methods=['POST'])
@cross_origin()
def startMeeting():
    API_KEY = cfg.WherebyConfig["API_KEY"]
    now = datetime.now()
    data = {
        "startDate": now.isoformat(),
        "endDate": (now+timedelta(hours=24)).isoformat(),
        "fields": ["hostRoomUrl"],
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.whereby.dev/v1/meetings",
        headers=headers,
        json=data
    )

    print("Status code:", response.status_code)
    data = json.loads(response.text)
    print(data)
    print("Room URL:", data["roomUrl"])
    print("Host room URL:", data["hostRoomUrl"])
    return jsonify({"room_url": data["roomUrl"]})


@app.route('/franchisee/convertToSubscriber', methods=['GET'])
@cross_origin()
@verify_token
def convertToSubscriber():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    data = mongo.db.clients.find_one({'firebase_id': decoded['user_id']})
    if "customer" in data["roles"]:
        mongo.db.clients.update_one(
            {'firebase_id': decoded['user_id']},
            {'$addToSet': {
                'roles': 'subscriber'
            }})
        return jsonify({"message": "Success"})
    return jsonify({"message": "User is not customer"}), 401


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
                if ('customer' in data['roles']) and (len(data['roles']) == 1):
                    return jsonify({"message": "Convert to subscriber"}), 201

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


@app.route('/franchisee/getLogo', methods=['GET'])
@cross_origin()
def getLogo():
    return send_from_directory(".", "logo.png")


@app.route('/franchisee/createZohoContact', methods=['POST'])
@cross_origin()
def createZohoContact():
    data = request.json
    zoho_record = {
        "First_Name": data.get("firstName"),
        "Last_Name": data.get("lastName"),
        "Email": data.get("email")
    }
    return jsonify(upsert_zoho_crm_contact(zoho_record))


@app.route('/franchisee/sendOTP', methods=['POST'])
@cross_origin()
def sendOTP():
    msg = "__OTP__ is your One Time Password for phone verification"
    typeOfMessage = 1
    if 'phone' in request.json:
        phone = request.json['phone']
        email = request.json['email']
        # email = 'jyotimay16@gmail.com'
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        data = {"message": msg, "phone": phone, "name": firstName,
                "email": email, "type": typeOfMessage,
                "mediaUrl": "http://15.207.147.88:5000/franchisee/getLogo"
                }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        mongo.db.clients.find_one({"mobile": phone})
        if False:
            return jsonify({"message":
                            "Mobile number already registered"}), 423
        else:
            try:
                response = requests.post(spring_url +
                                         'api/message/send-registration-otp',
                                         data=json.dumps(data),
                                         headers=headers)
                json_resp = json.loads(response.text)

                zoho_record = {
                    "First_Name": firstName,
                    "Last_Name": lastName,
                    "Email": email,
                    "Phone": phone
                }
                upsert_zoho_crm_contact(zoho_record)

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
            target_url = 'api/message/verify-registration-otp/{}/phone/{}/otp/{}'.format(
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


@app.route('/franchisee/saveAutofillInformation', methods=['POST'])
@cross_origin()
@verify_token
def saveAutofillInformation():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']

    valid_fields = [
        "title", "firstName", "lastName",
        "mobile", "aadhar", "fatherName",
        "address", "town", "pincode",
        "state", "location", "termsAndConditions"
        "isSubscriber", "isMulti", "gst_no", "gst_treatment"]
    data = {field: str(request.json.get(field, "")) for field in valid_fields}
    try:
        mongo.db.autofill_forms.update_one(
            {"email": email, "isConverted": False}, {
                "$set": data
            }, upsert=True)
        return jsonify({"message": "Successfully saved"})
    except Exception:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/getAutofillInformation', methods=['GET'])
@cross_origin()
@verify_token
def getAutofillInformation():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    try:
        obj = mongo.db.autofill_forms.find_one(
            {"email": email, "isConverted": {"$ne": True}}, {"_id": 0})
        if obj:
            return obj
        else:
            return jsonify({"message", "No saved data"}), 404
    except Exception:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/saveGeneralInformation', methods=['POST'])
@cross_origin()
@verify_token
def saveGeneralInformation():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    obj = mongo.db.general_forms.find_one(
        {'email': email, 'isConverted': False})

    valid_fields = [
        "title", "firstName", "lastName",
        "mobile", "aadhar", "fatherName",
        "address", "town", "pincode",
        "state", "location", "termsAndConditions"
        "isSubscriber", "isMulti", "gst_no", "gst_treatment"]
    data = {field: str(request.json.get(field, "")) for field in valid_fields}

    if obj:
        try:
            mongo.db.general_forms.update_one(
                {"email": email, "isConverted": False}, {
                    "$set": data
                })
            data.update({"isConverted": False, "email": email})
            update_zoho_book_contact(data)
            return jsonify({"message": "Successfully saved"})
        except Exception:
            return jsonify({"message": "Some error occurred"}), 500
    else:
        try:
            data.update({"isConverted": False, "email": email})
            mongo.db.general_forms.insert_one(email)
            update_zoho_book_contact(data)
            return jsonify({"message": "Successfully saved"})
        except Exception:
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
        obj = mongo.db.general_forms.find_one(
            {"email": email, "isConverted": {"$ne": True}}, {"_id": 0})
        if obj:
            return obj
        else:
            return jsonify({"message", "No saved data"}), 404
    except Exception:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/saveGeneralForm', methods=['POST'])
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
    subscription_type = request.json.get("subscription_type")
    franchisee_type = request.json.get("franchisee_type")
    if subscription_type is None or franchisee_type is None:
        return jsonify({"message": "Missing Parameters"}), 400
    isSubscription = subscription_type
    isMulti = franchisee_type
    valid_fields = [
        "title", "firstName", "lastName",
        "mobile", "aadhar", "fatherName",
        "address", "pincode",
        "state", "location", "termsAndConditions",
        "gst_no", "gst_treatment"]
    data = {field: str(request.json.get(field, "")) for field in valid_fields}
    if isSubscription and not isMulti:
        data["selectedTowns"] = [request.json.get("selectedTowns", "")]
    elif isSubscription or isMulti:
        data["selectedTowns"] = request.json.get("selectedTowns", [])
    else:
        data["town"] = request.json.get("selectedTowns", "")
    data["status"] = 0
    data["formId"] = generate_custom_id()
    data["email"] = email
    data["isSubscription"] = isSubscription
    data["isMulti"] = isMulti
    data["uid"] = request.json.get("uid")
    costing = mongo.db.costing.find_one({"uid": data["uid"]})
    if isSubscription:
        data["price"] = costing["subscriptionPrice"]
    else:
        data["price"] = costing["price"]
    data["createdDate"] = datetime.now()
    try:
        if data["gst_treatment"] not in [
                "business_registered_regular", "business_unregistered"]:
            raise ValueError
        if not isSubscription and not isMulti:
            mongo.db.general_forms.insert_one(data)
        else:
            mongo.db.review_general_forms.insert_one(data)
            mongo.db.clients.update_one(
                {'email': email},
                {'$addToSet': {
                    'roles': "in_review"
                }})
        return jsonify({"message": "Successfully saved"})
    except Exception:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/getCandidateForms', methods=['GET'])
@cross_origin()
@verify_token
def getCandidateForms():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    try:
        query = {"email": email}
        status = request.args.get("status")
        if status is not None:
            query["status"] = int(status)
        obj = mongo.db.review_general_forms.find(query, {"_id": 0})
        if obj:
            return jsonify({"forms": list(obj)})
        else:
            return jsonify({"message", "No saved data"}), 404
    except Exception:
        return jsonify({"message": "Some error occurred"}), 500


@app.route('/franchisee/acceptMultiUnitForm', methods=['POST'])
@cross_origin()
@verify_token
def acceptMultiUnitForm():
    formId = request.json.get("formId")
    accept = request.json.get("accept")
    if accept is None or formId is None:
        return jsonify({"message": "No formId/accept parameter"}), 400
    if accept:
        formData = mongo.db.review_general_forms.find_one_and_update(
            {"formId": formId},
            {"$set": {"status": 1}})
        email = formData["email"]
        mongo.db.clients.update_one(
            {'email': email},
            {
                '$addToSet': {'roles': 'form_accepted'}
            }, {
                '$pull': {'roles': 'in_review'}
            })
        return jsonify({"message": "Form is accepted"})
    else:
        formData = mongo.db.review_general_forms.find_one_and_update(
            {"formId": formId},
            {"$set": {"status": -1}})
        email = formData["email"]
        mongo.db.clients.update_one(
            {'email': email},
            {
                '$pull': {'roles': 'in_review'}
            })
        return jsonify({"message": "Form is rejected"})


@app.route('/franchisee/getPendingForms', methods=['GET'])
@cross_origin()
@verify_token
def getPendingForms():
    obj = mongo.db.review_general_forms.find({"status": 0}, {"_id": 0})
    return jsonify({"forms": list(obj)})


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
            d['model_image'] = ele['model_image']
            if 'subscriptionPrice' in ele:
                d['subscriptionPrice'] = ele['subscriptionPrice']
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
    # currentRoles = mongo.db.clients.find_one(
    #     {"email": txn_data['email']}, {"roles": 1})
    # currentRoles = currentRoles.get("roles", [])
    # newRole = None
    # if 'multi_unit_subscriber' in currentRoles:
    #     newRole = "multi_unit_paid_subscriber"
    # else:
    #     newRole = "paid_subscriber"
    mongo.db.clients.update_one(
        {"email": txn_data['email']},
        {"$addToSet": {
            "roles": 'paid_subscriber'
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
        "transaction_id": transaction_id,
        "deliveryDate": "",
        "isAgreement": False
    })
    data = mongo.db.general_forms.find_one(
        {"email": txn_data['email'], "isConverted": False})
    city = data['town']
    device_id = get_last_id(city)
    mongo.db.device_ids.insert_one({
        "email": txn_data['email'],
        "device_id": device_id,
        "state": data.get("state"),
        "town": city,
        "location": data.get("location"),
        "order_id": "EK-" + str(order_id),
        "isSubscriber": data["isSubscriber"]
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
        data = mongo.db.orders.find_one(
            {"email": email, "isAgreement": False}, {"_id": 0})
        return jsonify(data)
    except Exception:
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

                        except Exception:
                            return jsonify({"message":
                                            "Some Error Occurred"}), 500

        # currentRoles = mongo.db.clients.find_one(
        #     {"email": email}, {"roles": 1})
        # currentRoles = currentRoles.get("roles", [])
        # newRole = None
        # if 'multi_unit_paid_subscriber' in currentRoles:
        #     newRole = "multi_unit_franchisee"
        # else:
        #     newRole = "franchisee"
        mongo.db.clients.update_one({"email": email},
                                    {"$addToSet": {
                                        "roles": 'franchisee'
                                    }})

        client = mongo.db.general_forms.find_one_and_update(
            {"email": email, "isConverted": False},
            {"$set": {"isConverted": True}}
        )
        mongo.db.autofill_forms.update_one(
            {"email": email, "isConverted": False},
            {"$set": {"isConverted": True}}
        )
        order_data = mongo.db.orders.find_one_and_update(
            {"order_id": order_id},
            {"$set": {
                "status": "placed",
                "isAgreement": True
            }})
        mongo.db.order_history.insert_one({
            "order_id": order_id,
            "status": "placed",
            "date": int(round(time.time() * 1000))
        })
        payload = {
            "attachmentPaths": [],
            "bccAddresses": [],
            "ccAddresses": [],
            "mailBody": "Your Order "+str(order_id)+" has been successfully placed.",
            "mailSubject": "Order Successful",
            "toAddresses": [email, "ceo@epanipuricart.com"]
        }
        requests.post(mailer_url + 'send-mail', json=payload)

        # create Default Menu
        device_data = mongo.db.device_ids.find_one({"order_id": order_id})
        default_menu = cfg.DefaultMenu.copy()
        for category in default_menu["menu"]:
            category.update({"categoryId": generate_custom_id()})
            for item in category["items"]:
                item.update({"itemId": generate_custom_id()})
        mongo.db.menu.insert_one({"cartId": device_data["device_id"]},
                                 {"$set": default_menu})

        # trigger iot register api
        # modelType is hardcoded to 1
        costing_data = mongo.db.costing.find_one({"modelType": 1})
        model_type = costing_data.get("extension").strip()[0]
        name = client.get("firstName", "") + " " + client.get("lastName", "")
        iot_data = {
            "type": model_type,
            "uid": device_data["device_id"],
            "ownerType": 1,
            "owner": name.strip(),
            "address": ", ".join([device_data[key]
                                  for key in ["location", "town", "state"]])
        }
        requests.post(iot_api_url+"/wizard/registerDevice", json=iot_data)

        # zoho sales order
        model_uid = order_data.get("model_uid", 1)
        zohoId = mongo.db.zoho_customer.find_one({"email": email}, {"_id": 0})
        itemId = mongo.db.costing.find_one({"uid": model_uid})
        if zohoId and itemId:
            send_sales_mail(
                create_zoho_sales_order(
                    zohoId.get("zohoId"),
                    itemId.get("zoho_itemid")),
                email)

        return jsonify({"message": "Success"})


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
            orders_data = mongo.db.orders.find_one({"order_id": orderId})
            email = orders_data['email']
            user_data = mongo.db.general_forms.find_one({"email": email})
            docs_data = mongo.db.docs.find_one({"order_id": orderId})
            hash_data = mongo.db.hash_map.find_one(
                {"transaction_id": orders_data['transaction_id']})
            # base_path = r"C:\Users\Administrator\Desktop\EPanipuriKartz\Backend"
            name = user_data['title'] + user_data['firstName'] + " " + user_data[
                'lastName']
            aadhar = user_data['aadhar']
            brand = "E-Panipurii Kartz"
            customer_id = mongo.db.device_ids.find_one(
                {"order_id": orderId})['device_id']
            model = "Table Top"
            model_extension = "3-nozzle system"
            fName = user_data['fatherName']
            address = user_data['address'] + ',' + user_data[
                'state'] + ',' + user_data['town'] + ',' + str(
                    user_data['pincode'])
            mobile = user_data['mobile']
            amount = hash_data['amount']
            aadharLogoPath = os.path.join(app.config['UPLOAD_FOLDER'],
                                          docs_data['aadhar'])
            ap = str(os.path.abspath(aadharLogoPath))
            # ap = str(aadharLogoPath)
            customerPhotoPath = os.path.join(app.config['UPLOAD_FOLDER'],
                                             docs_data['photo'])
            cp = str(os.path.abspath(customerPhotoPath))
            # cp = str(customerPhotoPath)
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
                "firstPagePath": save_path,
                "panLogoPath": ""

            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            try:
                print(post)
                response = requests.post(agreement_url + 'generate-agreement',
                                         data=json.dumps(post),
                                         headers=headers)
                print(response.text)
                resData = response.json()
                mongo.db.digio_response.update_one({"order_id": orderId},
                                                   {"$set": resData},
                                                   upsert=True)
                # mongo.db.docs.update_one({"order_id": orderId},
                #                         {"$set": {
                #                             "pdf": str(response.text)
                #                         }})
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
                return jsonify({"message": "Success"})
            except Exception:
                return jsonify({"message": "Service Error"}), 423

        except Exception:
            return jsonify({"message": "Some Error Occurred"}), 500
    return jsonify({"message": "Only PDF files allowed"}), 400


@app.route('/franchisee/generateSamplePdf', methods=['GET'])
@cross_origin()
@verify_token
def generateSamplePdf():
    orderId = request.args.get('orderId')
    orders_data = mongo.db.orders.find_one({"order_id": orderId})
    email = orders_data['email']
    user_data = mongo.db.general_forms.find_one({"email": email})
    hash_data = mongo.db.hash_map.find_one(
        {"transaction_id": orders_data['transaction_id']})
    customer_id = mongo.db.device_ids.find_one(
        {"order_id": orderId})['device_id']
    name = user_data['title'] + user_data['firstName'] + " " + user_data[
        'lastName']
    SAMPLE_IMAGE = r"C:\public\img"
    aadhar_path = os.path.join(SAMPLE_IMAGE, "aadhar_sample.jpg")
    customer_path = os.path.join(SAMPLE_IMAGE, "person_sample.jpg")
    first_page_path = os.path.join(SAMPLE_IMAGE, "firstpage_sample.pdf")
    pancard_path = os.path.join(SAMPLE_IMAGE, "pancard_sample.jpg")
    request_data = {
        "aadhar": user_data['aadhar'],
        "aadharLogoPath": aadhar_path,
        "address": user_data['address'],
        "amount": str(hash_data['amount']),
        "brand": "E-Panipurii Kartz",
        "customerId": customer_id,
        "customerPhotoPath": customer_path,
        "email": email,
        "extension": "3-nozzle system",
        "firstPagePath": first_page_path,
        "fname": user_data['fatherName'],
        "mobile": user_data['mobile'],
        "model": "Table Top",
        "name": name,
        "panLogoPath": pancard_path
    }
    response = requests.post(
        agreement_url+'download-sample-pdf/dynamic', json=request_data).text
    print(response)
    response = os.path.split(response)[-1]
    print(response)
    return jsonify({"result": response})


@app.route('/franchisee/getSamplePdf', methods=['GET'])
@cross_origin()
@verify_token
def getSamplePdf():
    fileName = request.args.get("file")
    if os.path.isfile(os.path.join(MOU_PDF_PATH, fileName)):
        return send_from_directory(MOU_PDF_PATH, fileName)
    return jsonify({"message": "Error file not found"})


@app.route('/franchisee/deleteSamplePdf', methods=['GET'])
@cross_origin()
@verify_token
def deleteSamplePdf():
    fileName = request.args.get("file")
    headers = {'Content-Type': 'application/json'}
    filePath = os.path.join(MOU_PDF_PATH, fileName)
    if os.path.isfile(filePath):
        response = requests.delete(
            agreement_url+'delete-pdf', headers=headers, data=filePath).text
        print(response)
        return jsonify({"message": "Success"})
    return jsonify({"message": "Error file not found"})


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
        list_of_words = title.split()
        title_uri = "-".join([ele.lower() for ele in list_of_words])
        formatted_uri = title_uri + "-" + hex_form
        try:
            save_path = os.path.join(BLOG_PHOTO_FOLDER, enc_filename)
            mongo.db.blogs.insert_one(
                {
                    "blogId": hex_form,
                    "title": title,
                    "formatted_uri": formatted_uri,
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
    blogs_list = mongo.db.blogs.find({}, {"_id": 0}).sort("date", -1)
    return jsonify({"blogs": list(blogs_list)})


@app.route('/franchisee/ourBlogs/<path:path>', methods=['GET'])
@cross_origin()
def getBlogByURI(path):
    blog = mongo.db.blogs.find_one({"formatted_uri": path}, {"_id": 0})
    return jsonify({"blog": blog})


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
        if ext not in ["jpg", "png"]:
            return jsonify({"message": "Only JPG/PNG files allowed"}), 400
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


@app.route('/franchisee/login/wizard', methods=['POST'])
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
    device_id = request.json['customerId']
    data = mongo.db.alias_data.find({'device_id': device_id}, {"_id": 0})
    if (len(list(data)) == 2):
        return jsonify({"message": "Cannot Add more data"}), 400
    alias_email = request.json['aliasEmail']
    alias_name = request.json['aliasName']
    mongo.db.alias_data.insert_one({
        "alias_id": generate_custom_id(),
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


@app.route('/franchisee/updateAliasData', methods=['POST'])
@cross_origin()
@verify_token
def updateAliasData():
    aliasId = request.json.get("aliasId")
    aliasName = request.json.get("aliasName")
    if aliasId is None or aliasName is None:
        return jsonify({"message": "No alias id/name sent"}), 400
    mongo.db.alias_data.update_one(
        {"alias_id": aliasId},
        {
            "$set": {"alias_name": aliasName}
        })
    return jsonify({"message": "Success"})


@app.route('/franchisee/deleteAliasData', methods=['POST'])
@cross_origin()
@verify_token
def deleteAliasData():
    aliasId = request.json.get("aliasId")
    if aliasId is None:
        return jsonify({"message": "No alias id sent"}), 400
    mongo.db.alias_data.delete_one({"alias_id": aliasId})
    return jsonify({"message": "Success"})


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
        if not data.get("cartId"):
            return jsonify({"message": "No Cart ID sent"}), 400

        valid_fields = [
            "name", "img", "desc", "basePrice",
            "ingredients", "customDiscount", "isOutOfStock"]
        updateItem = {"menu.$.items.$[t]."+field: value for field,
                      value in data.items() if field in valid_fields}
        if "basePrice" in data:
            gst = mongo.db.menu.find_one({"cartId": data.get("cartId")})
            if not gst:
                return jsonify({"message": "Invalid Cart ID sent"}), 400
            gst = gst["gst"]
            updateItem.update({
                "menu.$.items.$[t].price": round(data["basePrice"]*(1+gst), 2)
            })
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
        valid_fields = ["isActive", "gst", "deliveryCharge", "flatDiscount"]
        updateCart = {field: value for field,
                      value in data.items() if field in valid_fields}
        if not updateCart.get("isActive", True):
            updateCart.update({"sid": []})
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


@app.route('/franchisee/getCitiesByState', methods=['GET'])
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


@app.route('/franchisee/getShoppingMenu', methods=['GET'])
@cross_origin()
@verify_token
def getShoppingMenu():
    items = mongo.db.shopping_menu.find({}, {"_id": 0})
    return jsonify({"items": list(items)})


@app.route('/franchisee/placeOrder', methods=['POST'])
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
        "deliveryAddress",
        "modeOfPayment",
        "transactionId"]
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
    createOrder = data
    valid_flag = all(field in data for field in valid_fields)
    items_arr = []

    if valid_flag:
        cart = mongo.db.shopping_cart.find_one(
            {"email": email}, {"_id": 0})
        if not cart:
            return jsonify({"message": "Cart Empty"}), 400
        itemsDict = {}
        for item in cart.get("items", []):
            itemsDict[item] = itemsDict.get(item, 0)+1

        data["items"] = [{"itemId": k, "qty": v} for k, v in itemsDict.items()]
        itemsList = list(itemsDict.keys())
        data = mongo.db.shopping_menu.aggregate([
            {"$unwind": "$items"},
            {
                "$match":
                {
                    "items.itemId": {"$in": itemsList}
                }
            },
            {
                "$project":
                {
                    "_id": 0,
                    "itemId": "$items.itemId",
                    "itemName": "$items.name",
                    "gst": 1,
                    "price": "$items.price",
                    "closeCategory": 1
                }
            }
        ])
        data = list(data)
        if any(d["closeCategory"] for d in data):
            return jsonify(
                {"message":
                 "One or more items are ordered from a closed category"}), 400
        subTotal = 0
        items_arr = []
        for d in data:
            qty = itemsDict.get(d["itemId"], 1)
            subTotal += float(d["price"])*int(qty)
            items_arr.append(
                {"itemId": d["itemId"], "itemName": d["itemName"],
                 "price": d["price"], "qty": qty, "gst": d["gst"]})
        orderFields = {
            "orderId": generate_custom_id(),
            "timestamp": int(round(time.time() * 1000)),
            "orderStatus": "placed",
            "subTotal": subTotal,
            "manualBilling": False,
            "total": round(subTotal, 2)
        }
        createOrder.update(orderFields)
        createOrder["items"] = items_arr
        mongo.db.shopping_orders.insert_one(createOrder)
        mongo.db.shopping_cart.delete_one({"email": email})
        createOrder.pop("_id", None)
        return jsonify(createOrder)
    return jsonify({"message": "Missing fields while creating order"}), 400


@app.route('/franchisee/getOrderDetails', methods=['GET'])
@cross_origin()
def getOrderDetails():
    orderId = request.args.get("orderId")
    if orderId:
        orderInfo = mongo.db.shopping_orders.find_one(
            {"orderId": orderId},
            {"_id": 0})
        if orderInfo:
            return jsonify(orderInfo)
        return jsonify({"message": "No such orderId exists"})
    return jsonify({"message": "No orderId sent"})


@app.route('/franchisee/updateOrderStatus', methods=['POST'])
@cross_origin()
@verify_token
def updateOrderStatus():
    data = request.json
    orderId = data.get("orderId")
    status = data.get("status")

    if orderId and status:
        mongo.db.shopping_orders.update_one(
            {"orderId": orderId},
            {"$set": {
                "orderStatus": status
            }})
        return jsonify({"message": "Success"})
    return jsonify({"message": "Missing fields"}), 400


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

    valid_fields = ["category", "closeCategory", "sellerName", "gst"]
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
        createItem.update({
            "itemId": generate_custom_id(),
            "rating": 0
        })
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
        return jsonify({"models": []})
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
        {"$set": {
            "models": [modelUid]
        }},
        upsert=True)
    zohoId = mongo.db.zoho_customer.find_one({"email": email}, {"_id": 0})
    itemId = mongo.db.costing.find_one({"uid": modelUid})
    if not zohoId or not itemId:
        return jsonify({"message": "Could not send estimate"})
    send_estimate_mail(
        create_zoho_estimate(zohoId.get("zohoId"), itemId.get("zoho_itemid")),
        email)
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


@app.route('/franchisee/sendSalesOrder', methods=['POST'])
@cross_origin()
@verify_token
def sendSalesOrder():
    token = request.headers['Authorization']
    decoded = jwt.decode(token,
                         options={
                             "verify_signature": False,
                             "verify_aud": False
                         })
    email = decoded['email']
    modelUid = request.json.get("uid")
    zohoId = mongo.db.zoho_customer.find_one({"email": email}, {"_id": 0})
    itemId = mongo.db.costing.find_one({"uid": modelUid})
    if not zohoId or not itemId:
        return jsonify({"message": "Could not send salesorder"})
    send_sales_mail(
        create_zoho_sales_order(zohoId.get("zohoId"),
                                itemId.get("zoho_itemid")),
        email)
    return jsonify({"message": "Success"})


@app.route('/franchisee/updateProfile', methods=['POST'])
@cross_origin()
@verify_token
def updateProfile():
    data = request.form
    cartId = data.get("cartId")
    if not cartId:
        return jsonify({"message": "No cartId sent"}), 400
    valid_fields = ["location", "google_location", "gstin", "fssai"]
    updateItem = {field: value for field,
                  value in data.items() if field in valid_fields}

    if 'file' in request.files:
        profile_img = request.files.get('file')
        first_name = profile_img.filename.split('.')[0]
        ext = profile_img.filename.split('.')[1]
        enc_filename = first_name + "_" + \
            str(int(round(time.time() * 1000))) + "." + ext
        enc_filename = secure_filename(enc_filename)
        save_path = os.path.abspath(
            os.path.join(PROFILE_FOLDER, enc_filename))

        profile_img.save(save_path)
        updateItem['profile'] = enc_filename

        mongo.db.device_ids.update_one(
            {
                "device_id": cartId
            },
            {
                "$set": updateItem
            }
        )
        return jsonify({"message": "Successfully updated profile image"})
        # try:
        #     save_path = os.path.abspath(
        #         os.path.join(PROFILE_FOLDER, enc_filename))

        #     profile_img.save(save_path)
        #     updateItem['profile'] = enc_filename

        #     mongo.db.device_ids.update_one(
        #         {
        #             "device_id": cartId
        #         },
        #         {
        #             "$set": updateItem
        #         }
        #     )
        #     return jsonify({"message": "Successfully updated profile image"})
        # except:
        #     return jsonify({"message": "Some error occurred"}), 500
    else:
        mongo.db.device_ids.update_one(
            {
                "device_id": cartId
            },
            {
                "$set": updateItem
            }
        )
        return jsonify({"message": "Success"})


@app.route('/franchisee/getCartProfile', methods=['GET'])
@cross_origin()
@verify_token
def getCartProfile():
    cartId = request.args.get("cartId")
    if not cartId:
        return jsonify({"message": "No cartId sent"}), 400
    data = mongo.db.device_ids.find_one({"device_id": cartId}, {"_id": 0})
    return data


@app.route('/franchisee/getProfileImage/<path:path>', methods=['GET'])
@cross_origin()
def getProfilee(path):
    return send_from_directory('public/profile', path)


@app.route('/upload', methods=['GET', 'POST'])
@cross_origin()
def upload():
    if request.method == "POST":
        timestamp = int(round(time.time() * 1000))
        data = request.json["values"]
        uid = request.json["deviceId"]
        print(data)
        for ele in data:
            ele["date"] = timestamp
        existing_data = mongo.db.stats.find_one({"uid": uid})['data']
        new_data = existing_data + data
        mongo.db.stats.update_one({'uid': uid}, {'$set': {"data": new_data}})
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

        mongo.db.counter.update_one({'uid': uid}, {'$set': {"data": arr}})
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization error"}), 403


@app.route('/uploadLevel', methods=['GET', 'POST'])
@cross_origin()
def uploadLevel():
    if request.method == "POST":
        timestamp = int(round(time.time() * 1000))
        data = request.json["values"]
        uid = request.json["deviceId"]
        for ele in data:
            ele["date"] = timestamp
        existing_data = mongo.db.levels.find_one({"uid": uid})['data']
        new_data = existing_data + data
        mongo.db.levels.update_one({'uid': uid}, {'$set': {"data": new_data}})
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization error"}), 403


@app.route("/verifyToken", methods=['GET', 'POST'])
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
                post = {"uid": message['uid'], "token": token}
                users.insert_one(post)
                return jsonify({"message": message['status']})
            else:
                return jsonify({"message": message['status']}), 401
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/deleteToken", methods=['GET', 'POST'])
@cross_origin()
def deleteToken():
    if request.method == "POST":
        token = request.headers['Authorizations']
        ele = mongo.db.users.find_one({"token": token})
        if ele:
            mongo.db.users.delete_one({"token": token})
            return jsonify({"message": "SUCCESS"})
        else:
            return jsonify({"message": "No record found"}),


@app.route("/postPowerOut", methods=['GET', 'POST'])
@cross_origin()
def postPowerOut():
    if request.method == "POST":
        uid = request.json["uid"]
        mongo.db.devices.update(
            {"uid": uid}, {'$set': {"deviceState": 0, "activeState": 0}})
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route("/getSwitchStatus", methods=['GET', 'POST'])
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


@app.route("/postDeviceStatus", methods=['GET', 'POST'])
@cross_origin()
def postDeviceStatus():
    if request.method == "POST":
        uid = request.json["uid"]
        deviceStatus = request.json["status"]
        try:
            mongo.db.devices.update_one(
                {"uid": uid}, {'$set': {"deviceState": deviceStatus}})
        except:
            print("Error!")
        return jsonify({"message": "SUCCESS"})
    else:
        return jsonify({"message": "Authorization Error"}), 403


@app.route('/franchisee/getAboutVideo', methods=['GET'])
@cross_origin()
def getAboutVideo():
    file = 'TableTop3nozzles.mp4'
    return send_from_directory('public/video', file)

# @scheduler.task('cron', id='zoho_crm_create', minute='*/30')
# def zoho_crm_create():
#     records = []
#     record = mongo.db.clients.find_one_and_update(
#         {"exportedZoho": False}, {"$set": {"exportedZoho": True}})
#     while record and len(records) < 100:
#         records.append(record)
#         record = mongo.db.clients.find_one_and_update(
#             {"exportedZoho": False}, {"$set": {"exportedZoho": True}})
#     if records:
#         send_data_to_zoho(records)


@scheduler.task('cron', id='zoho_token_refresh', minute='*/30')
def zoho_token_refresh():
    refresh_zoho_access_token(force=True)


@scheduler.task('cron', id='move_pdf', minute=0, hour=0)
def move_agreement_pdf():
    source_dir = 'public/agreement_pdf'
    target_dir = 'tmp/backup_pdf'
    os.makedirs(target_dir, exist_ok=True)
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        shutil.move(os.path.join(source_dir, file_name), target_dir)
    print(str(len(file_names)) + " Moved!!")


@scheduler.task('cron', id='clear_sid', minute=0, hour=2)
def clear_sid():
    mongo.db.menu.update_many({}, {"$set": {"sid": []}})
    mongo.db.devices.update_many({}, {"$set":
                                      {"activeState": 0, "deviceState": 0}})
    mongo.db.customer_sid.update_many({}, {"$set": {"sid": []}})
    for f in os.listdir(MOU_PDF_PATH):
        os.remove(os.path.join(MOU_PDF_PATH, f))


# @scheduler.task('cron', id='remind_otp', minute=0)
def remind_otp():

    otpDataList = mongo.db.otpRegistration.find({
        "active": 1,
        "created": {"$lt": datetime.now() - timedelta(minutes=10)},
        "reminded": {"$ne": True}
    })
    otpDataList = list(otpDataList)
    sent_numbers = list()
    for otpData in otpDataList:
        phone_number = otpData["phone_number"]
        if phone_number not in sent_numbers:
            sent_numbers.append(phone_number)
            mongo.db.otpRegistration.update({
                "phone_number": phone_number
            },
                {
                    "$set": {"reminded": True}
            })
            data = {
                "message": "You have not yet completed your registration.",
                "phone": phone_number,
                "name": "User",
                "email": otpData["email"],
                "type": 1,
                "mediaUrl": "http://15.207.147.88:5000/franchisee/getLogo"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            # whatsapp message
            requests.post(spring_url +
                          'api/message/send-order-reminder',
                          data=json.dumps(data),
                          headers=headers)

            # email
            payload = {
                "attachmentPaths": [],
                "bccAddresses": [],
                "ccAddresses": [],
                "mailBody": "You have not yet completed your registration.",
                "mailSubject": "Registration Pending",
                "toAddresses": [otpData["email"]]
            }
            requests.post(mailer_url + 'send-mail', json=payload)


if __name__ == "__main__":
    print("starting...")
    refresh_zoho_access_token(force=True)
    app.run(host=cfg.Flask['HOST'],
            port=cfg.Flask['PORT'],
            threaded=cfg.Flask['THREADED'],
            debug=True)
    # app.run(debug=True)
