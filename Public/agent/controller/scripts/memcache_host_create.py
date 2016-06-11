#!/usr/bin/env python

import sys
import os.path
import json
import ansible.playbook
from ansible.inventory import Inventory
from ansible import callbacks
from ansible import utils

sys.path.append("..")
from contrib import get_ansible_conf

class PlayBooks(object):
    
    def __init__(self, playbook, parameter):
        self.playbook = playbook
        self.parameter = parameter
        """
        0: the ip address of memcahce host
        1: remote_user
        2: remote_pass
        3: ssh_key
        """
        self._basedir = os.path.dirname(os.path.dirname(__file__))
    
    def __call__(self):
        playbook = os.path.join(self._basedir, self.playbook)
        host = self.parameter[0]
        ansible_conf = get_ansible_conf()
        remote_user = ansible_conf['remote_user']
        remote_pass = ansible_conf['remote_pass']
        private_key_file = None
        if ansible_conf.has_key('private_key_file'):
            private_key_file = ansible_conf['private_key_file']
        is_sudo = True
        if remote_user is 'root':
            is_sudo = False
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats,verbose=utils.VERBOSITY)
        if not private_key_file:
            res=ansible.playbook.PlayBook(
                                          inventory=Inventory([host]),
                                          playbook=self.playbook,
                                          remote_user=remote_user,
                                          remote_pass=remote_pass,
                                          extra_vars={'init_script':os.path.join(self._basedir, 'mcadmin/memcached')},
                                          stats=stats,
                                          sudo=is_sudo,
                                          callbacks=playbook_cb,
                                          runner_callbacks=runner_cb
                                          ).run()
        else:
            res=ansible.playbook.PlayBook(
                                          inventory=Inventory([self.parameter[0]]),
                                          playbook=self.playbook,
                                          remote_user=remote_user,
                                          remote_pass=remote_pass,
                                          private_key_file=private_key_file,
                                          extra_vars={'init_script':os.path.join(self._basedir, 'mcadmin/memcached')},
                                          stats=stats,
                                          sudo=is_sudo,
                                          callbacks=playbook_cb,
                                          runner_callbacks=runner_cb
                                          ).run()
        return res
        

def get_body(parameter):
    pb = PlayBooks('playbooks/memcachehost_creste.yml', parameter)
    return pb()


      