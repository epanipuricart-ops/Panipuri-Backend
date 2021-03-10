from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient()
db=client.digitalSignage
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)

data = db.tickets
post = {
    "id": 1,
  "tickets": [
    {
        'tickets_no' : '01',
        'vendor_name' : 'abc',
        'contact': '9437992433',
        'address': 'nayapalli',
        'issue' : 'xyz',
        'status' : 'open'
    },
    {
        'tickets_no' : '02',
        'vendor_name' : 'pyr',
        'contact': '9437992433',
        'address': 'nayapalli',
        'issue' : 'xyz',
        'status' : 'open'
    }
  ]
}
data.insert(post)
for ele in data.find():
    pprint(ele)