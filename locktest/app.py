# app.py
from flask import Flask
from flask_apscheduler import APScheduler
from flask_apscheduler.scheduler import BackgroundScheduler

scheduler=APScheduler(BackgroundScheduler({'apscheduler.timezone': 'Asia/Taipei','daemon':False}))


def my_job():
    print("執行 my_job 任務！")


def create_app():
    app = Flask(__name__)
    # 啟用 APScheduler 的 API（非必要，可依需求調整）
    app.config.update({
        'SCHEDULER_API_ENABLED': True,
    })
    scheduler.init_app(app)
    
    
    @app.route('/')
    def index():
        return "Hello, World!"
    
    
    @app.route('/delete')
    def delete():
        jobs = scheduler.get_jobs()
        for job in jobs:
            print(f"Job ID: {job.id}, Job Name: {job.name}, Trigger: {job.trigger}")
        scheduler.remove_all_jobs()
        
        scheduler.add_job(
            id='my_job',        # 任務識別碼
            func=my_job,        # 要執行的函數
            trigger='interval', # 間隔觸發器
            seconds=2          # 每 10 秒執行一次
        )
        for job in jobs:
            print(f"Job ID: {job.id}, Job Name: {job.name}, Trigger: {job.trigger}")
        
        return "Hello, World!"
    return app

def start_scheduler():
    """
    這個函數在 Flask 的應用上下文內初始化並啟動 APScheduler，
    並加入一個示範任務，每 10 秒印出一次訊息。
    """
    # 重新建立一個 app 實例，或可直接使用 create_app() 回傳的 app
    app = create_app()
    
    with app.app_context():
        # 定義一個任務函數

        
        # 新增任務
        scheduler.add_job(
            id='my_job',        # 任務識別碼
            func=my_job,        # 要執行的函數
            trigger='interval', # 間隔觸發器
            seconds=10          # 每 10 秒執行一次
        )
        # 啟動 APScheduler
        scheduler.start()
        print("APScheduler 已啟動！")

# 供 gunicorn 匯入使用
app = create_app()