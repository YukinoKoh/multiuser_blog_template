from util import BlogsHandler
import settings
from models import User


# page to sign in
class Signin(BlogsHandler):
    def get(self, blog_id='', message_num=''):
        name = self.get_cookie()
        message = ''
        # if user cookie valid, let the user in
        if name:
            self.redirect('/')
        # check if user directed with error message
        if message_num:
            message = self.message_from_num(message_num)
        # render signin page
        self.render("signin.html", sitename=settings.sitename, message=message)

    def post(self, blog_id='0', message_num=''):
        name = self.request.get("name")
        pw = self.request.get("pw")
        # check user has entered name and pw
        if name and pw:
            user = User.by_name(name)
            # check if name and password is valid
            if user and self.valid_pw(user, pw):
                # let user sign in to appropriate page
                self.set_cookie(name)
                url = self.url_from_num(blog_id)
                self.redirect(url)
        # if name and pw is wrong, show error
        error = 'Username or password seems wrong.'
        params = dict(sitename=settings.sitename, error=error, name=name,
                      pw=pw)
        self.render('signin.html', **params)

    # return prompt message in signin page
    def message_from_num(self, message_num):
        num = int(message_num)
        message = ''
        if num == 1:
            message = 'Sign in or sign up tp create a post'
        if num == 2:
            message = 'Sign in or sign up to like posts'
        if num == 3:
            message = 'Sign in or sign up to comment on posts'
        return message

