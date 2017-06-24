from util import BlogsHandler
import settings
from models import Blog
from models import Comment


# page to show an individual blog
class BlogPage(BlogsHandler):
    def get(self, blog_id, comment_id='0'):
        name = self.get_cookie()
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

    # deal with comment post/edit on the post
    def post(self, blog_id, comment_id='0'):
        name = self.get_cookie()
        comment = self.request.get("comment")
        edit_comment = self.request.get("edit_comment")
        url = self.url_from_num(blog_id)
        blog = Blog.get_by_id(int(blog_id))
        # new comment
        if name and comment:
            c = Comment(blog=blog,
                        name=name, comment=comment)
            c.put()
            self.redirect(url)
        # efit comment
        if name and edit_comment:
            c = Comment.get_by_id(int(comment_id))
            c.comment = edit_comment
            c.put()
            self.redirect(url)
        else:
            self.redirect('/signin/'+str(blog_id)+'/3')
