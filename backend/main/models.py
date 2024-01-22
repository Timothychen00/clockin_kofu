import datetime
import os, pymongo, requests
from dotenv import load_dotenv
from flask_restful import Resource, reqparse
import pandas as pd
from icecream import ic
from main.tools import send_notification,get_date,msg_gen


load_dotenv()

class DB():
    def __init__(self):
        self.client=pymongo.MongoClient("mongodb+srv://admin:"+os.environ['DB_PASS']+"@cluster0.ee06dbd.mongodb.net/?retryWrites=true&w=majority",tls=True,tlsAllowInvalidCertificates=True)
        self.db=self.client.staff
        self.collection=self.db.clockin

        # date
        # 
        
    def next_id(self):#get next id
        try:
            return int(self.collection.find().sort("_id",pymongo.DESCENDING).limit(1)[0]['_id'])+1
        except:
            return 1
    
    def save(self):
        df = pd.DataFrame(list(self.collection.find()))
        df.to_csv('data.csv',index=False)
        
        
    
db_model=DB()

class Today_Manage():
    def __init__(self):
        self.dbp=db_model.db.today_manage
        
    def check_out_of_date(self):
        '''check if the date is out of date
        '''
        result=self.dbp.find({'type':'today_manage'})
        if result.count()!=0:
            data=result[0]['data']
            if data['date']!=get_date()[1]:
                ic("out of date")
                self.reset()
        
        
    def reset(self):
        result=self.dbp.find({'type':'today_manage'})
        data={
            'date':get_date()[1],#get now date
            'clockin':[],
            'workovertime':[],
            'clockout':[],
        }
        if result.count()==0:
            ic('today建立')
            self.dbp.insert_one({'type':'today_manage','data':data})
        else:
            ic('today重置')
            self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
        ic("today reset")
        # pass
        
    def add(self,type,cardid):
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
        data=result[0]['data']
        ic(cardid)
        if (cardid not in data[type]) and cardid!=' ': 
            data[type].append(cardid)
            ic(data)
            self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
            return True
        else:
            return 'Already clocked'
    
    def remove(self,cardid):
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
        data=result[0]['data']
        
        for i in ['clockin','workovertime','clockout']:
            if cardid in data[i]:
                data[i].remove(cardid)
                self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
                ic(cardid+'removed from today_manage')
        return True
        
today_manage=Today_Manage()
