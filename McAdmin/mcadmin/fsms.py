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
    6.Offline: there is some thing wrong with the MemcacheHost.
    """
    
    def __init__(self):
        self.memcache_hosts = {}
        
        self.status_list = ['Preparing', 'Initializing', 'Ready', 'Online', 'Deleting', 'Deleted']
        self.map = [[0, 1, 4], [0, 2], [3, 4], [2], [2,5], [0]]
        
    def add(self, server_code, status):
        if self.memcache_hosts.has_key(server_code):
            raise Exception('host is exist')
        else:
            self.memcache_hosts[server_code] = status
            
    def add_by_model(self, host):
        if self.memcache_hosts.has_key(host.server_code):
            raise Exception('host is exist')
        else:
            self.memcache_hosts[host.server_code] = host.status
 
    def delete(self, server_code):
        if not self.memcache_hosts.has_key(server_code):
            raise Exception('host not exist')
        else:
            return self.memcache_hosts.pop(server_code)
        
    def cheage_status_to(self, server_code, status):
        if not self.memcache_hosts.has_key(server_code):
            print self.memcache_hosts['server_code']
            print server_code
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
            return self.status_list[status]
        else:
            return None


class MemcacheInstanceFSM(object):
    """
    this is a Finite-state machine(FSM), it use to manage the life cycle of MemcacheHost
    the meaning of statuses as below:
    0.Preparing: the begining of a MemcacheHost's life cycle.
    1.Initializing: the MemcacheHost is Initializing.
    2.Ready: the initializations of MemcacheHost is finished and ready to put into use.
    3.Running: the MemcacheHost is in use.
    4.Deleting: the MemcacheHost is deleting.
    5.Deleted: the MemcacheHost is deleted.
    6.Stoped: there is some thing wrong with the MemcacheHost.
    """
    
    def __init__(self):
        self.memcache_instances = {}
        
        self.status_list = ['Preparing', 'Initializing', 'Ready', 'Running', 'Deleting', 'Deleted', 'Stoped']
        self.map = [[0, 1, 4], [0, 2], [3, 4], [2, 6], [2,5], [0], [2, 3]]
        
    def add(self, instance_code, status):
        if self.memcache_instances.has_key(instance_code):
            raise Exception('instance is exist')
        else:
            self.memcache_instances[instance_code] = status
            
    def add_by_model(self, instance):
        if self.memcache_instances.has_key(instance.instance_code):
            raise Exception('instance is exist')
        else:
            self.memcache_instances[instance.instance_code] = instance.status
 
    def delete(self, instance_code):
        if not self.memcache_instances.has_key(instance_code):
            raise Exception('host not exist')
        else:
            return self.memcache_instances.pop(instance_code)
        
    def cheage_status_to(self, instance_code, status):
        if not self.memcache_instances.has_key(instance_code):
            raise Exception('host not exist')
        else:
            if status in self.map[self.memcache_instances[instance_code]]:
                self.memcache_instances[instance_code] = status
                return True
            else:
                return False
    
    def get_status(self, instance_code):
        if not self.memcache_instances.has_key(instance_code):
            raise Exception('host not exist')
        return self.memcache_instances[instance_code]

    def get_server_codes(self):
        return self.memcache_hosts.keys()
    
    def get_status_name(self, status):
        if status >= 0 and status <= 0 and isinstance(status, int):
            return self.status_list[status]
        else:
            return None
    
    

    