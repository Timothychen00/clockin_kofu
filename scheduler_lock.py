# scheduler_lock.py
import fcntl

def acquire_lock(lock_file_path='/tmp/scheduler.lock'):
    """
    嘗試透過檔案鎖來確保只有一個進程能啟動 scheduler，
    成功則回傳檔案描述符，否則回傳 None。
    """
    fp = open(lock_file_path, 'w')
    try:
        # 以非阻塞模式取得排他鎖
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fp
    except BlockingIOError:
        # 已有其他進程取得鎖
        return None
    
    # python scheduler.py &

# 使用 exec 启动 gunicorn 作为前台进程
# exec gunicorn --bind=0.0.0.0 --timeout 600 app:app