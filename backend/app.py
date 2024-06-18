import os

from flask import Flask,request
from flask_restful import Api
from falsk_restful import Resource
from dotenv import load_dotenv

from main.api import staff_manage
from main.api import staff
from main.api import settings
from main.routes import app_route

load_dotenv()

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
    block_start_string='(%',
    block_end_string='%)',
    variable_start_string='((',
    variable_end_string='))',
    comment_start_string='(#',
    comment_end_string='#)',
  ))
  
app=CustomFlask(__name__,static_folder="main/static",template_folder="main/templates")
api = Api(app)
app.register_blueprint(app_route)
api.add_resource(staff_manage,'/api/manage')
api.add_resource(staff,'/api/staff')
api.add_resource(settings,'/api/settings')

app.secret_key = 'os.environ.get("SECRET") or os.urandom(24)'
@app.before_request
def show():
    # print(request.headers,request.get_data().decode())
    pass

if __name__=="__main__":
    app.run(debug=True,port='8000',host='0.0.0.0')

