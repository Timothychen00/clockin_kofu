import requests
from icecream import ic
host='https://friedclockin.azurewebsites.net'
path='/api/staff'
headers={'Content-Type':'application/x-www-form-urlencoded'}
response=requests.post(host+path,headers=headers,data={'connection_mode':'buttonless','key':'cardid','value':'136ca72'})
ic( response.text)