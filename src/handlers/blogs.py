from bloghandler import BlogsHandler
import settings
from models import User
from models import Blog


# page to layout all blogs
class MainPage(BlogsHandler):
    def get(self):
        # check if user signin
        if self.user:
            name = self.get_cookie()
        # or let them browse
        else:
            name = ''
        # show instruction if no blog
        if not User.get_by_key_name('Instruction'):
            name = 'Instruction'
            pw_hash = self.make_pw_hash(name, settings.SECRET)
            instruction = User(key_name=name, name=name, pw_hash=pw_hash)
            instruction.put()
        if User.get_by_key_name('Instruction').user_blogs.count() < 1:
            user_instruction = User.get_by_key_name('Instruction')
            Blog(user=user_instruction, name='Instruction', title='Sample post',
                 content='Give vent to what\'s in your mind...',
                 like=['Instruction']).put()
        blogs = Blog.all().order('-created')
        self.render("main.html", name=name, sitename=settings.sitename,
                    blogs=blogs)


# page to layout user's blogs
class UserPage(BlogsHandler):
    def get(self, blogger_name):
        # check if user signin
        if self.user:
            name = self.get_cookie()
        # or let them browse
        else:
            name = ''
        blogs = User.get_by_key_name(blogger_name).user_blogs
        self.render("user.html", name=name, sitename=settings.sitename,
                    blogger_name=blogger_name, blogs=blogs)


