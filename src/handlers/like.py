from util import BlogsHandler
import settings
from models import Blog


# like a blog
class LikeBlog(BlogsHandler):
    def get(self, blog_id, page):
        # check if user signin proplerly
        if self.user:
            name = self.get_cookie()
            # check if blog exist
            if self.exist_blog(blog_id):
                blog = Blog.get_by_id(int(blog_id))
                # check if user has liked the post
                if not blog.check_like(name):
                    like = str(blog.like)+','+name
                    blog.like = like
                    blog.put()
                # something wrong? user clicked too many times?
                else:
                    pass
                # tell user reacting page
                if page == '0':
                    url = '/'
                else:
                    url = self.url_from_num(blog_id)
                self.redirect(url)
            # the blog doesn't exist
            else:
                message = 'We can\'t find the blog.'
                self.render_message(message, name)
        # let user sign in to like post
        else:
            self.redirect('/signout/'+blog_id+'/2')


# like a blog
class UnlikeBlog(BlogsHandler):
    def get(self, blog_id, page):
        # check if user signin proplerly
        if self.user:
            name = self.get_cookie()
            # check if blog exist
            if self.exist_blog(blog_id):
                blog = Blog.get_by_id(int(blog_id))
                # check if user has liked the post
                if blog.check_like(name):
                    like_list = str(blog.like).split(',')
                    name_index = like_list.index(str(name))
                    like_list.pop(name_index)
                    str_like = ','.join(like_list)
                    blog.like = str_like
                    blog.put()
                # something wrong? user clicked too many times?
                else:
                    pass
                # tell user react page
                if page == '0':
                    url = '/'
                else:
                    url = self.url_from_num(blog_id)
                self.redirect(url)
            # the blog doesn't exist
            else:
                message = 'We can\'t find the blog.'
                self.render_message(message, name)
        # error let user to sign in properly
        else:
            self.redirect('/signout')
