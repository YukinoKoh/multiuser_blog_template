import os
import jinja2
import webapp2
import re
import random
import string
import hashlib
import hmac

import settings
from models import User


# handling templates with jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# make randam salt for password
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(settings.RANGE))

# return hased val for cookie
def hash_str(s):
    return hmac.new(settings.SECRET, s).hexdigest()


# Security ----------------------------
# base handler
class BlogsHandler(webapp2.RequestHandler):
    ''' handle blogs'''
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # return given string (user id) | hased id
    def make_secure_cookie(self, s):
        return "%s|%s" % (s, str(hash_str(s)))

    # return user id if it is valid
    def check_secure_cookie(self, h):
        hashed = h.split('|')
        if hash_str(hashed[0]) == hashed[1]:
            return hashed[0]

    def make_pw_hash(self, name, pw, salt=None):
        if not salt:
            salt = make_salt()
        h = hashlib.sha256(name+pw+salt).hexdigest()
        return '%s,%s' % (salt, h)

    def get_cookie(self):
        user_id = self.request.cookies.get('user_id')
        # if User.get_by_key_name(user_id):
        if user_id:
            name = self.check_secure_cookie(user_id)
            u = User.get_by_key_name(name)
            if  u:
                return name

    def set_cookie(self, name):
        self.response.headers['Content-Type'] = 'text/plain'
        cookie_val = self.make_secure_cookie(str(name))
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % ('user_id', cookie_val))

    def valid_pw(self, user, pw):
        pw_hash = user.pw_hash.split(',')[1]
        salt = user.pw_hash.split(',')[0]
        return pw_hash == hashlib.sha256(user.name+pw+salt).hexdigest()

    # render a front page to add/edit a blog
    def render_front(self, name="", title="", content="",
                     error="", blog_id=""):
        self.render("newblog.html", name=name, sitename=settings.sitename, title=title,
                    content=content, error=error, blog_id=blog_id)

    # render erroe page
    def render_error(self, name=""):
        message = 'You can edit/delete only your own post.'
        self.render("message.html", name=name, sitename=settings.sitename,
                    message=message)

    # render message page
    def render_message(self, message, name=""):
        self.render("message.html", name=name, sitename=settings.sitename,
                    message=message)

    # return url to redirect
    def url_from_num(self, blog_id):
        num = int(blog_id)
        url = ''
        if num == 0:
            url = '/'
        elif num == 1:
            url = '/newblog'
        else:
            url = '/blog/'+blog_id
        return url

