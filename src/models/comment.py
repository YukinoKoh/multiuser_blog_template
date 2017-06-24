from google.appengine.ext import db
from models import Blog

# Comment db
def comment_key(name='default'):
    return db.Key.from_path('comment', name)


class Comment(db.Model):
    blog = db.ReferenceProperty(Blog,
                                collection_name='blog_comments')
    name = db.TextProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

