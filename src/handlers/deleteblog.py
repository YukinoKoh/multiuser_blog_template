from util import BlogsHandler
import settings
from models import Blog
from models import Comment


# delete a blog
class DeleteBlog(BlogsHandler):
    def get(self, blog_id):
        # check user signin properly
        if self.user:
            name = self.get_cookie()
            # check if blog exist
            if self.exist_blog(blog_id):
                blog = Blog.get_by_id(int(blog_id))
                # check if user owns the blog
                if blog.check_auth(name):
                    title = blog.title
                    comments = blog.blog_comments
                    for c in comments:
                        c.delete()
                    blog.delete()
                    message = 'Your blog \''+title+'\' has been deleted.'
                    self.render_message(message, name)
                # error user tryingt o delete someone else's blog
                else:
                    self.redirect('/signout/0/4')
            # the blog doesn't exist
            else:
                message = 'We can\'t find the blog.'
                self.render_message(message, name)
        # error, let user signout
        else:
            self.redirect('/signout/0/4')

# delete a comment
class DeleteComment(BlogsHandler):
    def get(self, blog_id, comment_id):
        if self.user:
            name = self.get_cookie()
            # check if comment exist
            if exist_comment(comment_id):
                c = Comment.get_by_id(int(comment_id))
                # check auth
                if comment.check_auth(name):
                    c.delete()
                # error user tryingt o delete someone else's comment
                else:
                    self.redirect('/signout/0/4')
            # comment doesn't exist, maybe user click multiple times..
            else:
                pass
            url = self.url_from_num(blog_id)
            self.redirect(url)
        # error, let user signout
        else:
            self.redirect('/signout/0/4')
