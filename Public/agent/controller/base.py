#!coding:utf-8

import webob.dec
import webob.exc
import json
import subprocess
import os.path
import logging

from webob import Request, Response
from cgi import parse_qs

def __init__():
    pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=os.path.join(BASE_DIR, 'logs/agent.log'),
                filemode='a')

class BaseController(object):
   
    def __init__(self, action='script', path = '/bin/bash'):
        self.action = action   #script or py
        self.request = None
        self.parameters = []
        self.script = None
        self.path = path
        self.start_response = None
        self.environ = None
        
    def index(self, req):
        logging.info('action index is not define.')
        return webob.exc.HTTPNotFound()
    def show(self, req, id):
        logging.info('action show is not define.')
        return webob.exc.HTTPNotFound()
    def create(self, req):
        logging.info('action create is not define.')
        return webob.exc.HTTPNotFound()
    def update(self, req, id):
        logging.info('action update is not define.')
        return webob.exc.HTTPNotFound()
    def delete(self, req, id):
        logging.info('action delete is not define.')
        return webob.exc.HTTPNotFound()
    
    def get_parameters(self):
        try:
            parameter_list = []
            if self.type != None:
                if self.request.environ.has_key('REQUEST_METHOD'):
                    if self.request.method == 'POST' or self.request.method == 'PUT':
                        if self.request.headers['Content-Type'] != 'application/json':
                            logging.info('Content-Type must set as application/json.')
                            raise webob.exc.HTTPBadRequest()
                        if self.request.environ.has_key('wsgi.input'):
                            obj = self.request.environ['wsgi.input'].read()
                            body = json.loads(obj)
                            for i in self.parameters:
                                if body.has_key(i):
                                    parameter_list.append(body[i])
                                else:
                                    raise webob.exc.HTTPBadRequest()
                    else:
                        if self.request.environ.has_key('QUERY_STRING'):
                            d = parse_qs(self.request.environ['QUERY_STRING'])  
                            for i in self.parameters:
                                if d.has_key(i):
                                    parameter_list.append(d[i])
                                else:
                                    raise webob.exc.HTTPBadRequest()
                            return parameter_list
                        else:
                            raise webob.exc.HTTPBadRequest()
            raise webob.exc.HTTPBadRequest()
        except Exception, e:
            return e
    
    def _exec_scripts(self):
        try:
            cmd = []
            cmd.append(self.path)
            script = os.path.join(os.path.join(CURRENT_DIR, 'scripts'), self.script)
            if not os.path.exists(script):
                raise webob.exc.HTTPInternalServerError(detail='shell script not exist.')
            cmd.addend(script)
            parameter = self.get_parameters()
            if isinstance(parameter, list):
                cmd += parameter
            else:
                return parameter
            fp_out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            response = Response(content_type='application/json', charset='json')
            fp_in = response.body_file
            if fp_out.stderr == None:
                fp_in.write(json.dump(fp_out.stdout.read()))
            else:
                fp_in.write(json.dump(fp_out.stderr.read()))
            return response(self.environ, self.start_response)
        except Exception, e:
            raise e
        
    def do_exec(self):
        try:
            if self.action == 'script':
                result = self._exec_scripts()
                return result
            else:
                msg = str(self.__class__) + ' type attribute is error, it must set as scripts or py'
                raise webob.exc.HTTPInternalServerError(detail=msg)
        except Exception, e:
            return e
            
       
    
    
