import os
import jinja2
import webapp2
import re
import random
import string
import hashlib
import hmac
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
sitename = 'Multiuser blog'
SECRET = 'imsupersecret'
RANGE = 5


# Security
# return hased val for cookie
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


# return given string (user id) | HASH
def make_secure_cookie(s):
    return "%s|%s" % (s, str(hash_str(s)))


# return user id if it is valid
def check_secure_cookie(h):
    hashed = h.split('|')
    if hash_str(hashed[0]) == hashed[1]:
        return hashed[0]


# make randam salt for password
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(RANGE))


def url_from_num(blog_id):
    num = int(blog_id)
    url = ''
    if num == 0:
        url = '/'
    elif num == 1:
        url = '/newblog'
    else:
        url = '/blog/'+blog_id
    return url


def message_from_num(blog_id):
    num = int(blog_id)
    message = ''
    if num == 1:
        message = 'Sign in or sign up tp create a post'
    if num == 2:
        message = 'Sign in or sign up to like posts'
    if num == 3:
        message = 'Sign in or sign up to comment on posts'
    return message

# Database
# User db
def user_key(name='default'):
    return db.Key.from_path('users', name)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    # return user entity of given name
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u



# Blog db
def blog_key(name='default'):
    return db.Key.from_path('posts', name)

class Blog(db.Model):
    name = db.StringProperty(required=True)
    title = db.TextProperty(required=True)
    content = db.TextProperty(required=True)
    like = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)
    # return blog entity of given id
    @classmethod
    def by_id(cls, uid):
        return Blog.get_by_id(uid, parent=blog_key())

    @classmethod
    def by_name(cls, name):
        b = Blog.all().filter('name =', name).get()
        return b

    def check_like(cls, name):
        like_list = str(cls.like).split(',')
        return name in like_list

    def count_like(cls):
        like_list = str(cls.like).split(',')
        count = len(like_list)-1
        if count > 0:
            return count
        else:
            return ''

    def get_like_style(cls, name):
        style = ''
        if cls.check_like(name):
            style = 'liked'
        else:
            style = 'like'
        return style

    def get_like_or_unlike(cls, name):
        url = ''
        if cls.check_like(name):
            url = 'unlike'
        else:
            url = 'like'
        return url

    def get_like_icon(cls, name):
        icon = ''
        if not cls.check_like(name):
            icon = '-empty'
        return icon

    def get_like_warning(cls, name):
        warning = ''
        if name:
            warning = 'You can\'t like your own post'
        else:
            warning = 'Sign in to like a post'
        return warning


# Comment db
def comment_key(name='default'):
    return db.Key.from_path('comment', name)


class Comment(db.Model):
    blog_id = db.StringProperty(required=True)
    name = db.TextProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, uid):
        return Comment.get_by_id(uid, parent=comment_key())


# Site front
# base handler
class BlogsHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get_cookie(self):
        user_id = self.request.cookies.get('user_id')
        if user_id:
            name = check_secure_cookie(user_id)
            return name

    def get_or_signout_cookie(self):
        name = self.get_cookie()
        if name:
            return name
        else:
            self.redirect('/signin')

    def set_cookie(self, name):
        self.response.headers['Content-Type'] = 'text/plain'
        cookie_val = make_secure_cookie(str(name))
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % ('user_id', cookie_val))

    def make_pw_hash(self, name, pw, salt=None):
        if not salt:
            salt = make_salt()
        h = hashlib.sha256(name+pw+salt).hexdigest()
        return '%s,%s' % (salt, h)

    def valid_pw(self, user, pw):
        pw_hash = user.pw_hash.split(',')[1]
        salt = user.pw_hash.split(',')[0]
        return pw_hash == hashlib.sha256(user.name+pw+salt).hexdigest()

    # render a front page to add/edit blog
    def render_front(self, name="", title="", content="",
                     error="", blog_id=""):
        self.render("newblog.html", name=name, sitename=sitename, title=title,
                    content=content, error=error, blog_id=blog_id)


# page to sign up
class Signup(BlogsHandler):
    def get(self):
        name = self.get_cookie()
        if name:
            self.redirect('/')
        else:
            self.render("signup.html", sitename=sitename)

    # check if user inputs match with 're' condition
    def valid(self, pattern_re, text):
        return re.match(pattern_re, text)

    # register user to User db
    def make_entity_user(self, name, pw, email):
        pw_hash = self.make_pw_hash(name, pw)
        user = User(name=name, pw_hash=pw_hash, email=email)
        user.put()
        return user

    def post(self):
        name = self.request.get("name")
        pw = self.request.get("pw")
        verify = self.request.get("verify")
        email = self.request.get("email")

        name_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        pw_re = re.compile(r"^.{3,20}$")
        email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")

        have_error = False
        params = dict(sitename=sitename, name=name, pw=pw, verify=verify,
                      email=email)
        if not self.valid(name_re, name):
            params['name_error'] = 'It doesn\'t seem a valid name'
            have_error = True
        elif User.by_name(name):
            params['name_error'] = 'This username already exists.'
            have_error = True

        if not self.valid(pw_re, pw):
            params['pw_error'] = 'It doesn\'t seem a valid password.'
            params['verify'] = ''
            have_error = True
        elif pw != verify:
            params['verify_error'] = 'password does not match.'
            have_error = True

        if email and not self.valid(email_re, email):
            params['email_error'] = 'It doesn\'t seem a valid email.'
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            user = self.make_entity_user(name, pw, email)
            self.set_cookie(user.name)
            self.redirect('/')


# page to sign in
class Signin(BlogsHandler):
    def get(self, blog_id='', message_num=''):
        name = self.get_cookie()
        message = ''
        if name:
            self.redirect('/')
        if message_num:
            message = message_from_num(message_num)
        self.render("signin.html", sitename=sitename, message=message)

    def post(self, blog_id='0', message_num=''):
        name = self.request.get("name")
        pw = self.request.get("pw")
        if name and pw:
            user = User.by_name(name)
            if user and self.valid_pw(user, pw):
                self.set_cookie(name)
                url = url_from_num(blog_id)
                self.redirect(url)
        error = 'Username or password seems wrong.'
        params = dict(sitename=sitename, error=error, name=name, pw=pw)
        self.render('signin.html', **params)


# sign out
class Signout(BlogsHandler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/signin/0/0')


# page to layout all blogs
class MainPage(BlogsHandler):
    def get(self):
        name = ''
        name = self.get_cookie()
        self.delete_or_create_init()
        blogs = Blog.all().order('-created')
        self.render("main.html", name=name, sitename=sitename, blogs=blogs)

    # check note and if note create one as instruction
    def delete_or_create_init(self):
        if Blog.all().count() == 0:
            name = 'Instruction'
            title = 'First blog'
            content = 'In my mind ...'
            like = 'Instruction'
            blog = Blog(parent=blog_key(), name=name, title=title,
                        content=content, like=like)
            blog.put()
        elif Blog.all().count() > 1:
            if Blog.by_name('Instruction'):
                b = Blog.by_name('Instruction')
                b.delete()


# page to layout user's blogs
class UserPage(BlogsHandler):
    def get(self, blogger_name):
        name = ''
        name = self.get_cookie()
        blogs = Blog.gql("WHERE name = '%s' ORDER BY created DESC" % blogger_name)
        self.render("user.html", name=name, sitename=sitename,
                    blogger_name=blogger_name, blogs=blogs)


# page to show an individual blog
class BlogPage(BlogsHandler):
    def get(self, blog_id, comment_id='0'):
        name = self.get_cookie()
        blog = Blog.by_id(int(blog_id))
        content = blog.content.replace('\n', '<br>')

        comments = Comment.gql("WHERE blog_id = '%s' ORDER BY created DESC" % blog_id)

        comment_id = int(comment_id)
        self.render("blog.html", name=name, sitename=sitename, blog=blog,
                    content=content, comments=comments,
                    comment_id=comment_id)

    def post(self, blog_id, comment_id='0'):
        name = self.get_cookie()
        comment = self.request.get("comment")
        edit_comment = self.request.get("edit_comment")
        url = url_from_num(blog_id)
        if name and comment:
            comment = Comment(parent=comment_key(), blog_id=blog_id,
                              name=name, comment=comment)
            comment.put()
            self.redirect(url)
        if name and edit_comment:
            c = Comment.by_id(int(comment_id)) 
            c.comment = edit_comment
            c.put()
            self.redirect(url)
        else:
            self.redirect('/signin/'+str(blog_id)+'/3')


# page to add a new blog
class NewBlog(BlogsHandler):
    def get(self):
        name = self.get_cookie()
        if name:
            self.render_front(name=name)
        else:
            self.redirect('/signin/1/1')

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        name = self.get_cookie()
        like = str(name)
        if title and content:
            blog = Blog(parent=blog_key(), name=name, title=title,
                        content=content, like=like)
            blog.put()
            blog_id = blog.key().id()
            url = url_from_num(str(blog_id))
            self.redirect(url)
        else:
            error = "Write both a subject and some content to create a post."
            self.render_front(name, title, content, error)


# page to edit a blog
class EditBlog(BlogsHandler):
    def get(self, name, blog_id):
        name = self.get_or_signout_cookie()
        blog = Blog.by_id(int(blog_id))
        self.render_front(name=name, title=blog.title, content=blog.content,
                          blog_id=blog_id)

    def post(self, name, blog_id):
        title = self.request.get("title")
        content = self.request.get("content")
        if title and content:
            blog = Blog.by_id(int(blog_id))
            blog.title = title
            blog.content = content
            blog.put()
            self.redirect('/blog/'+str(blog_id))
        else:
            error = "We need both a subject and some content"
            self.render_front(name, title, content, error)



# delete a blog
class DeleteBlog(BlogsHandler):
    def get(self, blog_id):
        name = self.get_or_signout_cookie()
        blog = Blog.by_id(int(blog_id))
        if blog:
            title = blog.title
            comments = Comment.gql("WHERE blog_id = '%s'" % blog_id)
            for c in comments:
                c.delete()
            blog.delete()
            message = 'Your blog \''+title+'\' has been deleted.'
        else:
            message = 'We can\'t find the blog.'
        self.render("message.html", name=name, sitename=sitename,
                    message=message)

# like a blog
class LikeBlog(BlogsHandler):
    def get(self, blog_id, name, page):
        blog = Blog.by_id(int(blog_id))
        if not blog.check_like(name):
            like = str(blog.like)+','+name
            blog.like = like
            blog.put()
        if page == '0':
            url = '/'
        else:
            url = url_from_num(blog_id) 
        self.redirect(url)


# like a blog
class UnlikeBlog(BlogsHandler):
    def get(self, blog_id, name, page):
        blog = Blog.by_id(int(blog_id))
        if blog.check_like(name):
            like_list = str(blog.like).split(',')
            name_index = like_list.index(str(name))
            like_list.pop(name_index)
            str_like = ','.join(like_list)
            blog.like = str_like
            blog.put()
        if page == '0':
            url = '/'
        else:
            url = url_from_num(blog_id) 
        self.redirect(url)


# delete a comment
class DeleteComment(BlogsHandler):
    def get(self, blog_id, comment_id):
        name = self.get_or_signout_cookie()
        c = Comment.by_id(int(comment_id))
        if c:
            c.delete()
            message = 'Your blog comment has been deleted.'
        else:
            pass
        url_from_num(blog_id)
        self.redirect(url)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Signup),
                               ('/signin', Signin),
                               ('/signin/([0-9]+)', Signin),
                               ('/signin/([0-9]+)/([0-9])', Signin),
                               ('/signout', Signout),
                               ('/newblog', NewBlog),
                               ('/like/([0-9]+)/([a-zA-Z0-9_-]+)/([0-9]+)', LikeBlog),
                               ('/unlike/([0-9]+)/([a-zA-Z0-9_-]+)/([0-9]+)', UnlikeBlog),
                               ('/blog/([0-9]+)', BlogPage),
                               ('/delete/([0-9]+)', DeleteBlog),
                               ('/~([a-zA-Z0-9_-]+)', UserPage),
                               ('/~([a-zA-Z0-9_-]+)/([0-9]+)', EditBlog),
                               ('/blog/([0-9]+)/([0-9]+)', BlogPage),
                               ('/commentdelete/([0-9]+)/([0-9]+)', DeleteComment)],
                              debug=True)
