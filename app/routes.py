from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, UpdateForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Oskar'}
    posts = [
        {
            'author': {'username': 'Gosia'},
            'body': 'I have made new chocolate cake'
        },
        {
            'author': {'username': 'Misio'},
            'body': 'This is my dinner, which i did today'
        }
    ]

    visits = [
        {
            'author': {'username': 'Oski'},
            'body': 'It was really great pleasure!'
        },
        {
            'author': {'username': 'Dosia'},
            'body': 'BMG is one of the best restaurant in Warsaw'
        },
    ]

    return render_template('index.html', title='Home Page', posts=posts, visits=visits)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>', methods=['GET', 'POST'])      # f.e. /user/oskarro   --> username=oskarro
@login_required
def user(username):
    form = UpdateForm()
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user', username=form.username.data, email=form.email.data))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    default = 'default.jpg'
    posts = [
        {'author': user, 'body': 'Test post #1', 'food_type': 'seafood'},
        {'author': user, 'body': 'Test post #2', 'food_type': 'polish food'}
    ]
    visits = [
        {'author': user, 'body': 'Test visit #1', 'food_type': 'greece good', 'place': 'BMG', 'rate': 8},
        {'author': user, 'body': 'Test visit #2', 'food_type': 'traditional food', 'place': 'Kucharek szesc', 'rate': 7}
    ]
    if url_for('static', filename='profile_pics/' + username):
        image_file = url_for('static', filename='profile_pics/' + default)
    else:
        image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('user.html', user=user, posts=posts, visits=visits, image_file=image_file, form=form)


