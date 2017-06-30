from bloghandler import BlogsHandler
import settings
from models import Blog
from models import Comment


# page to show an individual blog
class BlogPage(BlogsHandler):
    def get(self, blog_id, comment_id='0'):
        # check signin condition
        if self.user:
            name = self.get_cookie()
        # if not signin, browse as anonymous
        else:
            name = ''
        blog = Blog.get_by_id(int(blog_id))
        if blog:
            content = blog.content.replace('\n', '<br>')
            comments = blog.blog_comments
            comment_id = int(comment_id)
            self.render("blog.html", name=name, sitename=settings.sitename,
                        blog=blog, content=content, comments=comments,
                        comment_id=comment_id)
        else:
            message = "We can't find the post."
            self.render("message.html", name=name, sitename=settings.sitename,
                        message=message)

    # deal with post/edit comment
    def post(self, blog_id, comment_id='0'):
        # check if user signin properly to act
        if self.user:
            comment = self.request.get("comment")
            edit_comment = self.request.get("edit_comment")
            url = self.url_from_num(blog_id)
            blog = Blog.get_by_id(int(blog_id))
            name = self.get_cookie()
            # new comment
            if comment:
                c = Comment(blog=blog,
                            name=name, comment=comment)
                c.put()
                self.redirect(url)
            # efit comment
            elif edit_comment:
                c = Comment.get_by_id(int(comment_id))
                c.comment = edit_comment
                c.put()
                self.redirect(url)
            # if no input, just render the post
            else:
                self.redirect('/blog/'+str(blog_id))
        # let user signed to comment
        else:
            self.redirect('/signin/'+str(blog_id)+'/3')
