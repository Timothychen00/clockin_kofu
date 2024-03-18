import requests
from icecream import ic
host='http://127.0.0.1:8000'
path='/api/staff'
headers={'Content-Type':'application/x-www-form-urlencoded'}
response=requests.post(host+path,headers=headers,data={'connection_mode':'buttonless','key':'cardid','value':'cadkj'})
ic( response.text)