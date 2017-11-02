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
    posts = get_all_posts(db, user)
    return template('index', posts=posts, user=user)

@get('/login')
def login():
    if get_session(db):
        redirect('/')
    return template('login', errors=None, form=None, user=None)

def login_required(func):
    """ 
    Decorator which checks if the user is logged in before 
    accessing restricted routes 
    """
    def wrap(*args, **kwargs):
        if get_session(db):
            return func(*args, **kwargs)
        redirect('/login')
    return wrap

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

@get('/submit_post')
@login_required
def submit_post():
    user = get_session(db)
    return template('submit_post', errors=None, form=None, user=user)


@post('/submit_post')
@login_required
def do_submit_post():
    user = get_session(db)
    title = request.forms.get('title')
    url = request.forms.get('url')
    content = sanitize_html(request.forms.get('content'))
    post_form = PostForm(title, url, content)
    form = post_form.get_form_name()
    errors = post_form.validate()
    if not errors:
        post_id = new_post(db, title, url, content, user)
        # get keywords, insert into tables
        keywords = format_keywords(request.forms.get('keywords'))
        # Add keywords to table
        for keyword in keywords:
            add_keyword_to_post(db, post_id, keyword)
        redirect('/post/' + str(post_id))
    return template('submit_post', errors=errors, form=form, user=user)

@get('/submit_image')
@login_required
def submit_image():
    user = get_session(db)
    return template('submit_image', errors=None, form=None, user=user)


@post('/submit_image')
@login_required
def do_submit_image():
    user = get_session(db)
    title = request.forms.get('title')
    image = request.files.get('upload_image')
    image_form = ImageForm(title, image)
    form = image_form.get_form_name()
    errors = image_form.validate()
    if not errors:
        save_image(image)
        post_id = new_image_post(db, title, image.filename, user)
        # get keywords, insert into tables
        keywords = format_keywords(request.forms.get('keywords'))
        # Add keywords to table
        for keyword in keywords:
            add_keyword_to_post(db, post_id, keyword)
        redirect('/post/' + str(post_id))
    return template('submit_image', errors=errors, form=form, user=user)


def save_image(image):
    """
    Saves image on disk. If directory doesn't exist, a new one is created
    """
    path = os.getcwd() + "/static/img/"
    if not os.path.exists(path):
        os.makedirs(path)
    image.save(path, True)

@get('/post/<post_id:int>')
def view_post(post_id):
    user = get_session(db)
    post = get_post(db, post_id, user)
    comments = get_post_comments(db, post_id, user)
    if not post:
        redirect('/404')
    return template('post', post=post, comments=comments, user=user)

@get('/post/<post_id:int>/vote_up')
@login_required
def vote_post_up(post_id):
    do_vote_post_up(post_id)
    redirect('/post/' + str(post_id))


@get('/post/<post_id:int>/vote_down')
@login_required
def vote_post_down(post_id):
    do_vote_post_down(post_id)
    redirect('/post/' + str(post_id))


@post('/post/<post_id:int>/vote_up')
@login_required
def do_vote_post_up(post_id):
    user = get_session(db)
    vote_post(db, post_id, user, 1, 0)
    total_votes = get_post_votes(db, post_id)
    return str(total_votes)


@post('/post/<post_id:int>/vote_down')
@login_required
def do_vote_post_down(post_id):
    user = get_session(db)
    vote_post(db, post_id, user, 0, 1)
    total_votes = get_post_votes(db, post_id)
    return str(total_votes)

@post('/post/<post_id:int>/submit_comment')
@login_required
def do_submit_comment(post_id):
    user = get_session(db)
    content = request.forms.get('comment')
    # Sanitize
    content = sanitize_html(content)
    parent_id = request.forms.get('parent')
    if content:
        new_comment(db, content, user, post_id, parent_id)
    redirect('/post/' + str(post_id))

@get('/post/<post_id:int>/comment/<comment_id:int>/vote_up')
@login_required
def vote_comment_up(post_id, comment_id):
    do_vote_comment_up(post_id, comment_id)
    redirect('/post/' + str(post_id))


@get('/post/<post_id:int>/comment/<comment_id:int>/vote_down')
@login_required
def vote_comment_down(post_id, comment_id):
    do_vote_comment_down(post_id, comment_id)
    redirect('/post/' + str(post_id))


@post('/post/<post_id:int>/comment/<comment_id:int>/vote_up')
@login_required
def do_vote_comment_up(post_id, comment_id):
    user = get_session(db)
    vote_comment(db, comment_id, user, 1, 0)
    total_votes = get_comment_votes(db, comment_id)
    return str(total_votes)


@post('/post/<post_id:int>/comment/<comment_id:int>/vote_down')
@login_required
def do_vote_comment_down(post_id, comment_id):
    user = get_session(db)
    vote_comment(db, comment_id, user, 0, 1)
    total_votes = get_comment_votes(db, comment_id)
    return str(total_votes)

@error(404)
def error404(error):
    user = get_session(db)
    return template('404', user=user)

@route('/static/<filename>')
def server_static(filename):
    """
    For CSS
    """
    return static_file(filename, root='static/')

@route('/static/img/<filename>')
def server_image(filename):
    return static_file(filename, root='static/img/')

def format_keywords(keywords):
    """
    Accepts keyword list, separates them by comma, removes duplicates, empty and
    keywords exceeding character limit of 15, as well as sanitizes removes keywords
    above the maximum limit of 5 for a post
    """
    # Separate keywords by comma
    new_keywords = [x.strip() for x in keywords.split(',')]
    # Remove duplicates and strings longer than 15 as well preserving order
    exists = set()
    exists_add = exists.add
    new_keywords = [x for x in new_keywords if not (x in exists or exists_add(x)) and len(x) <= 15]
    # Remove empty strings
    new_keywords = list(filter(None, new_keywords))
    # Sanitize
    for x in range(len(new_keywords)):
        new_keywords[x] = re.sub('[^a-zA-Z0-9\+\-\.\#]', '', new_keywords[x])
    # Remove overflowing keywords (maximum 5)
    new_keywords = list(itertools.islice(new_keywords, 5))
    return new_keywords

if __name__ == '__main__':
    db = database()
    create_tables(db)

    # Testing purposes
    insert_sample_data(db)
    run(debug=True, host="localhost", post=3000)
