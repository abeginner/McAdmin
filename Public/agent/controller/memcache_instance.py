#-*-coding:utf-8-*-

from base import BaseController

class memcache_instance(BaseController):
        
    def create(self):
        print 'memcache_instance create() is called'
        self.action = 'py'
        self.script = 'memcache_instance_create.py'
        self.parameter_keys = ['host', 'port', 'max_memory', 'max_connection', 'is_bind']
        

def get_resources():
    return memcache_instance()