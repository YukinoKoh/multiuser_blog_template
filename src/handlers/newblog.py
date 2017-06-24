from util import BlogsHandler
import settings
from models import User
from models import Blog


# page to create a new blog
class NewBlog(BlogsHandler):
    def get(self):
        # check if user signin properly
        if self.user:
            name = self.get_cookie()
            self.render_front(name=name)
        # let user signin to create a post
        else:
            self.redirect('/signout/1/1')

    def post(self):
        # check if user signin properly
        if self.user:
            title = self.request.get("title")
            content = self.request.get("content")
            name = self.get_cookie()
            user = User.get_by_key_name(name)
            like = str(name)
            if title and content:
                blog = Blog(user=user, name=name, title=title,
                            content=content, like=like)
                blog.put()
                blog_id = blog.key().id()
                url = self.url_from_num(str(blog_id))
                self.redirect(url)
            else:
                error = "Write both a subject and some content to create a post."
                self.render_front(name, title, content, error)
        # let user signin to create a post
        else:
            self.redirect('/signout/1/1')


# page to edit a blog
class EditBlog(BlogsHandler):
    def get(self, name, blog_id):
        # check if user signin properly
        if self.user:
            blog = Blog.get_by_id(int(blog_id))
            # check if the post belong to the user
            if name == self.get_cookie():
                if name == blog.name:
                    self.render_front(name=name, title=blog.title,
                                      content=blog.content, blog_id=blog_id)
            # error let them signin properly
            else:
                self.redirect('/signout/0/4')
        # error let them signin properly
        else:
            self.redirect('/signout/0/4')

    def post(self, name, blog_id):
        # check if user signin properly
        if self.user:
            title = self.request.get("title")
            content = self.request.get("content")
            # check if the post belong to the user
            if name == self.get_cookie():
                if title and content:
                    blog = Blog.get_by_id(int(blog_id))
                    blog.title = title
                    blog.content = content
                    blog.put()
                    self.redirect(self.url_from_num(blog_id))
                else:
                    error = "We need both a subject and some content"
                    self.render_front(name, title, content, error)
            # error let them signin properly
            else:
                self.redirect('/signin/0/4')
        # error let them signin properly
        else:
            self.redirect('/signin/0/4')
