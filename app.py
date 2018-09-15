from flask import Flask, g
from flask_login import LoginManager

import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'


app = Flask(__name__)

app.secret_key = '3D713690FB9BF9175F2902300AA99D693910597C'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None




@app.before_request
def before_request():
    """ Connect to Database before each request"""
    g.db = models.DATABASE
    g.db.connect()


@app.after_request

def after_request(response):
    """close Database connection after each request"""
    g.db.close()
    return response




if __name__ == '__main__':
    models.initialise()

    app.run(debug=True, host=HOST, port=PORT)

