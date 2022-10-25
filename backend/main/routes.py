
from flask import Blueprint,render_template

app_route=Blueprint("app_route",__name__,static_folder="static",template_folder="templates")
@app_route.route("/")
def home():
    return render_template("index.html")

@app_route.route("/<id>")
def personal(id):
    return render_template("index2.html")