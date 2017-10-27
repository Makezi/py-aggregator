import sqlite3
import hashlib

class database():

  def __init__(self, dbname="database.db"):
    "Database constructor. Default database name is 'database.db'"
    self.dbname = dbname
    self.conn = sqlite3.connect(self.dbname)

    # Ensure that results returned from queries are strings
    self.conn.text_factory = str

  def cursor(self):
    "Return a cursor on the database"
    return self.conn.cursor()

  def commit(self):
    "Commit pending changes"
    self.conn.commit()

  def crypt(self, password):
    "Return hashed password"
    return hashlib.sha1(password.encode()).hexdigest()
  