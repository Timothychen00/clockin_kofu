import os
import time

from flask import Flask,request,abort
from flask_restful import Api
from flask_restful import Resource
from dotenv import load_dotenv
from termcolor import colored
from icecream import ic
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# 自動聯絡員工
# linebot
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,	
    ReplyMessageRequest,
    PushMessageRequest,  # 用來構造推播訊息的資料結構
    TextMessage
)


path=f"main/{os.environ.get('ENV_TYPE','')}.env"
print(os.getenv('ENV_TYPE'))
print(os.getenv(''))

print(colored("\n[Using ENV]->>>>>"+path+'\n',"green"))
load_dotenv(path)

from main.api import staff_manage
from main.api import staff
from main.api import notifications
from main.api import settings
from main.models import Settings,Notification
from main.routes import app_route
from main.tools import get_date


class Config(object):
    SCHEDULER_TIMEZONE = 'Asia/Taipei'  # 配置时区
    SCHEDULER_API_ENABLED = True  # 添加API

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    #如果要用vue要修改成以下這樣
  #   jinja_options.update(dict(
  #   block_start_string='(%',
  #   block_end_string='%)',
  #   variable_start_string='((',
  #   variable_end_string='))',
  #   comment_start_string='(#',
  #   comment_end_string='#)',
  # ))
  
channel_secret = os.getenv('Channel_secret', None)
channel_access_token = os.getenv('Channel_access_token', None)
handler = WebhookHandler(channel_secret)
configuration = Configuration(
    access_token=channel_access_token
)

  
app=CustomFlask(__name__,static_folder="main/static",template_folder="main/templates")
app.config.update({
    'SCHEDULER_API_ENABLED': True,
})

api = Api(app)
scheduler=APScheduler(BackgroundScheduler({'apscheduler.timezone': 'Asia/Taipei','daemon':False}))

app.register_blueprint(app_route)
api.add_resource(staff_manage,'/api/manage')
api.add_resource(staff,'/api/staff')
api.add_resource(settings,'/api/settings')
api.add_resource(notifications,'/api/notifications')

#Scheduler-------
times=0
def task1(x):
    global times
    times+=1
    
    print(f'task 1 executed --------: {times}', time.time())


def task2(x):
    print(f'task 2 executed --------: {x}', time.time())


app.secret_key = 'os.environ.get("SECRET") or os.urandom(24)'

@app.before_request
def show():
    # print(request.headers,request.get_data().decode())
    pass


# Bot Integration
# linebot callback--------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def reply_message(reply_token,messages):
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)
		line_bot_api.reply_message_with_http_info(
			ReplyMessageRequest(
				reply_token=reply_token,
				messages=messages
			)
		)
  
@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    # 當用戶輸入「綁定」時
	if "bind" in event.message.text.strip() :
		if '-' in event.message.text:
			recv_token=event.message.text.split('-')[1]
			print('[main][檢測綁定]')
			ic(recv_token)
			result=Settings().check_binding_token(recv_token)
			if result=='correct':
				Settings().bind(event.source.user_id)
				reply_message(event.reply_token,[TextMessage(text='綁定成功！確認網站上的推送時間正確後，就可以等待時間到的推送咯～')])
				return 0
			else:
				reply_message(event.reply_token,[TextMessage(text='綁定失敗！確認一下token有沒有錯誤吧～')])
				return 0
    
    
        # 定義一個延時推播的函數
		# with ApiClient(configuration) as api_client:
		# 	line_bot_api = MessagingApi(api_client)
		# 	line_bot_api.push_message_with_http_info(
        #         PushMessageRequest(
        #             to=event.source.user_id,
        #             messages=[TextMessage(text="記住了")]
        #         )
        #     )
        # 以 threading.Thread 開啟一個新的執行緒執行 delayed_push 函數，不阻塞主線
    
    # 同時回覆用戶原本的訊息（這裡依舊做 echo，如果你希望修改回覆內容，也可以在此改變）
	reply_message(event.reply_token,[TextMessage(text=event.message.text)])

def get_available_notifications(tag):
    processed_result=[]
    results=Notification().find({'status':"inqueue"})
    for result in results:
        if tag in result['tags']:
            ic(tag)
            ic()
            if get_date()[1]==result['timestamp'].split(' ')[0]:
                processed_result.append(result)

    return processed_result

def send_notifications():
    print('send_notification')
    current_setting=Settings().find()['data']
    ic(current_setting)
    users=current_setting['notification-userid']
    # 發送linebot訊息

    #獲取要發送的打卡訊息
    msgs=get_available_notifications('clockin')
    
    msg_str="打卡紀錄\n"
    ic(msgs)
    
    msgs_ids=[]
    for i in msgs:
        msgs_ids.append(i['_id'])
        msg_str+=i['content']+"|"+i['timestamp']+"\n"
    
    ic(msg_str)
    try:
        for user in users:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message_with_http_info(
                    PushMessageRequest(
                        to=user,
                        messages=[TextMessage(text=msg_str)]
                    )
                )
    except Exception as e:
        pass
    else:
        for id in msgs_ids:
            ic(Notification().edit({'_id':id},{'status':'sent'}))

        # change status
        


if __name__=="__main__":
    app.config.from_object(Config())
    scheduler.init_app(app)

    current_setting=Settings().find()
    notification_time=current_setting['data']['notification-time']

    if notification_time:
        for i in notification_time:
            if ':' in i :
                print("job created " + i)
                scheduler.add_job(id='通知時間'+i,func=send_notifications,trigger='cron',day='*', hour=i.split(':')[0], minute=i.split(':')[1],misfire_grace_time=900,timezone='Asia/Taipei')
            else:
                ic('格式錯誤')
    
	# scheduler.add_job(func=task1, args=('循环',), trigger='interval', seconds=5, id='interval_task')
    scheduler.start()
    app.run(debug=True,port='8000',host='0.0.0.0',use_reloader=False)


# --worker-class=gevent 
# https://blog.csdn.net/weixin_46072106/article/details/109708788