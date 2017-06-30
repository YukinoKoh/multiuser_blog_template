from bloghandler import BlogsHandler


def signin_required(func):
    """
    A decorator to confirm a user is signed in or redirect as needed.
    """
    def signin(self, *args, **kwargs):
        # Redirect to login if user not logged in, else execute func.
        if not self.user:
            self.redirect('signout/1/1')
        else:
            func(self, *args, **kwargs)
    return signin
