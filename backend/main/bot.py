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
from icecream import ic

from main.models import linebot_model
from main.models import Notification,Settings
from main.models import get_available_notifications

def send_bot_notifications():
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
            with ApiClient(linebot_model.configuration) as api_client:
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


def reply_message(reply_token,messages):
    with ApiClient(linebot_model.configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=messages
            )
        )
        
@linebot_model.handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    # 當用戶輸入「綁定」時
    if "bind" in event.message.text.strip() :
        if '-' in event.message.text:
            recv_token=event.message.text.split('-')[1]
            print('[main][檢測綁定]')
            ic(recv_token)
            result=Settings().check_binding_token(recv_token)
            if result=='correct':
                ic(event.source)
                ic(dict(event.source))
                target=event.source.user_id
                if 'group_id' in dict(event.source):
                    print('group_id',event.source.group_id)
                    target=event.source.group_id
                
                ic(target)
                # print(event.source.group_id)
                Settings().bind(target)
                reply_message(event.reply_token,[TextMessage(text='綁定成功！確認網站上的推送時間正確後，就可以等待時間到的推送咯～')])
                return 0
            else:
                reply_message(event.reply_token,[TextMessage(text='綁定失敗！確認一下token有沒有錯誤吧～')])
                return 0
    
    # 同時回覆用戶原本的訊息（這裡依舊做 echo，如果你希望修改回覆內容，也可以在此改變）
    reply_message(event.reply_token,[TextMessage(text=event.message.text)])
