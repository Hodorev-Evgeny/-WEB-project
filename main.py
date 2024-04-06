from flask import Flask, render_template, request, redirect
from data import db_session
from flask_login import LoginManager, current_user, login_user
from data.user import User
from forms.login_form import LoginForm
from uuid import uuid4
from forms.register_form import RegisterForm

app = Flask(__name__)
app.secret_key = 'secret'
login_mgr = LoginManager()
login_mgr.init_app(app)


@login_mgr.user_loader
def load_user(token):
    session = db_session.create_session()
    return session.query(User).filter(User.token == token).first()


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('login.html', form=LoginForm())
    return render_template('chat.html', user_id=0)


@app.route('/chat/<user_id>')
def chat(user_id):
    return render_template('chat.html', user_id=user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', form=LoginForm())
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', form=RegisterForm())
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', message='Пароли не совпадают')
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.username.data).first():
            return render_template('register.html', message='Такой пользователь уже есть')
        user = User()
        user.token = str(uuid4())
        user.email = form.username.data
        user.name = form.name.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')


if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run('0.0.0.0', port=5000, debug=True)

