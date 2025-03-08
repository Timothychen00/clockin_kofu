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
from main.bot import send_bot_notifications
from main.models import linebot_model

scheduler=APScheduler(BackgroundScheduler({'apscheduler.timezone': 'Asia/Taipei','daemon':False}))


def create_app():
    class Config(object):
        SCHEDULER_TIMEZONE = 'Asia/Taipei'  # 配置时区
        SCHEDULER_API_ENABLED = True  # 添加API
        
    app=Flask(__name__,static_folder="main/static",template_folder="main/templates")
    api = Api(app)
    scheduler.init_app(app)
    app.config.from_object(Config())
    
    app.register_blueprint(app_route)
    api.add_resource(staff_manage,'/api/manage')
    api.add_resource(staff,'/api/staff')
    api.add_resource(settings,'/api/settings')
    api.add_resource(notifications,'/api/notifications')
    app.secret_key = 'os.environ.get("SECRET") or os.urandom(24)'


# linebot callback--------------------
    @app.route("/callback", methods=['POST'])
    def callback():
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)
        try:
            linebot_model.handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return 'OK'
        
        
    return app


def start_scheduler():
    app = create_app()
    current_setting=Settings().find()
    notification_time=current_setting['data']['notification-time']

    if notification_time:
        for i in notification_time:
            if ':' in i :
                print("job created " + i)
                scheduler.add_job(id='通知時間'+i,func=send_bot_notifications,trigger='cron',day='*', hour=i.split(':')[0], minute=i.split(':')[1],misfire_grace_time=900,timezone='Asia/Taipei')
            else:
                ic('格式錯誤')
            # 啟動 APScheduler
        scheduler.start()
        print("APScheduler 已啟動！")



# 供 gunicorn 匯入使用
app=create_app()
# with app.app_context():
#     # 定義一個任務函數
#     # 新增任務

            
            
            

if __name__=="__main__":# gunicorn 執行的時候根本不會從這邊執行所以會出一點點小問題
    scheduler.init_app(app)
    # scheduler.start()
    app.run(debug=True,port='8000',host='0.0.0.0',use_reloader=False)

# --worker-class=gevent 
# https://blog.csdn.net/weixin_46072106/article/details/109708788