from google.appengine.ext import db
from models import User


# Blog db
def blog_key(name='default'):
    return None
    # return db.Key.from_path('posts', name)


class Blog(db.Model):
    user = db.ReferenceProperty(User,
                                collection_name='user_blogs')
    name = db.StringProperty(required=True)
    title = db.TextProperty(required=True)
    content = db.TextProperty(required=True)
    like = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)

    # return blog entity of the given id
    @classmethod
    def by_id(cls, uid):
        return Blog.get_by_id(uid, parent=blog_key())

    # return the first entity of the given name
    @classmethod
    def by_name(cls, name):
        b = Blog.all().filter('name =', name).get()
        return b

    def check_like(cls, name):
        like_list = str(cls.like).split(',')
        return name in like_list

    def count_like(cls):
        like_list = str(cls.like).split(',')
        count = len(like_list)-1
        if count > 0:
            return count
        else:
            return ''

    # return style of like icon
    def get_like_style(cls, name):
        style = ''
        if cls.check_like(name):
            style = 'liked'
        else:
            style = 'like'
        return style

    # return like icon
    def get_like_icon(cls, name):
        icon = ''
        if not cls.check_like(name):
            icon = '-empty'
        return icon

    # return a path to like/unlike function
    def get_like_or_unlike(cls, name):
        url = ''
        if cls.check_like(name):
            url = 'unlike'
        else:
            url = 'like'
        return url

    # return message for users trying to like their own post
    def get_like_warning(cls, name):
        warning = ''
        if name:
            warning = 'You can\'t like your own post'
        return warning

