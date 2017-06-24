from util import BlogsHandler
import settings
from models import User
from models import Blog


# page to layout all blogs
class MainPage(BlogsHandler):
    def get(self):
        if not User.get_by_key_name('Instruction'):
            name = 'Instruction'
            pw_hash = self.make_pw_hash(name, settings.SECRET)
            instruction = User(key_name=name, name=name, pw_hash=pw_hash)
            instruction.put()
        if User.get_by_key_name('Instruction').user_blogs.count() < 1:
            Blog(user=instruction, name='Instruction', title='Write a post',
                 content='Give vent to what\'s in your mind...',
                 like='Instruction').put()
        blogs = Blog.all().order('-created')
        name = self.get_cookie()
        self.render("main.html", name=name, sitename=settings.sitename,
                    blogs=blogs)


# page to layout user's blogs
class UserPage(BlogsHandler):
    def get(self, blogger_name):
        name = self.get_cookie()
        blogs = User.get_by_key_name(blogger_name).user_blogs
        self.render("user.html", name=name, sitename=settings.sitename,
                    blogger_name=blogger_name, blogs=blogs)


