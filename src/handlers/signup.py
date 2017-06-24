import re
from util import BlogsHandler
import settings
from models import User

# page to sign up
class Signup(BlogsHandler):
    def get(self):
        # if valid cookie, let user in
        name = self.get_cookie()
        if name:
            self.redirect('/')
        else:
            self.render("signup.html", sitename=settings.sitename)

    # check if user inputs match with 're' condition
    def valid(self, pattern_re, text):
        return re.match(pattern_re, text)

    # register a user to User db
    def make_entity_user(self, name, pw, email=''):
        pw_hash = self.make_pw_hash(name, pw)
        user = User(key_name=name, name=name, pw_hash=pw_hash, email=email)
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
        params = dict(sitename=settings.sitename, name=name, pw=pw, verify=verify,
                      email=email)
        if not self.valid(name_re, name):
            params['name_error'] = 'It doesn\'t seem a valid name'
            have_error = True
        elif User.get_by_key_name(name):
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


