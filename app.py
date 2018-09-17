from flask import (Flask, g, render_template, flash, redirect, url_for, abort, session)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

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
login_manager.anonymous_user = models.Anonymous



@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None




@app.before_request
def before_request():
    """ Connect to Database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """close Database connection after each request"""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        try:
            models.User.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            flash("You registered successfully", "success")

        except ValueError:
            flash("User already exists", "danger")

        else:
            return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    # if current_user.is_authenticated:
    #     curr_user_name = current_user.username
    # else:
    #     curr_user_name = 'Guest'

    if username and username != current_user.username:
        try:
            user = models.User.select().where(models.User.username**username).get()

        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)

    else:
        stream = current_user.get_stream().limit(100)
        user = current_user

    if username:
        template = 'user_stream.html'

    return render_template(template, stream=stream, user=user)





@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match", "danger")

        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match", "danger")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've just logout", "success")
    return redirect(url_for('index'))
    

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash("Message posted", "success")
        return redirect(url_for('index'))


    return render_template('post.html', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):

    try:
        to_user = models.User.get(models.User.username**username)

    except models.DoesNotExist:
        abort(404)

    else:
        try:
            models.RelationShip.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )

        except models.IntegrityError:
            pass

        else:
            flash("You're now following {}".format(to_user.username), "success")


    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):

    try:
        to_user = models.User.get(models.User.username**username)

    except models.DoesNotExist:
        abort(404)

    else:
        try:
            models.RelationShip.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()

        except models.IntegrityError:
            pass

        else:
            flash("You've unfollowed {}".format(to_user.username), "success")


    return redirect(url_for('stream', username=to_user.username))


@app.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):

    models.Post.get(models.Post.id == post_id).delete_instance()
    return redirect(url_for('stream', username=current_user.username))



if __name__ == '__main__':

    models.initialise()

    try:
        models.User.create_user(
            username='humac',
            email='hoomaac@gmail.com',
            password='123',
            admin=True
        )

    except ValueError:
        pass


    app.run(debug=True, host=HOST, port=PORT)

