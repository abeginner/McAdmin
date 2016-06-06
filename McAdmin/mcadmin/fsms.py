import logging

class MemcacheHostFSM(object):
    """
    this is a Finite-state machine(FSM), it use to manage the life cycle of MemcacheHost
    the meaning of statuses as below:
    0.Preparing: the begining of a MemcacheHost's life cycle.
    1.Initializing: the MemcacheHost is Initializing.
    2.Ready: the initializations of MemcacheHost is finished and ready to put into use.
    3.Online: the MemcacheHost is in use.
    4.Deleting: the MemcacheHost is deleting.
    5.Deleted: the MemcacheHost is deleted.
    """
    
    def __init__(self):
        self.memcache_hosts = {}
        
        self.status_list = ['Preparing', 'Initializing', 'Ready', 'Online', 'Deleting', 'Deleted']
        self.map = [[1], [2], [3, 4], [2], [5], [0]]
        
    def add(self, server_code, status):
        if self.memcache_hosts.has_key(server_code):
            raise Exception('host is exist')
        else:
            self.memcache_hosts[server_code] = status
            
    def add_by_model(self, host):
        if self.memcache_hosts.has_key(host['server_code']):
            raise Exception('host is exist')
        else:
            self.memcache_hosts[host['server_code']] = host['status']
 
    def delete(self, server_code):
        if not self.memcache_hosts.has_key(server_code):
            raise Exception('host not exist')
        else:
            return self.memcache_hosts.pop(server_code)
        
    def cheage_status_to(self, server_code, status):
        if not self.memcache_hosts.has_key(server_code):
            raise Exception('host not exist')
        else:
            if status in self.map[self.memcache_hosts[server_code]]:
                self.memcache_hosts[server_code] = status
                return True
            else:
                return False
    
    def get_status(self, server_code):
        if not self.memcache_hosts.has_key(server_code):
            raise Exception('host not exist')
        return self.memcache_hosts[server_code]

    def get_server_codes(self):
        return self.memcache_hosts.keys()
    
    def get_status_name(self, status):
        if status >= 0 and status <= 0 and isinstance(status, int):
            return self.status_list['status']
        else:
            return None



    