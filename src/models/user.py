from google.appengine.ext import db


# Database
# User db
def user_key(name='default'):
    return db.Key.from_path('users', name)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()
