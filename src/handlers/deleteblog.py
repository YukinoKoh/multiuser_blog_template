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
            blog = Blog.by_id(int(blog_id))
            # check if blog exists
            if blog:
                # check outh
                if name == blog.name:
                    title = blog.title
                    comments = blog.blog_comments
                    for c in comments:
                        c.delete()
                    blog.delete()
                    message = 'Your blog \''+title+'\' has been deleted.'
                    self.render_message(message, name)
                else:
                    self.render_error(name)
            # in case the blog doesn't exist
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
            c = Comment.get_by_id(int(comment_id))
            if c:
                # check auth
                if name == c.name:
                    c.delete()
            url = self.url_from_num(blog_id)
            self.redirect(url)
        # error, let user signout
        else:
            self.redirect('/signout/0/4')
