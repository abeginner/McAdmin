#-*-coding:utf-8-*-

from oslo.config import cfg

from eventlet import wsgi
import eventlet

import pprint
import glob
import sys
import re
import os, os.path
import logging

import routes
import webob.dec
import webob.exc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUB_PKG = os.path.join(os.path.dirname(BASE_DIR), 'public_pkg')
sys.path.append(PUB_PKG)
from RegEx import RegIp

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=os.path.join(BASE_DIR, 'logs/agent.log'),
                filemode='a')


class Server(object):
    
    def __init__(self):
        self._conf = None
        self._server = None
    
    @classmethod  
    def get_config(self):
        common_opts = [
                cfg.StrOpt('node',  
                   default='0.0.0.0',  
                   help='ip address of controller node.'),
                 cfg.StrOpt('bind_host',  
                   default='0.0.0.0',  
                   help='ip address to listen on.'),
                cfg.IntOpt('bind_port',  
                   default=9494,  
                   help='Port number to listen on.'),
                cfg.IntOpt('pool_size',  
                   default=1000,  
                   help='Size of eventlet greenpool.'),
                cfg.IntOpt('idc_id',  
                   default='0',  
                   help='id of idc.'),
            ]
        
        result = {}
        error_msg = None
        conf_file = os.path.join(BASE_DIR, 'agent.cfg')
        CONF = cfg.CONF
        CONF.register_opts(common_opts)
        CONF(default_config_files=[conf_file])
        if RegIp(CONF.bind_host):
            result['bind_host'] = CONF.bind_host
        else:
            error_msg = 'bind_host config error in agent.cfg.'
            logging.error(error_msg)
        if RegIp(CONF.node):
            result['node'] = CONF.node
        else:
            error_msg = 'node config error in agent.cfg.'
            logging.error(error_msg)
        if CONF.bind_port >= 1 and CONF.bind_port <= 65535:
            result['bind_port'] = CONF.bind_port
        else:
            error_msg = 'bind_port config error in agent.cfg, it must in range of(1, 65535).'
            logging.error(error_msg)
        if CONF.pool_size >= 1 and CONF.pool_size <= 9999:
            result['pool_size'] = CONF.pool_size
        else:
            error_msg = 'bind_port config error in agent.cfg, it must in range of(1, 65535).'
            logging.error(error_msg)
        if CONF.idc_id >= 1 and CONF.idc_id <= 9999:
            result['idc_id'] = CONF.idc_id
        else:
            error_msg = 'bind_port config error in agent.cfg, it must in range of(1, 65535).'
            logging.error(error_msg)
        if error_msg:
            raise Exception(error_msg)
        return result

    def start(self):
        try:
            self._conf = self.get_config()
        except Exception, e:
            raise e
        wsgiapp = application('memcache')
        if self._conf:
            max_size = 1024
            if self._conf['pool_size']:
                max_size = self._conf['pool_size']
                
            wsgi.server(sock=eventlet.listen((self._conf['bind_host'], self._conf['bind_port'])), site=wsgiapp, 
                        max_size=max_size, server_event=self._server)

          
class application(object):
    
    def __init__(self, app=None):
        self.mapper = routes.Mapper()
        self.app = app
        self.con_dir = os.path.join(BASE_DIR, 'controller')
        self.controllers = []
        self._regist_controllers()
        self.controller = None
        self.request = None

    @webob.dec.wsgify
    def __call__(self, request):
        self.request = request
        self._get_router()
        return self._router
                
    def _regist_controllers(self):
        sources = glob.glob(self.con_dir + '/*.py')
        for source in sources:
            filename = os.path.splitext(os.path.split(source)[1])[0]
            if filename != 'base':
                self.controllers.append(filename)
        logging.info('load controller ' + str(self.controllers))
    
    def _get_controller(self):
        if not self.app:
            raise webob.exc.HTTPNotFound()
        if not isinstance(self.app, basestring):
            raise webob.exc.HTTPServerError()
        path = self.request.environ['PATH_INFO']
        req_app = ''
        req_controller = ''
        n = 1
        for i in path[1::]:
            if i != '/':
                req_app += i
            else:
                n += 1
                break
            n += 1
        for i in path[n::]:
            if i != '/':
                req_controller += i
            else:
                break
            n += 1
        print self.request.environ['PATH_INFO']
        self.request.environ['PATH_INFO'] = path[n::]
        self.request.environ['RAW_PATH_INFO'] = self.request.environ['PATH_INFO']
        print self.request.environ['PATH_INFO']
        if req_app != self.app:
            logging.info('the application ' + str(req_app) + ' not exist.')
            raise webob.exc.HTTPNotFound()
        print req_controller
        if req_controller not in self.controllers:
            logging.info('the controller ' + str(req_controller) + ' not exist.')
            raise webob.exc.HTTPNotFound()
        
        try:
            contrib = os.path.join(BASE_DIR, 'controller')
            sys.path.append(contrib)
            module = __import__(req_controller)
            self.controller =  getattr(module, "get_resources")()
            logging.info('load controller ' + str(req_controller) + ' success.')
            return 0
        except Exception, e:
            raise e
        
    def _get_router(self):
        rs = self._get_controller()
        if rs == 0 and self.controller:
            self.mapper.connect("/",controller=self.controller, action="index", conditions={'method':['GET']})
            self.mapper.connect("/{id}/",controller=self.controller, action="show", conditions={'method':['GET']})
            self.mapper.connect("/",controller=self.controller, action="create", conditions={'method':['POST']})
            self.mapper.connect("/{id}/",controller=self.controller, action="update", conditions={'method':['POST']})
            self.mapper.connect("/",controller=self.controller, action="delete", conditions={'method':['DELETE']})
        self._router = routes.middleware.RoutesMiddleware(self._dispatch, self.mapper)
        
    def _dispatch(self):
        match = self.request.environ['wsgiorg.routing_args'][1]
        if not match:
            raise webob.exc.HTTPNotFound()
        controller = match['controller']
        action = match['action']
        if hasattr(controller,action):
            func = getattr(controller,action)
            logging.info('load ' + str(action) + ' from ' + str(controller) + ' success.')
            return func()
        else:
            logging.info('load ' + str(action) + ' from ' + str(controller) + ' fail.')
            raise webob.exc.HTTPNotFound()


