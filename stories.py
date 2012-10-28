import bottle
from bottle import route, get, post, run, request, redirect, template
from httplib2 import Http
from urllib import urlencode
import simplejson
import sys

from nltk import pos_tag
from nltk.tokenize import word_tokenize

bottle.debug(True)

TOKEN_URL = 'https://api.instagram.com/oauth/access_token/?'
AUTH_URL = 'https://api.instagram.com/oauth/authorize/?'
CLIENT_ID = 'c6dc9f5096444284ac66b894539ebd0a'
CLIENT_SECRET = ''
REDIRECT_URI = 'http://localhost:8000/input'

ACCEPTED_TAGS = ['NN','JJ','JJR','JJS','NN','NNS','VB','VBD','VBG','VBN','VBP','VBZ']

def get_access_token(c):
  # TODO: Consider caching something here
  data = dict(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, grant_type = 'authorization_code', redirect_uri = REDIRECT_URI, code = c)
  h = Http()
  resp, content = h.request(TOKEN_URL, "POST", urlencode(data))
  return simplejson.loads(content)

@route('/')
def auth():
  data = dict(client_id = CLIENT_ID,redirect_uri = REDIRECT_URI, response_type = 'code')
  r = AUTH_URL + urlencode(data)
  redirect(r)
  
@route('/input')
def home():
  code = request.GET.get("code")
  if not code:
    code = request.POST.get("code")
    if not code:
      return 'Missing code'
  return template('input', code = code)

@route('/present')
@post('/present')
def process():
  code = request.POST.get("code")
  if not code:
    return "Missing code"
  access_token = get_access_token(code)
  story = request.POST.get("story")
  tokenized = pos_tag(word_tokenize(story))
  words = filter(lambda (v,t): t in ACCEPTED_TAGS, tokenized)
  print words 
  return home()

CLIENT_SECRET = sys.argv[1]

run(host='localhost', port='8000', reloader=True)

