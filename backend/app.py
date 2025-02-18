import os
import time

from flask import Flask,request,abort
from flask_restful import Api
from flask_restful import Resource
from dotenv import load_dotenv
from termcolor import colored
from icecream import ic
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
from main.models import Settings
from main.routes import app_route



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
api = Api(app)
app.register_blueprint(app_route)
api.add_resource(staff_manage,'/api/manage')
api.add_resource(staff,'/api/staff')
api.add_resource(settings,'/api/settings')
api.add_resource(notifications,'/api/notifications')

app.secret_key = 'os.environ.get("SECRET") or os.urandom(24)'
@app.before_request
def show():
    # print(request.headers,request.get_data().decode())
    pass

# Bot Integration

# linebot callback
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


if __name__=="__main__":
    app.run(debug=True,port='8000',host='0.0.0.0')

