from flask import request,session
import requests
import datetime,pymongo,os
from dotenv import load_dotenv
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
    
def send_notification(message):
    token = os.environ['LINE_TOKEN']
    headers = { "Authorization": "Bearer " + token }
    data = { 'message': message }
    result=requests.post("https://notify-api.line.me/api/notify",
        headers = headers, data = data)
    print('notification send->',result.status_code)

class staff():
    def delete(key,value,time):
        result=db_model.collection.find_one({key:value})
        if result:
            log=result['log']
            
            month,day=get_date(time)[0:2]
            
            if month in log:#初始化
                del log[month][day]
                db_model.collection.update_one({key:value},{'$set':{'log':log}})
                return {'msg':'log '+day+' delete!'}
            return {'err':'month not in log'}
        return {'err':'document not found'}
    
    def get()

        
        
