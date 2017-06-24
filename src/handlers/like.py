from util import BlogsHandler
import settings
from models import Blog


# like a blog
class LikeBlog(BlogsHandler):
    def get(self, blog_id, page):
        name = self.get_cookie()
        blog = Blog.get_by_id(int(blog_id))
        # check if user has liked the post
        if not blog.check_like(name):
            like = str(blog.like)+','+name
            blog.like = like
            blog.put()
        # tell user react page
        if page == '0':
            url = '/'
        else:
            url = self.url_from_num(blog_id)
        self.redirect(url)


# like a blog
class UnlikeBlog(BlogsHandler):
    def get(self, blog_id, page):
        name = self.get_cookie()
        blog = Blog.get_by_id(int(blog_id))
        # check if user has liked the post
        if blog.check_like(name):
            like_list = str(blog.like).split(',')
            name_index = like_list.index(str(name))
            like_list.pop(name_index)
            str_like = ','.join(like_list)
            blog.like = str_like
            blog.put()
        # tell user react page
        if page == '0':
            url = '/'
        else:
            url = self.url_from_num(blog_id)
        self.redirect(url)
