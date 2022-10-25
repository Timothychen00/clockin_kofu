#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymongo,os
from dotenv import load_dotenv
load_dotenv()
import json


client=pymongo.MongoClient("mongodb+srv://admin:"+os.environ['DB_PASS']+"@cluster0.ee06dbd.mongodb.net/?retryWrites=true&w=majority",tls=True,tlsAllowInvalidCertificates=True)
db=client.staff
collection=db.clockin


results=list(collection.find())
length=len(results)
os.remove('data.json')


# write
with open('data.json','w+',encoding='utf-8')as f1:
    json.dump(results,f1,ensure_ascii=False)
    
# read
with open('data.json','r+',encoding='utf-8')as f2:
    # print(f2.read())
    data=json.load(f2)
    for i in data:
        i['_id']=str(i['_id'])
        collection.insert_one(i)
    
    print(data)