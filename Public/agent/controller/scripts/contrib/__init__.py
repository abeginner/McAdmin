import os.path

from oslo.config import cfg

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

def get_ansible_conf():
    conf_file = os.path.join(BASE_DIR, 'agent.cfg')
    common_opts = [
                cfg.StrOpt('remote_user',  
                   default='root',  
                   help='the ssh operator of ansible.'),
                 cfg.StrOpt('remote_pass',  
                   default='',  
                   help='the ssh password of ansible.'),
                cfg.StrOpt('private_key_file',  
                   default=None,  
                   help='the ssh private key file path.')]
    result={}
    CONF = cfg.CONF
    CONF.register_opts(common_opts)
    CONF(default_config_files=[conf_file])
    result['remote_user'] = CONF.remote_user
    result['remote_pass'] = CONF.remote_pass
    result['private_key_file'] = CONF.private_key_file
    return result