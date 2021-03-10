from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient()
db=client.digitalSignage
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)

data = db.slots
post = {
  "id": 1,
  "slots": [
    "10-11"
  ]
}
data.insert(post)
for ele in data.find():
    pprint(ele)