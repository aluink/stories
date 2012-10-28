import bottle
from bottle import route, get, post, run, request, redirect
from httplib2 import Http
from urllib import urlencode
import simplejson

bottle.debug(True)

TOKEN_URL = 'https://api.instagram.com/oauth/access_token/?'
AUTH_URL = 'https://api.instagram.com/oauth/authorize/?'
CLIENT_ID = '495253b2fc904fcea0c3a5b8a7288911'
CLIENT_SECRET = 'b9fd849077544f57b1580d632c24971a'
REDIRECT_URI = 'http://localhost:8000/input'

def get_access_token(c):
  data = dict(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, grant_type = 'authorization_code', redirect_uri = REDIRECT_URI, code = c)
  h = Http()
  resp, content = h.request(TOKEN_URL, "POST", urlencode(data))
  print "Response: ", resp
  print "Content: ", content

@route('/')
def auth():
  data = dict(client_id = CLIENT_ID,redirect_uri = REDIRECT_URL, response_type = 'code')
  r = AUTH_URL + urlencode(data)
  redirect(r)
  

@route('/input')
def home():
  code = request.GET.get("code")
  get_access_token(code)
  if not code:
    return 'Missing code'
  return '<form action="POST">Your Story: <textarea cols="80" rows="25" name="story"></textarea></br><input type="submit" value="GO!"/></form>'

@route('/present')
@post('/present')
def process():
  story = request.GET.get("story")
  print story
  return home()

run(host='localhost', port='8000', reloader=True)

