#-*-coding:utf-8-*-

from base import BaseController

class memcache_instance(BaseController):
        
    def create(self):
        print 'memcache_instance create() is called'
        self.action = 'py'
        self.script = 'memcache_host_create.py'
        self.parameter_keys = ['host']
        

def get_resources():
    return memcache_instance()