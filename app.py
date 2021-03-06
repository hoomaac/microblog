from flask import (Flask, g, render_template, flash, redirect, url_for)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required)

from flask_bcrypt import check_password_hash

import forms
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


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered successfully", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/')
def index():
    return 'Index'

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match", "error")

        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match", "error")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've just logout", "success")
    return redirect(url_for('index'))
    



if __name__ == '__main__':
    models.initialise()


    app.run(debug=True, host=HOST, port=PORT)

