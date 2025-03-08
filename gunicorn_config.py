# gunicorn_config.py
import os
from scheduler_lock import acquire_lock

# Gunicorn 的基本設定
bind = "0.0.0.0:8000"  # 監聽位址與埠號
workers = 3          # 啟動 3 個 worker
loglevel = "info"



def post_fork(server, worker):
    """
    在 worker fork 後嘗試取得檔案鎖，只有拿到鎖的 worker 會啟動 scheduler。
    """
    lock = acquire_lock()
    if lock:
        worker.log.info("Worker %s 成功取得 scheduler 鎖，啟動 APScheduler...", worker.pid)
        from app import start_scheduler
        start_scheduler()
    else:
        worker.log.info("Worker %s 未取得 scheduler 鎖，跳過 APScheduler 啟動。", worker.pid)