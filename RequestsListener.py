from flask import render_template, request, redirect, url_for, session, Blueprint, send_from_directory

import DataBaseManagement

base_request_listener = Blueprint('request_listener', __name__)


@base_request_listener.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('request_listener.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if DataBaseManagement.check_auth(login=username, password=password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('request_listener.dashboard'))
        else:
            error = 'Неправильное имя пользователя или пароль'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Страница регистрации
@base_request_listener.route('/register', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('request_listener.index'))
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']

        if DataBaseManagement.check_login_registered(username):
            error = 'Аккаунт с таким логином уже зарегистрирован'
            return render_template('register.html', error=error)
        elif DataBaseManagement.check_email_registered(email):
            error = 'Этот почтовый адрес уже занят'
            return render_template('register.html', error=error)
        else:
            if DataBaseManagement.register_user(fullname=fullname, login=username, password=password, email=email,
                                                role="участник"):
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('request_listener.dashboard'))
            else:
                return render_template('register.html', error='Ошибка при регистрации со стороны сервера')

    return render_template('register.html')


@base_request_listener.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        username = DataBaseManagement.get_value_of_user(session['username'], "fullname")
        user_info = DataBaseManagement.get_value_of_user(session['username'], "email")
        permission = bool(DataBaseManagement.get_value_of_user(session['username'], "role") != "участник")
        return render_template('dashboard.html'
                               , username=username, user_info=user_info, permission=permission)
    else:
        return render_template('index.html')


@base_request_listener.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        username = DataBaseManagement.get_value_of_user(session['username'], "fullname")
        user_info = DataBaseManagement.get_value_of_user(session['username'], "email")
        permission = bool(DataBaseManagement.get_value_of_user(session['username'], "role") != "участник")
        return render_template('dashboard.html'
                               , username=username, user_info=user_info, permission=permission)
    else:
        return redirect(url_for('request_listener.login'))


@base_request_listener.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'logged_in' in session and session['logged_in']:
        username = DataBaseManagement.get_value_of_user(session['username'], "fullname")
        password = DataBaseManagement.get_value_of_user(session['username'], "password")
        if request.method == 'GET':
            return render_template('profile.html', username=username, password=password)
        else:
            data = DataBaseManagement.load_data()
            newname = request.form['username-field']
            newpass = request.form['password-field']
            data['Users'][session['username']]['fullname'] = newname
            data['Users'][session['username']]['password'] = newpass
            DataBaseManagement.save_data(data)
            return redirect(url_for('request_listener.profile'))
    else:
        return redirect(url_for('request_listener.login'))


@base_request_listener.route('/recovery', methods=['GET', 'POST'])
def recovery():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('request_listener.index'))
    if request.method == 'POST':
        email = request.form['email']
        print("make recovery")

    return render_template('recovery.html')


@base_request_listener.route('/uploads/<filename>')
def display_file(filename):
    return send_from_directory('uploads', filename)


# Выход из системы
@base_request_listener.route('/logout')
def logout():
    if 'logged_in' in session and not session['logged_in']:
        return redirect(url_for('request_listener.index'))
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('request_listener.index'))
