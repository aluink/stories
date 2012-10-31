from bottle        import route, get, post, run, request, redirect, template, view
from httplib2      import Http
from urllib        import urlencode
from functools     import partial
from string        import replace
from nltk          import pos_tag
from nltk.tokenize import word_tokenize

import simplejson
import sys
import bottle

bottle.debug(True)

TOKEN_URL = 'https://api.instagram.com/oauth/access_token/?'
AUTH_URL = 'https://api.instagram.com/oauth/authorize/?'
CLIENT_ID = 'c6dc9f5096444284ac66b894539ebd0a'
CLIENT_SECRET = ''
REDIRECT_URI = 'http://localhost:8000/input'

# I'm using NLTK to parse the english into parts of speech.  I'm tokenizing 
# and filtering out parts of speech I don't want to find images for. These 
# are parts of speach I'd like to capture from the story.
# http://www.mozart-oz.org/mogul/doc/lager/brill-tagger/penn.html
ACCEPTED_TAGS = [ #'JJ',  # adjective
                  #'JJR', # comparative adjective
                  #'JJS', # superlative adjective
                  'NN',  # singular noun 
                  'NNS', # plural noun
                  #'VB',  # verb, base
                 # 'VBD', # verb, past tense
                 # 'VBG', # verb, gerund
                 # 'VBN', # verb, past participle
                 # 'VBP', # verb, singular, non 3-d
                 # 'VBZ'  # verd 3rd pers sing present
                  ]

# To help find "relevant" content, I've decided to find images with few tags.
# The idea is that an image with 40 tags where one of which matches my search,
# probably isn't related to my word.  However, an image with 2 tags where one 
# is my word is much more likely to be relevant.  Ugh, the joys of social
# media... and teenage girls :)
# 
# This setting drive the maximum number of tags an image can have to be kept.
# So far 2-3 is a good balance
TAG_COUNT = 3


def get_access_token(c):
  # TODO: Consider caching something here
  data = dict(client_id = CLIENT_ID, client_secret = CLIENT_SECRET,
              grant_type = 'authorization_code', redirect_uri = REDIRECT_URI,
              code = c)
  h = Http()
  resp, content = h.request(TOKEN_URL, "POST", urlencode(data))
  return simplejson.loads(content)

def get_image_for_word(token, word):
  h = Http()
  url = "https://api.instagram.com/v1/tags/" + word + "/media/recent?access_token=" + token['access_token']
  resp, content = h.request(url, "GET")
  json = simplejson.loads(content)
  for el in json['data']:
    if len(el['tags']) <= TAG_COUNT:
      return "<img height=\"60px\" src=\"" + el['images']['thumbnail']['url'] + "\"/></br>"

  # Instead of calling the 'next' pointer for the next page of data,
  # we'll just quit after the first page on the premise that this is
  # possibly an obscure word where relevant data isn't really possible
  return word

def get_images_for_words(token, words):
  m = dict()
  for word in words:
    m[word] = get_image_for_word(token,word)
  return m
def insert_images(story, images):
  for k,v in images.iteritems():
    story = story.replace(k,v)
  return story

@route('/')
def auth():
  data = dict(client_id = CLIENT_ID,redirect_uri = REDIRECT_URI, response_type = 'code')
  r = AUTH_URL + urlencode(data)
  redirect(r)
  
@route('/input')
def home():
  code = request.GET.get("code")
  if not code:
    return 'Missing code'
  return template('input', code = code)

@route('/test')
def test():
  return "word <img src=\"img\"/>"

@route('/present')
@post('/present')
def process():
  code = request.POST.get("code")
  if not code:
    return "Missing code"
  access_token = get_access_token(code)
  print access_token
  story = request.POST.get("story")
  tokenized = pos_tag(word_tokenize(story))
  print tokenized
  words = [w for (w,t) in tokenized if t in ACCEPTED_TAGS]
  word_images = get_images_for_words(access_token,set(words))
  story = insert_images(story, word_images)
  return story

CLIENT_SECRET = sys.argv[1]

run(host='localhost', port='8000', reloader=True)

