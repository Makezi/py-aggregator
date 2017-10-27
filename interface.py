from bottle import request, response

COOKIE = "sessionid"

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
  """
  cursor = db.cursor()
  cursor.executescript(query)
  db.commit()

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