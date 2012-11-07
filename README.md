Stories
=======

The purpose of this application is to take a short story and present it with contextual images using the Instagram API.

There are currently two branches of development.  An inexhaustive list of challenges for this application included finding relevant words to the story, finding relevant images for these words, interfacing with the Instagram API, and, in my case, learning Python.

In order to find relevant words to the story, I sought out a library that would extract words that are both relevant and would prove less abstract and therefore better depicted in images.  I thought sorting out nouns and adjectives would do just fine.  To do this, I wired up the Natual Language ToolKit (NLTK).  It proved quite useful, however pretty slow, in tagging relevant words.

Interfacing with the Instagram API wasn't really a problem once I got it figured out; their documentation is well laid out.  My original implementation did a one by one search of images.  In an attempt to parallelize the process I found the ThreadPoolExecutor class.  I've used this same construct before in Java and know that if it works, it works well.  Unfortunately, it is only available in Python3 and NLTK doesn't support Python3.  Therefore, I created the python3 branch to do this experimental work.

Having dropped NLTK support in my python3 branch, I sorted out relevant words by simply finding words longer than X characters.  While not as effective, it was significantly faster (9-12s to &lt;1s).  It now misses smaller words, but is great at throwing out grammatical words like "a", "the", "and", etc.  As for searching words that aren't really relevant such as say "grammatical", the way I pull relevant images deals with that just fine.

Once I have a set of words with which I want to find images for, I search recent images, this keeps the images changing over time, and I pull images that have less than X tags where at least one of them matches the word I'm searching for.  I did some searching around online for ways to find relevant images and found nothing.  I came up with this myself and so far isn't doing a great job, but most images have some relevance to what I'm searching for.  So unless I start writing a high-end image recognition engine, I feel this is the best I can do right now.

In the end, the speed/word filtering trade-offs of the two branches I feel favor the python3 branch.  While it doesn't filter words as well, the speed of both the filtering and parallel HTTP requests far outweigh the reduced word filtering.  I haven't merged it into master yet, but I think that would ultimately be the endgame here.

Dependencies
------------

I haven't built this from a clean machine yet, so let me know of any missing dependencies.

* <b>master</b>: NLTK, PyGAM, numpy, bottle, python2`

* <b>python3</b>: bottle, python3`

Usage
-----

To run it, edit stories.py to have your CLIENT\_ID and then simply pass your client secret to it as a command line argument.

`python stories ${CLIENT\_SECRET}`

Using your favorite browser, pull up http://localhost:8000.  This is automatically direct you to login with your Instagram UIDP.  Once logged in, you'll be redirected back to the application.  Simply paste your short story and click GO.  Due to the internets incredible ability to tags images with the weird relations, the result is less of an image relevance depiction and more of a wartime cryptogram.  However, since I love cryptography, I feel it's fitting as a little personal tidbit of me as a programmer.

ENJOY!
------
