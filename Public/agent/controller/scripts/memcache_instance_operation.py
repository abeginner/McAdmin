import sys
import os.path
import json
import ansible.playbook
from ansible.inventory import Inventory
from ansible import callbacks
from ansible import utils

sys.path.append("..")
from contrib import get_ansible_conf

class PlayBook(object):
    
    def __init__(self, playbook, parameter):
        self.playbook = playbook
        self.parameter = parameter
        """
        the meaning  of parameters:
        0: the ip address of memcahce host
        """
        self._basedir = os.path.dirname(os.path.abspath(__file__))

    def __call__(self):
        playbook = os.path.join(self._basedir, self.playbook)
        ansible_conf = get_ansible_conf()
        remote_user = ansible_conf['remote_user']
        remote_pass = ansible_conf['remote_pass']
        private_key_file = None
        if ansible_conf.has_key('private_key_file'):
            private_key_file = ansible_conf['private_key_file']
        host = self.parameter[0]
        operation = self.parameter[1]
        if len(self.parameter) == 3:
            obj = 'single'
            port = self.parameter[2]
            extra_vars = {"port":port, "operation":operation, "obj":obj}
        else:
            obj = 'all'
            extra_vars = {"operation":operation, "obj":obj}
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats,verbose=utils.VERBOSITY)
        if not private_key_file:
            res=ansible.playbook.PlayBook(
                                          inventory=Inventory([host]),
                                          playbook=playbook,
                                          remote_user=remote_user,
                                          remote_pass=remote_pass,
                                          extra_vars=extra_vars,
                                          stats=stats,
                                          sudo=True,
                                          sudo_user='root',
                                          sudo_pass=remote_pass,
                                          callbacks=playbook_cb,
                                          runner_callbacks=runner_cb
                                          ).run()
        else:
            res=ansible.playbook.PlayBook(
                                          inventory=Inventory([host]),
                                          playbook=playbook,
                                          remote_user=remote_user,
                                          remote_pass=remote_pass,
                                          private_key_file=private_key_file,
                                          extra_vars=extra_vars,
                                          stats=stats,
                                          sudo=True,
                                          sudo_user='root',
                                          sudo_pass=remote_pass,
                                          callbacks=playbook_cb,
                                          runner_callbacks=runner_cb
                                          ).run()
        return res   
        
        
def get_body(parameter):
    pb = PlayBook('playbooks/memcacheinstance_create.yml', parameter)
    return pb()        
        
        
        
        
        
        
        
