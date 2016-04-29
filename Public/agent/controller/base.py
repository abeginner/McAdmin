#!coding:utf-8

import webob
import routes
import json
import os

from cgi import parse_qs

class BaseResource(object):
    
    type = None   #script or py
    env = None
    parameters = []
    body = None
    path = '/bin/bash'
    
    def __init__(self, env=None):
        pass
        
    def show(self):
        return webob.exc.HTTPNotFound()
    def index(self):
        return webob.exc.HTTPNotFound()
    def update(self):
        return webob.exc.HTTPNotFound()
    def delete(self): 
        return webob.exc.HTTPNotFound()
    def detail(self): 
        return webob.exc.HTTPNotFound()
    def create(self):
        return webob.exc.HTTPNotFound()
    
    def get_parameters(self):
        parameter_list = []
        if self.type != None:
            if self.env.has_key('REQUEST_METHOD'):
                if self.env['REQUEST_METHOD'] == 'POST' or self.env['REQUEST_METHOD'] == 'PUT':
                    raise NotImplementedError, 'no implement exception', 'set_body() method need implement'
                else:
                    if self.env.has_key('QUERY_STRING'):
                        d = parse_qs(self.env['QUERY_STRING'])  
                        for i in self.parameters:
                            if d.has_key(i):
                                parameter_list.append(d[i])
                            else:
                                return webob.exc.HTTPBadRequest()
                        return parameter_list
                    else:
                        return webob.exc.HTTPBadRequest()
    
    def exec_scripts(self):
        try:
            cmd = self.bash_path
            for parameter in self.get_parameters():
                cmd += ' '
                cmd += parameter
            result = os.popen(cmd).read()
            
        except Exception, e:
            return e
                    
    def do_exec(self):
        pass
            
    
    
