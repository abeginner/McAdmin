#-*-coding:utf-8-*-

from base import BaseController

class memcache_instance(BaseController):
        
    def update(self):
        print 'memcache_instance create() is called'
        self.action = 'py'
        self.script = 'memcache_instance_operation_single.py'
        self.parameter_keys = ['host', 'port', 'operation']

def get_resources():
    return memcache_instance()