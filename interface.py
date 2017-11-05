from bottle import request, response
import sqlite3
import uuid
from util import format_date
from datetime import datetime
from html_sanitizer import Sanitizer

COOKIE = "sessionid"
avatar_site = "http://api.adorable.io/avatars/16/"

def create_tables(db):
    query = """
    DROP TABLE IF EXISTS users;
    CREATE TABLE users (
        username TEXT UNIQUE PRIMARY KEY COLLATE NOCASE,
        password TEXT NOT NULL,
        avatar TEXT
    );

    DROP TABLE IF EXISTS sessions;
    CREATE TABLE sessions (
        sessionid TEXT UNIQUE PRIMARY KEY,
        username TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    );

    DROP TABLE IF EXISTS posts;
    CREATE TABLE posts (
        id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT,
        image TEXT,
        content TEXT,
        username TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    );

    DROP TABLE IF EXISTS comments;
    CREATE TABLE comments (
        id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        post_id INTEGER NOT NULL,
        parent_id INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username),
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
    );

    DROP TABLE IF EXISTS post_votes;
    CREATE TABLE post_votes (
        post_id INTEGER,
        username TEXT NOT NULL,
        up INTEGER DEFAULT 0,
        down INTEGER DEFAULT 0,
        PRIMARY KEY (post_id, username),
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (username) REFERENCES users(username)
    );

    DROP TABLE IF EXISTS comment_votes;
    CREATE TABLE comment_votes (
        comment_id INTEGER,
        username TEXT NOT NULL,
        up INTEGER DEFAULT 0,
        down INTEGER DEFAULT 0,
        PRIMARY KEY (comment_id, username),
        FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
        FOREIGN KEY (username) REFERENCES users(username)
    );

    DROP TABLE IF EXISTS keywords;
    CREATE TABLE keywords (
        id INTEGER PRIMARY KEY,
        keyword TEXT NOT NULL UNIQUE
    );

    DROP TABLE IF EXISTS post_keywords;
    CREATE TABLE post_keywords (
        post_id INTEGER NOT NULL,
        keyword_id INTEGER NOT NULL,
        PRIMARY KEY (post_id, keyword_id),
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (keyword_id) REFERENCES keywords(id)
    );
    """
    cursor = db.cursor()
    cursor.executescript(query)
    db.commit()

# User table methods

def new_user(db, username, password):
    """
    Registers new user into the database.
    Returns false if user already exists
    """
    try:
        cursor = db.cursor()
        query = "INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)"
        cursor.execute(query, (username, db.crypt(password), avatar_site + username))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_login(db, username, password):
    """
    Returns True if username and password matches whats stored
    """
    cursor = db.cursor()
    query = "SELECT username FROM users WHERE username = ? and password = ?"
    cursor.execute(query, (username, db.crypt(password)))
    user = cursor.fetchone()
    if not user:
        return False
    return True

# Post table methods

def sanitize_html(content):
    """
    Converts content to safe HTML
    """
    sanitizer = Sanitizer()
    content = sanitizer.sanitize(content)
    return content

def new_post(db, title, url, content, username):
    """
    Adds a new post to the database.
    Date of the post will be the current date and time.
    Returns newly inserted row id
    """
    cursor = db.cursor()
    query = "INSERT INTO posts (title, url, content, username, timestamp) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (title, url, content, username, datetime.now()))
    db.commit()
    return cursor.lastrowid

def new_image_post(db, title, image, username):
    """
    Adds new image post to the database, with image filename being stored.
    Date of the post will be the current date and time.
    Returns newly isnerted row id
    """
    cursor = db.cursor()
    query = "INSERT INTO posts (title, image, username, timestamp) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (title, image, username, datetime.now()))
    db.commit()
    return cursor.lastrowid

def get_all_posts(db, user, keyword=''):
    """
    Return a list of posts, including user avatars, comment count,
    post votes and keywords, ordered by votes.
    Can return list of posts that can contain keyword
    """
    cursor = db.cursor()
    query = """
    SELECT p.*, u.avatar,
        (SELECT COUNT(*)
          FROM comments
          WHERE post_id = p.id),
        (SELECT COALESCE(SUM(up) - SUM(down), 0)
          FROM post_votes
          WHERE post_id = p.id) v,
        (SELECT SUM(up + -down)
          FROM post_votes
          WHERE post_id = p.id
          AND username = ?),
        GROUP_CONCAT(k.keyword)
    FROM users u
    LEFT OUTER JOIN posts p ON u.username = p.username
    LEFT OUTER JOIN  post_keywords pk ON p.id = pk.post_id
    LEFT OUTER JOIN keywords k ON pk.keyword_id = k.id
    WHERE p.id is not NULL
    GROUP BY p.id
    HAVING (p.title LIKE ? OR p.username LIKE ? OR GROUP_CONCAT(k.keyword) LIKE ?)
    ORDER BY v DESC
    """
    keyword = '%' + str(keyword) + '%'
    cursor.execute(query, (user, keyword, keyword, keyword))
    result = []
    for row in cursor:
        row = list(row)
        # Form date and time
        row[6] = format_date(row[6])
        # If vote count is None, set it as 0
        if row[9] is None:
            row[9] = 0
        # Split keywords into a list to be returned
        if row[11] is not None:
            row[11] = [x.strip() for x in row[11].split(',')]
        result.append(row)
    return result

def get_post(db, post_id, user):
    """
    Returns specific post by id if it exists, otherwise None
    """
    cursor = db.cursor()
    query = """
    SELECT p.*, u.avatar,
      (SELECT COALESCE(SUM(up) - SUM(down), 0)
        FROM post_votes
        WHERE post_id = p.id),
      (SELECT SUM(up + -down)
        FROM post_votes
        WHERE post_id = p.id
        AND username = ?),
      GROUP_CONCAT(k.keyword)
    FROM users u
    LEFT OUTER JOIN posts p ON u.username = p.username
    LEFT OUTER JOIN  post_keywords pk ON p.id = pk.post_id
    LEFT OUTER JOIN keywords k ON pk.keyword_id = k.id
    WHERE p.id = ?
    GROUP BY p.id
    """
    cursor.execute(query, (user, post_id))
    post = cursor.fetchone()
    if post:
        post = list(post)
        # Format date and time
        post[6] = format_date(post[6])
        # Split keywords into a list to be returned
        if post[10] is not None:
            post[10] = [x.strip() for x in post[10].split(',')]
        return post
    return None

def delete_post(db, post_id, user):
    """
    Delete a post from the database.
    Only the owner of the post can delete their posts
    """
    cursor = db.cursor()
    query = "DELETE FROM posts WHERE id = ? and username = ?"
    cursor.execute(query, (post_id, user))
    if cursor.rowcount == 1:
        return True
    return False

# Comments table methods

def new_comment(db, content, username, post_id, parent_id=None):
    """
    Adds a new comment to a post.
    Date of the comment will be the current date and time.
    """
    cursor = db.cursor()
    query = "INSERT INTO comments (content, username, post_id, parent_id, timestamp) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (content, username, post_id, parent_id, datetime.now()))
    db.commit()

def get_post_comments(db, post_id, user):
    """
    Returns list of all comments for specific post id, including user avatars and
    comment votes for the related comment.
    A vote count is also returned which determines if the logged in user has voted on
    a specific comment (1 being upvote, -1 being downvote, 0 for unvoted)
    """
    cursor = db.cursor()
    query = """
    SELECT c.*, u.avatar,
      (SELECT COALESCE(SUM(up) - SUM(down), 0)
        FROM comment_votes
        WHERE comment_id = c.id) v,
      (SELECT SUM(up + -down)
        FROM comment_votes
        WHERE comment_id = c.id
        AND username = ?)
    FROM users u
    LEFT OUTER JOIN comments c
    ON u.username = c.username
    WHERE c.post_id = ?
    AND c.id is not NULL
    ORDER BY v DESC
    """
    cursor.execute(query, (user, post_id))
    result = []
    for row in cursor:
        row = list(row)
        # Format date and time
        row[5] = format_date(row[5])
        # If vote count is None, set it to 0
        if row[7] is None:
            row[7] = 0
        result.append(row)
    return result

## Session table methods

def new_session(db, username):
    """
    Generate new session and a cookie to the request.
    User must exist in the database, otherwise return None.
    There should only be one active session per user at any point,
    if there is already a session active, use the existing
    session id from the cookie
    """
    # Check for valid user
    cursor = db.cursor()
    query = "SELECT username FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    if not user:
        return None
    # Check for existing session from user, otherwise generate new session
    query = "SELECT sessionid FROM sessions WHERE username = ?"
    cursor.execute(query, (username,))
    session = cursor.fetchone()
    if session:
        session_id = session[0]
    else:
        session_id = str(uuid.uuid4())
        query = "INSERT INTO sessions (sessionid, username) VALUES (?, ?)"
        cursor.execute(query, (session_id, user[0]))
        db.commit()
    response.set_cookie(COOKIE, session_id)
    return session_id

def delete_session(db, username):
    """
    Remove all sessions for a user
    """
    cursor = db.cursor()
    query = "DELETE FROM sessions WHERE username = ?"
    cursor.execute(query, (username,))
    db.commit()
    session_id = request.get_cookie(COOKIE)
    response.set_cookie(COOKIE, session_id, expires=0)

def get_session(db):
    """
    Attempt to retrieve user if an active session exists. Return None if
    there is no valid session
    """
    session_id = request.get_cookie(COOKIE)
    cursor = db.cursor()
    query = "SELECT username FROM sessions WHERE sessionid = ?"
    cursor.execute(query, (session_id,))
    user = cursor.fetchone()
    if user:
        return user[0]
    return None

# Votes table methods

def vote_post(db, post_id, username, up, down):
    """
    Allows user to vote on a post.
    Users can only vote once on a post
    """
    try:
        cursor = db.cursor()
        query = "INSERT INTO post_votes (post_id, username, up, down) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (post_id, username, up, down))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_post_votes(db, post_id):
    """
    Returns sum of votes for specific post
    """
    cursor = db.cursor()
    query = "SELECT SUM(up) - SUM(down) FROM post_votes WHERE post_id = ?"
    cursor.execute(query, (post_id,))
    row = cursor.fetchone()
    # If post has no votes, return 0
    if row is None:
        return 0
    return row[0]

def vote_comment(db, comment_id, username, up, down):
    """
    Allows user to vote on a comment.
    Users can only vote once on a comment
    """
    try:
        cursor = db.cursor()
        query = "INSERT INTO comment_votes (comment_id, username, up, down) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (comment_id, username, up, down))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_comment_votes(db, comment_id):
    """
    Returns sum of votes for specific comment
    """
    cursor = db.cursor()
    query = "SELECT SUM(up) - SUM(down) FROM comment_votes WHERE comment_id = ?"
    cursor.execute(query, (comment_id,))
    row = cursor.fetchone()
    # If comment has no votes, return 0
    if row is None:
        return 0
    return row[0]

# Keyword table methods

def new_keyword(db, keyword):
    """
    Inserts unique keyword into database
    """
    try:
        cursor = db.cursor()
        query = "INSERT INTO keywords (keyword) VALUES (?)"
        cursor.execute(query, (keyword,))
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return False

def add_keyword_to_post(db, post_id, keyword):
    """
    Links keyword stored in database to a post.
    If keyword doesn't exist, it is first created.
    Can not have duplicates keywords linked to a single post.
    """
    cursor = db.cursor()
    query = "SELECT id FROM keywords WHERE keyword = ?"
    cursor.execute(query, (keyword,))
    row = cursor.fetchone()
    if row is None:
        keyword_id = new_keyword(db, keyword)
    else:
        keyword_id = row[0]
    try:
        query = "INSERT INTO post_keywords (post_id, keyword_id) VALUES (?, ?)"
        cursor.execute(query, (post_id, keyword_id))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Sample data

def insert_sample_data(db):
    """ 
    Generate sample data for testing the application 
    """
    cursor = db.cursor()
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM posts")
    # Create users
    users = [('Jim', 'jim123', avatar_site + 'Jim'),
             ('Bruce', 'bruce123', avatar_site + 'Bruce'),
             ('Wally', 'wally123', avatar_site + 'Wally')]
    for username, password, avatar in users:
        query = "INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)"
        cursor.execute(query, (username, db.crypt(password), avatar))

    # Create posts
    posts = [("City Light at Night",
              None,
              "skyline.jpg",
              None,
              'Bruce',
              '2017-01-15 01:45:06'),
             ('KUNG FURY',
              'https://www.youtube.com/watch?v=bS5P_LAqiVg',
              None,
              '10/10',
              'Wally',
              '2017-04-21 00:54:53'),
             ("What is the thin buzzing sound that I hear when it's really quiet?",

              None,
              None,
              None,
              'Jim',
              '2017-05-3 22:24:14')]
    for title, url, image, content, username, timestamp in posts:
        query = "INSERT INTO posts (title, url, image, content, username, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (title, url, image, content, username, timestamp))
    # Create comments
    comments = [("I've been waiting for this moment ever since the Kickstarter came up!",
                 'Bruce',
                 2,
                 None,
                 '2017-04-21 00:55:27'),
                ('Pretty good',
                 'Jim',
                 2,
                 None,
                 '2017-04-21 00:57:12'),
                ('Yep, 10/10',
                 'Wally',
                 2,
                 1,
                 '2017-04-21 00:58:05'),
                ('Agreed.',
                 'Bruce',
                 2,
                 3,
                 '2017-04-21 00:59:05'),
                ("Very pretty!",
                 'Jim',
                 1,
                 None,
                 '2017-01-15 01:59:06'),
                ("I believe it is called 'Urban Static'. You will notice it goes away during heavy snow storms since "
                 "the snow starts adsorbing distant sounds.",
                 "Bruce",
                 3,
                 None,
                 "2017-05-3 22:26:24"),
                ("I love when it snows a lot because of how quiet the world becomes, it goes away for me during "
                 "heavy snow.",
                 "Wally",
                 3,
                 6,
                 "2017-05-3 22:27:34")]
    for content, username, post_id, parent_id, timestamp in comments:
        query = "INSERT INTO comments (content, username, post_id, parent_id, timestamp) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (content, username, post_id, parent_id, timestamp))
    # Create post votes
    post_votes = [(3, 'Jim', 0, 1), (2, 'Bruce', 1, 0), (2, 'Wally', 1, 0)]
    for post_id, username, up, down in post_votes:
        query = "INSERT INTO post_votes (post_id, username, up, down) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (post_id, username, up, down))

    # Create comment votes
    comment_votes = [(1, 'Jim', 1, 0), (1, 'Bruce', 1, 0)]
    for comment_id, username, up, down in comment_votes:
        query = "INSERT INTO comment_votes (comment_id, username, up, down) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (post_id, username, up, down))
    # Create post keywords
    keywords = [(1, 'science'), (2, 'funny'), (3, 'news'), (4, 'serious'), (5, 'relaxing')]
    for id, keyword in keywords:
        query = "INSERT INTO keywords (id, keyword) VALUES (?, ?)"
        cursor.execute(query, (id, keyword))
    post_keywords = [(1, 5), (2, 2), (2, 3), (3, 3)]
    for post_id, keyword_id in post_keywords:
        query = "INSERT INTO post_keywords (post_id, keyword_id) VALUES (?, ?)"
        cursor.execute(query, (post_id, keyword_id))