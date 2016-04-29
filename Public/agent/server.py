#-*-coding:utf-8-*-

from oslo.config import cfg

from eventlet import wsgi
import eventlet

import sys
import re
import os, os.path
import logging


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUB_PKG = os.path.join(os.path.dirname(BASE_DIR), 'public_pkg')
sys.path.append(PUB_PKG)
from RegEx import RegIp

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode=os.path.join(BASE_DIR, '/logs/agent.log'))

class Server(object):
    
    def __init__(self):
        self._conf = None
        self._server = None
        
    def _get_config(self):
        # 声明多配置项模式
        common_opts = [
                cfg.StrOpt('196.168.134.129',  
                   default='0.0.0.0',  
                   help='ip address of controller node.'),
                cfg.IntOpt('node_id',  
                   default=1,  
                   help='the agent id.'),
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
        try:
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
            if RegIp(CONF.controller):
                result['bind_host'] = CONF.controller
            else:
                error_msg = 'controller config error in agent.cfg.'
                logging.error(error_msg)
            if CONF.node_id >= 1 and CONF.node_id <= 65535:
                result['node_id'] = CONF.node_id
            else:
                error_msg =  'node_id config error in agent.cfg, it must in range of(1, 65535).'
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
        except Exception, e:
            return e
    
    def _application(self, env, start_response):
        

    def start(self):
        
            
#自定义异常

        
        
        
        
        
        
        
          