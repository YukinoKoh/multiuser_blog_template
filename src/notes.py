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
sitename = 'Coffee Notes'
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


# Note db
def note_key(name='default'):
    return db.Key.from_path('posts', name)


class Note(db.Model):
    name = db.StringProperty(required=True)
    title = db.TextProperty(required=True)
    content = db.TextProperty(required=True)
    like = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)

    # return note entity of given id
    @classmethod
    def by_id(cls, uid):
        return Note.get_by_id(uid, parent=note_key())

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

    def get_style(cls, name):
        style = ''
        if cls.check_like(name):
            style = 'liked'
        else:
            style = 'like'
        return style

    def get_icon(cls, name):
        icon = ''
        if not cls.check_like(name):
            icon = '-empty'
        return icon

# Site front
# base handler
class NotesHandler(webapp2.RequestHandler):
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

    # render a front page to add/edit note
    def render_front(self, name="", title="", content="",
                     error="", note_id=""):
        self.render("newnote.html", name=name, sitename=sitename, title=title,
                    content=content, error=error, note_id=note_id)


# page to sign up
class Signup(NotesHandler):
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
class Signin(NotesHandler):
    def get(self):
        name = self.get_cookie()
        if name:
            self.redirect('/')
        else:
            self.render("signin.html", sitename=sitename)

    def post(self):
        name = self.request.get("name")
        pw = self.request.get("pw")
        if name and pw:
            user = User.by_name(name)
            if user and self.valid_pw(user, pw):
                self.set_cookie(name)
                self.redirect('/')
        error = 'Username or password seems wrong.'
        params = dict(sitename=sitename, error=error, name=name, pw=pw)
        self.render('signin.html', **params)


# sign out
class Signout(NotesHandler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/signin')


# page to layout all notes
class MainPage(NotesHandler):
    def get(self):
        name = self.get_or_signout_cookie()
        self.note_or_create()
        notes = Note.all().order('-created')
        self.render("notes.html", name=name, sitename=sitename, notes=notes)

    # check note and if note create one as instruction
    def note_or_create(self):
        if Note.all().count() == 0:
            name = 'Instruction'
            title = 'First coffee note'
            content = 'Next holiday plan will be ...'
            like = 'Instruction'
            note = Note(parent=note_key(), name=name, title=title,
                        content=content, like=like)
            note.put()
        else:
            pass


# page to show an individual note
class NotePage(NotesHandler):
    def get(self, note_id):
        name = self.get_or_signout_cookie()
        note = Note.by_id(int(note_id))
        content = note.content.replace('\n', '<br>')
        like = ''
        self.render("note.html", name=name, sitename=sitename, note=note,
                    content=content)


# page to add a new note
class NewNote(NotesHandler):
    def get(self):
        name = self.get_or_signout_cookie()
        self.render_front(name=name)

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        name = self.get_cookie()
        like = ''
        if title and content:
            note = Note(parent=note_key(), name=name, title=title,
                        content=content, like=like)
            note.put()
            note_id = note.key().id()
            self.redirect('/note/'+str(note_id))
        else:
            error = "We need both a subject and some content"
            self.render_front(name, title, content, error)


# page to edit a note
class EditNote(NotesHandler):
    def get(self, name, note_id):
        name = self.get_or_signout_cookie()
        note = Note.by_id(int(note_id))
        self.render_front(name=name, title=note.title, content=note.content,
                          note_id=note_id)

    def post(self, name, note_id):
        title = self.request.get("title")
        content = self.request.get("content")
        if title and content:
            note = Note.by_id(int(note_id))
            note.title = title
            note.content = content
            note.put()
            self.redirect('/note/'+str(note_id))
        else:
            error = "We need both a subject and some content"
            self.render_front(name, title, content, error)


# delete a note
class DeleteNote(NotesHandler):
    def get(self, note_id):
        name = self.get_or_signout_cookie()
        note = Note.by_id(int(note_id))
        if note:
            title = note.title
            note.delete()
            message = 'Your note \''+title+'\' has been deleted.'
        else:
            message = 'We can\'t find the note.'
        self.render("message.html", name=name, sitename=sitename,
                    message=message)


# like a note
class LikeNote(NotesHandler):
    def get(self, note_id, name, page_num):
        note = Note.by_id(int(note_id))
        if not note.check_like(name):
            like = str(note.like)+','+name
            note.like = like
            note.put()

        if int(page_num) == 0:
            url = '/note/'+note_id
        else:
            url = '/'
        self.redirect(url) 


# page for new uesr to have a glance
class About(NotesHandler):
    def get(self):
        name = self.get_cookie()
        if name:
            self.redirect('/')
        else:
            self.render('about.html', sitename=sitename)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Signup),
                               ('/signin', Signin),
                               ('/signout', Signout),
                               ('/newnote', NewNote),
                               ('/delete/([0-9]+)', DeleteNote),
                               ('/like/([0-9]+)/([a-zA-Z0-9_-]+)/([0-9])', LikeNote),
                               ('/note/([0-9]+)', NotePage),
                               ('/u-([a-zA-Z0-9_-]+)/([0-9]+)', EditNote),
                               ('/about', About)],
                              debug=True)
