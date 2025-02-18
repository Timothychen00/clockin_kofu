
import os
import pymongo
import certifi
import secrets
import datetime
import string

from dotenv import load_dotenv
# import pandas as pd
from icecream import ic
from termcolor import colored
from flask import jsonify

from main.tools import get_date

class DB():
    def __init__(self):
        print(os.environ['DB_MODE'])
        if os.environ['DB_MODE']=='test':
            self.client=pymongo.MongoClient(os.environ['DB_STRING_TEST'])
            try:
                self.client.admin.command('ping')
                print(colored('【本地】測試伺服器連線成功 local success','green'))
            except Exception as e:
                print(colored('【本地】測試伺服器連線失敗 local failed','red'))
        else:
            self.client=pymongo.MongoClient(os.environ['DB_STRING'],tlsCAFile=certifi.where())
            try:
                self.client.admin.command('ping')
                print(colored('【雲端】測試伺服器連線成功 remote success','green'))
            except Exception as e:
                print(colored('【雲端】測試伺服器連線失敗 remote failed','red'))
        
        
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
    
    # def save(self):
    #     df = pd.DataFrame(list(self.collection.find()))
    #     df.to_csv('data.csv',index=False)
    
db_model=DB()

class Today_Manage():
    def __init__(self):
        self.dbp=db_model.db.today_manage
        
    def check_out_of_date(self):
        '''check if the date is out of date
        '''
        result=list(self.dbp.find({'type':'today_manage'}))# mongodb>4 deprecates the cursor.count()
        doc_count=len(result)
        print("est:::::",doc_count)
        if doc_count!=0:
            data=result[0]['data']
            if data['date']!=get_date()[1]:
                ic("out of date")
                self.reset()
        else:
            self.reset()
        
        
    def reset(self):
        result=list(self.dbp.find({'type':'today_manage'}))
        doc_count=len(result)
        data={
            'date':get_date()[1],#get now date
            'clockin':{},
            'workovertime':{},
            'clockout':{},
        }
        if doc_count==0:
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
        result=list(self.dbp.find({'type':'today_manage'}))
        doc_count=len(result)
        print("count:",doc_count)
        if doc_count==0:
            self.reset()
            result=list(self.dbp.find({'type':'today_manage'}))
        data=result[0]['data']
        if cardid in data[mode]:
            return data[mode][cardid]
        else:
            return False
        
    def add(self,type,cardid,date):
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
        ic(result[0])
        data=result[0]['data']
        
        ic(cardid)
        
        if date!=get_date()[1]:# only control today
            return True
        if (cardid not in data[type]) and cardid!=' ': 
            data[type][cardid]=get_date(None)[2]
            ic('add',cardid,data[type][cardid])
            ic(data)
            self.dbp.update_one({'type':'today_manage'},{'$set':{'data':data}})
            return True
        else:
            return 'Already clocked'
    
    def remove(self,cardid,date):
        self.check_out_of_date()
        result=self.dbp.find({'type':'today_manage'})
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

class Notification():
    def __init__(self):
        pass
        self.collection=db_model.db.notification
    
    def create(self,args):
        data={
            'tags':args['tags'],
            'title':args['title'],
            'content':args['content'],
            'timestamp':get_date()[1]+ ' ' + get_date()[2],
            'publisher':args['publisher'],
            'status':args['status'],
        }
        
        result=self.collection.insert_one(data)
        msg=f'notification id:{result.inserted_id} create successful'
        ic(msg)
        return {'msg':msg}
    
    def find(self,filter):
        if not filter:
            filter={}
        ic(filter)
        result=list(self.collection.find(filter))
        for i in result:
            i['_id']=str(i['_id'])
        # ic(result)
        counts=len(result)
        # ic(counts)
        return jsonify(result)

    def delete(self,filter,confirm):
        if not filter:
            filter={}
        result=self.collection.find(filter)
        counts=len(list(result))
        if counts>1:#needs confirm
            if confirm==True:
                self.collection.delete_many(filter)
            else:
                msg='many notifications found, needs confirm'
        else:
            self.collection.delete_one(filter)
            msg='success'
        ic(msg)
        return {'msg':msg}

        
    
    # def edit(self,filter,data):
    #     if not filter:
    #         msg=
            




## 以下全部需要測試

class Settings():
    def __init__(self):
        pass
        self.collection=db_model.db.settings
    
    def create(self,args={}):
        data={# default
            'type':'settings',
            'data':
                {
                    'unitpay':90,
                    'duration':30,
                    'bias':15,
                    'notification-status':'None',
                    'notification-bind-token':{},
                    'notification-time':[],
                    'notification-userid':[],
                    'allow-multi':False,
                }
        }
        
        # 更新設定
        if args:
            for i in args:
                data[i]=args[i]
        
        
        result=self.collection.insert_one(data)
        msg=f'settings id:{result.inserted_id} create successful'
        ic(msg)
        return {'msg':msg}
    
    def find(self):#要檢查遞回爆炸的問題
        result=list(self.collection.find({'type':'settings'}))
        if len(result)==1:
            ic(result)
            result=result[0]
            result['_id']=str(result['_id'])
            return result
        elif len(result)==0:
            self.create()
            result=self.find()
            ic(result)
            return result

    def bind(self,userid):# 通過linebot端進行綁定
        result=self.find()
        
        if result:
            if result['data']['allow-multi']==True:# append
                result['data']['notification-userid'].append(userid)
                result['data']['notification-status']='bound'
                ic('line-token is allow-multi mode, userid inserted')
            else:
                result['data']['notification-userid']=[userid]
                result['data']['notification-status']='bound'
                ic('line-token is not allow-multi mode, userid replaced')
            self.updateSettings({'notification-status':result['data']['notification-status'],"notification-userid":result['data']['notification-userid']})
            return 'success'
        return 'no data'
    
    def check_binding_token(self,token):
        #要檢查時間有沒有符合
        result=self.find()
        ic(result)
        if result:
            if 'notification-bind-token' in result['data']:
                if 'token' in result['data']['notification-bind-token']:#token存在
                    if result['data']['notification-bind-token']['token']==token:
                        print("correct")
                        return "correct"
                    else:
                        print("incorrect")
                        return 'incorrect'
                else:
                    print('token not generated')
                    return 'token not generated'
            else:
                print('key does not exist')
                return 'key does not exist'
                    
            
    
    def generate_binding_token(self,length=30,valid_minutes=5):
        characters = string.ascii_letters + string.digits  # ascii_letters: 所有英文字母；digits: 所有數字
        token = ''.join(secrets.choice(characters) for _ in range(length))
        
        timestamp = datetime.datetime.now().isoformat()
        data={
            "token": token,
            "timestamp": timestamp,
            "valid_minutes": valid_minutes
        }
        
        self.updateSettings({"notification-bind-token":data})
        ic('已經生成token',data)
        
        return data
    
    def unbind(self,unbindAll,userid=''):# 接觸綁定
        result=self.find()
        if result:
            if unbindAll:
                result['data']['notification-userid']=[]
                ic('unbound all users')
                self.updateSettings({'notification-status':'None',"notification-userid":result['data']['notification-userid']})
                return 'success'
            else:
                if userid in result['data']['notification-userid'] and userid != '':
                    result['data']['notification-userid'].remove(userid)
                    ic('unbound the user'+ userid)
                    self.updateSettings({'notification-status':'None',"notification-userid":result['data']['notification-userid']})
                    return 'success'
                else:
                    ic('not bound!')
                    return 'not bound'
            
        return 'no data'
    
    def updateSettings(self,data):# from website
        result=list(self.collection.find({'type':'settings'}))
        result=result[0]
        for i in data:
            if i in ['unitpay','bias','duration','notification-time','notification-bind-token','notification-status','notification-userid']:
                result['data'][i]=data[i]
                
            else:
                print('not able')
                return 'err not able'
                
        self.collection.update_one({'type':"settings"},{'$set':result})
        return 'success'
    

    def delete(self,filter,confirm):
        if not filter:
            filter={}
        result=self.collection.find(filter)
        counts=len(list(result))
        if counts>1:#needs confirm
            if confirm==True:
                self.collection.delete_many(filter)
            else:
                msg='many notifications found, needs confirm'
        else:
            self.collection.delete_one(filter)
            msg='success'
        ic(msg)
        return {'msg':msg}