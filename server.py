from bottle import *
from db import database
from interface import *
from form_validator import *

# Sets global variables for template use
BaseTemplate.defaults['title'] = 'POSTIT'
BaseTemplate.defaults['request'] = request

@get('/')
def index():
    user = get_session(db)
    return template('index', user=user)

@get('/login')
def login():
    if get_session(db):
        redirect('/')
    return template('login', errors=None, form=None, user=None)

@get('/logout')
def logout():
    user = get_session(db)
    if user:
        delete_session(db, user)
        redirect('/')
    else:
        redirect('/login')

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    login_form = LoginForm(username, password)
    form = login_form.get_form_name()
    errors = login_form.validate()
    if not errors:
        if check_login(db, username, password):
            new_session(db, username)
            redirect('/')
        else:
            errors.append('Username or password is incorrect')
    return template('login', errors=errors, form=form, user=None)

@get('/register')
def register():
    if get_session(db):
        redirect('/')
    return template('login', errors=None, form=None, user=None)

@post('/register')
def do_register():
    username = request.forms.get('username')
    password = request.forms.get('password')
    verify_password = request.forms.get('verify_password')
    register_form = RegisterForm(username, password, verify_password)
    form = register_form.get_form_name()
    errors = register_form.validate()
    if not errors:
        if new_user(db, username, password):
            do_login()
        else:
            errors.append('Username already registered')
    return template('login', errors=errors, form=form, user=None)

@error(404)
def error404(error):
    user = get_session(db)
    return template('404', user=user)

if __name__ == '__main__':
    db = database()
    create_tables(db)
    run(debug=True, host="localhost", post=3000)
