# clockin_kofu!

## 電路圖
![clockin_bb](https://github.com/Timothychen00/clockin_kofu/assets/52665482/7bc5bd4b-77b4-4d14-bb3c-ff95fd1646ba)

- frtizing檔案：
- BOM：<img width="412" alt="CleanShot 2024-06-12 at 14 38 48@2x" src="https://github.com/Timothychen00/clockin_kofu/assets/52665482/281463ea-d02b-4d0f-a982-1448d4b75658">

## 本地測試
## 環境1:
```
export ENV=fried
```
## 環境2:
```
export ENV=bao7
```
## 啟動
```
OAUTHLIB_INSECURE_TRANSPORT=1 
cd backend
pipenv run python app.py
```

## sol
- ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
    -> numpy version