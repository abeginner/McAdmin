#-*-coding:utf-8-*-

from base import BaseController

class memcache_host(BaseController):
        
    def create(self):
        print 'memcache_host create() is called'
        self.action = 'py'
        self.script = 'memcache_host_create.py'
        

def get_resources():
    return memcache_host()