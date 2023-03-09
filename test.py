from flask import session,Flask
app=Flask(__name__)

app.secret_key='1'


@app.route('/')
def home():
    session.clear()
    session['login']='99999999999999999999999999'
    return '11'


if __name__=='__main__':
    app.run(port=8000)