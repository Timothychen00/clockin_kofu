# -*- coding: utf-8 -*-

import os
import time

from flask import Flask, request, abort
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

app = Flask(__name__)

# 從環境變數中取得 channel_secret 與 channel_access_token
channel_secret = os.getenv('Channel_secret', None)
channel_access_token = os.getenv('Channel_access_token', None)

handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

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

@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    # 當用戶輸入「綁定」時
    if event.message.text.strip() == "綁定":
        # 定義一個延時推播的函數
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.push_message_with_http_info(
                PushMessageRequest(
                    to=event.source.user_id,
                    messages=[TextMessage(text="記住了")]
                )
            )
        # 以 threading.Thread 開啟一個新的執行緒執行 delayed_push 函數，不阻塞主線
    
    # 同時回覆用戶原本的訊息（這裡依舊做 echo，如果你希望修改回覆內容，也可以在此改變）
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

if __name__ == "__main__":
    app.run(debug=True, port=8000)