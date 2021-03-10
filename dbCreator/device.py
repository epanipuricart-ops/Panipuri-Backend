from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient()
db=client.digitalSignage
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)

data = db.devices
post = {
    "id": 1,
  "devices": [
    {
        'device_id' : 200000,
        'address' : 'abcfgh',
        'category': 'electronics',
        'store_name': 'raj electronics'

    }
  ]
}
data.insert(post)
for ele in data.find():
    pprint(ele)