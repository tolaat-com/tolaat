import flask_login
from flask import request, redirect, url_for, render_template
from os import environ
from . import hebrew as h
from . import forms

def add_login(app):
    app.secret_key = environ['APP_SECRET_KEY']
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view ='login'


    users = {'andyworms@gmail.com': {'name': 'אנדי', 'password': environ['A_PASSWORD']},
             'zomerg@gmail.com': {'name': 'גיא', 'password': environ['G_PASSWORD']}}


    class User(flask_login.UserMixin):
        pass

    @login_manager.user_loader
    def user_loader(email):
        if email not in users:
            return

        user = User()
        user.id = email
        user.name = users[email]['name']
        return user

    @login_manager.request_loader
    def request_loader(request):
        form = forms.LoginForm()
        email = form.data['email']
        if email not in users:
            return
        if not form.validate_on_submit():
            return

        user = User()
        user.id = email
        user.is_authenticated = form.data['password'] == users[email]['password']
        return user

    @app.route(f'/{h.logout}')
    def logout():
        user = flask_login.current_user
        flask_login.logout_user()
        return render_template('logout.html', user=user)

    @app.route(f'/{h.login}', methods=['GET', 'POST'])
    def login():
        form = forms.LoginForm()
        if request.method == 'GET':
            return render_template('login.html', form=form)

        if not form.validate_on_submit():
            return render_template('login.html', form=form)



        email = form.data['email']
        password = form.data['password']
        if email in users and password == users[email]['password']:
            user = User()
            user.id = email
            flask_login.login_user(user)
            next = request.form.get('next', url_for('view_blueprint.main'))
            if next:
                assert next[0] == '/' and next[:2] != '//'
            return redirect(next)

        return render_template('login-bad.html'), 403
