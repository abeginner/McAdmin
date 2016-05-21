#-*-coding:utf-8-*-

from base import BaseController

class helloworld(BaseController):
    
    def index(self, req):
        print 'helloworld index() is called'
        print req['PATH_INFO']
        self.request = req
        self.action = 'script'
        self.script = 'helloworld.sh'
        return self.do_exec()

def get_resources():
    return helloworld()