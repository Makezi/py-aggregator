from bottle import request, response
import sqlite3
import uuid

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
    """"Attempt to retrieve user if an active session exists. Return None if
    there is no valid session"""
    session_id = request.get_cookie(COOKIE)
    cursor = db.cursor()
    query = "SELECT username FROM sessions WHERE sessionid = ?"
    cursor.execute(query, (session_id,))
    user = cursor.fetchone()
    if user:
        return user[0]
    return None