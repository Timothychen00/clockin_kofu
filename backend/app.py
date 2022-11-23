from flask import Flask,request
from main.routes import app_route
from flask_restful import Api,Resource
from main.models import staff_manage,staff
import os
from dotenv import load_dotenv
load_dotenv()

app=Flask(__name__,static_folder="main/static",template_folder="main/templates")
api = Api(app)
app.register_blueprint(app_route)
api.add_resource(staff_manage,'/api/manage')
api.add_resource(staff,'/api/staff')

app.secret_key = os.environ.get("SECRET") or os.urandom(24)
@app.before_request
def show():
    print(request.headers,request.get_data().decode())

if __name__=="__main__":
    app.run(debug=True)

