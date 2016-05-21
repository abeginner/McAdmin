#-*-coding:utf-8-*-

import pprint
import glob
import sys
import re
import os, os.path
import logging

import eventlet
import routes
import routes.middleware
import webob.dec
import webob.exc
from eventlet import wsgi
from paste import deploy
from oslo.config import cfg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUB_PKG = os.path.join(os.path.dirname(BASE_DIR), 'public_pkg')
sys.path.append(PUB_PKG)
sys.path.append(BASE_DIR)
from RegEx import RegIp

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=os.path.join(BASE_DIR, 'logs/agent.log'),
                filemode='a')


class Server(object):
    
    def __init__(self, app=None, app_name=None, paste_conf=None):
        self._conf = None
        self._server = None
        self.app = app
        self.app_name = app_name
        self.paste_conf = paste_conf
        
    def _load_paste_app(self):
        logging.info("Loading %(app_name) from %(conf_file)",
                {'app_name':self.app_name, 'conf_file':self.paste_conf})
        try:
            app = deploy.loadapp("config:%s" % os.path.join(BASE_DIR, self.paste_conf), name=self.app_name)
            return app
        except (LookupError, ImportError) as e:
            logging.error(str(e))
            raise RuntimeError(str(e))

    
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
        wsgiapp = self._load_paste_app()
        if self._conf:
            max_size = 1024
            if self._conf['pool_size']:
                max_size = self._conf['pool_size']
                
            wsgi.server(sock=eventlet.listen((self._conf['bind_host'], self._conf['bind_port'])), site=wsgiapp, 
                        max_size=max_size, server_event=self._server)

          
class application(object):
    
    def __init__(self, app=None):
        self.mapper = None
        self.app = app
        self.con_dir = os.path.join(BASE_DIR, 'controller')
        self.controllers = []
        self._regist_controllers()
        self.controller = None
        self.controller_name = None

    @webob.dec.wsgify
    def __call__(self, request):  
        return self._router
    
    @classmethod
    def factory(cls, global_conf, **local_conf):
        return cls()
                
    def _regist_controllers(self):
        sources = glob.glob(self.con_dir + '/*.py')
        for source in sources:
            filename = os.path.splitext(os.path.split(source)[1])[0]
            if filename != 'base':
                self.controllers.append(filename)
        logging.info('regist controllers ' + str(self.controllers))
    
    def _get_controller(self, request):
        if not self.app:
            raise webob.exc.HTTPNotFound()
        if not isinstance(self.app, basestring):
            raise webob.exc.HTTPServerError()
        path = request.environ['PATH_INFO']
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
        if req_app != self.app:
            logging.info('the application ' + str(req_app) + ' not exist.')
            raise webob.exc.HTTPNotFound()
        if req_controller not in self.controllers:
            logging.info('the controller ' + str(req_controller) + ' not exist.')
            raise webob.exc.HTTPNotFound()
        self.controller_name = req_controller
        try:
            contrib = os.path.join(BASE_DIR, 'controller')
            sys.path.append(contrib)
            module = __import__(req_controller)
            self.controller =  getattr(module, "get_resources")()
            logging.info('load controller ' + str(req_controller) + ' success.')
            return 0
        except Exception, e:
            raise e
    
    @webob.dec.wsgify   
    def _get_router(self, request):
        self.mapper = routes.Mapper()
        rs = self._get_controller(request)
        if rs == 0 and self.controller:
            resource = '/' + self.app + '/' + self.controller_name
            self.mapper.connect(resource, controller=self.controller, action="index", conditions={'method':['GET']})
            self.mapper.connect(resource+"/{id}", controller=self.controller, action="show", conditions={'method':['GET']})
            self.mapper.connect(resource, controller=self.controller, action="create", conditions={'method':['POST']})
            self.mapper.connect(resource+"/{id}", controller=self.controller, action="update", conditions={'method':['POST']})
            self.mapper.connect(resource, controller=self.controller, action="delete", conditions={'method':['DELETE']})
        self._router = routes.middleware.RoutesMiddleware(self._dispatch, self.mapper)
        
    @staticmethod
    @webob.dec.wsgify
    def _dispatch(request):
        match_dict = request.environ['wsgiorg.routing_args'][1]
        if not match_dict:
            return webob.exc.HTTPNotFound()
        app = match_dict['controller']
        return app
    



