import os
import datetime
import sys

import requests
from icecream import ic

def send_notification(message,mode='test'):
    if mode=='production':
        token = os.environ['LINE_TOKEN']
    else:
        token=os.environ['TEST_LINE_TOKEN']
    headers = { "Authorization": "Bearer " + token }
    data = { 'message': message }
    result=requests.post("https://notify-api.line.me/api/notify",
        headers = headers, data = data)
    ic('notification send->',result.status_code)

def get_date(date=None,time_type=''):
    '''return(month,date,time)
        defualt type returns not modified date
    '''
    # ic(date)
    if not date:
        date_object=datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=+8)))
        #按照打卡時間表進行處理
        # ic('[打卡]')
        date=date_object.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # ic('[補打卡]')
        send_notification('補打卡','test')
    
    
    ic("get : day",date)
    if ' 'in date:
        date=datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        if time_type=='clockin':
            if date.minute<=10:
                date=date.replace(minute=0)
                date=date.replace(second=0)
            elif date.minute>=20 and date.minute<=40:
                date=date.replace(minute=30)
                date=date.replace(second=0)
            elif date.minute>=50:        
                date=date.replace(minute=0)
                date=date.replace(second=0)
                date=date+datetime.timedelta(hours=1)
        date=date.strftime("%Y-%m-%d %H:%M:%S")
        
        time=date.split()[1]
        day=date.split()[0]
    else:
        time='0:0:0'
        day=date
    month="-".join(day.split('-')[:-1])
    return (month,day,time)

def msg_gen(data,text,target_time=''):
    '''generate message
        args for present args variables
        text for text message
    '''
    message=f"""
姓名：{data['name']}
卡片ID:{data['cardid']}
時間戳：{get_date()[1]} {get_date()[2]} | {target_time}
==========
{text}
"""
    return message

def debug_info(e):
    ic('----[ERROR]----')
    ic(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    ic(exc_type, fname, exc_tb.tb_lineno)
    ic('----[ERROR]----')