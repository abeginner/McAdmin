#!coding:utf-8

import webob.dec
import webob.exc
import json
import subprocess
import sys
import os.path
import logging

from webob import Response
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
   
    def __init__(self):
        pass
    
    @webob.dec.wsgify 
    def __call__(self, req):
        print 'BaseController __call__() is called.'
        return self.do_exec(req)
        
    def index(self):
        logging.info('action index is not define.')
        return webob.exc.HTTPNotFound()
    def show(self):
        logging.info('action show is not define.')
        return webob.exc.HTTPNotFound()
    def create(self):
        logging.info('action create is not define.')
        return webob.exc.HTTPNotFound()
    def update(self):
        logging.info('action update is not define.')
        return webob.exc.HTTPNotFound()
    def delete(self):
        logging.info('action delete is not define.')
        return webob.exc.HTTPNotFound()
    
    def get_parameter_values(self, req):
        print "get_parameter_values is called"
        parameter_values = []
        r_id = req.environ['wsgiorg.routing_args'][1].get('id', None)
        action = req.environ['wsgiorg.routing_args'][1]['action']
        if r_id:
            parameter_values.append(str(r_id))
        if action == 'update' or action == 'create':
            try:
                body = json.loads(req.environ['wsgi.input'].read())
                if not isinstance(body, dict):
                    return webob.exc.HTTPBadRequest(detail='request body must be dict and dumps by json.')
                for key in self.parameter_keys:
                    if body.has_key(key):
                        parameter_values.append(body[key])
                    else:
                        return webob.exc.HTTPBadRequest(detail='query string error parameter ' + str(key) + ' is not set.')
            except Exception, e:
                return webob.exc.HTTPInternalServerError(str(e))
        else:
            if req.environ.has_key('QUERY_STRING'):
                query_string_dict = parse_qs(req.environ['QUERY_STRING'])
                for key in self.parameter_keys:
                    if query_string_dict.has_key(key):
                        parameter_values.append(query_string_dict[key])
                    else:
                        return webob.exc.HTTPBadRequest(detail='query string error parameter ' + str(key) + ' is not set.')
        return parameter_values
   
    def _exec_shell(self, req):
        print '_exec_shell is called.'
        try:
            cmd = []
            cmd.append(self.path)
            response_body = {'stdout':[], 'stderr':None}
            response = Response(content_type='application/json', charset='json')
            script = os.path.join(os.path.join(CURRENT_DIR, 'scripts'), self.script)
            if not os.path.exists(script):
                return webob.exc.HTTPInternalServerError(detail='shell script not exist.')
            cmd.append(script)
            print cmd
            parameter = self.get_parameter_values(req)
            print parameter
            if isinstance(parameter, list):
                cmd += parameter
            else:
                return parameter
            fp_out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)           
            if fp_out.stderr != None:
                response_body['stderr'] = fp_out.stderr.read()
            if fp_out.stdout != None:
                for line in fp_out.stdout.readlines():
                    response_body['stdout'].append(line)
            response.status = 200
            response.body = json.dumps(response_body)
            return response
        except Exception, e:
            return webob.exc.HTTPInternalServerError(detail=str(e))
    
    def _exec_py(self, req):
        print '_exec_py is called.'
        try:
            scripts_path = os.path.join(CURRENT_DIR, 'scripts')
            response_body = {'stdout':[], 'stderr':None}
            response = Response(content_type='application/json', charset='json')
            script = os.path.join(scripts_path, self.script)
            if not os.path.exists(script):
                return webob.exc.HTTPInternalServerError(detail='shell script not exist.')
            sys.path.append(scripts_path)
            pkg_name = os.path.splitext(self.script)[0]
            module = __import__(pkg_name)
            func =  getattr(module, "get_body")
            parameter = self.get_parameter_values(req)
            if not isinstance(parameter, list):
                return parameter
            body = func(parameter)
            response_body['stdout'] = json.dump(body)
            response.status = 200
            response.body = json.dumps(response_body)
            return response
        except Exception, e:
            return webob.exc.HTTPInternalServerError(detail=str(e))
        
    def do_exec(self, req):
        self.parameter_keys = None
        self.action = None  #'shell', 'py', or 'ssh'.
        self.script = None  #shell scrpit or python script path, string.
        self.path = None  #if action='shell' it must be set, it means the exec path of shell script. 
        self.remote = None  # if action='ssh' it must be set, it means the ip address of remote host.  
                            # it takes from the request body or query string.
                                        
        if req.environ['CONTENT_TYPE'] != 'application/json':
            return webob.exc.HTTPBadRequest(detail='CONTENT_TYPE must set as application/json.')        
        action = req.environ['wsgiorg.routing_args'][1]['action']
        if action == 'index':
            self.index()
        elif action == 'show':
            self.show()
        elif action == 'create':
            self.create()
        elif action == 'update':
            self.update()
        elif action == 'delete':
            self.delete()
        else:
            return webob.exc.HTTPNotFound()
        
        controller_name = str(req.environ['wsgiorg.routing_args'][1].get('controller', None))
        action_name = str(req.environ['wsgiorg.routing_args'][1].get('action', None))
        if not self.action:
            msg = controller_name + ' method ' + action_name + ' self.action  attribute is not set.'
            return webob.exc.HTTPInternalServerError(detail=msg)
        if not isinstance(self.action, basestring):
            msg = controller_name + ' method ' + action_name + ' self.action  attribute must be type of basestring.'
            return webob.exc.HTTPInternalServerError(detail=msg)
        if self.action == 'shell':
            if not self.path:
                self.path = '/bin/bash'
            if not self.parameter_keys:
                self.parameter_keys = []
            if not self.script:
                msg = controller_name + ' method ' + action_name + ' self.script  attribute is not set.'
                return webob.exc.HTTPInternalServerError(detail=msg)
            return self._exec_shell(req)
        if self.action == 'py':
            if not self.parameter_keys:
                self.parameter_keys = []
            if not self.script:
                msg = controller_name + ' method ' + action_name + ' self.script  attribute is not set.'
                return webob.exc.HTTPInternalServerError(detail=msg)
            return self._exec_py(req)
        else:
            msg = controller_name + ' method ' + action_name + ' self.action is set as ' + str(self.action) + '. it must be basestring.'
            return webob.exc.HTTPInternalServerError(detail=msg)




       