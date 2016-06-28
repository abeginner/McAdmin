#-*-coding:utf-8-*-

from base import BaseController

class helloworld(BaseController):
    
    def index(self):
        self.action = 'shell'
        self.script = 'helloworld.sh'

def get_resources():
    return helloworld()