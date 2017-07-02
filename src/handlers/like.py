from bloghandler import BlogsHandler
import settings
from models import Blog


def return_url(blog_id, page):
    if page == '0':
        url = '/'
    else:
        url = self.url_from_num(blog_id)
    return url

# like a blog
class LikeBlog(BlogsHandler):
    def get(self, blog_id, page):
        if not self.user:
            self.redirect('signout/1/2')
        name = self.get_cookie()
        # check if blog exist
        if self.exist_blog(blog_id):
            blog = Blog.get_by_id(int(blog_id))
            # check if author tries to like own post
            if blog.name == name:
                 pass
            else:
                # check if user has liked the post
                if not blog.check_like(name):
                    like_list = blog.like
                    like_list.append(str(name))
                    blog.like = like_list
                    blog.put()
                # something wrong? user clicked too many times?
                else:
                    pass
            url = return_url(blog_id,  page)
            self.redirect(url)
        # the blog doesn't exist
        else:
            message = 'We can\'t find the blog.'
            self.render_message(message, name)


# Unlike a blog
class UnlikeBlog(BlogsHandler):
    def get(self, blog_id, page):
        name = self.get_cookie()
        # check if blog exist
        if self.exist_blog(blog_id):
            blog = Blog.get_by_id(int(blog_id))
            # check if user has liked the post
            if blog.check_like(name):
                like_list = blog.like
                name_index = like_list.index(str(name))
                like_list.pop(name_index)
                blog.like = like_list
                blog.put()
            # something wrong? user clicked too many times?
            else:
                pass
            # tell user react page
            url = return_url(blog_id,  page)
            self.redirect(url)
            # the blog doesn't exist
        else:
            message = 'We can\'t find the blog.'
            self.render_message(message, name)
