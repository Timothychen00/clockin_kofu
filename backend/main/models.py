import os
import pymongo

from dotenv import load_dotenv
import pandas as pd
from icecream import ic
from termcolor import colored

from main.tools import get_date

class DB():
    def __init__(self):
        print(os.environ['DB_MODE'])
        if os.environ['DB_MODE']=='test':
            try:
                self.client=pymongo.MongoClient(os.environ['DB_STRING_TEST'])
                print(colored('【本地】測試伺服器連線成功 local success','green'))
            except:
                print(colored('【本地】測試伺服器連線失敗 local failed','red'))
        else:
            try:
                self.client=pymongo.MongoClient(os.environ['DB_STRING'],tls=True,tlsAllowInvalidCertificates=True)
                print(colored('【雲端】測試伺服器連線成功 local success','green'))
            except:
                print(colored('【雲端】伺服器連線失敗 cloud failed','red'))
        
        
        # self.client=pymongo.MongoClient(os.environ['DB_STRING_TEST'])
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
            'clockin':{},
            'workovertime':{},
            'clockout':{},
        }
        if result.count()==0:
            ic('today建立')
            self.dbp.insert_one({'type':'today_manage','data':data})
        else:
            ic('today重置')
            self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
        ic("today reset")
        # pass
        
    def check_inside(self,cardid,mode):
        '''check if the cardid is inside the today_manage
        '''
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
        # if result.count()==0:
        #     self.reset()
        #     result=self.dbp.find({'type':'today_manage'})
        data=result[0]['data']
        if cardid in data[mode]:
            return data[mode][cardid]
        else:
            return False
        
    def add(self,type,cardid,date):
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
        # if result.count()==0:
        #     self.reset()
        #     result=self.dbp.find({'type':'today_manage'})
        data=result[0]['data']
        
        ic(cardid)
        
        
        if date!=get_date()[1]:# only control today
            return True
        if (cardid not in data[type]) and cardid!=' ': 
            data[type][cardid]=get_date(None,'clockin')[2]
            ic('add',cardid,data[type][cardid])
            ic(data)
            self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
            return True
        else:
            return 'Already clocked'
    
    def remove(self,cardid,date):
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
        # if result.count()==0:
        #     self.reset()
        #     result=self.dbp.find({'type':'today_manage'})
        data=result[0]['data']
        data=result[0]['data']
        
        if date==get_date()[1]:# only control today
            for i in ['clockin','workovertime','clockout']:
                if cardid in data[i]:
                    data[i].pop(cardid)
                    self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
                    ic(cardid+'removed from today_manage')
            return True
        
today_manage=Today_Manage()
