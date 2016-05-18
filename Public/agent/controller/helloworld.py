#-*-coding:utf-8-*-

from base import BaseController

class helloworld(BaseController):
    
    def index(self, req):
        self.request = req
        self.action = 'script'
        self.script = 'helloworld.sh'
        return self.do_exec()

def get_resources():
    return helloworld()