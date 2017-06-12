import os
import jinja2
import webapp2
import re
import random
import string
import hashlib
import hmac
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
sitename = 'Coffee Blog'


# Page handler
class Handler(webapp2.RequestHandler):
    # need to keep *a, NOT **a
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # **params means take extra param in python defult library
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # set cookie val
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))


# DB class object for user info
class User(db.Model):
    # set type
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    salt = db.StringProperty(required = True)
    email = db.StringProperty()
 
# create user key
def user_key(name = 'default'):
    return db.Key.from_path('users', name)

# Password handling
# hashing password and username
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(5))


# returns a sha256 hashed password of the format: 
# HASH(name + pw + salt), salt
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)


# check pw by comparing hashed pw
def valid_pw(name, pw, h):
    salt = h.split('|')[1]
    return  h.split('|')[0] == hashlib.sha256(name + pw + salt).hexdigest()


# ID handling
# returns hased val, combined SECRET and string
SECRET = 'imsupersecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


# Takes a string s -> s,HASH
def make_secure_val(s):
    return "%s|%s" %  (s, str(hash_str(s)))



# returns s if passed s, HASH are euqal
def check_secure_val(h):
    hashed = h.split('|')
    if hash_str(hashed[0]) == hashed[1]:
        return hashed[0]


class MainPage(Handler):
    def get(self):
        self.write(sitename)


class SignUp(Handler):
    def get(self):
        self.render("signup.html", sitename=sitename)
    
    def valid(self, pattern_re, text):
        return re.match(pattern_re, text)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        username_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        password_re = re.compile(r"^.{3,20}$")
        email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")

        have_error = False 
        params = dict(sitename=sitename, username = username, password=password, verify=verify,  email = email)

        if not self.valid(username_re, username):
            params['username_error'] = 'It doesn\'t seem a valid name'
            have_error = True
        elif User.all().filter('username =', username).get(): 
            params['username_error'] = 'This username already exists.'
            have_error = True
            
        if not self.valid(password_re, password):
            params['password_error'] = 'It doesn\'t seem a valid password'
            params['verify'] = ''
            have_error = True
        elif password != verify:
            params['verify_error'] = 'password does not match' 
            have_error = True

        if email and not self.valid(email_re, email):
            params['email_error'] = 'It doesn\'t seem a valid email'
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            # create entity for this user
            hashed = make_pw_hash(username, password).split('|')
            pw_hash = hashed[0]
            salt = hashed[1] 
            user = User(username=username, pw_hash=pw_hash, salt=salt, email=email)
            user.put()   

            # set userid cookie
            self.response.headers['Content-Type'] = 'text/plain'
            self.set_secure_cookie('user_id', str(user.key().id()))

            self.redirect('/welcome')

class Login(Handler):
    def get(self):
        self.render("login.html", sitename=sitename)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        if username and password:
            user = User.all().filter('username =', username).get() 
            if user:
                pw_hash = user.pw_hash
                salt = user.salt
                test = '%s|%s' % (pw_hash, salt)
                if valid_pw(username, password, test):
                    # set userid cookie
                    self.response.headers['Content-Type'] = 'text/plain'
                    self.set_secure_cookie('user_id', str(user.key().id()))
                    self.redirect('/welcome')
        error = 'Username or password seems wrong.'
        params = dict(sitename=sitename, error=error, username=username, password=password)
        self.render('login.html', **params)

class WelcomePage(Handler):
    def get(self):
        user_id = self.request.cookies.get('user_id')
        u_key = check_secure_val(user_id)
        if u_key:
            user = User.get_by_id(int(u_key))
            self.render("Welcome.html", username = user.username)
        else:
            self.redirect('/signup')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', SignUp),
                               ('/login', Login),
                               ('/welcome', WelcomePage)],
                              debug=True)
