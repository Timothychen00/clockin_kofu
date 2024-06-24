import os
import sys
import datetime

from flask_restful import Resource, reqparse
from icecream import ic
from termcolor import colored

from main.tools import get_date
from main.tools import send_notification
from main.tools import msg_gen
from main.tools import debug_info
from main.models import db_model
from main.models import today_manage

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
            'hash_id':
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
        send_notification(ic(msg_gen(data,'加入成功')),mode='test')
        
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
        send_notification(ic(msg_gen(data,'刪除成功')),mode='test')
        
    
class staff(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('type',type=str,location=['values'])
    parser.add_argument('time',type=str,location=['values'])
    parser.add_argument('connection_mode',type=str,location=['values'])
    parser.add_argument('value',type=str,location=['values'],required=True)
    parser.add_argument('key',type=str,location=['values'],required=True)
    
    def get(self):#獲取用戶的打卡狀況（當天&當月）
        args=self.parser.parse_args()
        result=db_model.collection.find_one({args['key']:args['value']})
        return result,200

    def post(self):#進行（上班、下班、加班）的操作
        # try:
        args=self.parser.parse_args()
        ic('[post]')
        ic(args)
        data=db_model.collection.find_one({args['key']:args['value']})
        
        if args['connection_mode']=='buttonless':
            ic('configing connection_mode into buttonless')
            now_time=datetime.datetime.strptime(get_date(None,'clockin')[2],"%H:%M:%S")
            if today_manage.check_inside(args['value'],'clockin')==False:
                ic('set mode to clockin')
                args['type']='clockin'
                
            elif today_manage.check_inside(args['value'],'clockout')==False:
                ic('set mode to clockout')
                clockin_time=datetime.datetime.strptime(today_manage.check_inside(args['value'],'clockin'),"%H:%M:%S")
                if now_time-clockin_time>datetime.timedelta(minutes=60):
                    args['type']='clockout'
                else:
                    ic('60分鐘內重複打卡clockin->clockout')
                    return "already done!"
            else:
                ic('60分鐘內重複打卡clockout->clockout')
                return "already done!"
                
        
    #暫時倒流
        if args['type']=='workovertime':
            args['type']='clockin'
            
        print('\033[93m','[EDIT-CLOCKING]','\033[0m')
        print(data)
        print(args)
        if data:
            log=data['log']
            work=data['work']
            workover=data['workover']
            
            month,date,time=ic(get_date(args['time'],'clockin'))
            
            
            work[month]=[0,0]
            workover[month]=[0,0]
            
            if month not in log:
                log[month]={}
                ic('new month')
            
            if date not in log[month]:#初始化
                
                log[month][date]={'clockin':'0:0:0','workovertime':'0:0:0','clockout':'0:0:0','duration':[[0,0],[0,0]]}
                
            if args['type'] in ['clockin','workovertime','clockout']:
                ic('111111:')
                ic(args['type'])
                ic(data['cardid'])
                ic(date)
                if ic(today_manage.add(args['type'],data['cardid'],date))=='Already clocked':
                    send_notification(ic(msg_gen(data,'重複打卡 '+args['type'],args['time'])),'test')
                    return '已經打卡'
                else:
                    log[month][date][args['type']]=time#紀錄打卡時間
                
                ic("當前時間:",time)


                #calculate working hours
                if args['type']=='clockin':
                    log[month][date]['duration'][0]=[0,0]
                    log[month][date]['duration'][1]=[0,0]
                    
                elif args['type']=='clockout' or args['type']=='workovertime':
                    d1=datetime.datetime.strptime(log[month][date]['clockin'],"%H:%M:%S")
                    d2=datetime.datetime.strptime(log[month][date]['workovertime'],"%H:%M:%S")
                    d3=datetime.datetime.strptime(log[month][date]['clockout'],"%H:%M:%S")
                
                    if args['type']=='workovertime':
                        log[month][date]['duration'][0]=[(d2-d1).seconds//3600,((d2-d1).seconds//60)%60]
                        
                    elif args['type']=='clockout':
                        
                        if log[month][date]['workovertime']=='0:0:0':
                            log[month][date]['duration'][0]=[(d3-d1).seconds//3600,((d3-d1).seconds//60)%60]
                            log[month][date]['duration'][1]=[0,0]
                        else:
                            log[month][date]['duration'][1]=[(d3-d2).seconds//3600,((d3-d2).seconds//60)%60]

                for i in log[month]:#counting all the working hours

                    work[month][0]+=log[month][i]['duration'][0][0]
                    work[month][1]+=log[month][i]['duration'][0][1]
                    workover[month][0]+=log[month][i]['duration'][1][0]
                    workover[month][1]+=log[month][i]['duration'][1][1]

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
                send_notification(ic(msg_gen(data,dtype+'成功',args['time'])),mode=os.environ['MODE'])
                
            db_model.collection.update_one({args['key']:args['value']},{'$set':{'log':log,'work':work,'workover':workover}})
            return 'OK'
        else:
            print(colored("Card Not Found!",'red'))
            return 'Not Found'
        # except Exception as e:
        #     debug_info(e)
        #     return 'Failed'
            
    
    def delete(self):#刪除記錄
        ic('delete')
        args=self.parser.parse_args()
        data=db_model.collection.find_one({args['key']:args['value']})
        log=data['log']
        
        if args['time']:
            month,day=get_date(args['time'])[0:2]
            
        else:
            return "No time input!",413
        
        ic(month,day)
        ic(log)
        ic(log[month])
        if month in log:#初始化
            today_manage.remove(data['cardid'],day)

            del log[month][day]
            db_model.collection.update_one({args['key']:args['value']},{'$set':{'log':log}})
            send_notification(ic(msg_gen(data,'刪除'+day+'打卡記錄',args['time'])),mode='test')
            return {'msg':'log '+day+' delete!'}


class settings(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('unitpay',type=int,location=['values'])
    parser.add_argument('duration',type=int,location=['values'])
    parser.add_argument('bias',type=int,location=['values'])
    def get(self):
        result=db_model.db.settings.find_one({'type':'settings'})
        if result:
            return result['data']
        else:
            db_model.db.settings.insert_one({'type':'settings','data':{'unitpay':90,'duration':30,'bias':15}})
            
    def put(self):
        args=self.parser.parse_args()
        result=db_model.db.settings.find_one({'type':'settings'})
        if args['unitpay']:
            result['data']['unitpay']=args['unitpay']
        if args['duration']: 
            result['data']['duration']=args['duration']
        if args['bias']:    
            result['data']['bias']=args['bias']
        print(result)
        db_model.db.settings.update_one({"type":'settings'},{'$set':{'data':result['data']}})
        return 'OK'