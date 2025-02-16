import os

import certifi
import pymongo
from icecream import ic

client=pymongo.MongoClient("mongodb://localhost:27017")
db=client.staff
collection=db.today_manage
result=collection.find({'type':'today_manage'})
collection.insert_one({'type':'today_manage'})
ic(result[0])
