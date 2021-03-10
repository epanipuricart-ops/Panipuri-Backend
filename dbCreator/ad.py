from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient()
db=client.digitalSignage
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)

data = db.advertisement
post = {
    "ad": [
    {
      "name": "demo",
      "uid": 1,
      "category": "footwear",
      "vendor_name": "abc",
      "address": "demo_address",
      "slot": "10-11",
      "duration": 30,
      "status": "active",
      "day": "null"
    },
    {
      "name": "1568484610.jpg",
      "category": "clothing",
      "vendor_name": "abc",
      "address": "xyz",
      "slot": "10-11",
      "duration": 15,
      "uid": 4,
      "status": "active",
      "day": "null"
    },
    {
      "name": "1568484611.jpg",
      "category": "clothing",
      "vendor_name": "abc",
      "address": "xyz",
      "slot": "10-11",
      "duration": 15,
      "uid": 5,
      "status": "active",
      "day": "null"
    },
    {
      "name": "1568484612.jpg",
      "category": "clothing",
      "vendor_name": "abc",
      "address": "xyz",
      "slot": "10-11",
      "duration": 15,
      "uid": 6,
      "status": "active",
      "day": "null"
    },
    {
      "name": "1568484613.jpg",
      "category": "clothing",
      "address": "xyz",
      "slot": "10-11",
      "duration": 15,
      "uid": 7,
      "vendor_name": "abc",
      "day": "25-03-2020",
      "status": "scheduled"
    }
  ],
  "id": 1
}
data.insert(post)
for ele in data.find():
    pprint(ele)