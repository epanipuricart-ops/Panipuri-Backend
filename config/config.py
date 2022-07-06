#!/usr/bin/env python3
# -*- coding: utf-8 -*-


Flask = {
    'HOST': "0.0.0.0",
    'PORT': 5000,
    'THREADED': True
}

OrderFlask = {
    'HOST': "0.0.0.0",
    'PORT': 5001,
    'THREADED': True
}

IOTFlask = {
    'HOST': "0.0.0.0",
    'PORT': 5002,
    'THREADED': True
}
WherebyConfig = {
    "API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmFwcGVhci5pbiIsImF1ZCI6Imh0dHBzOi8vYXBpLmFwcGVhci5pbi92MSIsImV4cCI6OTAwNzE5OTI1NDc0MDk5MSwiaWF0IjoxNjMwMTMwNzE0LCJvcmdhbml6YXRpb25JZCI6MTI2MjkyLCJqdGkiOiI3NWJmODYyMS1iZThmLTQwZWUtYjk1NS02NmM5M2Q2MjY4OWUifQ.fpDBFa8l-BfKrOUQ56L65KPoWrKT2V9So-vs9uJCLB4"
}

FIREBASE_KEY = "AAAAy-ge0a8:APA91bEFsUxaUNvX21r2zqvVRjgQ_hVxRe5W6mucLA87_kYQ-3sdM6sV8ug61Fqecd948yR72Xz8k66us2aYXVIm0SUdmFSUknFeQEwhmiBvxyZSIxBYaDYh2Ym65vsniMdSVSJSkwYU"

ZohoConfig = {
    "refresh_token": "1000.b705a2f90c6a7badb070831561fe6729.6e5e655a279b83ff193ffbd14f066d66",
    "client_id": "1000.TM9579QXAQRONAPUYM8I9V3JR1AIZY",
    "client_secret": "3e4811b9ced7df56e36e1e5090c49b012c03092fb9",
    "organization_id": "60003188756"
}

DEVICE_SHUTDOWN_EXCEPTION = ["epanipuricart.Bhubaneswar.1"]

DefaultMenu = {
    "cartName": "My Cart",
    "deliveryCharge": 0,
    "flatDiscount": 0,
    "gst": 0,
    "isActive": False,
    "menu": [
        {
            "category": "Panipuri Shots",
            "closeCategory": False,
            "items": [
                {
                    "name": "Hingoli",
                    "img": "",
                    "desc": "",
                    "price": 25,
                    "ingredients": "",
                    "customDiscount": "",
                    "isOutOfStock": False,
                    "gst": 0
                },
                {
                    "name": "Lemon",
                    "img": "",
                    "desc": "",
                    "price": 35,
                    "ingredients": "",
                    "customDiscount": "",
                    "isOutOfStock": False,
                    "gst": 0
                }
            ]
        },
        {
            "category": "Panipuri Fills",
            "closeCategory": False,
            "items": [
                {
                    "name": "Pudina",
                    "img": "",
                    "desc": "",
                    "price": 50,
                    "ingredients": "",
                    "customDiscount": "",
                    "isOutOfStock": False,
                    "gst": 0
                },
                {
                    "name": "Hajmola",
                    "img": "",
                    "desc": "",
                    "price": 40,
                    "ingredients": "",
                    "customDiscount": "",
                    "isOutOfStock": False,
                    "gst": 0
                }
            ]
        }
    ]
}


STATE_CODES = {
    "Andhra Pradesh": "AD",
    "Arunachal Pradesh": "AR",
    "Assam": "AS",
    "Bihar": "BR",
    "Chattisgarh":	"CG",
    "Delhi": "DL",
    "Goa": "GA",
    "Gujarat": "GJ",
    "Haryana": "HR",
    "Himachal Pradesh": "HP",
    "Jammu and Kashmir": "JK",
    "Jharkhand": "JH",
    "Karnataka": "KA",
    "Kerala": "KL",
    "Lakshadweep Islands": "LD",
    "Madhya Pradesh": "MP",
    "Maharashtra": "MH",
    "Manipur": "MN",
    "Meghalaya": "ML",
    "Mizoram": "MZ",
    "Nagaland": "NL",
    "Odisha": "OD",
    "Pondicherry": "PY",
    "Punjab": "PB",
    "Rajasthan": "RJ",
    "Sikkim": "SK",
    "Tamil Nadu": "TN",
    "Telangana": "TS",
    "Tripura": "TR",
    "Uttar Pradesh": "UP",
    "Uttarakhand": "UK",
    "West Bengal": "WB",
    "Andaman and Nicobar Islands": "AN",
    "Chandigarh": "CH",
    "Dadra & Nagar Haveli and Daman & Diu": "DNHDD",
    "Ladakh": "LA",
    "Other Territory": "OT"

}

estimate_mail_body = """
<div style="background: #fbfbfb;">
    <div>
        <div style="padding: 2% 3%;max-width: 150px;max-height:50px;"><img style="max-width: 100%; height: auto; max-height: 50px;" alt="Water" name="Logo" src="https://books.epanipuricart.com/api/v3/settings/templates/invoicelogo/2-148fcfdf6724e4d7879ccf1c8460f5d8448689471b4376428f6afbeeae440c91357e9cc5674702088f7640642e2af0f6"></div>
    </div>
    <div style="padding:3%;text-align:center;background: #4190f2;">
        <div style="color:#fff;font-size:20px;font-weight:500;">Estimate #{est_num}</div>
    </div>
    <div style="max-width:560px;margin:auto;padding: 0 3%;">
        <div style="padding: 30px 0; color: #555;line-height: 1.7;">Dear {name}, <br><br>Thank you for contacting us. Your estimate can be viewed, printed and downloaded as PDF from the link below. <br></div>
        <div style="padding: 3%; background: #fefff1; border: 1px solid #e8deb5; color: #333;">
            <div style="padding: 0 3% 3%; border-bottom: 1px solid #e8deb5; text-align: center;">
                <h4 style="margin-bottom: 0;"> ESTIMATE AMOUNT</h4>
                <h2 style="color: #D61916; margin-top: 10px;">Rs.{amount}</h2>
            </div>
            <div style="margin:auto; max-width:350px; padding: 3%;">
                <p><span style="width: 35%; padding-left: 10%; float:left;">Estimate No</span><span style="width: 40%; padding-left: 10%;display: inline-block;"><b>{est_num}</b></span></p>
                <p><span style="width: 35%;padding-left: 10%;float:left;">Estimate Date</span><span style="width: 40%; padding-left: 10%;"><b>{date}</b></span></p>
            </div>
            <div style="text-align: center;margin: 25px 0;visibility: hidden;">
                <a style="text-decoration: none;" href="https://books.epanipuricart.com/portal/wnsfpl/secure?CEstimateID=2-0a8ede9d6a7dbfe7652d2e78aaa73bb0624af194769192a07ddd07a490adccc080f85942f69cb7cdf593e7bb4efd382bd568e698835815da3dee0aeec546433f99935a6181fa8eb0">
                    <span style="background-color:#4dcf59; border: 1px solid #49bd54; cursor: pointer; text-align: center; min-width: 140px; color: #fff; display: inline-block; text-decoration: none; padding: 10px 20px">VIEW ESTIMATE</span></a>
            </div>
        </div><br>
        <div style="padding: 3% 0;line-height: 1.6;"> Regards,
            <div style="color: #8c8c8c; font-weight: 400">Harish Neotia </div>
            <div style="color: #b1b1b1">Water N Spices Foodsz Pvt Ltd</div>
        </div>
    </div>
</div><br><br>
<div>Harish Neotia </div>Water N Spices Foodsz Pvt Ltd
<div>www.epanipuricart.com</div>
"""

ZOHO_OAUTH_SCOPES = "ZohoBooks.contacts.ALL,ZohoBooks.estimates.ALL, ZohoBooks.salesorders.ALL, ZohoCRM.modules.contacts.ALL,ZohoBooks.invoices.ALL,ZohoBooks.customerpayments.ALL"
