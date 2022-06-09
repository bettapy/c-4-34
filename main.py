from os import path
from os.path import normpath

from json import load, dump

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.login import LoginForm
from data.register import RegisterForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'g3rf-jio4-1jre-opfs-12lq-wqe0'
login_manager = LoginManager()
login_manager.init_app(app)

db_path = normpath('db/database.sqlite')
db_session.global_init(db_path)


@app.route('/')
def home():
    return render_template('home_page.html', title='AFK Arena')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/profile')
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такой пользователь уже есть")

        user = User(name=str(form.name.data), email=str(form.email.data))

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile')
def user_profile():
    return render_template('profile.html', title='Профиль')


@app.errorhandler(404)
def page_not_found(message):
    return render_template('404.html'), 404


@app.errorhandler(401)
def authorization_required(message):
    return render_template('401.html'), 401


def main():
    app.run(port='8080')


if __name__ == '__main__':
    main()
