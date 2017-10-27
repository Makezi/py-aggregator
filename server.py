from bottle import get, run, template, BaseTemplate
from db import database
from interface import *

# Sets global variables for template use
BaseTemplate.defaults['title'] = 'POSTIT'

@get("/")
def index():
  user = get_session(db)
  return template("index", user=user)

if __name__ == '__main__':
  db = database()
  create_tables(db)
  run(debug=True, host="localhost", post=3000)
