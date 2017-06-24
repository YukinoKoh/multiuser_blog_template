import os
import jinja2
import webapp2
import random
import string
import hashlib
import hmac
from google.appengine.ext import db

from models import User
from models import Blog
from models import Comment
from handlers import Signout
from handlers import Signin
from handlers import Signup
from handlers import MainPage
from handlers import UserPage
from handlers import BlogPage
from handlers import DeleteComment
from handlers import DeleteBlog
from handlers import NewBlog
from handlers import EditBlog
from handlers import LikeBlog
from handlers import UnlikeBlog
import settings
settings.init()

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Signup),
                               ('/signin', Signin),
                               ('/signin/([0-9]+)', Signin),
                               ('/signin/([0-9]+)/([0-9])', Signin),
                               ('/signout', Signout),
                               ('/newblog', NewBlog),
                               ('/like/([0-9]+)/([0-9]+)', LikeBlog),
                               ('/unlike/([0-9]+)/([0-9]+)', UnlikeBlog),
                               ('/blog/([0-9]+)', BlogPage),
                               ('/delete/([0-9]+)', DeleteBlog),
                               ('/~([a-zA-Z0-9_-]+)', UserPage),
                               ('/~([a-zA-Z0-9_-]+)/([0-9]+)', EditBlog),
                               ('/blog/([0-9]+)/([0-9]+)', BlogPage),
                               ('/commentdelete/([0-9]+)/([0-9]+)',
                                DeleteComment)],
                              debug=True)
