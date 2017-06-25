from util import BlogsHandler


class Signout(BlogsHandler):
    def get(self, directory='0', message_num='0'):
        self.response.delete_cookie('user_id')
        self.redirect('/signin/'+directory+'/'+message_num)
