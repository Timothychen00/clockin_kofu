import datetime
import os, pymongo, requests
from dotenv import load_dotenv
from flask_restful import Resource, reqparse
import pandas as pd


load_dotenv()

class DB():
    def __init__(self):
        self.client=pymongo.MongoClient("mongodb+srv://admin:"+os.environ['DB_PASS']+"@cluster0.ee06dbd.mongodb.net/?retryWrites=true&w=majority",tls=True,tlsAllowInvalidCertificates=True)
        self.db=self.client.staff
        self.collection=self.db.clockin
        self.today={
            'date':'',
            'clockin':[],
            'workovertime':[],
            'clockout':[],
        }
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

class staff_manage(Resource):
    #define argument parser
    parser=reqparse.RequestParser()
    parser.add_argument('name',type=str,location=['values'])
    parser.add_argument('place',type=str,location=['values'])
    parser.add_argument('value',type=str,location=['values'])
    parser.add_argument('jointime',type=str,location=['values'])
    parser.add_argument('key',type=str,location=['values'])
    parser.add_argument('cardid',type=str,location=['values'])
    
    def get(self):
        args = self.parser.parse_args()
        filters={}
        # print('filters',filters)
        print(args['key'],args['value'])
        if args['key']:
            filters={args['key']:args['value']}

        results=list(db_model.collection.find(filters))
        # print(results)
        return results,200

    def post(self):
        args=self.parser.parse_args()
        print(args)
        data={
            '_id':str(db_model.next_id()),
            'name':args['name'],
            'cardid':args['cardid'],
            'jointime':args['jointime'],
            'place':args['place'],
            'log':{},
            'work':{},
            'workover':{}
        }

        print(data)
        db_model.collection.insert_one(data)
        send_notification(message='\n姓名：'+data['name']+'\n'+data['cardid']+'\n加入成功',mode='test')
        return {'data':data,'msg':'data inserted!'},200
    
    def put(self):#進行（上班、下班、加班）的操作
        args=self.parser.parse_args()
        print(args)
        db_model.collection.update_one({args['key']:args['value']},{'$set':{'name':args['name'],'place':args['place'],'cardid':args['cardid'],'jointime':args['jointime']}})
    
    def delete(self):
        args=self.parser.parse_args()
        print(args)
        data=db_model.collection.find_one({args['key']:args['value']})
        db_model.collection.delete_one({args['key']:args['value']})
        send_notification(message='\n姓名：'+data['name']+'\n'+data['cardid']+'\n刪除成功',mode='test')
        
    
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
        print('\033[93m','[EDIT-CLOCKING]','\033[0m')
        print(data)
        print(args)
        if data:
            log=data['log']
            work=data['work']
            workover=data['workover']
            
            month,date,time=get_date(args['time'],'clockin')
            
            work[month]=[0,0]
            workover[month]=[0,0]
            
            if not month in log:
                log[month]={}
            
            if not date in log[month]:#初始化 上班打卡
                
                if data['cardid'] in db_model.today['clockin']:
                    send_notification(message='\n時間：'+str(time)+'\n姓名：'+data['name']+'\n'+data['cardid']+'\n'+'重複打卡 上班',mode='test')
                    return '已經打卡'
                
                log[month][date]={'clockin':'0:0:0','workovertime':'0:0:0','clockout':'0:0:0','duration':[[0,0],[0,0]]}
                
                if db_model.today['date']!=get_date()[1]:#up date to today
                    db_model.today['date']=get_date()[1]
                    db_model.today['clockin']=[]
                    db_model.today['workovertime']=[]
                    db_model.today['clockout']=[]
                else:
                    db_model.today['clockin'].append(data['cardid'])
                
                
            if args['type'] in ['clockin','workovertime','clockout']:
                if date not in log[month]:
                    return "請先上班"
                
                if data['cardid'] not in db_model.today[args['type']]:
                    log[month][date][args['type']]=time
                print("當前時間:",time)

                d1=datetime.datetime.strptime(log[month][date]['clockin'],"%H:%M:%S")
                d2=datetime.datetime.strptime(log[month][date]['workovertime'],"%H:%M:%S")
                d3=datetime.datetime.strptime(log[month][date]['clockout'],"%H:%M:%S")
                
                
                #calculate working hours
                if args['type']=='workovertime':
                    if data['cardid'] in db_model.today['workovertime']:
                        send_notification(message='\n時間：'+str(time)+'\n姓名：'+data['name']+'\n'+data['cardid']+'\n'+'重複打卡 加班',mode='test')
                        return '已經打卡'
                    
                    else:
                        log[month][date]['duration'][0]=[(d2-d1).seconds//3600,((d2-d1).seconds//60)%60]
                    
                    db_model.today['workovertime'].append(data['cardid'])
                    
                elif args['type']=='clockout':
                    if data['cardid'] in db_model.today['clockout']:
                        send_notification(message='\n時間：'+str(time)+'\n姓名：'+data['name']+'\n'+data['cardid']+'\n'+'重複打卡 下班',mode='test')
                        return '已經打卡'
                    
                    elif log[month][date]['workovertime']=='0:0:0':
                        log[month][date]['duration'][0]=[(d3-d1).seconds//3600,((d3-d1).seconds//60)%60]
                        log[month][date]['duration'][1]=[0,0]
                    else:
                        log[month][date]['duration'][1]=[(d3-d2).seconds//3600,((d3-d2).seconds//60)%60]
                        
                    db_model.today['clockout'].append(data['cardid'])

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
                
                # 發送即時通知
                dtype='上班打卡'
                if args['type']=='clockout':
                    dtype='下班打卡'
                elif args['type']=='workovertime':
                    dtype='加班加班'
                send_notification(message='\n時間：'+str(time)+'\n姓名：'+data['name']+'\n'+data['cardid']+'\n'+dtype+'成功',mode=os.environ['MODE'])
                
            db_model.collection.update_one({args['key']:args['value']},{'$set':{'log':log,'work':work,'workover':workover}})
            return 'OK'
        else:
            return 'Failed'
    
    def delete(self):#刪除記錄
        print('delete')
        args=self.parser.parse_args()
        data=db_model.collection.find_one({args['key']:args['value']})
        log=data['log']
        
        if args['time']:
            month,day=get_date(args['time'])[0:2]
            
        else:
            return "No time input!",413
        
        print(month,day)
        print(log)
        print(log[month])
        if month in log:#初始化
            if data['cardid'] in db_model.today['clockin']:
                db_model.today['clockin'].remove(data['cardid'])
            if data['cardid'] in db_model.today['workovertime']:
                db_model.today['workovertime'].remove(data['cardid'])
            if data['cardid'] in db_model.today['clockout']:
                db_model.today['clockout'].remove(data['cardid'])

            del log[month][day]
            db_model.collection.update_one({args['key']:args['value']},{'$set':{'log':log}})
            send_notification(message='\n時間：'+'\n姓名：'+data['name']+'\n'+data['cardid']+'\n'+'刪除'+day+'打卡紀錄',mode='test')
            return {'msg':'log '+day+' delete!'}


def get_date(date=None,time_type=''):
    '''return(month,date,time)
        defualt type returns not modified date
    '''
    print(date)
    if not date:
        date_object=datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=+8)))
        #按照打卡時間表進行處理
        print('[打卡]')
        date=date_object.strftime("%Y-%m-%d %H:%M:%S")
    else:
        print('[補打卡]')
        send_notification('補打卡','test')
        
    if ' 'in date:
        date=datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        if time_type=='clockin':
            if date.minute<=10:
                date=date.replace(minute=0)
            elif date.minute>=20 and date.minute<=40:
                date=date.replace(minute=30)
            elif date.minute>=50:        
                date=date.replace(minute=0)
                date=date+datetime.timedelta(hours=1)
        date=date.strftime("%Y-%m-%d %H:%M:%S")
        
        time=date.split()[1]
        day=date.split()[0]
    else:
        time=None
        day=date
    month="-".join(day.split('-')[:-1])
    return (month,day,time)

def send_notification(message,mode='production'):
    if mode=='production':
        token = os.environ['LINE_TOKEN']
    else:
        token=os.environ['TEST_LINE_TOKEN']
    headers = { "Authorization": "Bearer " + token }
    data = { 'message': message }
    result=requests.post("https://notify-api.line.me/api/notify",
        headers = headers, data = data)
    print('notification send->',result.status_code)
    