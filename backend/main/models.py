import datetime
import os

import pymongo
from dotenv import load_dotenv
from flask_restful import Resource, reqparse

load_dotenv()

class DB():
    def __init__(self):
        self.client=pymongo.MongoClient("mongodb+srv://admin:"+os.environ['DB_PASS']+"@cluster0.ee06dbd.mongodb.net/?retryWrites=true&w=majority",tls=True,tlsAllowInvalidCertificates=True)
        self.db=self.client.staff
        self.collection=self.db.clockin
        
    def next_id(self):#get next id
        try:
            return int(self.collection.find().sort("_id",pymongo.DESCENDING).limit(1)[0]['_id'])+1
        except:
            return 1
db_model=DB()

class staff_manage(Resource):
    #define argument parser
    parser=reqparse.RequestParser()
    parser.add_argument('name',type=str,location=['values'])
    parser.add_argument('place',type=str,location=['values'])
    parser.add_argument('value',type=str,location=['values'])
    parser.add_argument('key',type=str,location=['values'])
    parser.add_argument('cardid',type=str,location=['values'])
    
    def get(self):
        args = self.parser.parse_args()
        filters={}
        print('filters',filters)
        print(args['key'],args['value'])
        if args['key']:
            filters={args['key']:args['value']}

        results=list(db_model.collection.find(filters))
        print(results)
        return results,200

    def post(self):
        args=self.parser.parse_args()
        print(args)
        data={
            '_id':str(db_model.next_id()),
            'name':args['name'],
            'cardid':args['cardid'],
            'place':args['place'],
            'log':{},
            'work':{},
            'workover':{}
        }

        print(data)
        db_model.collection.insert_one(data)
        return {'data':data,'msg':'data inserted!'},200
    
    def put(self):#進行（上班、下班、加班）的操作
        args=self.parser.parse_args()
        print(args)
        db_model.collection.update_one({args['key']:args['value']},{'$set':{'name':args['name'],'place':args['place'],'cardid':args['cardid']}})
    
    def delete(self):
        args=self.parser.parse_args()
        print(args)
        db_model.collection.delete_one({args['key']:args['value']})
        
    
class staff(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('type',type=str,location=['values'])
    parser.add_argument('time',type=str,location=['values'])
    parser.add_argument('value',type=str,location=['values'],required=True)
    parser.add_argument('key',type=str,location=['values'],required=True)
    
    def get(self):#獲取用戶的打卡狀況（當天&當月）
        args=self.parser.parse_args()
        result=db_model.collection.find_one({args['key']:args['value']})
        return result,200

    def post(self):#進行（上班、下班、加班）的操作
        args=self.parser.parse_args()
        data=db_model.collection.find_one({args['key']:args['value']})
        err=[]
        print(data)
        log=data['log']
        work=data['work']
        workover=data['workover']
        
        month,date,time=get_date(args['time'])
        
        work[month]=[0,0]
        workover[month]=[0,0]
        
        if not month in log:
            log[month]={}
        
        if not date in log[month]:#初始化
            log[month][date]={'clockin':'0:0:0','workovertime':'0:0:0','clockout':'0:0:0','duration':[[0,0],[0,0]]}
        if args['type'] in ['clockin','workovertime','clockout']:
            log[month][date][args['type']]=time

            d1=datetime.datetime.strptime(log[month][date]['clockin'],"%H:%M:%S")
            d2=datetime.datetime.strptime(log[month][date]['workovertime'],"%H:%M:%S")
            d3=datetime.datetime.strptime(log[month][date]['clockout'],"%H:%M:%S")
            
            if args['type']=='workovertime':
                if log[month][date]['clockin']=='0:0:0':
                    err.append('請先上班')
                else:
                    log[month][date]['duration'][0]=[(d2-d1).seconds//3600,((d2-d1).seconds//60)%60]
            elif args['type']=='clockout':
                if log[month][date]['clockin']=='0:0:0':
                    err.append('請先上班')
                elif log[month][date]['workovertime']=='0:0:0':
                    log[month][date]['duration'][0]=[(d3-d1).seconds//3600,((d3-d1).seconds//60)%60]
                    log[month][date]['duration'][1]=[0,0]
                else:
                    log[month][date]['duration'][1]=[(d3-d2).seconds//3600,((d3-d2).seconds//60)%60]
                     
            # work=[0,0]
            # workover=[0,0]
            print(1)
            for i in log[month]:#counting all the working hours
                print(i)
                print(log[month][i]['duration'][0])
                work[month][0]+=log[month][i]['duration'][0][0]
                work[month][1]+=log[month][i]['duration'][0][1]
                workover[month][0]+=log[month][i]['duration'][1][0]
                workover[month][1]+=log[month][i]['duration'][1][1]
                print(work)
                if work[month][1]>=60:
                    work[month][0]+=work[month][1]//60
                    work[month][1]%=60
                if workover[month][1]>=60:
                    workover[month][0]+=workover[month][1]//60
                    workover[month][1]%=60
            
        db_model.collection.update_one({args['key']:args['value']},{'$set':{'log':log,'work':work,'workover':workover}})
        return {'id':data['_id'],"type":args['type'],'log':log}
    

        
    
    def delete(self):#刪除記錄
        args=self.parser.parse_args()
        data=db_model.collection.find_one({args['key']:args['value']})
        log=data['log']
        
        month,day=get_date(args['time'])[0:2]
        
        if month in log:#初始化
            del log[month][day]
            db_model.collection.update_one({args['key']:args['value']},{'$set':{'log':log}})
            return {'msg':'log '+day+' delete!'}
        
    # def put(self):
    #     self.parser.add_argument('name',type=str,location='form')
    #     self.parser.add_argument('place',type=str,location='form')
    #     args=self.parser.parse_args()
    #     print(args)
    #     db_model.collection.update_one({args['key']:args['value']},{'$set':{'name':args['name'],'place':args['place']}})
    #     return {'msg':'data updated!'},200

def get_date(date=None):
    '''return(month,date,time)'''
    print(date)
    if not date:
        date=datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=+8))).strftime("%Y-%m-%d %H:%M:%S")
    if ' 'in date:
        time=date.split()[1]
        day=date.split()[0]
    else:
        time=None
        day=date
    month="-".join(day.split('-')[:-1])
    return (month,day,time)
    