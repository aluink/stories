from bottle        import route, get, post, run, request, redirect, view
from httplib2      import Http
from urllib        import urlencode
from string        import replace
from functools     import partial
from time          import time
""" Natural Language ToolKit.
These two functions are what give me the ability to seek out the 
important words in the text.  I'm categorizing by parts of speech
"""
from nltk          import pos_tag
from nltk.tokenize import word_tokenize

# to easily parse json data returned from the Instagram API
import simplejson
import sys

"""
I chose this web framework because it was light and simple. With a few 
simple decorators and a call to run, I had a web app.  I didn't have the
need for anything grandios, so this was my chose.  Less is more.
"""
import bottle

""" 
Gives me a little extra information on what's being called. Can probably 
be turned off if this were to go to production and performance was an issue.
"""
#bottle.debug(True)

# Used to get the client code
AUTH_URL = 'https://api.instagram.com/oauth/authorize/?'

# Used to get the access_token which is needed for secure requests
TOKEN_URL = 'https://api.instagram.com/oauth/access_token/?'

# Used to search for images by tag name
TAG_SEARCH_URL = 'https://api.instagram.com/v1/tags/TAG/media/recent?access_token='

# Unique client ID setup in the online account settings, public info
CLIENT_ID = 'c6dc9f5096444284ac66b894539ebd0a'

# Client secret used to get an access_token.  This is private and not to be shared.
# It's loaded as a command line argument
CLIENT_SECRET = ''

# URL the OAuth API redirects to.  This has to match what is setup in the client 
# settings online.
REDIRECT_URI = 'http://localhost:8000/input'

"""
I'm using NLTK to parse the english into parts of speech.  I'm tokenizing 
and filtering out parts of speech I don't want to find images for. These 
are parts of speach I'd like to capture from the story.
http://www.mozart-oz.org/mogul/doc/lager/brill-tagger/penn.html
"""
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

""" 
To help find "relevant" content, I've decided to find images with few tags.
The idea is that an image with 40 tags where one of which matches my search,
probably isn't related to my word.  However, an image with 2 tags where one 
is my word is much more likely to be relevant.  Ugh, the joys of social
media... and teenage girls :)
 
This setting drive the maximum number of tags an image can have to be kept.
So far 2-3 is a good balance
"""
TAG_COUNT = 3

#***************#
# API Functions #
#***************#

"""
This section could be rewritten as a class, but there's no real need here given 
the simplicity.  Should we grow this app to needing more nad more API calls, we 
should probably do that to effectively refactor common pieces
"""

"""
Using a client code, this function calls the Instagram API and gets an access_token.  
This token is used by all secure API calls.
"""
def get_access_token(c):
  # TODO: Consider caching something here
  data = dict(client_id = CLIENT_ID, client_secret = CLIENT_SECRET,
              grant_type = 'authorization_code', redirect_uri = REDIRECT_URI,
              code = c)
  h = Http()
  resp, content = h.request(TOKEN_URL, "POST", urlencode(data))
  return simplejson.loads(content)

"""
With an acces_token and a word, this function attempts to get a relevant image from 
the Instagram API
"""
def get_image_for_word(token, word):
  h = Http()
  url = TAG_SEARCH_URL.replace('TAG',word) + token['access_token']
  resp, content = h.request(url, "GET")
  json = simplejson.loads(content)
  img = ''
  for el in json['data']:
    if len(el['tags']) <= TAG_COUNT:
      return "<img height=\"60px\" src=\"" + el['images']['thumbnail']['url'] + "\"/>"

  # Instead of calling the 'next' pointer for the next page of data,
  # we'll just quit after the first page on the premise that this is
  # possibly an obscure word where relevant data isn't really possible
  return word

"""
Uses get_image_for_word to get a set of images for a set of words
"""
def get_images_for_words(token, words):
  m = dict()
  for word in words:
    m[word] = get_image_for_word(token,word)

  return m

#*********#
# Utility #
#*********#

"""
With a map of (word,image_tag), this function replaces all occurences of 
a word with its relevant image
"""
def insert_images(story, images):
  print story
  for k,v in images.iteritems():
    print k, v
    story = story.replace(k,v)
  return story

#*************#
# HTTP Routes #
#*************#

"""
This is the landing page route.  It just redirects you to the Intagram login
"""
@route('/')
def auth():
  data = dict(client_id = CLIENT_ID,redirect_uri = REDIRECT_URI, response_type = 'code')
  r = AUTH_URL + urlencode(data)
  redirect(r)
 

"""
Once you successfully log into Instagram, you get redirected to this page. Using input.tpl, this route just puts the client code in a hidden form element.
"""
@route('/input')
@view('input')
def home():
  code = request.GET.get("code")
  if not code:
    return 'Missing code'
  return dict(code = code)

"""
A simple route that's not part of the standard flow.  I used it to test stuff and POC some ideas
"""
@route('/test')
def test():
  return "word <img src=\"img\"/>"

"""
This is where all the magic happens.  The general idea is as follows
1. Get the access code
2. Tokenize and tag the words by parts of speech
3. Filter out all the parts of speech we don't care about
4. Using the remaining words, go find relevant images on Instagram
5. Replace those words with the images
6. Render the new "imaged" story
"""
@route('/present')
@post('/present')
def process():
  code = request.POST.get("code")
  if not code:
    return "Missing code"
  start = time()
  
  access_token = get_access_token(code)
  story = request.POST.get("story")
  print "token", (time() - start)
  start = time()
  
  tokenized = pos_tag(word_tokenize(story))
  print "tokenize", (time() - start)
  start = time()

  words = [w for (w,t) in tokenized if t in ACCEPTED_TAGS]
  print "filter", (time() - start)
  start = time()
  
  word_images = get_images_for_words(access_token,set(words))
  print "get images", (time() - start)
  start = time()

  r = insert_images(story, word_images)
  print "replace", (time() - start)

  return r


#****#
# GO #
#****#

CLIENT_SECRET = sys.argv[1]

run(host='0.0.0.0', port='8000', reloader=True)

