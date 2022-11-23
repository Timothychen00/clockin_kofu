
from flask import Blueprint,render_template,redirect,request,session
import requests,os,json
from main.decorators import login_required
from oauthlib.oauth2 import WebApplicationClient
from dotenv import load_dotenv
load_dotenv()

app_route=Blueprint("app_route",__name__,static_folder="static",template_folder="templates")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
GOOGLE_CLIENT_ID=os.environ['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET=os.environ['SECRET']

client = WebApplicationClient(GOOGLE_CLIENT_ID)
available_emails=['timothychenpc@gmail.com','tim20060112@gmail.com']


@app_route.route("/")
@login_required
def home():
    return render_template("index.html")

@app_route.route("/<id>")
def personal(id):
    return render_template("index2.html")

@app_route.route('/login')
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app_route.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app_route.route("/login/callback")
def callback():
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    print(code)
    token_url, headers, body = client.prepare_token_request(token_endpoint,authorization_response=request.url,redirect_url=request.base_url,code=code)
    token_response = requests.post(token_url,headers=headers,data=body,auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),)
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    print(userinfo_endpoint,'','')
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
# Parse the tokens!
    print(userinfo_response.json())
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        if users_email in available_emails:
            session['logged_in']=userinfo_response.json()
        return redirect('/')

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()