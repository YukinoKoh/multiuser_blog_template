from util import BlogsHandler


class Signout(BlogsHandler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/signin/0')

