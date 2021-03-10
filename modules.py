import requests
import time
import os
from datetime import datetime
from pymongo import MongoClient
import urllib.parse
import urllib.request
from urllib.error import URLError,HTTPError
import json

client = MongoClient()
db=client.panipuriKartz

url = "http://epanipuricart.com/online/WebApi/verifyToken"

def checkValidity(tok):
    values = {}
    headers = {'Authorizations': tok}

    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    try:
        req = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            status_code = response.getcode()
        return data, status_code
    except HTTPError as e:
        data = json.loads(e.read())
        status_code = e.code
        return data, status_code


def authenticate(tok):
    verificationStatus = 0
    ele = db.users.find_one({"token":tok})
    if ele:
        verificationStatus = 1
        uid = ele['uid']

    if verificationStatus == 1:
        return True, uid
    else:
        return False, None 

def create_dict(t):
    if t == '3':
        return [{"name": "n1"},{"name":"n2"},{"name":"n3"}]
    elif t == '6':
        return [{"name": "n1"},{"name":"n2"},{"name":"n3"}, {"name": "n4"}, {"name": "n5"}, {"name": "n6"}]
    else:
        return [{"name": "n1"},{"name":"n2"},{"name":"n3"}, {"name": "n4"}, {"name": "n5"}, {"name": "n6"}, {"name": "n7"}, {"name": "n8"}, {"name": "n9"}]

def sort(uid):
    response = db.stats.find_one({"uid": uid})
    if response:
        if response['data']:
            t = db.devices.find_one({"uid": uid})["type"]
            if t == '3':
                arr = []
                d1 = {}
                d2 = {}
                d3 = {}
                l1 = []
                l2 = []
                l3 = []

                for ele in response["data"]:   
                    if ele['name'] == 'n1':
                        a = {}
                        a['date'] = ele['date']
                        a['status'] = ele['status']
                        #a['low'] = ele['low']
                        l1.append(a)
                    elif ele['name'] == 'n2':
                        a = {}
                        a['date'] = ele['date']
                        a['status'] = ele['status']
                        #a['low'] = ele['low']
                        l2.append(a)
                    else:
                        a = {}
                        a['date'] = ele['date']
                        a['status'] = ele['status']
                        #a['low'] = ele['low']
                        l3.append(a)
                d1['name'] = 'n1'
                d2['name'] = 'n2'
                d3['name'] = 'n3'
                if len(l1) < 50:
                    d1['data'] = l1
                    d2['data'] = l2
                    d3['data'] = l3
                else:
                    d1['data'] = l1[-50:]
                    d2['data'] = l2[-50:]
                    d3['data'] = l3[-50:]
                arr.append(d1)
                arr.append(d2)
                arr.append(d3)
                return True,arr
            
        else:
            arr=[]
            return True, arr
    else:
        return False, None

def sort_level(uid):
    response = db.levels.find_one({"uid": uid})
    if response:
        if response['data']:
            t = db.devices.find_one({"uid": uid})["type"]
            if t == '3':
                arr = []
                d1 = {}
                d2 = {}
                d3 = {}
                l1 = []
                l2 = []
                l3 = []

                for ele in response["data"]:   
                    if ele['name'] == 'n1':
                        a = {}
                        a['date'] = ele['date']
                        a['low'] = ele['low']
                        #a['low'] = ele['low']
                        l1.append(a)
                    elif ele['name'] == 'n2':
                        a = {}
                        a['date'] = ele['date']
                        a['low'] = ele['low']
                        #a['low'] = ele['low']
                        l2.append(a)
                    else:
                        a = {}
                        a['date'] = ele['date']
                        a['low'] = ele['low']
                        #a['low'] = ele['low']
                        l3.append(a)
                d1['name'] = 'n1'
                d2['name'] = 'n2'
                d3['name'] = 'n3'
                if len(l1) < 20:
                    d1['data'] = l1
                    d2['data'] = l2
                    d3['data'] = l3
                else:
                    d1['data'] = l1[-20:]
                    d2['data'] = l2[-20:]
                    d3['data'] = l3[-20:]
                arr.append(d1)
                arr.append(d2)
                arr.append(d3)
                return True,arr
            
        else:
            arr=[]
            return True, arr
    else:
        return False, None
        