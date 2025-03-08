import pymongo
from icecream import ic

from main.models import db_model

result=ic(list(db_model.collection.find({})))
for i in result:
    i['_id']=int(i['_id'])
    db_model.collection.insert_one(i)
